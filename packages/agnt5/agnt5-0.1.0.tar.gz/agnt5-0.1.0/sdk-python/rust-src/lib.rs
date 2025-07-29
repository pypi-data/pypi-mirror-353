//! AGNT5 Python SDK - Thin PyO3 Bridge
//! 
//! This module provides a minimal Rust-Python bridge using PyO3,
//! exposing only the essential agnt5-sdk-core functionality to Python.

use pyo3::prelude::*;

mod worker;
mod handlers; 
mod types;

use worker::PyDurableWorker;
use handlers::PyHandler;
use types::{PyWorkerConfig, PyContext, PyInvocationResult, AgntError};

/// Initialize Rust logging with tracing
#[pyfunction]
fn init_logging(level: Option<&str>) -> PyResult<()> {
    use std::env;
    
    // Set RUST_LOG if not already set
    if env::var("RUST_LOG").is_err() {
        let log_level = level.unwrap_or("info");
        env::set_var("RUST_LOG", format!("agnt5_sdk_core={},agnt5_python={}", log_level, log_level));
    }
    
    // Initialize tracing subscriber if not already initialized
    static INIT: std::sync::Once = std::sync::Once::new();
    INIT.call_once(|| {
        tracing_subscriber::fmt::init();
    });
    
    Ok(())
}

/// Minimal Python module - thin bridge to sdk-core
#[pymodule]
fn _core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Initialize logging
    init_logging(None)?;
    
    // Add only essential classes for thin bridge
    m.add_class::<PyDurableWorker>()?;
    m.add_class::<PyHandler>()?;
    m.add_class::<PyWorkerConfig>()?;
    m.add_class::<PyContext>()?;
    m.add_class::<PyInvocationResult>()?;
    
    // Add minimal utility functions
    m.add_function(wrap_pyfunction!(create_worker, m)?)?;
    m.add_function(wrap_pyfunction!(create_config, m)?)?;
    m.add_function(wrap_pyfunction!(init_logging, m)?)?;
    
    // Add error type
    m.add("AgntError", _py.get_type::<pyo3::exceptions::PyRuntimeError>())?;
    
    Ok(())
}

/// Create a new durable worker with the given configuration
#[pyfunction]
fn create_worker(
    _py: Python,
    worker_id: String,
    service_name: String,
    version: String,
    coordinator_endpoint: Option<String>,
) -> PyResult<PyDurableWorker> {
    let config = PyWorkerConfig {
        worker_id,
        service_name,
        version,
        max_concurrent_invocations: 100,
        heartbeat_interval_seconds: 30,
        graceful_shutdown_timeout_seconds: 30,
    };
    
    PyDurableWorker::new(config, coordinator_endpoint)
}

/// Create a worker configuration object
#[pyfunction]
fn create_config(
    worker_id: String,
    service_name: String,
    version: String,
    max_concurrent_invocations: Option<u32>,
    heartbeat_interval_seconds: Option<u32>,
    graceful_shutdown_timeout_seconds: Option<u32>,
) -> PyResult<PyWorkerConfig> {
    Ok(PyWorkerConfig {
        worker_id,
        service_name,
        version,
        max_concurrent_invocations: max_concurrent_invocations.unwrap_or(100),
        heartbeat_interval_seconds: heartbeat_interval_seconds.unwrap_or(30),
        graceful_shutdown_timeout_seconds: graceful_shutdown_timeout_seconds.unwrap_or(30),
    })
}