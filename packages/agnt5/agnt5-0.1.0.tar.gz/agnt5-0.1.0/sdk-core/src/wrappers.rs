//! Type-safe wrappers for protocol buffer messages

use crate::error::SdkResult;
use crate::pb::*;
use std::collections::HashMap;

/// Type-safe wrapper for service registration
#[derive(Debug, Clone)]
pub struct ServiceRegistrationBuilder {
    service_name: String,
    version: String,
    handlers: Vec<String>,
    endpoint: String,
    service_type: ServiceType,
    metadata: HashMap<String, String>,
}

impl ServiceRegistrationBuilder {
    pub fn new(service_name: String, version: String) -> Self {
        Self {
            service_name,
            version,
            handlers: Vec::new(),
            endpoint: String::new(),
            service_type: ServiceType::Function,
            metadata: HashMap::new(),
        }
    }

    pub fn with_handler(mut self, handler_name: String) -> Self {
        self.handlers.push(handler_name);
        self
    }

    pub fn with_handlers(mut self, handlers: Vec<String>) -> Self {
        self.handlers = handlers;
        self
    }

    pub fn with_endpoint(mut self, endpoint: String) -> Self {
        self.endpoint = endpoint;
        self
    }

    pub fn with_service_type(mut self, service_type: ServiceType) -> Self {
        self.service_type = service_type;
        self
    }

    pub fn with_metadata(mut self, key: String, value: String) -> Self {
        self.metadata.insert(key, value);
        self
    }

    pub fn build(self) -> ServiceRegistration {
        ServiceRegistration {
            service_name: self.service_name,
            version: self.version,
            handlers: self.handlers,
            endpoint: self.endpoint,
            protocol_version: "1.0".to_string(),
            supported_protocol_versions: vec!["1.0".to_string()],
            service_type: self.service_type as i32,
            metadata: self.metadata,
        }
    }
}

/// Type-safe wrapper for state operations
#[derive(Debug, Clone)]
pub enum StateOperationRequest {
    Get { key: String },
    Set { key: String, value: Vec<u8> },
    Delete { key: String },
}

impl StateOperationRequest {
    pub fn to_proto(self) -> StateOperation {
        match self {
            StateOperationRequest::Get { key } => StateOperation {
                operation_type: Some(state_operation::OperationType::Get(
                    GetStateRequest { key: key.into_bytes() }
                )),
            },
            StateOperationRequest::Set { key, value } => StateOperation {
                operation_type: Some(state_operation::OperationType::Set(
                    SetStateRequest { key: key.into_bytes(), value }
                )),
            },
            StateOperationRequest::Delete { key } => StateOperation {
                operation_type: Some(state_operation::OperationType::Delete(
                    DeleteStateRequest { key: key.into_bytes() }
                )),
            },
        }
    }
}

/// Type-safe wrapper for service calls
#[derive(Debug, Clone)]
pub struct ServiceCallBuilder {
    service_name: String,
    handler_name: String,
    input_data: Vec<u8>,
    object_key: Option<String>,
    promise_id: String,
}

impl ServiceCallBuilder {
    pub fn new(service_name: String, handler_name: String, input_data: Vec<u8>) -> Self {
        Self {
            service_name,
            handler_name,
            input_data,
            object_key: None,
            promise_id: uuid::Uuid::new_v4().to_string(),
        }
    }

    pub fn with_object_key(mut self, object_key: String) -> Self {
        self.object_key = Some(object_key);
        self
    }

    pub fn with_promise_id(mut self, promise_id: String) -> Self {
        self.promise_id = promise_id;
        self
    }

    pub fn build(self) -> ServiceCall {
        ServiceCall {
            service_name: self.service_name,
            handler_name: self.handler_name,
            input_data: self.input_data,
            object_key: self.object_key.unwrap_or_default(),
            promise_id: self.promise_id,
        }
    }
}

/// Type-safe wrapper for creating service messages
#[derive(Debug, Clone)]
pub struct ServiceMessageBuilder {
    invocation_id: String,
}

impl ServiceMessageBuilder {
    pub fn new(invocation_id: String) -> Self {
        Self { invocation_id }
    }

    pub fn response(self, output_data: Vec<u8>, completed: bool) -> ServiceMessage {
        ServiceMessage {
            invocation_id: self.invocation_id,
            message_type: Some(service_message::MessageType::Response(
                InvocationResponse {
                    output_data,
                    completed,
                }
            )),
        }
    }

    pub fn state_operation(self, state_op: StateOperationRequest) -> ServiceMessage {
        ServiceMessage {
            invocation_id: self.invocation_id,
            message_type: Some(service_message::MessageType::StateOp(
                state_op.to_proto()
            )),
        }
    }

    pub fn service_call(self, service_call: ServiceCallBuilder) -> ServiceMessage {
        ServiceMessage {
            invocation_id: self.invocation_id,
            message_type: Some(service_message::MessageType::ServiceCall(
                service_call.build()
            )),
        }
    }

    pub fn await_promise(self, promise_id: String) -> ServiceMessage {
        ServiceMessage {
            invocation_id: self.invocation_id,
            message_type: Some(service_message::MessageType::AwaitPromise(
                AwaitPromise { promise_id }
            )),
        }
    }

    pub fn sleep_request(self, duration_ms: i64, promise_id: String) -> ServiceMessage {
        ServiceMessage {
            invocation_id: self.invocation_id,
            message_type: Some(service_message::MessageType::SleepRequest(
                SleepRequest {
                    duration_ms,
                    promise_id,
                }
            )),
        }
    }
}

/// Utility for extracting data from runtime messages
#[derive(Debug, Clone)]
pub enum RuntimeMessageType {
    InvocationStart {
        service_name: String,
        handler_name: String,
        input_data: Vec<u8>,
        metadata: HashMap<String, String>,
    },
    JournalEntry {
        entry_type: Option<journal_entry::EntryType>,
    },
    InvocationComplete {
        success: bool,
        message: String,
    },
    SuspensionComplete {
        promise_id: String,
        result_data: Vec<u8>,
        error: Option<String>,
    },
}

impl RuntimeMessageType {
    pub fn from_runtime_message(msg: RuntimeMessage) -> SdkResult<(String, Self)> {
        let invocation_id = msg.invocation_id;
        
        let message_type = match msg.message_type {
            Some(runtime_message::MessageType::Start(start)) => {
                RuntimeMessageType::InvocationStart {
                    service_name: start.service_name,
                    handler_name: start.handler_name,
                    input_data: start.input_data,
                    metadata: start.metadata,
                }
            },
            Some(runtime_message::MessageType::JournalEntry(entry)) => {
                RuntimeMessageType::JournalEntry {
                    entry_type: entry.entry_type,
                }
            },
            Some(runtime_message::MessageType::Complete(complete)) => {
                RuntimeMessageType::InvocationComplete {
                    success: complete.success,
                    message: complete.error_message,
                }
            },
            Some(runtime_message::MessageType::SuspensionComplete(suspension)) => {
                RuntimeMessageType::SuspensionComplete {
                    promise_id: suspension.promise_id,
                    result_data: suspension.result_data,
                    error: if suspension.error.is_empty() { None } else { Some(suspension.error) },
                }
            },
            Some(runtime_message::MessageType::ServiceRegistrationResponse(_response)) => {
                // For now, we don't have a specific wrapper for registration responses
                // They will be handled at the connection level
                return Err(crate::error::SdkError::Internal("ServiceRegistrationResponse should be handled at connection level".to_string()));
            },
            Some(runtime_message::MessageType::ServiceUnregistrationResponse(_response)) => {
                // For now, we don't have a specific wrapper for unregistration responses
                // They will be handled at the connection level
                return Err(crate::error::SdkError::Internal("ServiceUnregistrationResponse should be handled at connection level".to_string()));
            },
            None => {
                return Err(crate::error::SdkError::Internal("Empty runtime message".to_string()));
            }
        };

        Ok((invocation_id, message_type))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_registration_builder() {
        let registration = ServiceRegistrationBuilder::new(
            "test-service".to_string(),
            "1.0".to_string()
        )
        .with_handler("handler1".to_string())
        .with_handler("handler2".to_string())
        .with_endpoint("localhost:8080".to_string())
        .with_metadata("env".to_string(), "test".to_string())
        .build();

        assert_eq!(registration.service_name, "test-service");
        assert_eq!(registration.version, "1.0");
        assert_eq!(registration.handlers.len(), 2);
        assert_eq!(registration.endpoint, "localhost:8080");
        assert_eq!(registration.metadata.get("env"), Some(&"test".to_string()));
    }

    #[test]
    fn test_state_operation_get() {
        let state_op = StateOperationRequest::Get {
            key: "test-key".to_string(),
        };
        
        let proto = state_op.to_proto();
        match proto.operation_type {
            Some(state_operation::OperationType::Get(get_req)) => {
                assert_eq!(get_req.key, b"test-key");
            },
            _ => panic!("Expected Get operation"),
        }
    }

    #[test]
    fn test_service_call_builder() {
        let service_call = ServiceCallBuilder::new(
            "external-service".to_string(),
            "process".to_string(),
            b"test-input".to_vec(),
        )
        .with_object_key("obj-123".to_string())
        .build();

        assert_eq!(service_call.service_name, "external-service");
        assert_eq!(service_call.handler_name, "process");
        assert_eq!(service_call.input_data, b"test-input");
        assert_eq!(service_call.object_key, "obj-123");
    }

    #[test]
    fn test_service_message_builder() {
        let invocation_id = "inv-123".to_string();
        let builder = ServiceMessageBuilder::new(invocation_id.clone());
        
        let response_msg = builder.clone().response(b"result".to_vec(), true);
        assert_eq!(response_msg.invocation_id, invocation_id);
        
        match response_msg.message_type {
            Some(service_message::MessageType::Response(response)) => {
                assert_eq!(response.output_data, b"result");
                assert!(response.completed);
            },
            _ => panic!("Expected Response message type"),
        }
    }
}