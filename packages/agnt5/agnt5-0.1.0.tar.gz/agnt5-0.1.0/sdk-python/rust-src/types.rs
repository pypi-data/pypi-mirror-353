//! Essential types for Python-Rust bridge - thin bridge only

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Python wrapper for worker configuration
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PyWorkerConfig {
    #[pyo3(get, set)]
    pub worker_id: String,
    
    #[pyo3(get, set)]
    pub service_name: String,
    
    #[pyo3(get, set)]
    pub version: String,
    
    #[pyo3(get, set)]
    pub max_concurrent_invocations: u32,
    
    #[pyo3(get, set)]
    pub heartbeat_interval_seconds: u32,
    
    #[pyo3(get, set)]
    pub graceful_shutdown_timeout_seconds: u32,
}

#[pymethods]
impl PyWorkerConfig {
    #[new]
    pub fn new(
        worker_id: String,
        service_name: String,
        version: String,
        max_concurrent_invocations: Option<u32>,
        heartbeat_interval_seconds: Option<u32>,
        graceful_shutdown_timeout_seconds: Option<u32>,
    ) -> Self {
        PyWorkerConfig {
            worker_id,
            service_name,
            version,
            max_concurrent_invocations: max_concurrent_invocations.unwrap_or(100),
            heartbeat_interval_seconds: heartbeat_interval_seconds.unwrap_or(30),
            graceful_shutdown_timeout_seconds: graceful_shutdown_timeout_seconds.unwrap_or(30),
        }
    }
    
    /// Create a default configuration
    #[staticmethod]
    pub fn default(worker_id: String, service_name: String, version: String) -> Self {
        Self::new(worker_id, service_name, version, None, None, None)
    }
    
    /// Convert to dictionary
    pub fn to_dict(&self) -> HashMap<String, PyObject> {
        Python::with_gil(|py| {
            let mut dict = HashMap::new();
            dict.insert("worker_id".to_string(), self.worker_id.to_object(py));
            dict.insert("service_name".to_string(), self.service_name.to_object(py));
            dict.insert("version".to_string(), self.version.to_object(py));
            dict.insert("max_concurrent_invocations".to_string(), self.max_concurrent_invocations.to_object(py));
            dict.insert("heartbeat_interval_seconds".to_string(), self.heartbeat_interval_seconds.to_object(py));
            dict.insert("graceful_shutdown_timeout_seconds".to_string(), self.graceful_shutdown_timeout_seconds.to_object(py));
            dict
        })
    }
    
    /// String representation
    fn __str__(&self) -> String {
        format!(
            "WorkerConfig(id={}, service={}@{}, max_concurrent={}, heartbeat={}s, shutdown_timeout={}s)",
            self.worker_id,
            self.service_name,
            self.version,
            self.max_concurrent_invocations,
            self.heartbeat_interval_seconds,
            self.graceful_shutdown_timeout_seconds
        )
    }
    
    /// Representation
    fn __repr__(&self) -> String {
        format!("{:?}", self)
    }
}

/// Convert to core WorkerConfig - essential bridge functionality
impl From<PyWorkerConfig> for agnt5_sdk_core::WorkerConfig {
    fn from(py_config: PyWorkerConfig) -> Self {
        agnt5_sdk_core::WorkerConfig {
            worker_id: py_config.worker_id,
            service_name: py_config.service_name,
            version: py_config.version,
            max_concurrent_invocations: py_config.max_concurrent_invocations,
            heartbeat_interval_seconds: py_config.heartbeat_interval_seconds as u64,
            graceful_shutdown_timeout_seconds: py_config.graceful_shutdown_timeout_seconds as u64,
        }
    }
}

/// Minimal context stub for Python compatibility
#[pyclass]
#[derive(Clone, Debug)]
pub struct PyContext {
    #[pyo3(get)]
    pub execution_id: String,
}

#[pymethods]
impl PyContext {
    #[new]
    pub fn new(execution_id: String) -> Self {
        PyContext { execution_id }
    }
}

/// Simple result wrapper for Python compatibility
#[pyclass]
#[derive(Clone, Debug)]
pub struct PyInvocationResult {
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub data: Option<PyObject>,
    #[pyo3(get)]
    pub error: Option<String>,
}

#[pymethods]
impl PyInvocationResult {
    #[new]
    pub fn new(success: bool, data: Option<PyObject>, error: Option<String>) -> Self {
        PyInvocationResult { success, data, error }
    }
}

/// Basic error type for Python compatibility
#[derive(Debug)]
pub struct AgntError(pub String);

impl std::fmt::Display for AgntError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "AGNT5 Error: {}", self.0)
    }
}

impl std::error::Error for AgntError {}

impl From<AgntError> for PyErr {
    fn from(err: AgntError) -> PyErr {
        pyo3::exceptions::PyRuntimeError::new_err(err.to_string())
    }
}