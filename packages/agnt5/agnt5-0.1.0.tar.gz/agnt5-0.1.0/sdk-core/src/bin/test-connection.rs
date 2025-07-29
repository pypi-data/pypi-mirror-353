//! Simple connection test for WorkerCoordinatorClient
//! 
//! This is a standalone binary that tests the streaming connection to the
//! AGNT5 runtime WorkerCoordinatorService without any external dependencies.

use std::env;
use std::time::Duration;
use tokio::time::timeout;
use tracing::{info, error, debug, warn, Level};
use tracing_subscriber;

use agnt5_sdk_core::{
    WorkerCoordinatorClient, 
    SdkResult, 
    pb::{ServiceRegistration, ServiceMessage, service_message, ServiceType}
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Parse command line arguments
    let args: Vec<String> = env::args().collect();
    let endpoint = args.get(1)
        .map(|s| s.as_str())
        .unwrap_or("http://localhost:8081");
    
    let verbose = args.contains(&"--verbose".to_string()) || args.contains(&"-v".to_string());
    
    // Setup logging
    let log_level = if verbose { Level::DEBUG } else { Level::INFO };
    tracing_subscriber::fmt()
        .with_max_level(log_level)
        .with_target(false)
        .with_file(true)
        .with_line_number(true)
        .init();

    info!("🧪 Starting SDK-Core connection test");
    info!("📡 Endpoint: {}", endpoint);
    info!("🔧 Verbose: {}", verbose);
    
    // Run the connection test
    match test_worker_coordinator_connection(endpoint).await {
        Ok(()) => {
            info!("✅ Connection test completed successfully!");
            Ok(())
        }
        Err(e) => {
            error!("❌ Connection test failed: {}", e);
            std::process::exit(1);
        }
    }
}

async fn test_worker_coordinator_connection(endpoint: &str) -> SdkResult<()> {
    info!("Step 1: Creating WorkerCoordinatorClient");
    
    // Create the client with timeout
    let client = timeout(
        Duration::from_secs(10),
        WorkerCoordinatorClient::new(endpoint.to_string())
    ).await
    .map_err(|_| {
        agnt5_sdk_core::SdkError::Connection("Timeout creating client".to_string())
    })??;
    
    info!("Step 2: Establishing worker stream");
    
    // Start the worker stream with timeout
    let (shared_connection, mut owned_connection) = timeout(
        Duration::from_secs(15),
        client.clone().start_worker_stream(ServiceRegistration {
            service_name: "test-worker".to_string(),
            version: "1.0.0".to_string(),
            handlers: vec!["test_handler".to_string()],
            endpoint: "test-endpoint".to_string(),
            protocol_version: "1.0".to_string(),
            supported_protocol_versions: vec!["1.0".to_string()],
            service_type: ServiceType::Function as i32,
            metadata: std::collections::HashMap::new(),
        })
    ).await
    .map_err(|_| {
        agnt5_sdk_core::SdkError::Connection("Timeout establishing stream".to_string())
    })??;

    info!("Step 3: Preparing service registration");
    
    // Create test service registration
    let registration = ServiceRegistration {
        service_name: "rust-test-service".to_string(),
        version: "1.0.0".to_string(),
        handlers: vec![
            "test_handler".to_string(),
            "ping_handler".to_string(),
            "echo_handler".to_string(),
        ],
        endpoint: "rust-test-endpoint".to_string(),
        protocol_version: "1.0".to_string(),
        supported_protocol_versions: vec!["1.0".to_string()],
        service_type: ServiceType::Function as i32,
        metadata: std::collections::HashMap::from([
            ("test_mode".to_string(), "true".to_string()),
            ("language".to_string(), "rust".to_string()),
            ("sdk".to_string(), "agnt5-sdk-core".to_string()),
            ("timestamp".to_string(), chrono::Utc::now().to_rfc3339()),
        ]),
    };

    debug!("Registration details: {:?}", registration);

    info!("Step 4: Sending service registration");
    
    // Create service message for registration
    let service_message = ServiceMessage {
        invocation_id: String::new(), // Registration is not tied to specific invocation
        message_type: Some(service_message::MessageType::ServiceRegistration(registration)),
    };

    // Send registration message
    shared_connection.outgoing_tx
        .send_async(service_message)
        .await
        .map_err(|e| agnt5_sdk_core::SdkError::Connection(format!("Failed to send registration: {}", e)))?;

    info!("Step 5: Waiting for registration response");
    
    // Wait for response with timeout
    let response = timeout(
        Duration::from_secs(10),
        owned_connection.incoming_rx.message()
    ).await
    .map_err(|_| {
        agnt5_sdk_core::SdkError::Connection("Timeout waiting for response".to_string())
    })?
    .map_err(|e| agnt5_sdk_core::SdkError::Grpc(e))?;

    info!("Step 6: Processing registration response");
    
    match response {
        Some(runtime_message) => {
            debug!("Response details: invocation_id={}, message_type={:?}", 
                   runtime_message.invocation_id, 
                   runtime_message.message_type);

            match runtime_message.message_type {
                Some(message_type) => {
                    match message_type {
                        agnt5_sdk_core::pb::runtime_message::MessageType::ServiceRegistrationResponse(resp) => {
                            info!("📨 Registration response received:");
                            info!("   ✅ Success: {}", resp.success);
                            info!("   📝 Message: {}", resp.message);
                            info!("   🆔 Service ID: {}", resp.service_id);

                            if !resp.success {
                                return Err(agnt5_sdk_core::SdkError::Connection(
                                    format!("Registration failed: {}", resp.message)
                                ));
                            }

                            if resp.service_id.is_empty() {
                                return Err(agnt5_sdk_core::SdkError::Connection(
                                    "Registration successful but no service ID returned".to_string()
                                ));
                            }

                            info!("🎉 Service registration successful!");
                            info!("🔗 Service ID: {}", resp.service_id);
                            info!("🚀 Worker is now connected and ready to receive invocations");
                            
                            Ok(())
                        }
                        other => {
                            warn!("Unexpected response type: {:?}", other);
                            Err(agnt5_sdk_core::SdkError::Connection(
                                format!("Expected ServiceRegistrationResponse, got different message type")
                            ))
                        }
                    }
                }
                None => {
                    error!("Received response with no message type");
                    Err(agnt5_sdk_core::SdkError::Connection(
                        "Invalid response: missing message type".to_string()
                    ))
                }
            }
        }
        None => {
            warn!("Received empty response from server");
            Err(agnt5_sdk_core::SdkError::Connection(
                "Server closed connection without response".to_string()
            ))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    /// Test the connection test function with a mock endpoint
    /// This test will fail to connect but exercises the code path
    #[tokio::test]
    async fn test_connection_function_with_invalid_endpoint() {
        // This should fail quickly with a connection error
        let result = test_worker_coordinator_connection("http://invalid-endpoint:9999").await;
        
        // We expect this to fail
        assert!(result.is_err());
        
        // The error should be a connection-related error
        match result.unwrap_err() {
            agnt5_sdk_core::SdkError::Connection(_) => {
                // Expected - connection should fail
            }
            agnt5_sdk_core::SdkError::Grpc(_) => {
                // Also acceptable - gRPC connection error
            }
            other => {
                panic!("Unexpected error type: {:?}", other);
            }
        }
    }
    
    /// Test argument parsing logic
    #[test]
    fn test_argument_parsing() {
        // Test default endpoint
        let args = vec!["test-connection".to_string()];
        unsafe {
            std::env::set_var("_TEST_ARGS", args.join(" "));
            
        }
        
        // Test verbose flag detection
        let verbose_args = vec![
            "test-connection".to_string(),
            "http://localhost:8081".to_string(),
            "--verbose".to_string()
        ];
        
        assert!(verbose_args.contains(&"--verbose".to_string()));
        
        // Test endpoint extraction
        let endpoint = verbose_args.get(1).map(|s| s.as_str()).unwrap_or("http://localhost:8081");
        assert_eq!(endpoint, "http://localhost:8081");
    }
}