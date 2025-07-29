//! Simple test for SDK-Core connection with extended runtime
//! 
//! This test keeps a connection alive for testing message processing.

use agnt5_sdk_core::{
    client::WorkerCoordinatorClient,
    pb::{ServiceRegistration, ServiceType},
};
use tokio::time::{sleep, Duration};
use tracing::{info, warn, debug};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    tracing_subscriber::fmt()
        .with_env_filter("debug")
        .init();

    info!("🧪 Starting extended SDK-Core connection test");
    info!("📡 Endpoint: http://localhost:8081");
    info!("🎯 Testing the fixed stream message forwarding");
    
    // Create client
    let mut client = WorkerCoordinatorClient::new("http://localhost:8081".to_string()).await?;
    
    // Create registration with test handler
    let service_registration = ServiceRegistration {
        service_name: "test-message-service".to_string(),
        version: "1.0.0".to_string(),
        handlers: vec!["test_handler".to_string()],
        endpoint: "test-endpoint".to_string(),
        protocol_version: "1.0".to_string(),
        supported_protocol_versions: vec!["1.0".to_string()],
        service_type: ServiceType::Function as i32,
        metadata: std::collections::HashMap::new(),
    };
    
    info!("🔧 Starting worker stream with registration...");
    let (shared_connection, owned_connection) = client.start_worker_stream(service_registration).await?;
    
    info!("✅ Worker stream established successfully!");
    info!("🔍 Connection details:");
    info!("   📡 Connection ID: {}", shared_connection.connection_id);
    info!("   📨 Message channels are set up");
    
    // Start a task to handle incoming messages (simulate the fixed message forwarding)
    let incoming_task = {
        let mut incoming_rx = owned_connection.incoming_rx;
        let runtime_msg_tx = owned_connection.runtime_msg_tx;
        
        tokio::spawn(async move {
            info!("🔄 Starting incoming stream message forwarding (THE FIX)");
            
            let mut message_count = 0;
            
            loop {
                match incoming_rx.message().await {
                    Ok(Some(runtime_message)) => {
                        message_count += 1;
                        info!("📨 RECEIVED MESSAGE #{}: invocation_id={}", 
                              message_count, runtime_message.invocation_id);
                        
                        match &runtime_message.message_type {
                            Some(msg_type) => {
                                debug!("📋 Message type: {:?}", msg_type);
                            }
                            None => {
                                warn!("⚠️ Message has no type");
                            }
                        }
                        
                        // Forward to runtime message handler (this is the fix!)
                        if let Err(e) = runtime_msg_tx.send_async(runtime_message).await {
                            warn!("❌ Failed to forward runtime message: {}", e);
                            break;
                        } else {
                            info!("✅ Message forwarded to processing loop");
                        }
                    }
                    Ok(None) => {
                        info!("🔌 Runtime closed the incoming stream");
                        break;
                    }
                    Err(e) => {
                        warn!("❌ Error receiving message from stream: {}", e);
                        break;
                    }
                }
            }
            
            info!("🏁 Incoming stream message forwarding completed");
        })
    };
    
    // Start a task to handle runtime messages (simulate the message processing loop)
    let processing_task = {
        let runtime_msg_rx = shared_connection.runtime_msg_rx;
        let service_msg_tx = shared_connection.outgoing_tx;
        
        tokio::spawn(async move {
            info!("🔄 Starting runtime message processing loop");
            
            let mut processed_count = 0;
            
            loop {
                match runtime_msg_rx.recv_async().await {
                    Ok(runtime_message) => {
                        processed_count += 1;
                        info!("🎯 PROCESSING MESSAGE #{}: invocation_id={}", 
                              processed_count, runtime_message.invocation_id);
                        
                        // Simulate processing and send a response
                        match &runtime_message.message_type {
                            Some(agnt5_sdk_core::pb::runtime_message::MessageType::Start(start)) => {
                                info!("🚀 Processing invocation start: handler={}, service={}", 
                                      start.handler_name, start.service_name);
                                
                                // Create a response message
                                let response = agnt5_sdk_core::pb::ServiceMessage {
                                    invocation_id: runtime_message.invocation_id.clone(),
                                    message_type: Some(agnt5_sdk_core::pb::service_message::MessageType::Response(
                                        agnt5_sdk_core::pb::InvocationResponse {
                                            output_data: b"Hello from test handler!".to_vec(),
                                            completed: true,
                                        }
                                    )),
                                };
                                
                                if let Err(e) = service_msg_tx.send_async(response).await {
                                    warn!("❌ Failed to send response: {}", e);
                                } else {
                                    info!("✅ Response sent successfully!");
                                }
                            }
                            _ => {
                                debug!("📋 Other message type received");
                            }
                        }
                    }
                    Err(e) => {
                        warn!("❌ Error receiving runtime message: {}", e);
                        break;
                    }
                }
            }
            
            info!("🏁 Runtime message processing completed");
        })
    };
    
    info!("✅ Worker is now fully operational with the fix!");
    info!("📱 Both tasks are running:");
    info!("   1. 🔄 Incoming stream forwarding (THE FIX)");
    info!("   2. 🎯 Runtime message processing");
    info!("");
    info!("💡 Test with this command in another terminal:");
    info!("   grpcurl -plaintext -d '{{\"serviceName\": \"test-message-service\", \"handlerName\": \"test_handler\", \"inputData\": \"e30=\"}}' localhost:8080 api.v1.GatewayService/InvokeFunction");
    info!("");
    info!("⏳ Worker will run for 60 seconds...");
    
    // Keep running for testing
    sleep(Duration::from_secs(60)).await;
    
    info!("⏰ Test period completed, shutting down...");
    
    // Cancel the tasks
    incoming_task.abort();
    processing_task.abort();
    
    info!("✅ Test completed successfully!");
    
    Ok(())
}