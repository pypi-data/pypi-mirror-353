//! gRPC client implementations for AGNT5 services

use crate::error::{SdkError, SdkResult};
use crate::pb::*;
use tonic::transport::Channel;
use tonic::{Request, Streaming};
use flume;
use futures::stream::Stream;
use std::pin::Pin;
use opentelemetry::{global, Context, propagation::Injector};
use tonic::{metadata::MetadataMap, Status};
use tracing::{instrument, info, error, warn};
use opentelemetry::metrics::{Counter, Histogram, Meter};
use std::time::{Duration, Instant};
use std::collections::HashMap;

/// Configuration for connecting to AGNT5 runtime services
#[derive(Debug, Clone)]
pub struct ClientConfig {
    pub gateway_endpoint: String,
    pub worker_coordinator_endpoint: String,
    pub timeout_seconds: u64,
    pub retry_attempts: u32,
}

impl Default for ClientConfig {
    fn default() -> Self {
        Self {
            gateway_endpoint: "http://localhost:8080".to_string(),
            worker_coordinator_endpoint: "http://localhost:8081".to_string(),
            timeout_seconds: 30,
            retry_attempts: 3,
        }
    }
}

/// Client for communicating with the AGNT5 Gateway Service
#[derive(Debug, Clone)]
pub struct GatewayClient {
    client: gateway_service_client::GatewayServiceClient<Channel>,
}

impl GatewayClient {
    /// Create a new gateway client
    pub async fn new(endpoint: String) -> SdkResult<Self> {
        let channel = Channel::from_shared(endpoint)
            .map_err(|e| SdkError::Connection(e.to_string()))?
            .connect()
            .await
            .map_err(|e| SdkError::Connection(e.to_string()))?;
            
        let client = gateway_service_client::GatewayServiceClient::new(channel);
        
        Ok(Self { client })
    }
    
    /// Get the underlying gRPC client
    pub fn inner(&mut self) -> &mut gateway_service_client::GatewayServiceClient<Channel> {
        &mut self.client
    }
}

/// Message stream for bidirectional communication
pub type ServiceMessageStream = Pin<Box<dyn Stream<Item = ServiceMessage> + Send>>;

/// Shared connection handle that can be cloned across tasks
#[derive(Clone)]
pub struct StreamingConnection {
    pub outgoing_tx: flume::Sender<ServiceMessage>,
    pub runtime_msg_rx: flume::Receiver<RuntimeMessage>,
    pub connection_id: String,
}

/// Internal connection handle with owned streaming receiver
pub struct OwnedStreamingConnection {
    pub outgoing_tx: flume::Sender<ServiceMessage>,
    pub outgoing_rx: flume::Receiver<ServiceMessage>,
    pub incoming_rx: Streaming<RuntimeMessage>,
    pub runtime_msg_tx: flume::Sender<RuntimeMessage>,
    pub connection_id: String,
}

/// Client for communicating with the AGNT5 Worker Coordinator Service
#[derive(Debug, Clone)]
pub struct WorkerCoordinatorClient {
    client: worker_coordinator_service_client::WorkerCoordinatorServiceClient<Channel>,
    endpoint: String,
    metrics: ClientMetrics,
}

impl WorkerCoordinatorClient {
    /// Create a new worker coordinator client
    #[instrument(fields(endpoint = %endpoint))]
    pub async fn new(endpoint: String) -> SdkResult<Self> {
        info!("Creating WorkerCoordinatorClient");
        
        let meter = global::meter("sdk-core-client");
        let metrics = ClientMetrics::new(&meter);
        
        metrics.record_connection_attempt();
        
        let channel = Channel::from_shared(endpoint.clone())
            .map_err(|e| {
                error!(error = %e, "Failed to parse endpoint");
                metrics.record_connection_failure();
                SdkError::Connection(e.to_string())
            })?;
        
        info!("Attempting to connect to gRPC endpoint");
        
        let channel = channel
            .connect()
            .await
            .map_err(|e| {
                error!(error = %e, "Failed to connect to worker coordinator");
                metrics.record_connection_failure();
                SdkError::Connection(e.to_string())
            })?;
            
        let client = worker_coordinator_service_client::WorkerCoordinatorServiceClient::new(channel);
        
        info!("gRPC channel created (service availability not yet verified)");
        metrics.record_connection_success();
        
        Ok(Self { 
            client,
            endpoint,
            metrics,
        })
    }
    
    /// Get the underlying gRPC client
    pub fn inner(&mut self) -> &mut worker_coordinator_service_client::WorkerCoordinatorServiceClient<Channel> {
        &mut self.client
    }
    
    // Note: Service registration/unregistration is now handled via WorkerStream
    // Use start_worker_stream() and send_registration_via_stream() instead
    
    /// Perform a health check with trace context propagation
    #[instrument(fields(endpoint = %self.endpoint))]
    pub async fn health_check(&mut self, request: HealthCheckRequest) -> SdkResult<HealthCheckResponse> {
        let start_time = Instant::now();
        
        // Create request with trace context
        let request = self.create_request_with_tracing(request);
        
        info!("Sending health check");
        
        match self.client
            .health_check(request)
            .await {
            Ok(response) => {
                let duration = start_time.elapsed();
                info!(duration_ms = duration.as_millis(), "Health check successful");
                self.metrics.record_request_success("health_check", duration);
                Ok(response.into_inner())
            }
            Err(e) => {
                let duration = start_time.elapsed();
                error!(error = %e, duration_ms = duration.as_millis(), "Health check failed");
                self.metrics.record_request_failure("health_check", duration);
                Err(SdkError::Grpc(e))
            }
        }
    }
    
    /// Start bidirectional streaming for worker communication with registration
    /// This method handles the complete worker stream setup including service registration
    #[instrument(fields(endpoint = %self.endpoint))]
    pub async fn start_worker_stream(&mut self, registration: ServiceRegistration) -> SdkResult<(StreamingConnection, OwnedStreamingConnection)> {
        use uuid::Uuid;
        
        info!("Starting worker stream with service registration for: {}", registration.service_name);
        let start_time = Instant::now();
        
        // Create channels for ongoing message routing
        let (outgoing_tx, outgoing_rx) = flume::unbounded::<ServiceMessage>();
        let (runtime_msg_tx, runtime_msg_rx) = flume::unbounded::<RuntimeMessage>();
        
        // Create the registration message
        let registration_message = ServiceMessage {
            invocation_id: String::new(),
            message_type: Some(service_message::MessageType::ServiceRegistration(registration)),
        };
        
        // Create stream that yields registration immediately, then handles ongoing messages
        let outgoing_rx_for_stream = outgoing_rx.clone();
        let outgoing_stream = async_stream::stream! {
            // First, yield the registration message immediately
            info!("Sending registration message via stream");
            yield registration_message;
            
            // Then, handle ongoing messages from the channel
            loop {
                match outgoing_rx_for_stream.recv_async().await {
                    Ok(msg) => yield msg,
                    Err(_) => break, // Channel closed
                }
            }
        };
        
        // Create request with trace context
        let request = self.create_streaming_request_with_tracing(outgoing_stream);
        
        // Establish the gRPC stream 
        let mut response_stream = self.client.worker_stream(request)
            .await
            .map_err(|e| {
                error!(error = %e, "Failed to establish gRPC stream");
                self.metrics.record_stream_failure();
                SdkError::Grpc(e)
            })?
            .into_inner();
        
        info!("Waiting for registration acknowledgment");
        
        // Wait for registration response
        let registration_response = tokio::time::timeout(
            Duration::from_secs(10),
            response_stream.message()
        )
        .await
        .map_err(|_| {
            error!("Timeout waiting for registration response");
            SdkError::Connection("Registration timeout - no response from runtime".to_string())
        })?
        .map_err(|e| {
            error!(error = %e, "Failed to receive registration response");
            SdkError::Grpc(e)
        })?;
        
        // Process registration response
        if let Some(runtime_message) = registration_response {
            match runtime_message.message_type {
                Some(runtime_message::MessageType::ServiceRegistrationResponse(resp)) => {
                    if resp.success {
                        info!("✅ Registration successful - Service ID: {}", resp.service_id);
                    } else {
                        error!("❌ Registration failed: {}", resp.message);
                        return Err(SdkError::Connection(format!("Registration failed: {}", resp.message)));
                    }
                }
                _ => {
                    error!("❌ Unexpected response type to registration");
                    return Err(SdkError::Connection("Unexpected response to registration".to_string()));
                }
            }
        } else {
            error!("❌ No registration response received");
            return Err(SdkError::Connection("No registration response received".to_string()));
        }
        
        let duration = start_time.elapsed();
        info!(duration_ms = duration.as_millis(), "Worker stream completed successfully");
        self.metrics.record_stream_success(duration);
        
        let connection_id = Uuid::new_v4().to_string();
        
        let shared_connection = StreamingConnection {
            outgoing_tx: outgoing_tx.clone(),
            runtime_msg_rx,
            connection_id: connection_id.clone(),
        };
        
        let owned_connection = OwnedStreamingConnection {
            outgoing_tx,
            outgoing_rx,
            incoming_rx: response_stream,
            runtime_msg_tx,
            connection_id,
        };
        
        Ok((shared_connection, owned_connection))
    }

    /// Send a service unregistration message through the worker stream
    pub async fn send_unregistration_via_stream(
        connection: &StreamingConnection,
        unregistration: ServiceUnregistration,
    ) -> SdkResult<()> {
        let message = ServiceMessage {
            invocation_id: String::new(),
            message_type: Some(crate::pb::service_message::MessageType::ServiceUnregistration(unregistration)),
        };

        connection.outgoing_tx
            .send_async(message)
            .await
            .map_err(|e| SdkError::Connection(format!("Failed to send unregistration: {}", e)))?;

        Ok(())
    }

}

/// Combined client manager for all AGNT5 services
#[derive(Debug)]
pub struct ServiceClients {
    pub gateway: GatewayClient,
    pub worker_coordinator: WorkerCoordinatorClient,
    pub config: ClientConfig,
}

impl ServiceClients {
    /// Create new service clients with the given configuration
    pub async fn new(config: ClientConfig) -> SdkResult<Self> {
        let gateway = GatewayClient::new(config.gateway_endpoint.clone()).await?;
        let worker_coordinator = WorkerCoordinatorClient::new(config.worker_coordinator_endpoint.clone()).await?;
        
        Ok(Self {
            gateway,
            worker_coordinator,
            config,
        })
    }
    
    /// Create new service clients with default configuration
    pub async fn default() -> SdkResult<Self> {
        Self::new(ClientConfig::default()).await
    }
}

/// gRPC metadata injector for trace context propagation
struct GrpcMetadataInjector<'a>(&'a mut MetadataMap);

impl<'a> Injector for GrpcMetadataInjector<'a> {
    fn set(&mut self, key: &str, value: String) {
        // Convert headers to gRPC metadata format
        let grpc_key = match key {
            "traceparent" => "x-trace-parent",
            "tracestate" => "x-trace-state", 
            "baggage" => "x-baggage",
            _ => key,
        };
        
        if let Ok(metadata_key) = tonic::metadata::MetadataKey::from_bytes(grpc_key.as_bytes()) {
            if let Ok(metadata_value) = tonic::metadata::MetadataValue::try_from(value) {
                self.0.insert(metadata_key, metadata_value);
            }
        }
    }
}

impl WorkerCoordinatorClient {
    /// Create request with comprehensive trace context injection
    fn create_request_with_tracing<T>(&self, message: T) -> Request<T> {
        let mut request = Request::new(message);
        
        // Inject trace context into gRPC metadata
        let mut metadata = MetadataMap::new();
        let context = Context::current();
        global::get_text_map_propagator(|propagator| {
            propagator.inject_context(&context, &mut GrpcMetadataInjector(&mut metadata));
        });
        
        // Add service identification headers
        let key = tonic::metadata::MetadataKey::from_static("x-service-name");
        if let Ok(value) = tonic::metadata::MetadataValue::try_from("sdk-core") {
            metadata.insert(key, value);
        }
        
        let key = tonic::metadata::MetadataKey::from_static("x-component");
        if let Ok(value) = tonic::metadata::MetadataValue::try_from("rust-sdk") {
            metadata.insert(key, value);
        }
        
        let key = tonic::metadata::MetadataKey::from_static("x-endpoint");
        if let Ok(value) = tonic::metadata::MetadataValue::try_from(&self.endpoint) {
            metadata.insert(key, value);
        }
        
        *request.metadata_mut() = metadata;
        request
    }
    
    /// Create streaming request with trace context
    fn create_streaming_request_with_tracing<T>(&self, stream: T) -> Request<T> {
        let mut request = Request::new(stream);
        
        // Inject trace context into gRPC metadata
        let mut metadata = MetadataMap::new();
        let context = Context::current();
        global::get_text_map_propagator(|propagator| {
            propagator.inject_context(&context, &mut GrpcMetadataInjector(&mut metadata));
        });
        
        // Add service identification headers for streaming
        let key = tonic::metadata::MetadataKey::from_static("x-service-name");
        if let Ok(value) = tonic::metadata::MetadataValue::try_from("sdk-core") {
            metadata.insert(key, value);
        }
        
        let key = tonic::metadata::MetadataKey::from_static("x-stream-type");
        if let Ok(value) = tonic::metadata::MetadataValue::try_from("worker-stream") {
            metadata.insert(key, value);
        }
        
        *request.metadata_mut() = metadata;
        request
    }
}

/// Client-side metrics for gRPC operations
#[derive(Clone, Debug)]
pub struct ClientMetrics {
    connection_attempts: Counter<u64>,
    request_counter: Counter<u64>,
    request_duration: Histogram<f64>,
    stream_operations: Counter<u64>,
    connection_events: Counter<u64>,
}

impl ClientMetrics {
    pub fn new(meter: &Meter) -> Self {
        Self {
            connection_attempts: meter
                .u64_counter("client_connection_attempts_total")
                .with_description("Total number of connection attempts")
                .init(),
            request_counter: meter
                .u64_counter("client_requests_total")
                .with_description("Total number of gRPC requests")
                .init(),
            request_duration: meter
                .f64_histogram("client_request_duration_seconds")
                .with_description("Duration of gRPC requests")
                .init(),
            stream_operations: meter
                .u64_counter("client_stream_operations_total")
                .with_description("Total number of streaming operations")
                .init(),
            connection_events: meter
                .u64_counter("client_connection_events_total")
                .init(),
        }
    }
    
    pub fn record_connection_attempt(&self) {
        self.connection_attempts.add(1, &[
            opentelemetry::KeyValue::new("result", "attempted"),
        ]);
    }
    
    pub fn record_connection_success(&self) {
        self.connection_attempts.add(1, &[
            opentelemetry::KeyValue::new("result", "success"),
        ]);
    }
    
    pub fn record_connection_failure(&self) {
        self.connection_attempts.add(1, &[
            opentelemetry::KeyValue::new("result", "failure"),
        ]);
    }
    
    pub fn record_request_success(&self, method: &str, duration: std::time::Duration) {
        self.request_counter.add(1, &[
            opentelemetry::KeyValue::new("method", method.to_string()),
            opentelemetry::KeyValue::new("status", "success"),
        ]);
        self.request_duration.record(duration.as_secs_f64(), &[
            opentelemetry::KeyValue::new("method", method.to_string()),
            opentelemetry::KeyValue::new("status", "success"),
        ]);
    }
    
    pub fn record_request_failure(&self, method: &str, duration: std::time::Duration) {
        self.request_counter.add(1, &[
            opentelemetry::KeyValue::new("method", method.to_string()),
            opentelemetry::KeyValue::new("status", "failure"),
        ]);
        self.request_duration.record(duration.as_secs_f64(), &[
            opentelemetry::KeyValue::new("method", method.to_string()),
            opentelemetry::KeyValue::new("status", "failure"),
        ]);
    }
    
    pub fn record_stream_success(&self, duration: std::time::Duration) {
        self.stream_operations.add(1, &[
            opentelemetry::KeyValue::new("operation", "start"),
            opentelemetry::KeyValue::new("status", "success"),
        ]);
        self.request_duration.record(duration.as_secs_f64(), &[
            opentelemetry::KeyValue::new("method", "worker_stream"),
            opentelemetry::KeyValue::new("status", "success"),
        ]);
    }
    
    pub fn record_stream_failure(&self) {
        self.stream_operations.add(1, &[
            opentelemetry::KeyValue::new("operation", "start"),
            opentelemetry::KeyValue::new("status", "failure"),
        ]);
    }
    
    pub fn record_connection_change(&self, event: &'static str) {
        self.connection_events.add(1, &[
            opentelemetry::KeyValue::new("event", event),
        ]);
    }
}