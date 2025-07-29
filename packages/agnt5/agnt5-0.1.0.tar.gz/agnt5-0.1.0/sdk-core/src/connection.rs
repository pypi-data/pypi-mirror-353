//! Connection lifecycle management for worker coordinator streaming

use crate::error::{SdkError, SdkResult};
use crate::client::{WorkerCoordinatorClient, StreamingConnection, OwnedStreamingConnection};
use crate::pb::*;
use flume;
use tokio::time::{Duration, Instant, sleep};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use tracing::{info, warn, error, debug};
use tonic::Code;

/// Callback trait for handling connection events
#[async_trait::async_trait]
pub trait ConnectionCallback: Send + Sync {
    /// Called when connection is established (including reconnections)
    async fn on_connected(&self, service_msg_tx: &flume::Sender<ServiceMessage>) -> SdkResult<()>;
    
    /// Called when connection is lost
    async fn on_disconnected(&self, reason: &str) -> SdkResult<()>;
}

/// Configuration for connection management
#[derive(Debug, Clone)]
pub struct ConnectionConfig {
    /// Maximum number of reconnection attempts (0 = unlimited)
    pub max_reconnect_attempts: u32,
    /// Initial reconnection delay
    pub initial_reconnect_delay: Duration,
    /// Maximum reconnection delay
    pub max_reconnect_delay: Duration,
    /// Exponential backoff multiplier
    pub reconnect_backoff_multiplier: f64,
    /// Heartbeat interval for keep-alive
    pub heartbeat_interval: Duration,
    /// Connection timeout
    pub connection_timeout: Duration,
    /// Graceful shutdown timeout
    pub shutdown_timeout: Duration,
}

impl Default for ConnectionConfig {
    fn default() -> Self {
        Self {
            max_reconnect_attempts: 0, // Unlimited
            initial_reconnect_delay: Duration::from_millis(100),
            max_reconnect_delay: Duration::from_secs(30),
            reconnect_backoff_multiplier: 2.0,
            heartbeat_interval: Duration::from_secs(30),
            connection_timeout: Duration::from_secs(10),
            shutdown_timeout: Duration::from_secs(30),
        }
    }
}

/// Connection state tracking
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ConnectionState {
    /// Initial state, not connected
    Disconnected,
    /// Attempting to connect
    Connecting,
    /// Successfully connected and streaming
    Connected,
    /// Connection lost, attempting to reconnect
    Reconnecting,
    /// Graceful shutdown in progress
    ShuttingDown,
    /// Connection permanently closed
    Closed,
}

/// Statistics for connection health monitoring
#[derive(Debug, Default)]
pub struct ConnectionStats {
    pub total_connections: AtomicU64,
    pub reconnection_attempts: AtomicU64,
    pub successful_reconnections: AtomicU64,
    pub messages_sent: AtomicU64,
    pub messages_received: AtomicU64,
    pub last_heartbeat: Arc<tokio::sync::Mutex<Option<Instant>>>,
}

/// Manages the lifecycle of the streaming connection to the worker coordinator
pub struct ConnectionManager {
    config: ConnectionConfig,
    client: WorkerCoordinatorClient,
    state: Arc<tokio::sync::RwLock<ConnectionState>>,
    stats: Arc<ConnectionStats>,
    shutdown_signal: Arc<AtomicBool>,
    current_connection: Arc<tokio::sync::Mutex<Option<StreamingConnection>>>,
    callback: Option<Arc<dyn ConnectionCallback>>,
    service_registration: Option<ServiceRegistration>,
}

impl ConnectionManager {
    /// Create a new connection manager
    pub fn new(config: ConnectionConfig, client: WorkerCoordinatorClient) -> Self {
        Self {
            config,
            client,
            state: Arc::new(tokio::sync::RwLock::new(ConnectionState::Disconnected)),
            stats: Arc::new(ConnectionStats::default()),
            shutdown_signal: Arc::new(AtomicBool::new(false)),
            current_connection: Arc::new(tokio::sync::Mutex::new(None)),
            callback: None,
            service_registration: None,
        }
    }

    /// Set the service registration for connections
    pub fn set_service_registration(&mut self, registration: ServiceRegistration) {
        self.service_registration = Some(registration);
    }

    /// Set a callback for connection events
    pub fn set_callback(&mut self, callback: Arc<dyn ConnectionCallback>) {
        self.callback = Some(callback);
    }

    /// Get the current connection state
    pub async fn get_state(&self) -> ConnectionState {
        *self.state.read().await
    }

    /// Get connection statistics
    pub fn get_stats(&self) -> &Arc<ConnectionStats> {
        &self.stats
    }

    /// Start the connection with automatic reconnection
    /// Returns both the runtime message receiver and service message sender
    pub async fn start(&mut self) -> SdkResult<(flume::Receiver<RuntimeMessage>, flume::Sender<ServiceMessage>)> {
        info!("Starting connection manager");
        
        // Create a channel for runtime messages that will be shared across reconnections
        let (runtime_msg_tx, runtime_msg_rx) = flume::unbounded();
        
        // Create a channel for service messages that will be used to send to runtime
        let (service_msg_tx, service_msg_rx) = flume::unbounded();
        
        let mut connection_manager = self.clone_for_task();
        connection_manager.runtime_msg_tx = Some(runtime_msg_tx);
        connection_manager.service_msg_rx = Some(service_msg_rx);
        
        // Spawn the main connection management task
        // TODO: Fix Send trait issue
        // tokio::spawn(async move {
        //     connection_manager.connection_loop().await;
        // });

        Ok((runtime_msg_rx, service_msg_tx))
    }

    /// Send a service message through the current connection
    pub async fn send_message(&self, message: ServiceMessage) -> SdkResult<()> {
        let connection_guard = self.current_connection.lock().await;
        
        if let Some(connection) = connection_guard.as_ref() {
            connection.outgoing_tx.send_async(message).await
                .map_err(|_| SdkError::Connection("Failed to send message - channel closed".to_string()))?;
            
            self.stats.messages_sent.fetch_add(1, Ordering::Relaxed);
            debug!("Sent service message");
            Ok(())
        } else {
            Err(SdkError::Connection("No active connection".to_string()))
        }
    }

    /// Initiate graceful shutdown
    pub async fn shutdown(&self) -> SdkResult<()> {
        info!("Initiating graceful shutdown");
        
        {
            let mut state = self.state.write().await;
            *state = ConnectionState::ShuttingDown;
        }
        
        self.shutdown_signal.store(true, Ordering::Relaxed);
        
        // Wait for graceful shutdown with timeout
        let shutdown_timeout = tokio::time::timeout(
            self.config.shutdown_timeout,
            self.wait_for_shutdown(),
        );
        
        match shutdown_timeout.await {
            Ok(_) => {
                info!("Graceful shutdown completed");
                Ok(())
            }
            Err(_) => {
                warn!("Shutdown timeout exceeded, forcing close");
                {
                    let mut state = self.state.write().await;
                    *state = ConnectionState::Closed;
                }
                Ok(())
            }
        }
    }

    /// Wait for shutdown to complete
    async fn wait_for_shutdown(&self) {
        loop {
            let state = *self.state.read().await;
            if state == ConnectionState::Closed {
                break;
            }
            sleep(Duration::from_millis(100)).await;
        }
    }

    /// Clone for use in async tasks
    fn clone_for_task(&self) -> ConnectionManagerTask {
        ConnectionManagerTask {
            config: self.config.clone(),
            client: self.client.clone(),
            state: self.state.clone(),
            stats: self.stats.clone(),
            shutdown_signal: self.shutdown_signal.clone(),
            current_connection: self.current_connection.clone(),
            callback: self.callback.clone(),
            runtime_msg_tx: None, // Will be set later
            service_msg_rx: None, // Will be set later
            service_registration: self.service_registration.clone(),
        }
    }
}

/// Task-safe version of ConnectionManager for async execution
#[derive(Clone)]
struct ConnectionManagerTask {
    config: ConnectionConfig,
    client: WorkerCoordinatorClient,
    state: Arc<tokio::sync::RwLock<ConnectionState>>,
    stats: Arc<ConnectionStats>,
    shutdown_signal: Arc<AtomicBool>,
    current_connection: Arc<tokio::sync::Mutex<Option<StreamingConnection>>>,
    callback: Option<Arc<dyn ConnectionCallback>>,
    runtime_msg_tx: Option<flume::Sender<RuntimeMessage>>,
    service_msg_rx: Option<flume::Receiver<ServiceMessage>>,
    service_registration: Option<ServiceRegistration>,
}

impl ConnectionManagerTask {
    /// Main connection management loop
    async fn connection_loop(self) {
        let mut reconnect_attempts = 0u32;
        let mut reconnect_delay = self.config.initial_reconnect_delay;

        loop {
            // Check for shutdown signal
            if self.shutdown_signal.load(Ordering::Relaxed) {
                info!("Shutdown signal received, closing connection");
                break;
            }

            // Attempt to establish connection
            match self.establish_connection().await {
                Ok((shared_connection, owned_connection)) => {
                    info!("Worker successfully connected to AGNT5 runtime service");
                    reconnect_attempts = 0;
                    reconnect_delay = self.config.initial_reconnect_delay;
                    
                    // Store the shared connection
                    let shared_connection_clone = shared_connection.clone();
                    {
                        let mut conn_guard = self.current_connection.lock().await;
                        *conn_guard = Some(shared_connection);
                    }

                    // Update state to connected
                    {
                        let mut state = self.state.write().await;
                        *state = ConnectionState::Connected;
                    }

                    // Call the connection callback if set
                    if let Some(callback) = &self.callback {
                        // Use the connection's outgoing_tx directly for the callback
                        if let Err(e) = callback.on_connected(&shared_connection_clone.outgoing_tx).await {
                            warn!("Connection callback failed: {}", e);
                        }
                    }

                    // Start service message forwarding task
                    let service_forwarding_task = if let Some(service_msg_rx) = &self.service_msg_rx {
                        let outgoing_tx = shared_connection_clone.outgoing_tx.clone();
                        let service_rx = service_msg_rx.clone();
                        Some(tokio::spawn(async move {
                            while let Ok(service_message) = service_rx.recv_async().await {
                                if let Err(e) = outgoing_tx.send_async(service_message).await {
                                    debug!("Failed to forward service message: {}", e);
                                    break;
                                }
                            }
                            debug!("Service message forwarding task completed");
                        }))
                    } else {
                        None
                    };

                    // Handle the connection until it fails or shutdown
                    let disconnect_reason = self.handle_connection(owned_connection).await;
                    
                    // Cleanup forwarding task
                    if let Some(task) = service_forwarding_task {
                        task.abort();
                    }
                    
                    // Clear the connection
                    {
                        let mut conn_guard = self.current_connection.lock().await;
                        *conn_guard = None;
                    }

                    // Check if shutdown was requested
                    if self.shutdown_signal.load(Ordering::Relaxed) {
                        info!("Shutdown requested during connection handling");
                        break;
                    }

                    warn!("Connection lost: {}", disconnect_reason);
                    
                    // Call the disconnection callback if set
                    if let Some(callback) = &self.callback {
                        if let Err(e) = callback.on_disconnected(&disconnect_reason).await {
                            warn!("Disconnection callback failed: {}", e);
                        }
                    }
                    
                    // Update state for reconnection
                    {
                        let mut state = self.state.write().await;
                        *state = ConnectionState::Reconnecting;
                    }
                }
                Err(e) => {
                    // Provide more specific error messages based on the error type
                    match &e {
                        SdkError::Grpc(status) if status.code() == Code::Unimplemented => {
                            error!("Runtime service not available: WorkerCoordinatorService not found at endpoint. Is the AGNT5 runtime server running?");
                        }
                        SdkError::Connection(_) => {
                            error!("Network connection failed: {}. Check if the endpoint is correct and reachable.", e);
                        }
                        _ => {
                            error!("Failed to establish connection: {}", e);
                        }
                    }
                    reconnect_attempts += 1;
                    self.stats.reconnection_attempts.fetch_add(1, Ordering::Relaxed);

                    // Check if we've exceeded max attempts
                    if self.config.max_reconnect_attempts > 0 && 
                       reconnect_attempts >= self.config.max_reconnect_attempts {
                        error!("Max reconnection attempts exceeded, giving up");
                        break;
                    }

                    // Exponential backoff
                    sleep(reconnect_delay).await;
                    reconnect_delay = std::cmp::min(
                        Duration::from_millis(
                            (reconnect_delay.as_millis() as f64 * self.config.reconnect_backoff_multiplier) as u64
                        ),
                        self.config.max_reconnect_delay,
                    );
                }
            }
        }

        // Final state update
        {
            let mut state = self.state.write().await;
            *state = ConnectionState::Closed;
        }
        
        info!("Connection manager loop terminated");
    }

    /// Establish a new streaming connection
    async fn establish_connection(&self) -> SdkResult<(StreamingConnection, OwnedStreamingConnection)> {
        {
            let mut state = self.state.write().await;
            *state = ConnectionState::Connecting;
        }

        let mut client = self.client.clone();
        info!("Attempting to establish worker stream connection to runtime");
        
        // Use service registration if available, otherwise create a default one
        let registration = if let Some(registration) = &self.service_registration {
            info!("Using service registration with {} handlers", registration.handlers.len());
            registration.clone()
        } else {
            warn!("No service registration provided - creating default registration");
            ServiceRegistration {
                service_name: "sdk-core-worker".to_string(),
                version: "1.0.0".to_string(),
                handlers: vec![],
                endpoint: "worker-default".to_string(),
                protocol_version: "1.0".to_string(),
                supported_protocol_versions: vec!["1.0".to_string()],
                service_type: ServiceType::Function as i32,
                metadata: std::collections::HashMap::new(),
            }
        };
        
        let (shared_connection, owned_connection) = client.start_worker_stream(registration).await?;
        
        info!("Worker stream connection established - ready to process invocations");
        
        self.stats.total_connections.fetch_add(1, Ordering::Relaxed);
        
        Ok((shared_connection, owned_connection))
    }

    /// Handle an active connection until it disconnects
    async fn handle_connection(&self, owned_connection: OwnedStreamingConnection) -> String {
        let mut heartbeat_interval = tokio::time::interval(self.config.heartbeat_interval);
        let mut last_message_time = Instant::now();
        
        info!("Starting active connection handling loop");
        
        // Destructure the owned connection
        let OwnedStreamingConnection {
            mut incoming_rx,
            outgoing_rx,
            outgoing_tx,
            runtime_msg_tx,
            connection_id: _,
        } = owned_connection;
        
        // Spawn a task to forward outgoing messages from the flume channel to gRPC stream
        let outgoing_task = {
            let _outgoing_tx_clone = outgoing_tx.clone();
            tokio::spawn(async move {
                while let Ok(_service_message) = outgoing_rx.recv_async().await {
                    debug!("Forwarding outgoing service message to gRPC stream");
                    // In a real gRPC implementation, we would send this to the stream
                    // For now, we'll just log it since the gRPC stream sending is handled by tonic
                }
                debug!("Outgoing message forwarding task completed");
            })
        };
        
        // Main message processing loop
        loop {
            tokio::select! {
                // Handle incoming messages from runtime
                msg_result = incoming_rx.message() => {
                    match msg_result {
                        Ok(Some(runtime_message)) => {
                            last_message_time = Instant::now();
                            self.stats.messages_received.fetch_add(1, Ordering::Relaxed);
                            debug!("Received runtime message: {:?}", runtime_message.message_type);
                            
                            // Forward to runtime message handler
                            if let Err(e) = runtime_msg_tx.send_async(runtime_message).await {
                                warn!("Failed to forward runtime message: {}", e);
                                outgoing_task.abort();
                                return "Message forwarding failed".to_string();
                            }
                        }
                        Ok(None) => {
                            info!("Runtime closed the stream");
                            outgoing_task.abort();
                            return "Stream closed by runtime".to_string();
                        }
                        Err(e) => {
                            warn!("Error receiving message: {}", e);
                            outgoing_task.abort();
                            return format!("Receive error: {}", e);
                        }
                    }
                }
                
                // Send periodic heartbeats
                _ = heartbeat_interval.tick() => {
                    debug!("Sending heartbeat");
                    
                    // Update last heartbeat time
                    {
                        let mut last_heartbeat = self.stats.last_heartbeat.lock().await;
                        *last_heartbeat = Some(Instant::now());
                    }
                    
                    // TODO: Send actual heartbeat message through outgoing_tx
                    // For now, we'll just record the heartbeat
                }
                
                // Check for connection timeout
                _ = tokio::time::sleep(Duration::from_secs(30)) => {
                    if last_message_time.elapsed() > Duration::from_secs(60) {
                        warn!("Connection timeout - no messages received for 60 seconds");
                        outgoing_task.abort();
                        return "Connection timeout".to_string();
                    }
                }
                
                // Check for shutdown signal
                _ = async {
                    loop {
                        if self.shutdown_signal.load(Ordering::Relaxed) {
                            break;
                        }
                        tokio::time::sleep(Duration::from_millis(100)).await;
                    }
                } => {
                    info!("Shutdown signal received in connection handler");
                    outgoing_task.abort();
                    return "Graceful shutdown".to_string();
                }
            }
        }
    }
}