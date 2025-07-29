//! Message handling and serialization utilities

use crate::error::{SdkError, SdkResult};
use crate::pb::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Trait for serializing and deserializing function arguments and return values
/// Note: This trait is not object-safe due to generic methods, so we'll use an enum instead
pub trait MessageSerializer: Send + Sync {
    /// Serialize a value to bytes
    fn serialize<T: Serialize>(&self, value: &T) -> SdkResult<Vec<u8>>;
    
    /// Deserialize bytes to a value
    fn deserialize<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T>;
}

/// JSON-based message serializer (default)
#[derive(Debug, Clone)]
pub struct JsonSerializer;

impl MessageSerializer for JsonSerializer {
    fn serialize<T: Serialize>(&self, value: &T) -> SdkResult<Vec<u8>> {
        let json = serde_json::to_vec(value)
            .map_err(|e| SdkError::Serialization(format!("JSON serialization failed: {}", e)))?;
        Ok(json)
    }
    
    fn deserialize<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T> {
        let value = serde_json::from_slice(bytes)
            .map_err(|e| SdkError::Serialization(format!("JSON deserialization failed: {}", e)))?;
        Ok(value)
    }
}

/// Binary serializer using bincode for better performance
/// For now, falls back to JSON until we properly implement bincode 2.0 support
#[derive(Debug, Clone)]
pub struct BinarySerializer;

impl MessageSerializer for BinarySerializer {
    fn serialize<T: Serialize>(&self, value: &T) -> SdkResult<Vec<u8>> {
        // TODO: Implement proper bincode 2.0 serialization
        // For now, use JSON as fallback
        let json = serde_json::to_vec(value)
            .map_err(|e| SdkError::Serialization(format!("Binary serialization fallback failed: {}", e)))?;
        Ok(json)
    }
    
    fn deserialize<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T> {
        // TODO: Implement proper bincode 2.0 deserialization
        // For now, use JSON as fallback
        let value = serde_json::from_slice(bytes)
            .map_err(|e| SdkError::Serialization(format!("Binary deserialization fallback failed: {}", e)))?;
        Ok(value)
    }
}

/// Raw bytes serializer (no serialization/deserialization)
#[derive(Debug, Clone)]
pub struct RawSerializer;

impl MessageSerializer for RawSerializer {
    fn serialize<T: Serialize>(&self, value: &T) -> SdkResult<Vec<u8>> {
        // For raw serializer, T must be Vec<u8> or similar
        // This is a simplified implementation
        let json = serde_json::to_vec(value)
            .map_err(|e| SdkError::Serialization(format!("Raw serialization fallback failed: {}", e)))?;
        Ok(json)
    }
    
    fn deserialize<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T> {
        let value = serde_json::from_slice(bytes)
            .map_err(|e| SdkError::Serialization(format!("Raw deserialization fallback failed: {}", e)))?;
        Ok(value)
    }
}

/// Configurable serializer that can use different formats based on content type
#[derive(Debug, Clone)]
pub struct ConfigurableSerializer {
    default_format: SerializationFormat,
    formatters: HashMap<String, SerializationFormat>,
}

#[derive(Debug, Clone)]
pub enum SerializationFormat {
    Json,
    Binary,
    Raw,
}

/// Enum to hold different serializer types (object-safe alternative)
#[derive(Debug, Clone)]
pub enum SerializerEnum {
    Json(JsonSerializer),
    Binary(BinarySerializer),
    Raw(RawSerializer),
}

impl MessageSerializer for SerializerEnum {
    fn serialize<T: Serialize>(&self, value: &T) -> SdkResult<Vec<u8>> {
        match self {
            SerializerEnum::Json(s) => s.serialize(value),
            SerializerEnum::Binary(s) => s.serialize(value),
            SerializerEnum::Raw(s) => s.serialize(value),
        }
    }
    
    fn deserialize<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T> {
        match self {
            SerializerEnum::Json(s) => s.deserialize(bytes),
            SerializerEnum::Binary(s) => s.deserialize(bytes),
            SerializerEnum::Raw(s) => s.deserialize(bytes),
        }
    }
}

impl ConfigurableSerializer {
    pub fn new(default_format: SerializationFormat) -> Self {
        Self {
            default_format,
            formatters: HashMap::new(),
        }
    }
    
    pub fn with_format_for_type(mut self, type_name: String, format: SerializationFormat) -> Self {
        self.formatters.insert(type_name, format);
        self
    }
    
    fn get_serializer(&self, content_type: Option<&str>) -> SerializerEnum {
        let format = content_type
            .and_then(|ct| self.formatters.get(ct))
            .unwrap_or(&self.default_format);
            
        match format {
            SerializationFormat::Json => SerializerEnum::Json(JsonSerializer),
            SerializationFormat::Binary => SerializerEnum::Binary(BinarySerializer),
            SerializationFormat::Raw => SerializerEnum::Raw(RawSerializer),
        }
    }
}

impl MessageSerializer for ConfigurableSerializer {
    fn serialize<T: Serialize>(&self, value: &T) -> SdkResult<Vec<u8>> {
        let serializer = self.get_serializer(None);
        serializer.serialize(value)
    }
    
    fn deserialize<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T> {
        let serializer = self.get_serializer(None);
        serializer.deserialize(bytes)
    }
}

/// Utility functions for working with protocol buffer messages
pub mod proto_utils {
    use super::*;
    
    /// Create a service message for an invocation response
    pub fn create_invocation_response(
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
    
    /// Create a service message for a state get operation
    pub fn create_state_get(
        invocation_id: String,
        key: String,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::StateOp(
                StateOperation {
                    operation_type: Some(state_operation::OperationType::Get(
                        GetStateRequest { key: key.into_bytes() }
                    )),
                }
            )),
        }
    }
    
    /// Create a service message for a state set operation
    pub fn create_state_set(
        invocation_id: String,
        key: String,
        value: Vec<u8>,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::StateOp(
                StateOperation {
                    operation_type: Some(state_operation::OperationType::Set(
                        SetStateRequest { key: key.into_bytes(), value }
                    )),
                }
            )),
        }
    }
    
    /// Create a service message for a state delete operation
    pub fn create_state_delete(
        invocation_id: String,
        key: String,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::StateOp(
                StateOperation {
                    operation_type: Some(state_operation::OperationType::Delete(
                        DeleteStateRequest { key: key.into_bytes() }
                    )),
                }
            )),
        }
    }
    
    /// Create a service message for an external service call
    pub fn create_service_call(
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
    
    /// Create a service message for waiting on a promise
    pub fn create_await_promise(
        invocation_id: String,
        promise_id: String,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::AwaitPromise(
                AwaitPromise {
                    promise_id,
                }
            )),
        }
    }
    
    /// Create a service message for a sleep request
    pub fn create_sleep_request(
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
    
    /// Create a service message for an invocation error
    pub fn create_invocation_error(
        invocation_id: String,
        error_code: String,
        error_message: String,
        retryable: bool,
    ) -> ServiceMessage {
        ServiceMessage {
            invocation_id,
            message_type: Some(service_message::MessageType::Error(
                InvocationError {
                    error_code,
                    error_message,
                    retryable,
                }
            )),
        }
    }
    
    /// Extract the invocation ID from a runtime message
    pub fn extract_invocation_id(message: &RuntimeMessage) -> Option<String> {
        Some(message.invocation_id.clone())
    }
    
    /// Validate that a RuntimeMessage has all required fields
    pub fn validate_runtime_message(message: &RuntimeMessage) -> SdkResult<()> {
        // Check if this is a lifecycle message that doesn't require invocation_id
        let is_lifecycle_message = matches!(
            &message.message_type,
            Some(runtime_message::MessageType::ServiceRegistrationResponse(_)) | 
            Some(runtime_message::MessageType::ServiceUnregistrationResponse(_))
        );
        
        if !is_lifecycle_message && message.invocation_id.is_empty() {
            return Err(SdkError::InvalidMessage("Missing invocation_id".to_string()));
        }
        
        match &message.message_type {
            Some(runtime_message::MessageType::Start(start)) => {
                validate_invocation_start(start)?;
            }
            Some(runtime_message::MessageType::JournalEntry(entry)) => {
                validate_journal_entry(entry)?;
            }
            Some(runtime_message::MessageType::Complete(_)) => {
                // InvocationComplete is simple, just needs invocation_id which we already checked
            }
            Some(runtime_message::MessageType::SuspensionComplete(suspension)) => {
                if suspension.promise_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing promise_id in SuspensionComplete".to_string()));
                }
            }
            Some(runtime_message::MessageType::ServiceRegistrationResponse(_)) => {
                // Registration responses don't need invocation_id validation
            }
            Some(runtime_message::MessageType::ServiceUnregistrationResponse(_)) => {
                // Unregistration responses don't need invocation_id validation
            }
            None => {
                return Err(SdkError::InvalidMessage("Missing message_type".to_string()));
            }
        }
        
        Ok(())
    }
    
    /// Validate that a ServiceMessage has all required fields
    pub fn validate_service_message(message: &ServiceMessage) -> SdkResult<()> {
        // Check if this is a lifecycle message that doesn't require invocation_id
        let is_lifecycle_message = matches!(
            &message.message_type,
            Some(service_message::MessageType::ServiceRegistration(_)) | 
            Some(service_message::MessageType::ServiceUnregistration(_))
        );
        
        if !is_lifecycle_message && message.invocation_id.is_empty() {
            return Err(SdkError::InvalidMessage("Missing invocation_id".to_string()));
        }
        
        match &message.message_type {
            Some(service_message::MessageType::ServiceRegistration(registration)) => {
                if registration.service_name.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing service_name in ServiceRegistration".to_string()));
                }
                // Registration messages don't need invocation_id
            }
            Some(service_message::MessageType::ServiceUnregistration(unregistration)) => {
                if unregistration.service_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing service_id in ServiceUnregistration".to_string()));
                }
                // Unregistration messages don't need invocation_id
            }
            Some(service_message::MessageType::Response(_)) => {
                // InvocationResponse validation is simple
            }
            Some(service_message::MessageType::StateOp(state_op)) => {
                validate_state_operation(state_op)?;
            }
            Some(service_message::MessageType::ServiceCall(call)) => {
                if call.service_name.is_empty() || call.handler_name.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing service_name or handler_name in ServiceCall".to_string()));
                }
            }
            Some(service_message::MessageType::AwaitPromise(await_promise)) => {
                if await_promise.promise_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing promise_id in AwaitPromise".to_string()));
                }
            }
            Some(service_message::MessageType::SleepRequest(sleep)) => {
                if sleep.promise_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing promise_id in SleepRequest".to_string()));
                }
                if sleep.duration_ms <= 0 {
                    return Err(SdkError::InvalidMessage("Invalid duration_ms in SleepRequest".to_string()));
                }
            }
            Some(service_message::MessageType::Error(_)) => {
                // InvocationError validation is simple
            }
            None => {
                return Err(SdkError::InvalidMessage("Missing message_type".to_string()));
            }
        }
        
        Ok(())
    }
    
    fn validate_invocation_start(start: &InvocationStart) -> SdkResult<()> {
        if start.service_name.is_empty() {
            return Err(SdkError::InvalidMessage("Missing service_name in InvocationStart".to_string()));
        }
        if start.handler_name.is_empty() {
            return Err(SdkError::InvalidMessage("Missing handler_name in InvocationStart".to_string()));
        }
        Ok(())
    }
    
    fn validate_journal_entry(entry: &JournalEntry) -> SdkResult<()> {
        match &entry.entry_type {
            Some(journal_entry::EntryType::StateUpdate(update)) => {
                if update.invocation_id.is_empty() || update.key.is_empty() {
                    return Err(SdkError::InvalidMessage("Invalid StateUpdateEntry".to_string()));
                }
            }
            Some(journal_entry::EntryType::StateDelete(delete)) => {
                if delete.invocation_id.is_empty() || delete.key.is_empty() {
                    return Err(SdkError::InvalidMessage("Invalid StateDeleteEntry".to_string()));
                }
            }
            Some(journal_entry::EntryType::AwaitCall(await_call)) => {
                if await_call.invocation_id.is_empty() || await_call.promise_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Invalid AwaitEntry".to_string()));
                }
            }
            Some(journal_entry::EntryType::ResolveAwait(resolve)) => {
                if resolve.invocation_id.is_empty() || resolve.promise_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Invalid ResolveAwaitEntry".to_string()));
                }
            }
            Some(journal_entry::EntryType::Output(output)) => {
                if output.invocation_id.is_empty() {
                    return Err(SdkError::InvalidMessage("Invalid OutputEntry".to_string()));
                }
            }
            Some(journal_entry::EntryType::Input(input)) => {
                if input.invocation_id.is_empty() || input.service_name.is_empty() {
                    return Err(SdkError::InvalidMessage("Invalid InputEntry".to_string()));
                }
            }
            None => {
                return Err(SdkError::InvalidMessage("Missing entry_type in JournalEntry".to_string()));
            }
        }
        Ok(())
    }
    
    fn validate_state_operation(state_op: &StateOperation) -> SdkResult<()> {
        match &state_op.operation_type {
            Some(state_operation::OperationType::Get(get)) => {
                if get.key.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing key in GetStateRequest".to_string()));
                }
            }
            Some(state_operation::OperationType::Set(set)) => {
                if set.key.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing key in SetStateRequest".to_string()));
                }
            }
            Some(state_operation::OperationType::Delete(delete)) => {
                if delete.key.is_empty() {
                    return Err(SdkError::InvalidMessage("Missing key in DeleteStateRequest".to_string()));
                }
            }
            None => {
                return Err(SdkError::InvalidMessage("Missing operation_type in StateOperation".to_string()));
            }
        }
        Ok(())
    }
}

/// Higher-level message handling utilities
pub mod message_handlers {
    use super::*;
    
    /// Handler for processing incoming runtime messages
    pub struct MessageHandler {
        serializer: SerializerEnum,
    }
    
    impl MessageHandler {
        pub fn new(serializer: SerializerEnum) -> Self {
            Self { serializer }
        }
        
        /// Process a runtime message and extract typed data
        pub async fn handle_runtime_message(&self, message: RuntimeMessage) -> SdkResult<ProcessedMessage> {
            proto_utils::validate_runtime_message(&message)?;
            
            tracing::debug!("Processing runtime message with serializer: {:?}", self.serializer);
            
            match message.message_type {
                Some(runtime_message::MessageType::Start(start)) => {
                    Ok(ProcessedMessage::InvocationStart {
                        invocation_id: message.invocation_id,
                        start,
                    })
                }
                Some(runtime_message::MessageType::JournalEntry(entry)) => {
                    Ok(ProcessedMessage::JournalEntry {
                        invocation_id: message.invocation_id,
                        entry,
                    })
                }
                Some(runtime_message::MessageType::Complete(complete)) => {
                    Ok(ProcessedMessage::InvocationComplete {
                        invocation_id: message.invocation_id,
                        complete,
                    })
                }
                Some(runtime_message::MessageType::SuspensionComplete(suspension)) => {
                    Ok(ProcessedMessage::SuspensionComplete {
                        invocation_id: message.invocation_id,
                        suspension,
                    })
                }
                Some(runtime_message::MessageType::ServiceRegistrationResponse(response)) => {
                    Ok(ProcessedMessage::ServiceRegistrationResponse {
                        response,
                    })
                }
                Some(runtime_message::MessageType::ServiceUnregistrationResponse(response)) => {
                    Ok(ProcessedMessage::ServiceUnregistrationResponse {
                        response,
                    })
                }
                None => Err(SdkError::InvalidMessage("Missing message_type".to_string())),
            }
        }
        
        /// Serialize data using the configured serializer
        pub fn serialize_data<T: Serialize>(&self, data: &T) -> SdkResult<Vec<u8>> {
            self.serializer.serialize(data)
        }
        
        /// Deserialize data using the configured serializer
        pub fn deserialize_data<T: for<'de> Deserialize<'de>>(&self, bytes: &[u8]) -> SdkResult<T> {
            self.serializer.deserialize(bytes)
        }
        
        /// Create a validated service message
        pub fn create_service_message(&self, message_data: ServiceMessageData) -> SdkResult<ServiceMessage> {
            let message = match message_data {
                ServiceMessageData::Response { invocation_id, output_data, completed } => {
                    proto_utils::create_invocation_response(invocation_id, output_data, completed)
                }
                ServiceMessageData::StateGet { invocation_id, key } => {
                    proto_utils::create_state_get(invocation_id, key)
                }
                ServiceMessageData::StateSet { invocation_id, key, value } => {
                    proto_utils::create_state_set(invocation_id, key, value)
                }
                ServiceMessageData::StateDelete { invocation_id, key } => {
                    proto_utils::create_state_delete(invocation_id, key)
                }
                ServiceMessageData::ServiceCall { invocation_id, service_name, handler_name, input_data, object_key, promise_id } => {
                    proto_utils::create_service_call(invocation_id, service_name, handler_name, input_data, object_key, promise_id)
                }
                ServiceMessageData::Error { invocation_id, error_code, error_message, retryable } => {
                    proto_utils::create_invocation_error(invocation_id, error_code, error_message, retryable)
                }
            };
            
            proto_utils::validate_service_message(&message)?;
            Ok(message)
        }
    }
    
    /// Enumeration of processed runtime messages
    #[derive(Debug)]
    pub enum ProcessedMessage {
        InvocationStart {
            invocation_id: String,
            start: InvocationStart,
        },
        JournalEntry {
            invocation_id: String,
            entry: JournalEntry,
        },
        InvocationComplete {
            invocation_id: String,
            complete: InvocationComplete,
        },
        SuspensionComplete {
            invocation_id: String,
            suspension: SuspensionComplete,
        },
        ServiceRegistrationResponse {
            response: ServiceRegistrationResponse,
        },
        ServiceUnregistrationResponse {
            response: ServiceUnregistrationResponse,
        },
    }
    
    /// Data for creating service messages
    #[derive(Debug)]
    pub enum ServiceMessageData {
        Response {
            invocation_id: String,
            output_data: Vec<u8>,
            completed: bool,
        },
        StateGet {
            invocation_id: String,
            key: String,
        },
        StateSet {
            invocation_id: String,
            key: String,
            value: Vec<u8>,
        },
        StateDelete {
            invocation_id: String,
            key: String,
        },
        ServiceCall {
            invocation_id: String,
            service_name: String,
            handler_name: String,
            input_data: Vec<u8>,
            object_key: String,
            promise_id: String,
        },
        Error {
            invocation_id: String,
            error_code: String,
            error_message: String,
            retryable: bool,
        },
    }
}