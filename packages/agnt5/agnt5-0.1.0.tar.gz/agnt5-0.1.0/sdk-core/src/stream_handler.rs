//! Streaming message handler for processing runtime communication

use crate::error::SdkResult;
use crate::pb::*;
use crate::messages::{SerializerEnum, message_handlers::{MessageHandler, ProcessedMessage}};
use tokio::time::{Duration, Instant, interval};
use tracing::{info, warn, debug, error};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

/// Configuration for stream handling
#[derive(Debug, Clone)]
pub struct StreamHandlerConfig {
    pub heartbeat_interval: Duration,
    pub message_timeout: Duration,
    pub max_concurrent_invocations: u32,
}

impl Default for StreamHandlerConfig {
    fn default() -> Self {
        Self {
            heartbeat_interval: Duration::from_secs(30),
            message_timeout: Duration::from_secs(60),
            max_concurrent_invocations: 10,
        }
    }
}

/// Handles the bidirectional streaming protocol with the runtime
pub struct StreamHandler {
    config: StreamHandlerConfig,
    message_handler: MessageHandler,
    shutdown_signal: Arc<AtomicBool>,
}

impl StreamHandler {
    /// Create a new stream handler
    pub fn new(config: StreamHandlerConfig, serializer: SerializerEnum) -> Self {
        Self {
            config,
            message_handler: MessageHandler::new(serializer),
            shutdown_signal: Arc::new(AtomicBool::new(false)),
        }
    }

    /// Process runtime messages and route them to appropriate handlers
    /// This method works with the runtime message receiver from a shared connection
    pub async fn process_runtime_messages(
        &self,
        runtime_msg_rx: flume::Receiver<RuntimeMessage>,
        service_msg_tx: flume::Sender<ServiceMessage>,
        message_router: Arc<MessageRouter>,
    ) -> SdkResult<String> {
        info!("Starting runtime message processing loop");
        
        let mut last_message_time = Instant::now();
        let mut heartbeat_interval = interval(self.config.heartbeat_interval);
        
        loop {
            tokio::select! {
                // Handle incoming runtime messages
                Ok(runtime_message) = runtime_msg_rx.recv_async() => {
                    last_message_time = Instant::now();
                    
                    // Log detailed request information when received
                    match &runtime_message.message_type {
                        Some(runtime_message::MessageType::Start(start)) => {
                            info!("📨 Received invocation request: invocation_id={}, handler={}, service={}, input_size={} bytes",
                                runtime_message.invocation_id,
                                start.handler_name,
                                start.service_name,
                                start.input_data.len()
                            );
                        },
                        Some(runtime_message::MessageType::JournalEntry(entry)) => {
                            debug!("📋 Received journal entry: invocation_id={}, entry_type={:?}",
                                runtime_message.invocation_id,
                                entry.entry_type
                            );
                        },
                        Some(runtime_message::MessageType::Complete(complete)) => {
                            info!("✅ Received invocation complete: invocation_id={}, success={}",
                                runtime_message.invocation_id,
                                complete.success
                            );
                        },
                        Some(runtime_message::MessageType::ServiceRegistrationResponse(response)) => {
                            info!("🔗 Received service registration response: success={}, service_id={}, message={}",
                                response.success,
                                response.service_id,
                                response.message
                            );
                        },
                        Some(runtime_message::MessageType::ServiceUnregistrationResponse(response)) => {
                            info!("🔌 Received service unregistration response: success={}, message={}",
                                response.success,
                                response.message
                            );
                        },
                        Some(other) => {
                            debug!("📥 Received runtime message: invocation_id={}, type={:?}",
                                runtime_message.invocation_id,
                                other
                            );
                        },
                        None => {
                            warn!("⚠️ Received runtime message with no message type: invocation_id={}",
                                runtime_message.invocation_id
                            );
                        }
                    }
                    
                    // Process the message
                    match self.process_runtime_message(runtime_message).await {
                        Ok(processed) => {
                            debug!("Processed runtime message: {:?}", processed);
                            
                            // Route to appropriate handler
                            if let Err(e) = message_router.route_message(processed, &service_msg_tx).await {
                                error!("Failed to route message: {}", e);
                                
                                // Send error response
                                let error_msg = ServiceMessage {
                                    invocation_id: "unknown".to_string(),
                                    message_type: Some(service_message::MessageType::Error(
                                        InvocationError {
                                            error_code: "ROUTING_ERROR".to_string(),
                                            error_message: e.to_string(),
                                            retryable: false,
                                        }
                                    )),
                                };
                                let _ = service_msg_tx.send_async(error_msg).await;
                            }
                        }
                        Err(e) => {
                            error!("Failed to process runtime message: {}", e);
                            
                            // Send error response
                            let error_msg = ServiceMessage {
                                invocation_id: "unknown".to_string(),
                                message_type: Some(service_message::MessageType::Error(
                                    InvocationError {
                                        error_code: "PROCESSING_ERROR".to_string(),
                                        error_message: e.to_string(),
                                        retryable: false,
                                    }
                                )),
                            };
                            let _ = service_msg_tx.send_async(error_msg).await;
                        }
                    }
                }
                
                // Send periodic heartbeats
                _ = heartbeat_interval.tick() => {
                    debug!("Sending heartbeat");
                    // Note: Heartbeats could be implemented as a special ServiceMessage type
                    // For now, we just log that we would send one
                }
                
                // Check for message timeout
                _ = tokio::time::sleep(Duration::from_millis(1000)) => {
                    if last_message_time.elapsed() > self.config.message_timeout {
                        warn!("Message timeout - no messages received for {:?}", self.config.message_timeout);
                        return Ok("Message timeout".to_string());
                    }
                }
                
                // Check for shutdown signal
                _ = tokio::time::sleep(Duration::from_millis(100)) => {
                    if self.shutdown_signal.load(Ordering::Relaxed) {
                        info!("Shutdown signal received in stream handler");
                        return Ok("Graceful shutdown".to_string());
                    }
                }
            }
        }
    }

    /// Process an incoming runtime message
    async fn process_runtime_message(&self, message: RuntimeMessage) -> SdkResult<ProcessedMessage> {
        self.message_handler.handle_runtime_message(message).await
    }

    /// Create a service message for an invocation response
    pub fn create_invocation_response(
        &self,
        invocation_id: String,
        output_data: Vec<u8>,
        completed: bool,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::Response(
                InvocationResponse {
                    output_data,
                    completed,
                }
            )),
        }
    }

    /// Create a service message for a state operation
    pub fn create_state_operation(
        &self,
        invocation_id: String,
        operation: StateOperation,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::StateOp(operation)),
        }
    }

    /// Create a service message for an external service call
    pub fn create_service_call(
        &self,
        invocation_id: String,
        service_name: String,
        handler_name: String,
        input_data: Vec<u8>,
        object_key: String,
        promise_id: String,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::ServiceCall(
                ServiceCall {
                    service_name,
                    handler_name,
                    input_data,
                    object_key,
                    promise_id,
                }
            )),
        }
    }

    /// Create a service message to await a promise
    pub fn create_await_promise(
        &self,
        invocation_id: String,
        promise_id: String,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::AwaitPromise(
                AwaitPromise { promise_id }
            )),
        }
    }

    /// Create a service message for a sleep request
    pub fn create_sleep_request(
        &self,
        invocation_id: String,
        promise_id: String,
        duration_ms: i64,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::SleepRequest(
                SleepRequest {
                    duration_ms,
                    promise_id,
                }
            )),
        }
    }

    /// Signal shutdown
    pub fn shutdown(&self) {
        self.shutdown_signal.store(true, Ordering::Relaxed);
    }
}

/// Message router that handles different types of runtime messages
pub struct MessageRouter {
    pub handlers: std::collections::HashMap<String, Box<dyn InvocationHandler>>,
}

impl MessageRouter {
    pub fn new() -> Self {
        Self {
            handlers: std::collections::HashMap::new(),
        }
    }

    /// Register a handler for a specific service method
    pub fn register_handler(&mut self, name: String, handler: Box<dyn InvocationHandler>) {
        self.handlers.insert(name, handler);
    }

    /// Route a processed message to the appropriate handler
    pub async fn route_message(
        &self,
        processed: ProcessedMessage,
        service_msg_tx: &flume::Sender<ServiceMessage>,
    ) -> SdkResult<()> {
        match processed {
            ProcessedMessage::InvocationStart { invocation_id, start } => {
                debug!("Routing invocation start: {} -> {}", invocation_id, start.handler_name);
                
                if let Some(handler) = self.handlers.get(&start.handler_name) {
                    // Execute handler in background
                    let handler_clone = handler.clone_box();
                    let service_tx = service_msg_tx.clone();
                    
                    tokio::spawn(async move {
                        let result = handler_clone.handle_invocation(invocation_id.clone(), start, &service_tx).await;
                        
                        let response = match result {
                            Ok(output) => ServiceMessage {
                                invocation_id: invocation_id.clone(),
                                message_type: Some(service_message::MessageType::Response(
                                    InvocationResponse {
                                        output_data: output,
                                        completed: true,
                                    }
                                )),
                            },
                            Err(e) => ServiceMessage {
                                invocation_id: invocation_id.clone(),
                                message_type: Some(service_message::MessageType::Error(
                                    InvocationError {
                                        error_code: "HANDLER_ERROR".to_string(),
                                        error_message: e.to_string(),
                                        retryable: true,
                                    }
                                )),
                            },
                        };
                        
                        if let Err(e) = service_tx.send_async(response).await {
                            error!("Failed to send invocation response: {}", e);
                        }
                    });
                } else {
                    warn!("No handler found for: {}", start.handler_name);
                    let error_response = ServiceMessage {
                        invocation_id,
                        message_type: Some(service_message::MessageType::Error(
                            InvocationError {
                                error_code: "HANDLER_NOT_FOUND".to_string(),
                                error_message: format!("No handler registered for: {}", start.handler_name),
                                retryable: false,
                            }
                        )),
                    };
                    if let Err(e) = service_msg_tx.send_async(error_response).await {
                        warn!("Failed to send error response: {}", e);
                    }
                }
            }
            
            ProcessedMessage::JournalEntry { invocation_id, entry: _ } => {
                debug!("Processing journal entry for invocation: {}", invocation_id);
                // TODO: Implement journal replay logic
            }
            
            ProcessedMessage::InvocationComplete { invocation_id, complete } => {
                debug!("Invocation {} completed: success={}", invocation_id, complete.success);
                // TODO: Cleanup invocation state
            }
            
            ProcessedMessage::SuspensionComplete { invocation_id, suspension } => {
                debug!("Suspension completed for invocation {}, promise {}", 
                       invocation_id, suspension.promise_id);
                // TODO: Resume suspended invocation
            }
            
            ProcessedMessage::ServiceRegistrationResponse { response } => {
                if response.success {
                    info!("Service registration successful: service_id={}", response.service_id);
                } else {
                    warn!("Service registration failed: {}", response.message);
                }
                // Registration responses are handled at the connection level
            }
            
            ProcessedMessage::ServiceUnregistrationResponse { response } => {
                if response.success {
                    info!("Service unregistration successful");
                } else {
                    warn!("Service unregistration failed: {}", response.message);
                }
                // Unregistration responses are handled at the connection level  
            }
        }
        
        Ok(())
    }
}

/// Trait for handling invocations
#[async_trait::async_trait]
pub trait InvocationHandler: Send + Sync {
    async fn handle_invocation(
        &self, 
        invocation_id: String, 
        start: InvocationStart,
        service_msg_tx: &flume::Sender<ServiceMessage>,
    ) -> SdkResult<Vec<u8>>;
    fn clone_box(&self) -> Box<dyn InvocationHandler>;
}

impl Default for MessageRouter {
    fn default() -> Self {
        Self::new()
    }
}