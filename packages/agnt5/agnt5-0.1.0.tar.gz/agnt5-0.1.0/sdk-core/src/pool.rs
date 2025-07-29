//! Connection pooling and retry logic for reliable communication

use crate::error::{SdkError, SdkResult};
use crate::client::{WorkerCoordinatorClient, ClientConfig};
use crate::connection::{ConnectionManager, ConnectionConfig};
use std::sync::Arc;
use std::collections::VecDeque;
use tokio::sync::{Mutex, Semaphore};
use tokio::time::{Duration, Instant, sleep};
use tracing::{info, warn, debug};
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};

/// Configuration for connection pooling
#[derive(Debug, Clone)]
pub struct PoolConfig {
    /// Minimum number of connections to maintain
    pub min_connections: usize,
    /// Maximum number of connections allowed
    pub max_connections: usize,
    /// Maximum time to wait for an available connection
    pub connection_timeout: Duration,
    /// How long to keep idle connections alive
    pub idle_timeout: Duration,
    /// How often to clean up idle connections
    pub cleanup_interval: Duration,
    /// Retry configuration
    pub retry_config: RetryConfig,
}

impl Default for PoolConfig {
    fn default() -> Self {
        Self {
            min_connections: 2,
            max_connections: 10,
            connection_timeout: Duration::from_secs(30),
            idle_timeout: Duration::from_secs(300), // 5 minutes
            cleanup_interval: Duration::from_secs(60), // 1 minute
            retry_config: RetryConfig::default(),
        }
    }
}

/// Configuration for retry logic
#[derive(Debug, Clone)]
pub struct RetryConfig {
    /// Maximum number of retry attempts
    pub max_attempts: u32,
    /// Initial delay between retries
    pub initial_delay: Duration,
    /// Maximum delay between retries
    pub max_delay: Duration,
    /// Multiplier for exponential backoff
    pub backoff_multiplier: f64,
    /// Jitter factor to avoid thundering herd
    pub jitter_factor: f64,
}

impl Default for RetryConfig {
    fn default() -> Self {
        Self {
            max_attempts: 3,
            initial_delay: Duration::from_millis(100),
            max_delay: Duration::from_secs(30),
            backoff_multiplier: 2.0,
            jitter_factor: 0.1,
        }
    }
}

/// Statistics for connection pool monitoring
#[derive(Debug, Default)]
pub struct PoolStats {
    pub total_connections_created: AtomicU64,
    pub total_connections_destroyed: AtomicU64,
    pub active_connections: AtomicUsize,
    pub idle_connections: AtomicUsize,
    pub failed_connection_attempts: AtomicU64,
    pub successful_operations: AtomicU64,
    pub failed_operations: AtomicU64,
    pub average_connection_time: AtomicU64, // in milliseconds
}

/// A pooled connection wrapper
struct PooledConnection {
    pub connection_manager: ConnectionManager,
    pub created_at: Instant,
    pub last_used: Instant,
    pub use_count: u64,
}

impl PooledConnection {
    fn new(connection_manager: ConnectionManager) -> Self {
        let now = Instant::now();
        Self {
            connection_manager,
            created_at: now,
            last_used: now,
            use_count: 0,
        }
    }
    
    fn mark_used(&mut self) {
        self.last_used = Instant::now();
        self.use_count += 1;
    }
    
    fn is_idle(&self, idle_timeout: Duration) -> bool {
        self.last_used.elapsed() > idle_timeout
    }
    
    fn age(&self) -> Duration {
        self.created_at.elapsed()
    }
}

/// Connection pool for managing multiple worker coordinator connections
pub struct ConnectionPool {
    config: PoolConfig,
    client_config: ClientConfig,
    connection_config: ConnectionConfig,
    available_connections: Arc<Mutex<VecDeque<PooledConnection>>>,
    active_connections: Arc<AtomicUsize>,
    semaphore: Arc<Semaphore>,
    stats: Arc<PoolStats>,
    shutdown_signal: Arc<tokio::sync::Notify>,
}

impl ConnectionPool {
    /// Create a new connection pool
    pub fn new(
        pool_config: PoolConfig,
        client_config: ClientConfig,
        connection_config: ConnectionConfig,
    ) -> Self {
        let semaphore = Arc::new(Semaphore::new(pool_config.max_connections));
        
        Self {
            config: pool_config,
            client_config,
            connection_config,
            available_connections: Arc::new(Mutex::new(VecDeque::new())),
            active_connections: Arc::new(AtomicUsize::new(0)),
            semaphore,
            stats: Arc::new(PoolStats::default()),
            shutdown_signal: Arc::new(tokio::sync::Notify::new()),
        }
    }
    
    /// Start the connection pool and initialize minimum connections
    pub async fn start(&self) -> SdkResult<()> {
        info!("Starting connection pool with {} min connections", self.config.min_connections);
        
        // Pre-warm the pool with minimum connections
        for _ in 0..self.config.min_connections {
            match self.create_connection().await {
                Ok(conn) => {
                    let mut available = self.available_connections.lock().await;
                    available.push_back(conn);
                }
                Err(e) => {
                    warn!("Failed to create initial connection: {}", e);
                    // Continue trying to create other connections
                }
            }
        }
        
        // Start cleanup task
        self.start_cleanup_task();
        
        Ok(())
    }
    
    /// Get a connection from the pool
    pub async fn get_connection(self: &Arc<Self>) -> SdkResult<PooledConnectionHandle> {
        let start_time = Instant::now();
        
        // Acquire semaphore permit (limits total connections)
        let permit = self.semaphore
            .clone()
            .acquire_owned()
            .await
            .map_err(|_| SdkError::Connection("Failed to acquire connection permit".to_string()))?;
        
        // Try to get an existing connection
        let mut connection = {
            let mut available = self.available_connections.lock().await;
            available.pop_front()
        };
        
        // If no available connection, create a new one
        if connection.is_none() {
            match self.create_connection().await {
                Ok(conn) => connection = Some(conn),
                Err(e) => {
                    self.stats.failed_connection_attempts.fetch_add(1, Ordering::Relaxed);
                    return Err(e);
                }
            }
        }
        
        let mut conn = connection.unwrap();
        conn.mark_used();
        
        self.active_connections.fetch_add(1, Ordering::Relaxed);
        self.stats.average_connection_time.store(
            start_time.elapsed().as_millis() as u64,
            Ordering::Relaxed,
        );
        
        debug!("Connection acquired from pool");
        
        Ok(PooledConnectionHandle {
            connection: Some(conn),
            pool: self.clone(),
            permit: Some(permit),
        })
    }
    
    /// Execute an operation with retry logic
    pub async fn execute_with_retry<F, T, Fut>(&self, operation: F) -> SdkResult<T>
    where
        F: Fn() -> Fut + Send + Sync,
        Fut: std::future::Future<Output = SdkResult<T>> + Send,
        T: Send,
    {
        let mut attempt = 0;
        let mut delay = self.config.retry_config.initial_delay;
        
        loop {
            attempt += 1;
            
            match operation().await {
                Ok(result) => {
                    self.stats.successful_operations.fetch_add(1, Ordering::Relaxed);
                    return Ok(result);
                }
                Err(e) => {
                    if attempt >= self.config.retry_config.max_attempts {
                        self.stats.failed_operations.fetch_add(1, Ordering::Relaxed);
                        return Err(e);
                    }
                    
                    if !self.is_retryable_error(&e) {
                        self.stats.failed_operations.fetch_add(1, Ordering::Relaxed);
                        return Err(e);
                    }
                    
                    warn!("Operation failed (attempt {}), retrying in {:?}: {}", attempt, delay, e);
                    
                    // Apply jitter to avoid thundering herd
                    let jittered_delay = self.apply_jitter(delay);
                    sleep(jittered_delay).await;
                    
                    // Exponential backoff
                    delay = std::cmp::min(
                        Duration::from_millis(
                            (delay.as_millis() as f64 * self.config.retry_config.backoff_multiplier) as u64
                        ),
                        self.config.retry_config.max_delay,
                    );
                }
            }
        }
    }
    
    /// Get pool statistics
    pub fn get_stats(&self) -> &Arc<PoolStats> {
        &self.stats
    }
    
    /// Shutdown the connection pool gracefully
    pub async fn shutdown(&self) -> SdkResult<()> {
        info!("Shutting down connection pool");
        
        // Signal shutdown to cleanup task
        self.shutdown_signal.notify_waiters();
        
        // Close all available connections
        let mut available = self.available_connections.lock().await;
        while let Some(conn) = available.pop_front() {
            if let Err(e) = conn.connection_manager.shutdown().await {
                warn!("Error shutting down connection: {}", e);
            }
            self.stats.total_connections_destroyed.fetch_add(1, Ordering::Relaxed);
        }
        
        // Wait for active connections to be returned
        // In a real implementation, we might want to force close after a timeout
        
        info!("Connection pool shutdown complete");
        Ok(())
    }
    
    /// Create a new connection
    async fn create_connection(&self) -> SdkResult<PooledConnection> {
        let client = WorkerCoordinatorClient::new(self.client_config.worker_coordinator_endpoint.clone()).await?;
        let connection_manager = ConnectionManager::new(self.connection_config.clone(), client);
        
        self.stats.total_connections_created.fetch_add(1, Ordering::Relaxed);
        
        Ok(PooledConnection::new(connection_manager))
    }
    
    /// Return a connection to the pool
    async fn return_connection(&self, connection: PooledConnection) {
        // Check if connection is still healthy
        // In a real implementation, you might want to validate the connection
        
        self.active_connections.fetch_sub(1, Ordering::Relaxed);
        
        // If pool is at capacity, close the connection
        let current_idle = {
            let available = self.available_connections.lock().await;
            available.len()
        };
        
        if current_idle >= self.config.max_connections - self.active_connections.load(Ordering::Relaxed) {
            // Pool is full, close the connection
            if let Err(e) = connection.connection_manager.shutdown().await {
                warn!("Error closing excess connection: {}", e);
            }
            self.stats.total_connections_destroyed.fetch_add(1, Ordering::Relaxed);
        } else {
            // Return to pool
            let mut available = self.available_connections.lock().await;
            available.push_back(connection);
        }
    }
    
    /// Start the cleanup task for idle connections
    fn start_cleanup_task(&self) {
        let available_connections = self.available_connections.clone();
        let config = self.config.clone();
        let stats = self.stats.clone();
        let shutdown_signal = self.shutdown_signal.clone();
        
        tokio::spawn(async move {
            let mut cleanup_interval = tokio::time::interval(config.cleanup_interval);
            
            loop {
                tokio::select! {
                    _ = cleanup_interval.tick() => {
                        Self::cleanup_idle_connections(&available_connections, &config, &stats).await;
                    }
                    _ = shutdown_signal.notified() => {
                        debug!("Cleanup task shutting down");
                        break;
                    }
                }
            }
        });
    }
    
    /// Clean up idle connections
    async fn cleanup_idle_connections(
        available_connections: &Arc<Mutex<VecDeque<PooledConnection>>>,
        config: &PoolConfig,
        stats: &Arc<PoolStats>,
    ) {
        let mut available = available_connections.lock().await;
        let initial_count = available.len();
        
        // Keep minimum connections, remove idle ones beyond that
        let mut connections_to_remove = Vec::new();
        let mut kept_connections = VecDeque::new();
        
        while let Some(conn) = available.pop_front() {
            if kept_connections.len() < config.min_connections || !conn.is_idle(config.idle_timeout) {
                kept_connections.push_back(conn);
            } else {
                debug!("Removing idle connection (age: {:?}, idle: {:?})", 
                       conn.age(), conn.last_used.elapsed());
                connections_to_remove.push(conn);
            }
        }
        
        let kept_count = kept_connections.len();
        *available = kept_connections;
        stats.idle_connections.store(available.len(), Ordering::Relaxed);
        
        // Close removed connections outside the lock
        drop(available);
        
        for conn in connections_to_remove {
            if let Err(e) = conn.connection_manager.shutdown().await {
                warn!("Error closing idle connection: {}", e);
            }
            stats.total_connections_destroyed.fetch_add(1, Ordering::Relaxed);
        }
        
        let removed_count = initial_count - kept_count;
        if removed_count > 0 {
            debug!("Cleaned up {} idle connections", removed_count);
        }
    }
    
    /// Check if an error is retryable
    fn is_retryable_error(&self, error: &SdkError) -> bool {
        match error {
            SdkError::Connection(_) => true,
            SdkError::Grpc(status) => {
                // Retry on certain gRPC status codes
                matches!(
                    status.code(),
                    tonic::Code::Unavailable | 
                    tonic::Code::DeadlineExceeded | 
                    tonic::Code::Internal |
                    tonic::Code::ResourceExhausted
                )
            }
            SdkError::Timeout(_) => true,
            _ => false,
        }
    }
    
    /// Apply jitter to delay to prevent thundering herd
    fn apply_jitter(&self, delay: Duration) -> Duration {
        let jitter_ms = (delay.as_millis() as f64 * self.config.retry_config.jitter_factor) as u64;
        let jitter = fastrand::u64(0..=jitter_ms);
        delay + Duration::from_millis(jitter)
    }
}

/// Handle for a pooled connection that automatically returns to pool when dropped
pub struct PooledConnectionHandle {
    connection: Option<PooledConnection>,
    pool: Arc<ConnectionPool>,
    permit: Option<tokio::sync::OwnedSemaphorePermit>,
}

impl PooledConnectionHandle {
    /// Get a reference to the connection manager
    pub fn connection_manager(&mut self) -> Option<&mut ConnectionManager> {
        self.connection.as_mut().map(|c| &mut c.connection_manager)
    }
    
    /// Check if the handle has a valid permit (connection slot)
    pub fn has_permit(&self) -> bool {
        self.permit.is_some()
    }
}

impl Drop for PooledConnectionHandle {
    fn drop(&mut self) {
        if let Some(connection) = self.connection.take() {
            let pool = self.pool.clone();
            tokio::spawn(async move {
                pool.return_connection(connection).await;
            });
        }
        // Permit is automatically dropped, releasing the semaphore
    }
}

/// Utility functions for creating common pool configurations
pub mod pool_presets {
    use super::*;
    
    /// Create a pool configuration optimized for high throughput
    pub fn high_throughput() -> PoolConfig {
        PoolConfig {
            min_connections: 5,
            max_connections: 50,
            connection_timeout: Duration::from_secs(10),
            idle_timeout: Duration::from_secs(60),
            cleanup_interval: Duration::from_secs(30),
            retry_config: RetryConfig {
                max_attempts: 5,
                initial_delay: Duration::from_millis(50),
                max_delay: Duration::from_secs(10),
                backoff_multiplier: 1.5,
                jitter_factor: 0.2,
            },
        }
    }
    
    /// Create a pool configuration optimized for low latency
    pub fn low_latency() -> PoolConfig {
        PoolConfig {
            min_connections: 10,
            max_connections: 20,
            connection_timeout: Duration::from_secs(5),
            idle_timeout: Duration::from_secs(30),
            cleanup_interval: Duration::from_secs(15),
            retry_config: RetryConfig {
                max_attempts: 3,
                initial_delay: Duration::from_millis(25),
                max_delay: Duration::from_secs(2),
                backoff_multiplier: 1.2,
                jitter_factor: 0.1,
            },
        }
    }
    
    /// Create a pool configuration optimized for resource conservation
    pub fn resource_conservative() -> PoolConfig {
        PoolConfig {
            min_connections: 1,
            max_connections: 5,
            connection_timeout: Duration::from_secs(60),
            idle_timeout: Duration::from_secs(600), // 10 minutes
            cleanup_interval: Duration::from_secs(300), // 5 minutes
            retry_config: RetryConfig::default(),
        }
    }
}