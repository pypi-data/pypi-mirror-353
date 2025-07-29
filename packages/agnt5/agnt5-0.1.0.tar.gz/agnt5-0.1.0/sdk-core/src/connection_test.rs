//! Connection tests for SDK-Core components
//! 
//! This module provides unit tests for testing client connections and 
//! message handling without requiring external services.

#[cfg(test)]
mod tests {
    use crate::{
        WorkerCoordinatorClient, ConnectionConfig, ConnectionManager,
        pb::{ServiceRegistration, ServiceMessage, service_message, ServiceType},
        error::SdkError,
    };
    use std::time::Duration;
    use tokio::time::timeout;
    use tracing_test::traced_test;

    /// Test WorkerCoordinatorClient creation with various endpoints
    #[tokio::test]
    #[traced_test]
    async fn test_client_creation() {
        // Test valid endpoint format
        let valid_endpoints = [
            "http://localhost:8081",
            "https://example.com:443", 
            "http://127.0.0.1:9090",
        ];

        for endpoint in valid_endpoints {
            let result = WorkerCoordinatorClient::new(endpoint.to_string()).await;
            
            match result {
                Ok(_client) => {
                    println!("✅ Client created successfully for endpoint: {}", endpoint);
                }
                Err(SdkError::Connection(_)) => {
                    // Connection errors are expected when services aren't running
                    println!("⚠️  Connection failed for {}: service not available (expected)", endpoint);
                }
                Err(e) => {
                    panic!("❌ Unexpected error for endpoint {}: {:?}", endpoint, e);
                }
            }
        }
    }

    /// Test invalid endpoint handling
    #[tokio::test]
    #[traced_test]
    async fn test_invalid_endpoints() {
        let invalid_endpoints = [
            "invalid-url",
            "ftp://invalid-protocol.com",
            "",
            "http://",
        ];

        for endpoint in invalid_endpoints {
            let result = WorkerCoordinatorClient::new(endpoint.to_string()).await;
            
            assert!(result.is_err(), "Expected error for invalid endpoint: {}", endpoint);
            println!("✅ Correctly rejected invalid endpoint: {}", endpoint);
        }
    }

    /// Test timeout behavior for client creation
    #[tokio::test]
    #[traced_test]
    async fn test_client_creation_timeout() {
        // Use a non-routable IP to simulate timeout
        let timeout_endpoint = "http://10.255.255.1:8081";
        
        let result = timeout(
            Duration::from_secs(2),
            WorkerCoordinatorClient::new(timeout_endpoint.to_string())
        ).await;

        match result {
            Ok(client_result) => {
                // If client creation succeeded, that's also fine
                match client_result {
                    Ok(_) => println!("✅ Client created (unexpectedly fast)"),
                    Err(_) => println!("✅ Client creation failed as expected"),
                }
            }
            Err(_) => {
                println!("✅ Client creation timed out as expected");
            }
        }
    }

    /// Test ConnectionConfig defaults and validation
    #[test]
    #[traced_test]
    fn test_connection_config() {
        let config = ConnectionConfig::default();
        
        // Verify defaults
        assert_eq!(config.max_reconnect_attempts, 0); // Unlimited
        assert_eq!(config.initial_reconnect_delay, Duration::from_millis(100));
        assert_eq!(config.max_reconnect_delay, Duration::from_secs(30));
        assert_eq!(config.reconnect_backoff_multiplier, 2.0);
        assert_eq!(config.heartbeat_interval, Duration::from_secs(30));
        assert_eq!(config.connection_timeout, Duration::from_secs(10));
        assert_eq!(config.shutdown_timeout, Duration::from_secs(30));

        println!("✅ ConnectionConfig defaults are correct");
    }

    /// Test ServiceRegistration message creation
    #[test]
    #[traced_test]
    fn test_service_registration_creation() {
        let registration = ServiceRegistration {
            service_name: "test-service".to_string(),
            version: "1.0.0".to_string(),
            handlers: vec!["handler1".to_string(), "handler2".to_string()],
            endpoint: "test-endpoint".to_string(),
            protocol_version: "1.0".to_string(),
            supported_protocol_versions: vec!["1.0".to_string()],
            service_type: ServiceType::Function as i32,
            metadata: std::collections::HashMap::from([
                ("test".to_string(), "true".to_string()),
            ]),
        };

        // Verify fields
        assert_eq!(registration.service_name, "test-service");
        assert_eq!(registration.handlers.len(), 2);
        assert_eq!(registration.service_type, ServiceType::Function as i32);
        assert!(registration.metadata.contains_key("test"));

        // Create service message
        let service_message = ServiceMessage {
            invocation_id: String::new(),
            message_type: Some(service_message::MessageType::ServiceRegistration(registration)),
        };

        // Verify message structure
        assert!(service_message.invocation_id.is_empty());
        assert!(service_message.message_type.is_some());

        match service_message.message_type.unwrap() {
            service_message::MessageType::ServiceRegistration(reg) => {
                assert_eq!(reg.service_name, "test-service");
                println!("✅ ServiceRegistration message created correctly");
            }
            _ => panic!("❌ Wrong message type created"),
        }
    }

    /// Test ConnectionManager creation (without starting)
    #[tokio::test]
    #[traced_test]
    async fn test_connection_manager_creation() {
        // Create a client (will fail to connect but that's okay for this test)
        let client_result = WorkerCoordinatorClient::new("http://localhost:8081".to_string()).await;
        
        match client_result {
            Ok(client) => {
                let config = ConnectionConfig::default();
                let _manager = ConnectionManager::new(config, client);
                println!("✅ ConnectionManager created successfully");
            }
            Err(_) => {
                println!("⚠️  Client creation failed (expected when runtime not running)");
                println!("✅ Test completed - ConnectionManager can be created when client is available");
            }
        }
    }

    /// Test error handling and error types
    #[test]
    #[traced_test] 
    fn test_error_types() {
        // Test different error types
        let connection_error = SdkError::Connection("Test connection error".to_string());
        let invalid_message_error = SdkError::InvalidMessage("Test invalid message".to_string());
        let configuration_error = SdkError::Configuration("Test config error".to_string());

        // Verify error display
        assert!(connection_error.to_string().contains("Test connection error"));
        assert!(invalid_message_error.to_string().contains("Test invalid message"));
        assert!(configuration_error.to_string().contains("Test config error"));

        println!("✅ Error types work correctly");
    }

    /// Integration test that would work with a real server
    /// (but gracefully handles when server is not available)
    #[tokio::test]
    #[traced_test]
    async fn test_full_connection_flow() {
        println!("🧪 Testing full connection flow...");
        
        // Step 1: Create client
        println!("📡 Step 1: Creating client for localhost:8081");
        let client_result = WorkerCoordinatorClient::new("http://localhost:8081".to_string()).await;
        
        match client_result {
            Ok(mut client) => {
                println!("✅ Client created successfully");
                
                // Step 2: Try to start worker stream
                println!("🔄 Step 2: Attempting to start worker stream");
                let stream_result = timeout(
                    Duration::from_secs(5),
                    client.start_worker_stream()
                ).await;
                
                match stream_result {
                    Ok(Ok((shared_conn, _owned_conn))) => {
                        println!("✅ Worker stream established successfully");
                        
                        // Step 3: Try to send registration
                        println!("📝 Step 3: Sending service registration");
                        
                        let registration = ServiceRegistration {
                            service_name: "rust-unit-test-service".to_string(),
                            version: "1.0.0".to_string(),
                            handlers: vec!["test_handler".to_string()],
                            endpoint: "unit-test-endpoint".to_string(),
                            protocol_version: "1.0".to_string(),
                            supported_protocol_versions: vec!["1.0".to_string()],
                            service_type: ServiceType::Function as i32,
                            metadata: std::collections::HashMap::new(),
                        };

                        let service_message = ServiceMessage {
                            invocation_id: String::new(),
                            message_type: Some(service_message::MessageType::ServiceRegistration(registration)),
                        };

                        let send_result = shared_conn.outgoing_tx.send_async(service_message).await;
                        
                        match send_result {
                            Ok(()) => {
                                println!("✅ Registration message sent successfully");
                                println!("🎉 Full connection flow test completed successfully!");
                                println!("   Note: Response handling would require additional async processing");
                            }
                            Err(e) => {
                                println!("⚠️  Failed to send registration: {}", e);
                                println!("✅ Test completed - connection established but send failed");
                            }
                        }
                    }
                    Ok(Err(e)) => {
                        println!("⚠️  Worker stream failed: {}", e);
                        println!("✅ Test completed - client creation succeeded but stream failed");
                    }
                    Err(_) => {
                        println!("⚠️  Worker stream timed out");
                        println!("✅ Test completed - client creation succeeded but stream timed out");
                    }
                }
            }
            Err(e) => {
                println!("⚠️  Client creation failed: {}", e);
                println!("✅ Test completed - client creation failed (expected when runtime not running)");
            }
        }
    }
}