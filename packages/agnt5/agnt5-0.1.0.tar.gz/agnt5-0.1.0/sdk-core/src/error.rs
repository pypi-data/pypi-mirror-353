//! Error types for the AGNT5 SDK Core

use thiserror::Error;

#[derive(Error, Debug)]
pub enum SdkError {
    #[error("gRPC error: {0}")]
    Grpc(#[from] tonic::Status),
    
    #[error("Connection error: {0}")]
    Connection(String),
    
    #[error("Serialization error: {0}")]
    Serialization(String),
    
    #[error("Invalid configuration: {0}")]
    Configuration(String),
    
    #[error("Worker registration failed: {0}")]
    Registration(String),
    
    #[error("Invocation error: {0}")]
    Invocation(String),
    
    #[error("State management error: {0}")]
    State(String),
    
    #[error("Timeout error: {0}")]
    Timeout(String),
    
    #[error("Invalid message: {0}")]
    InvalidMessage(String),
    
    #[error("Internal error: {0}")]
    Internal(String),
    
    #[error("Replay error: {0}")]
    ReplayError(String),
    
    #[error("Service call error: {0}")]
    ServiceCallError(String),
    
    #[error("Execution suspended: {0}")]
    SuspendedExecution(String),
    
    #[error("Internal error: {0}")]
    InternalError(String),
    
    #[error("Telemetry error: {0}")]
    TelemetryError(String),
}

pub type SdkResult<T> = Result<T, SdkError>;