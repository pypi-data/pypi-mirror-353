//! Worker management and lifecycle

use crate::error::{SdkError, SdkResult};
use crate::client::WorkerCoordinatorClient;
use crate::stream_handler::{StreamHandler, StreamHandlerConfig, MessageRouter, InvocationHandler};
use crate::messages::SerializerEnum;
use crate::pb::*;
use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use tokio::sync::{RwLock, Mutex};
use tokio::time::{Duration, timeout};
use uuid::Uuid;
use tracing::{instrument, info, error, warn, Span};
use opentelemetry::{global, Context, KeyValue, propagation::Injector};
use opentelemetry::metrics::{Counter, Histogram, Meter};
use std::time::Instant;

/// Configuration for a durable worker
#[derive(Debug, Clone)]
pub struct WorkerConfig {
    pub service_name: String,
    pub version: String,
    pub worker_id: String,
    pub max_concurrent_invocations: u32,
    pub heartbeat_interval_seconds: u64,
    pub graceful_shutdown_timeout_seconds: u64,
}

impl WorkerConfig {
    pub fn new(service_name: String, version: String) -> Self {
        Self {
            service_name,
            version,
            worker_id: Uuid::new_v4().to_string(),
            max_concurrent_invocations: 10,
            heartbeat_interval_seconds: 30,
            graceful_shutdown_timeout_seconds: 30,
        }
    }
}

/// Handler trait for processing invocations
#[async_trait::async_trait]
pub trait Handler: Send + Sync {
    /// Process an invocation with the given context and input
    async fn invoke(&self, ctx: InvocationContext, input: Vec<u8>) -> SdkResult<Vec<u8>>;
}

/// Context provided to handlers during invocation
#[derive(Clone)]
pub struct InvocationContext {
    pub invocation_id: String,
    pub handler_name: String,
    pub state_manager: Arc<dyn StateManager>,
    pub span_context: Option<opentelemetry::trace::SpanContext>,
    // TODO: Add promise registry, external call manager, etc.
}

/// Trait for managing invocation state
#[async_trait::async_trait]
pub trait StateManager: Send + Sync {
    async fn get(&self, key: &str) -> SdkResult<Option<Vec<u8>>>;
    async fn set(&self, key: &str, value: Vec<u8>) -> SdkResult<()>;
    async fn delete(&self, key: &str) -> SdkResult<()>;
}

/// Shutdown state and task tracking for graceful shutdown
#[derive(Debug)]
struct WorkerShutdownState {
    /// Signal that shutdown has been requested
    shutdown_requested: AtomicBool,
    /// Number of active invocations
    active_invocations: AtomicU64,
    /// Running task handles for cleanup
    task_handles: Mutex<Vec<tokio::task::JoinHandle<()>>>,
}

impl WorkerShutdownState {
    fn new() -> Self {
        Self {
            shutdown_requested: AtomicBool::new(false),
            active_invocations: AtomicU64::new(0),
            task_handles: Mutex::new(Vec::new()),
        }
    }
}

/// Durable worker that registers with the coordinator and processes invocations
pub struct DurableWorker {
    config: WorkerConfig,
    client: WorkerCoordinatorClient,
    pub handlers: Arc<RwLock<HashMap<String, Arc<dyn Handler>>>>,
    state_manager: Arc<dyn StateManager>,
    stream_handler: Option<StreamHandler>,
    message_router: MessageRouter,
    shutdown_state: Arc<WorkerShutdownState>,
    metrics: WorkerMetrics,
}

impl DurableWorker {
    /// Create a new durable worker
    pub fn new(
        config: WorkerConfig,
        client: WorkerCoordinatorClient,
        state_manager: Arc<dyn StateManager>,
    ) -> Self {
        let meter = global::meter("sdk-core-worker");
        let metrics = WorkerMetrics::new(&meter);
        
        Self {
            config,
            client,
            handlers: Arc::new(RwLock::new(HashMap::new())),
            state_manager,
            stream_handler: Some(StreamHandler::new(
                StreamHandlerConfig::default(),
                SerializerEnum::Json(crate::messages::JsonSerializer)
            )),
            message_router: MessageRouter::new(),
            shutdown_state: Arc::new(WorkerShutdownState::new()),
            metrics,
        }
    }
    
    /// Create a new durable worker with custom stream handler config
    pub fn with_stream_config(
        config: WorkerConfig,
        client: WorkerCoordinatorClient,
        state_manager: Arc<dyn StateManager>,
        stream_config: StreamHandlerConfig,
        serializer: SerializerEnum,
    ) -> Self {
        let meter = global::meter("sdk-core-worker");
        let metrics = WorkerMetrics::new(&meter);
        
        Self {
            config,
            client,
            handlers: Arc::new(RwLock::new(HashMap::new())),
            state_manager,
            stream_handler: Some(StreamHandler::new(stream_config, serializer)),
            message_router: MessageRouter::new(),
            shutdown_state: Arc::new(WorkerShutdownState::new()),
            metrics,
        }
    }
    
    
    /// Register a handler for a specific function name
    pub async fn register_handler(&self, name: String, handler: Arc<dyn Handler>) {
        let mut handlers = self.handlers.write().await;
        handlers.insert(name, handler);
    }
    
    /// Start the worker and begin processing invocations
    #[instrument(
        fields(
            worker_id = %self.config.worker_id,
            service = %self.config.service_name,
            version = %self.config.version
        ),
        skip(self)
    )]
    pub async fn start(&mut self) -> SdkResult<()> {
        let span = Span::current();
        span.record("operation", "worker_start");
        
        info!("Starting durable worker");
        
        // Start the worker stream with registration
        self.start_worker_stream().await?;
        
        info!("Worker initialization completed - attempting connection to runtime");
        self.metrics.record_worker_start();
        
        Ok(())
    }
    
    /// Build service registration with current handlers
    async fn build_service_registration(&self) -> ServiceRegistration {
        let handlers = self.handlers.read().await;
        let handler_names: Vec<String> = handlers.keys().cloned().collect();
        
        ServiceRegistration {
            service_name: self.config.service_name.clone(),
            version: self.config.version.clone(),
            handlers: handler_names,
            endpoint: format!("worker-{}", self.config.worker_id),
            protocol_version: "1.0".to_string(),
            supported_protocol_versions: vec!["1.0".to_string()],
            service_type: ServiceType::Function as i32,
            metadata: std::collections::HashMap::from([
                ("worker_id".to_string(), self.config.worker_id.clone()),
                ("language".to_string(), "rust".to_string()),
                ("sdk".to_string(), "agnt5-sdk-core".to_string()),
            ]),
        }
    }
    
    /// Start the worker stream with service registration
    async fn start_worker_stream(&mut self) -> SdkResult<()> {
        tracing::info!("Starting worker stream for worker: {}", self.config.worker_id);
        
        // Wait a moment for any pending handler registrations to complete
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        
        // Build service registration with current handlers
        let service_registration = self.build_service_registration().await;
        tracing::info!("Built service registration with {} handlers: {:?}", 
            service_registration.handlers.len(), 
            service_registration.handlers
        );
        
        // Start worker stream with registration
        let mut client = self.client.clone();
        let (shared_connection, owned_connection) = client.start_worker_stream(service_registration).await?;
        tracing::info!("Worker stream connection established and registration completed");
        
        // Set up the channels for message handling
        let runtime_msg_rx = shared_connection.runtime_msg_rx.clone();
        let service_msg_tx = shared_connection.outgoing_tx.clone();
        
        // Start task to handle incoming stream messages and forward to runtime_msg_rx
        let stream_forwarding_task = {
            let mut incoming_rx = owned_connection.incoming_rx;
            let runtime_msg_tx = owned_connection.runtime_msg_tx;
            
            tokio::spawn(async move {
                tracing::info!("Starting incoming stream message forwarding");
                
                loop {
                    match incoming_rx.message().await {
                        Ok(Some(runtime_message)) => {
                            tracing::debug!("Forwarding incoming message: invocation_id={}", runtime_message.invocation_id);
                            
                            if let Err(e) = runtime_msg_tx.send_async(runtime_message).await {
                                tracing::error!("Failed to forward runtime message to processing loop: {}", e);
                                break;
                            }
                        }
                        Ok(None) => {
                            tracing::info!("Runtime closed the incoming stream");
                            break;
                        }
                        Err(e) => {
                            tracing::error!("Error receiving message from stream: {}", e);
                            break;
                        }
                    }
                }
                
                tracing::info!("Incoming stream message forwarding completed");
            })
        };
        
        // Store the stream forwarding task for proper shutdown
        {
            let mut task_handles = self.shutdown_state.task_handles.lock().await;
            task_handles.push(stream_forwarding_task);
        }
        
        // Set up the stream handler
        let stream_handler = self.stream_handler.take()
            .ok_or_else(|| SdkError::Configuration("No stream handler configured".to_string()))?;
        
        // Set up the message router with handlers
        let mut message_router = MessageRouter::new();
        {
            let handlers = self.handlers.read().await;
            for (name, handler) in handlers.iter() {
                let adapter = HandlerAdapter::new(handler.clone(), self.shutdown_state.clone(), self.metrics.clone());
                message_router.register_handler(name.clone(), Box::new(adapter));
            }
        }
        
        tracing::info!("Starting message processing with {} handlers", message_router.handlers.len());
        
        // Start message processing (routes runtime messages to handlers and sends responses)
        let message_processing_task = {
            let message_router = Arc::new(message_router);
            
            tokio::spawn(async move {
                match stream_handler.process_runtime_messages(
                    runtime_msg_rx,
                    service_msg_tx,
                    message_router,
                ).await {
                    Ok(reason) => tracing::info!("Message processing completed: {}", reason),
                    Err(e) => tracing::error!("Message processing error: {}", e),
                }
            })
        };
        
        // Store the task handle for proper shutdown
        {
            let mut task_handles = self.shutdown_state.task_handles.lock().await;
            task_handles.push(message_processing_task);
        }
        
        tracing::info!("Worker stream started successfully");
        tracing::info!("Listening for invocations from runtime...");
        
        Ok(())
    }
    
    
    /// Gracefully shutdown the worker
    pub async fn shutdown(&self) -> SdkResult<()> {
        tracing::info!("Initiating graceful shutdown for worker: {}", self.config.worker_id);
        
        // Signal shutdown to all components
        self.shutdown_state.shutdown_requested.store(true, Ordering::Relaxed);
        
        let shutdown_timeout = Duration::from_secs(self.config.graceful_shutdown_timeout_seconds);
        
        // Graceful shutdown with timeout
        match timeout(shutdown_timeout, self.shutdown_internal()).await {
            Ok(result) => {
                tracing::info!("Graceful shutdown completed for worker: {}", self.config.worker_id);
                result
            }
            Err(_) => {
                tracing::warn!("Graceful shutdown timeout exceeded, forcing shutdown for worker: {}", self.config.worker_id);
                self.force_shutdown().await
            }
        }
    }
    
    /// Force immediate shutdown without waiting for active invocations
    pub async fn force_shutdown(&self) -> SdkResult<()> {
        tracing::warn!("Forcing immediate shutdown for worker: {}", self.config.worker_id);
        
        // Signal shutdown to all components
        self.shutdown_state.shutdown_requested.store(true, Ordering::Relaxed);
        
        // Abort all running tasks immediately
        let mut task_handles = self.shutdown_state.task_handles.lock().await;
        for handle in task_handles.drain(..) {
            handle.abort();
        }
        
        // Note: connection management is now handled directly in start_worker_stream
        
        tracing::info!("Force shutdown completed for worker: {}", self.config.worker_id);
        Ok(())
    }
    
    /// Internal graceful shutdown logic
    async fn shutdown_internal(&self) -> SdkResult<()> {
        tracing::info!("Starting graceful shutdown sequence...");
        
        // Step 1: Stop accepting new invocations (already done by setting shutdown_requested)
        
        // Step 2: Wait for active invocations to complete
        self.wait_for_active_invocations().await;
        
        // Step 3: Connection cleanup (handled automatically when tasks complete)
        
        // Step 4: Wait for all tasks to complete
        self.wait_for_tasks_completion().await;
        
        tracing::info!("Graceful shutdown sequence completed");
        Ok(())
    }
    
    /// Wait for all active invocations to complete
    async fn wait_for_active_invocations(&self) {
        tracing::info!("Waiting for active invocations to complete...");
        
        let check_interval = Duration::from_millis(100);
        loop {
            let active_count = self.shutdown_state.active_invocations.load(Ordering::Relaxed);
            if active_count == 0 {
                tracing::info!("All active invocations completed");
                break;
            }
            
            tracing::debug!("Waiting for {} active invocations to complete", active_count);
            tokio::time::sleep(check_interval).await;
        }
    }
    
    /// Wait for all spawned tasks to complete
    async fn wait_for_tasks_completion(&self) {
        tracing::info!("Waiting for background tasks to complete...");
        
        let mut task_handles = self.shutdown_state.task_handles.lock().await;
        let handles = task_handles.drain(..).collect::<Vec<_>>();
        drop(task_handles);
        
        for handle in handles {
            if let Err(e) = handle.await {
                if e.is_cancelled() {
                    tracing::debug!("Task was cancelled during shutdown");
                } else {
                    tracing::warn!("Task completed with error during shutdown: {}", e);
                }
            }
        }
        
        tracing::info!("All background tasks completed");
    }
    
    /// Check if shutdown has been requested
    pub fn is_shutdown_requested(&self) -> bool {
        self.shutdown_state.shutdown_requested.load(Ordering::Relaxed)
    }
    
    /// Get the number of active invocations
    pub fn active_invocations_count(&self) -> u64 {
        self.shutdown_state.active_invocations.load(Ordering::Relaxed)
    }
    
    
    /// Process a single invocation with shutdown awareness
    #[instrument(
        fields(
            invocation_id = %invocation_id,
            handler = %invocation.handler_name,
            input_size = invocation.input_data.len(),
            worker_id = %self.config.worker_id
        ),
        skip(self, invocation)
    )]
    pub async fn process_invocation(&self, invocation: InvocationStart, invocation_id: String) -> SdkResult<InvocationResponse> {
        let span = Span::current();
        let start_time = Instant::now();
        
        // Check if shutdown has been requested
        if self.is_shutdown_requested() {
            warn!("Rejecting new invocation {} - shutdown in progress", invocation_id);
            self.metrics.record_invocation_rejected(&invocation.handler_name);
            return Ok(InvocationResponse {
                output_data: Vec::new(),
                completed: false,
            });
        }
        
        // Increment active invocation counter
        self.shutdown_state.active_invocations.fetch_add(1, Ordering::Relaxed);
        
        // Ensure counter is decremented when function exits
        let _guard = InvocationGuard::new(&self.shutdown_state.active_invocations, &self.metrics);
        
        let handlers = self.handlers.read().await;
        
        let handler = handlers.get(&invocation.handler_name)
            .ok_or_else(|| SdkError::Invocation(format!("Handler not found: {}", invocation.handler_name)))?;
        
        let ctx = InvocationContext {
            invocation_id: invocation_id.clone(),
            handler_name: invocation.handler_name.clone(),
            state_manager: self.state_manager.clone(),
            span_context: None, // TODO: Extract span context properly
        };
        
        info!("Processing invocation");
        
        match handler.invoke(ctx, invocation.input_data).await {
            Ok(output) => {
                let duration = start_time.elapsed();
                
                info!(
                    duration_ms = duration.as_millis(),
                    output_size = output.len(),
                    "Invocation completed successfully"
                );
                
                // Record success metrics
                self.metrics.record_invocation_success(&invocation.handler_name, duration);
                span.record("output_size", output.len());
                
                Ok(InvocationResponse {
                    output_data: output,
                    completed: true,
                })
            },
            Err(e) => {
                let duration = start_time.elapsed();
                
                error!(
                    error = %e,
                    duration_ms = duration.as_millis(),
                    "Invocation failed"
                );
                
                // Record failure metrics
                self.metrics.record_invocation_failure(&invocation.handler_name, duration);
                span.record("error", &e.to_string());
                span.record("error.type", &std::any::type_name_of_val(&e));
                
                Ok(InvocationResponse {
                    output_data: Vec::new(),
                    completed: false,
                })
            },
        }
    }
}

/// Enhanced metrics collection for worker operations
#[derive(Clone)]
pub struct WorkerMetrics {
    invocation_counter: Counter<u64>,
    invocation_duration: Histogram<f64>,
    registration_attempts: Counter<u64>,
    rejected_invocations: Counter<u64>,
}

impl WorkerMetrics {
    pub fn new(meter: &Meter) -> Self {
        Self {
            invocation_counter: meter
                .u64_counter("worker_invocations_total")
                .init(),
            invocation_duration: meter
                .f64_histogram("worker_invocation_duration_seconds")
                .init(),
            registration_attempts: meter
                .u64_counter("worker_registrations_total")
                .init(),
            rejected_invocations: meter
                .u64_counter("worker_rejected_invocations_total")
                .init(),
        }
    }
    
    pub fn record_invocation_success(&self, handler: &str, duration: Duration) {
        self.invocation_counter.add(1, &[
            KeyValue::new("handler", handler.to_string()),
            KeyValue::new("status", "success"),
        ]);
        self.invocation_duration.record(duration.as_secs_f64(), &[
            KeyValue::new("handler", handler.to_string()),
            KeyValue::new("status", "success"),
        ]);
    }
    
    pub fn record_invocation_failure(&self, handler: &str, duration: Duration) {
        self.invocation_counter.add(1, &[
            KeyValue::new("handler", handler.to_string()),
            KeyValue::new("status", "failure"),
        ]);
        self.invocation_duration.record(duration.as_secs_f64(), &[
            KeyValue::new("handler", handler.to_string()),
            KeyValue::new("status", "failure"),
        ]);
    }
    
    pub fn record_invocation_rejected(&self, handler: &str) {
        self.rejected_invocations.add(1, &[
            KeyValue::new("handler", handler.to_string()),
            KeyValue::new("reason", "shutdown"),
        ]);
    }
    
    pub fn record_registration_attempt(&self) {
        self.registration_attempts.add(1, &[
            KeyValue::new("result", "attempted"),
        ]);
    }
    
    pub fn record_registration_success(&self) {
        self.registration_attempts.add(1, &[
            KeyValue::new("result", "success"),
        ]);
    }
    
    pub fn record_registration_failure(&self) {
        self.registration_attempts.add(1, &[
            KeyValue::new("result", "failure"),
        ]);
    }
    
    pub fn record_connection_event(&self, connected: bool) {
        self.registration_attempts.add(1, &[
            KeyValue::new("event", if connected { "connected" } else { "disconnected" }),
        ]);
    }
    
    pub fn record_worker_start(&self) {
        // This can be used for worker lifecycle tracking
        info!("Worker metrics initialized");
    }
}

/// RAII guard to automatically decrement active invocation counter
struct InvocationGuard<'a> {
    counter: &'a AtomicU64,
    metrics: &'a WorkerMetrics,
}

impl<'a> InvocationGuard<'a> {
    fn new(counter: &'a AtomicU64, metrics: &'a WorkerMetrics) -> Self {
        Self { counter, metrics }
    }
}

impl<'a> Drop for InvocationGuard<'a> {
    fn drop(&mut self) {
        self.counter.fetch_sub(1, Ordering::Relaxed);
    }
}

/// Adapter to bridge the Handler trait with InvocationHandler trait
struct HandlerAdapter {
    handler: Arc<dyn Handler>,
    shutdown_state: Arc<WorkerShutdownState>,
    metrics: WorkerMetrics,
}

impl HandlerAdapter {
    fn new(handler: Arc<dyn Handler>, shutdown_state: Arc<WorkerShutdownState>, metrics: WorkerMetrics) -> Self {
        Self { handler, shutdown_state, metrics }
    }
}

#[async_trait::async_trait]
impl InvocationHandler for HandlerAdapter {
    async fn handle_invocation(
        &self, 
        invocation_id: String, 
        start: InvocationStart,
        service_msg_tx: &flume::Sender<crate::pb::ServiceMessage>,
    ) -> SdkResult<Vec<u8>> {
        // Check if shutdown has been requested
        if self.shutdown_state.shutdown_requested.load(Ordering::Relaxed) {
            tracing::warn!("Rejecting invocation {} - shutdown in progress", invocation_id);
            return Err(SdkError::Invocation("Worker is shutting down".to_string()));
        }
        
        // Increment active invocation counter
        self.shutdown_state.active_invocations.fetch_add(1, Ordering::Relaxed);
        
        // Ensure counter is decremented when function exits
        let _guard = InvocationGuard::new(&self.shutdown_state.active_invocations, &self.metrics);
        
        // Create remote state manager with access to service channel
        let state_manager = Arc::new(crate::state::RemoteStateManager::new(
            invocation_id.clone(),
            service_msg_tx.clone(),
        ));
        
        // Create invocation context with remote state manager
        let ctx = InvocationContext {
            invocation_id: invocation_id.clone(),
            handler_name: start.handler_name.clone(),
            state_manager,
            span_context: None, // TODO: Extract from gRPC metadata
        };
        
        // Call the handler
        self.handler.invoke(ctx, start.input_data).await
    }
    
    fn clone_box(&self) -> Box<dyn InvocationHandler> {
        Box::new(HandlerAdapter {
            handler: self.handler.clone(),
            shutdown_state: self.shutdown_state.clone(),
            metrics: self.metrics.clone(),
        })
    }
}
