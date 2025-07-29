//! State management for durable functions

use crate::error::{SdkError, SdkResult};
use crate::worker::StateManager;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// In-memory state manager implementation (for testing and development)
#[derive(Debug)]
pub struct InMemoryStateManager {
    data: Arc<RwLock<HashMap<String, Vec<u8>>>>,
}

impl InMemoryStateManager {
    pub fn new() -> Self {
        Self {
            data: Arc::new(RwLock::new(HashMap::new())),
        }
    }
}

impl Default for InMemoryStateManager {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait::async_trait]
impl StateManager for InMemoryStateManager {
    async fn get(&self, key: &str) -> SdkResult<Option<Vec<u8>>> {
        let data = self.data.read().await;
        Ok(data.get(key).cloned())
    }
    
    async fn set(&self, key: &str, value: Vec<u8>) -> SdkResult<()> {
        let mut data = self.data.write().await;
        data.insert(key.to_string(), value);
        Ok(())
    }
    
    async fn delete(&self, key: &str) -> SdkResult<()> {
        let mut data = self.data.write().await;
        data.remove(key);
        Ok(())
    }
}

/// Remote state manager that communicates with the runtime
#[derive(Debug, Clone)]
pub struct RemoteStateManager {
    invocation_id: String,
    service_msg_tx: flume::Sender<crate::pb::ServiceMessage>,
}

impl RemoteStateManager {
    pub fn new(invocation_id: String, service_msg_tx: flume::Sender<crate::pb::ServiceMessage>) -> Self {
        Self {
            invocation_id,
            service_msg_tx,
        }
    }
}

#[async_trait::async_trait]
impl StateManager for RemoteStateManager {
    async fn get(&self, key: &str) -> SdkResult<Option<Vec<u8>>> {
        use crate::pb::*;
        
        tracing::debug!("RemoteStateManager: get key '{}' for invocation {}", key, self.invocation_id);
        
        let state_op = ServiceMessage {
            invocation_id: self.invocation_id.clone(),
            message_type: Some(service_message::MessageType::StateOp(
                StateOperation {
                    operation_type: Some(state_operation::OperationType::Get(
                        GetStateRequest {
                            key: key.as_bytes().to_vec(),
                        }
                    )),
                }
            )),
        };
        
        // Send the state operation
        self.service_msg_tx.send_async(state_op).await
            .map_err(|e| SdkError::State(format!("Failed to send state get operation: {}", e)))?;
        
        // TODO: Wait for response and return the value
        // For now, return None (this would be a synchronous operation in real implementation)
        tracing::warn!("RemoteStateManager: get operation sent but response handling not implemented");
        Ok(None)
    }
    
    async fn set(&self, key: &str, value: Vec<u8>) -> SdkResult<()> {
        use crate::pb::*;
        
        tracing::debug!("RemoteStateManager: set key '{}' ({} bytes) for invocation {}", 
                       key, value.len(), self.invocation_id);
        
        let state_op = ServiceMessage {
            invocation_id: self.invocation_id.clone(),
            message_type: Some(service_message::MessageType::StateOp(
                StateOperation {
                    operation_type: Some(state_operation::OperationType::Set(
                        SetStateRequest {
                            key: key.as_bytes().to_vec(),
                            value,
                        }
                    )),
                }
            )),
        };
        
        // Send the state operation
        self.service_msg_tx.send_async(state_op).await
            .map_err(|e| SdkError::State(format!("Failed to send state set operation: {}", e)))?;
        
        tracing::debug!("RemoteStateManager: set operation sent for key '{}'", key);
        Ok(())
    }
    
    async fn delete(&self, key: &str) -> SdkResult<()> {
        use crate::pb::*;
        
        tracing::debug!("RemoteStateManager: delete key '{}' for invocation {}", key, self.invocation_id);
        
        let state_op = ServiceMessage {
            invocation_id: self.invocation_id.clone(),
            message_type: Some(service_message::MessageType::StateOp(
                StateOperation {
                    operation_type: Some(state_operation::OperationType::Delete(
                        DeleteStateRequest {
                            key: key.as_bytes().to_vec(),
                        }
                    )),
                }
            )),
        };
        
        // Send the state operation
        self.service_msg_tx.send_async(state_op).await
            .map_err(|e| SdkError::State(format!("Failed to send state delete operation: {}", e)))?;
        
        tracing::debug!("RemoteStateManager: delete operation sent for key '{}'", key);
        Ok(())
    }
}