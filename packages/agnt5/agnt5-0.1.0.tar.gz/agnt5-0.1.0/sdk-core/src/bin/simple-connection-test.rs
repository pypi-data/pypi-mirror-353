//! Simple connection test matching the Go pattern exactly
//! 
//! This test follows the exact same flow as the successful Go test

use std::time::Duration;
use tonic::Request;
use tokio_stream::{Stream, StreamExt};
use tracing::{info, error, Level};
use tracing_subscriber;

use agnt5_sdk_core::pb::{
    ServiceRegistration, ServiceMessage, service_message, ServiceType,
    worker_coordinator_service_client::WorkerCoordinatorServiceClient
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup logging  
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .with_target(false)
        .with_file(true)
        .with_line_number(true)
        .init();

    info!("🧪 Starting simplified SDK-Core connection test (matching Go pattern)");
    
    // Step 1: Create gRPC connection (matching Go grpc.Dial)
    info!("Step 1: Establishing gRPC connection");
    let endpoint = "http://localhost:8081";
    let channel = tonic::transport::Channel::from_static("http://localhost:8081")
        .connect()
        .await?;
        
    info!("Step 2: Creating WorkerCoordinatorService client");
    let mut client = WorkerCoordinatorServiceClient::new(channel);
    
    // Step 3: Establish worker stream (matching Go client.WorkerStream)
    info!("Step 3: Establishing worker stream");
    let outbound = async_stream::stream! {
        // We'll send the registration message here
        let registration = ServiceRegistration {
            service_name: "rust-simple-test-service".to_string(),
            version: "1.0.0".to_string(),
            handlers: vec!["test_handler".to_string(), "ping_handler".to_string()],
            endpoint: "test-endpoint".to_string(),
            protocol_version: "1.0".to_string(),
            supported_protocol_versions: vec!["1.0".to_string()],
            service_type: ServiceType::Function as i32,
            metadata: std::collections::HashMap::from([
                ("test_mode".to_string(), "true".to_string()),
                ("test_time".to_string(), chrono::Utc::now().to_rfc3339()),
            ]),
        };

        let service_message = ServiceMessage {
            invocation_id: String::new(), // Registration is not tied to specific invocation
            message_type: Some(service_message::MessageType::ServiceRegistration(registration)),
        };
        
        info!("Step 4: Sending service registration");
        yield service_message;
    };

    let request = Request::new(outbound);
    let mut response_stream = client.worker_stream(request).await?.into_inner();
    
    info!("Step 5: Waiting for registration response");
    
    // Wait for response
    if let Some(response) = response_stream.next().await {
        let runtime_message = response?;
        info!("Step 6: Processing registration response");
        
        match runtime_message.message_type {
            Some(agnt5_sdk_core::pb::runtime_message::MessageType::ServiceRegistrationResponse(resp)) => {
                info!("📨 Registration response received:");
                info!("   ✅ Success: {}", resp.success);
                info!("   📝 Message: {}", resp.message);
                info!("   🆔 Service ID: {}", resp.service_id);

                if resp.success {
                    info!("🎉 Service registration successful!");
                    info!("🔗 Service ID: {}", resp.service_id);
                    info!("✅ Connection test completed successfully!");
                } else {
                    error!("❌ Registration failed: {}", resp.message);
                    return Err(format!("Registration failed: {}", resp.message).into());
                }
            }
            other => {
                error!("❌ Unexpected response type: {:?}", other);
                return Err("Unexpected response type".into());
            }
        }
    } else {
        error!("❌ No response received from server");
        return Err("No response received".into());
    }
    
    Ok(())
}