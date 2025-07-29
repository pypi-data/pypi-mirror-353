//! Minimal Python function handlers - thin bridge

use pyo3::prelude::*;

/// Python wrapper for function handlers
#[pyclass]
#[derive(Clone, Debug)]
pub struct PyHandler {
    name: String,
    pub handler: PyObject,  // Make public so worker.rs can access it
    timeout_secs: u64,
    retry_attempts: u32,
}

#[pymethods]
impl PyHandler {
    /// Create a new Python function handler
    #[new]
    pub fn new(
        name: String,
        handler: PyObject,
        timeout_secs: u64,
        retry_attempts: u32,
    ) -> Self {
        PyHandler {
            name,
            handler,
            timeout_secs,
            retry_attempts,
        }
    }
    
    /// Get the handler name
    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }
    
    /// Get the timeout configuration
    #[getter]
    pub fn timeout_secs(&self) -> u64 {
        self.timeout_secs
    }
    
    /// Get the retry attempts configuration
    #[getter]
    pub fn retry_attempts(&self) -> u32 {
        self.retry_attempts
    }
}

// NOTE: Actual Handler trait implementation is in worker.rs
// This PyHandler is just a simple container for Python function metadata