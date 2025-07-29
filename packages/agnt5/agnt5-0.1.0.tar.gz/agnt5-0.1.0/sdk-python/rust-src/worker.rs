//! Thin PyO3 bridge for DurableWorker from sdk-core

use pyo3::prelude::*;
use pyo3_asyncio::tokio::future_into_py;
use agnt5_sdk_core::{DurableWorker, WorkerCoordinatorClient, WorkerConfig, Handler, InvocationContext, SdkResult, StateManager};
use std::sync::Arc;
use tokio::sync::Mutex;
use std::collections::HashMap;

use crate::handlers::PyHandler;
use crate::types::PyWorkerConfig;

/// Simple in-memory state manager for Python SDK
/// TODO: This could be enhanced to use Python-side state storage
#[derive(Debug)]
struct PythonStateManager;

#[async_trait::async_trait]
impl StateManager for PythonStateManager {
    async fn get(&self, _key: &str) -> SdkResult<Option<Vec<u8>>> {
        // TODO: Bridge to Python state management
        Ok(None)
    }
    
    async fn set(&self, _key: &str, _value: Vec<u8>) -> SdkResult<()> {
        // TODO: Bridge to Python state management
        Ok(())
    }
    
    async fn delete(&self, _key: &str) -> SdkResult<()> {
        // TODO: Bridge to Python state management
        Ok(())
    }
}

/// Bridge between Rust Handler trait and Python functions
#[derive(Debug)]
struct PythonHandlerBridge {
    name: String,
    py_handler: PyHandler,
}

impl PythonHandlerBridge {
    fn new(name: String, py_handler: PyHandler) -> Self {
        Self { name, py_handler }
    }
}

#[async_trait::async_trait]
impl Handler for PythonHandlerBridge {
    async fn invoke(&self, _ctx: InvocationContext, input: Vec<u8>) -> SdkResult<Vec<u8>> {
        tracing::info!("Python handler bridge called for: {}", self.name);
        
        // Convert input to string for Python
        let input_str = String::from_utf8(input).unwrap_or_else(|_| "{}".to_string());
        
        // Call Python function with proper GIL management
        let result = Python::with_gil(|py| -> Result<String, PyErr> {
            // Get the Python handler function
            let handler = &self.py_handler.handler;
            
            // Create a simple context object (for now)
            let ctx_dict = pyo3::types::PyDict::new(py);
            ctx_dict.set_item("invocation_id", "test-invocation")?;
            
            // Parse input as JSON or use as string
            let input_data = if input_str.trim().starts_with('{') {
                // Try to parse as JSON
                match serde_json::from_str::<serde_json::Value>(&input_str) {
                    Ok(json_val) => {
                        // Convert JSON to Python dict
                        let py_dict = pyo3::types::PyDict::new(py);
                        if let serde_json::Value::Object(map) = json_val {
                            for (key, value) in map {
                                let py_value = match value {
                                    serde_json::Value::String(s) => s.to_object(py),
                                    serde_json::Value::Number(n) => {
                                        if let Some(i) = n.as_i64() {
                                            i.to_object(py)
                                        } else if let Some(f) = n.as_f64() {
                                            f.to_object(py)
                                        } else {
                                            n.to_string().to_object(py)
                                        }
                                    }
                                    serde_json::Value::Bool(b) => b.to_object(py),
                                    serde_json::Value::Null => py.None(),
                                    _ => value.to_string().to_object(py),
                                };
                                py_dict.set_item(key, py_value)?;
                            }
                        }
                        py_dict.to_object(py)
                    }
                    Err(_) => input_str.to_object(py)
                }
            } else {
                input_str.to_object(py)
            };
            
            // Call the Python function: handler(ctx, data)
            let result = handler.call1(py, (ctx_dict, input_data))?;
            
            // Convert result to JSON string
            if result.is_none(py) {
                Ok(r#"{"result": null}"#.to_string())
            } else if let Ok(dict) = result.downcast::<pyo3::types::PyDict>(py) {
                // If it's already a dict, try to serialize it
                let mut json_parts = Vec::new();
                for (key, value) in dict.iter() {
                    let key_str = key.extract::<String>()?;
                    let value_str = if value.is_none() {
                        "null".to_string()
                    } else if let Ok(s) = value.extract::<String>() {
                        format!("\"{}\"", s.replace('"', "\\\""))
                    } else if let Ok(n) = value.extract::<i64>() {
                        n.to_string()
                    } else if let Ok(f) = value.extract::<f64>() {
                        f.to_string()
                    } else if let Ok(b) = value.extract::<bool>() {
                        b.to_string()
                    } else {
                        format!("\"{}\"", value.to_string().replace('"', "\\\""))
                    };
                    json_parts.push(format!("\"{}\": {}", key_str, value_str));
                }
                Ok(format!("{{{}}}", json_parts.join(", ")))
            } else if let Ok(s) = result.extract::<String>(py) {
                Ok(format!(r#"{{"result": "{}"}}"#, s.replace('"', "\\\"")))
            } else {
                Ok(format!(r#"{{"result": "{}"}}"#, result.to_string().replace('"', "\\\"")))
            }
        });
        
        match result {
            Ok(response_json) => {
                tracing::info!("✅ Python function executed successfully: {}", self.name);
                Ok(response_json.into_bytes())
            }
            Err(e) => {
                tracing::error!("❌ Python function execution failed: {}: {}", self.name, e);
                let error_response = format!(
                    r#"{{"error": "Python function execution failed", "handler": "{}", "details": "{}"}}"#,
                    self.name, e.to_string().replace('"', "\\\"")
                );
                Err(agnt5_sdk_core::SdkError::Connection(error_response))
            }
        }
    }
}

/// Thin PyO3 wrapper around sdk-core's DurableWorker
#[pyclass]
pub struct PyDurableWorker {
    worker: Arc<Mutex<Option<DurableWorker>>>,
    config: PyWorkerConfig,
    coordinator_endpoint: String,
    handlers: Arc<Mutex<HashMap<String, PyHandler>>>,
}

#[pymethods]
impl PyDurableWorker {
    /// Create a new worker (thin wrapper around DurableWorker)
    #[new]
    pub fn new(
        config: PyWorkerConfig,
        coordinator_endpoint: Option<String>,
    ) -> PyResult<Self> {
        Ok(PyDurableWorker {
            worker: Arc::new(Mutex::new(None)),
            config,
            coordinator_endpoint: coordinator_endpoint.unwrap_or_else(|| "http://localhost:8081".to_string()),
            handlers: Arc::new(Mutex::new(HashMap::new())),
        })
    }
    
    /// Register a Python function handler
    pub fn register_function<'p>(
        &self,
        _py: Python<'p>,
        name: String,
        handler: PyObject,
        timeout_secs: Option<u64>,
        retry_attempts: Option<u32>,
    ) -> PyResult<()> {
        let py_handler = PyHandler::new(
            name.clone(),
            handler,
            timeout_secs.unwrap_or(300),
            retry_attempts.unwrap_or(3),
        );
        
        // Store handler for later registration with DurableWorker
        let handlers = self.handlers.clone();
        let handler_name = name.clone();
        
        // Use a simple blocking approach for registration
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to create runtime: {}", e)
            ))?;
        
        rt.block_on(async {
            let mut handlers_guard = handlers.lock().await;
            handlers_guard.insert(handler_name.clone(), py_handler);
            tracing::info!("Registered Python function handler: {}", handler_name);
        });
        
        Ok(())
    }
    
    /// Start the worker (delegates to sdk-core DurableWorker)
    pub fn start<'p>(&mut self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let config = self.config.clone();
        let endpoint = self.coordinator_endpoint.clone();
        let handlers = self.handlers.clone();
        let worker = self.worker.clone();
        
        future_into_py(py, async move {
            // Create client
            let client = WorkerCoordinatorClient::new(endpoint)
                .await
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyConnectionError, _>(
                    format!("Failed to create client: {}", e)
                ))?;
            
            // Create state manager
            let state_manager = Arc::new(PythonStateManager) as Arc<dyn StateManager>;
            
            // Convert config and create DurableWorker
            let worker_config = WorkerConfig::from(config);
            let mut durable_worker = DurableWorker::new(worker_config, client, state_manager);
            
            // Register all Python handlers with the DurableWorker
            {
                let handlers_guard = handlers.lock().await;
                for (name, py_handler) in handlers_guard.iter() {
                    let handler_bridge = Arc::new(PythonHandlerBridge::new(
                        name.clone(),
                        py_handler.clone(),
                    ));
                    
                    durable_worker.register_handler(name.clone(), handler_bridge).await;
                    tracing::info!("Registered Python handler with DurableWorker: {}", name);
                }
            }
            
            // Start the DurableWorker (this handles all connection/registration logic)
            durable_worker.start().await.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Failed to start DurableWorker: {}", e)
                )
            })?;
            
            // Store the worker
            {
                let mut worker_guard = worker.lock().await;
                *worker_guard = Some(durable_worker);
            }
            
            tracing::info!("Python worker started successfully (using sdk-core DurableWorker)");
            Ok(())
        })
    }
    
    /// Stop the worker (delegates to sdk-core DurableWorker)
    pub fn stop<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let worker = self.worker.clone();
        
        future_into_py(py, async move {
            let mut worker_guard = worker.lock().await;
            if let Some(durable_worker) = worker_guard.as_ref() {
                durable_worker.shutdown().await.map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        format!("Failed to stop DurableWorker: {}", e)
                    )
                })?;
                tracing::info!("Python worker stopped successfully");
            }
            *worker_guard = None;
            Ok(())
        })
    }
    
    /// Wait for the worker to finish
    pub fn wait<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        future_into_py(py, async move {
            // Simple wait implementation
            tokio::time::sleep(tokio::time::Duration::from_secs(u64::MAX)).await;
            Ok(())
        })
    }
    
    /// Get the worker configuration
    #[getter]
    pub fn config(&self) -> PyResult<PyWorkerConfig> {
        Ok(self.config.clone())
    }
    
    /// List registered function handlers
    pub fn list_handlers<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let handlers = self.handlers.clone();
        
        future_into_py(py, async move {
            let handlers_guard = handlers.lock().await;
            let names: Vec<String> = handlers_guard.keys().cloned().collect();
            Ok(Python::with_gil(|py| names.to_object(py)))
        })
    }
}