//! Durable Flow support for the AGNT5 SDK Core
//! 
//! Provides flow orchestration with:
//! - Multi-step process coordination
//! - Shared state management across steps
//! - Checkpoint and replay capabilities
//! - Parallel execution support
//! - Error handling and recovery

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{RwLock, Mutex};
use serde::{Deserialize, Serialize};
use async_trait::async_trait;
use uuid::Uuid;

use crate::error::{SdkError, SdkResult};
use crate::worker::StateManager;
use crate::durable_context::DurableContext;

/// Configuration for durable flows
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DurableFlowConfig {
    /// Flow name for identification
    pub name: String,
    /// Flow version
    pub version: String,
    /// Checkpoint interval in steps
    pub checkpoint_interval: usize,
    /// Maximum number of retries per step
    pub max_retries: usize,
    /// Timeout per step in seconds
    pub step_timeout_seconds: u64,
    /// Maximum concurrent steps
    pub max_concurrent_steps: usize,
    /// Enable deterministic execution
    pub deterministic: bool,
}

impl Default for DurableFlowConfig {
    fn default() -> Self {
        Self {
            name: "unnamed_flow".to_string(),
            version: "1.0.0".to_string(),
            checkpoint_interval: 1,
            max_retries: 3,
            step_timeout_seconds: 300, // 5 minutes
            max_concurrent_steps: 10,
            deterministic: true,
        }
    }
}

/// Flow execution state
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum FlowState {
    /// Flow is starting
    Starting,
    /// Flow is running
    Running,
    /// Flow is paused/suspended
    Suspended,
    /// Flow completed successfully
    Completed,
    /// Flow failed with error
    Failed,
    /// Flow was cancelled
    Cancelled,
}

/// Step execution status
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum StepStatus {
    /// Step is pending execution
    Pending,
    /// Step is currently running
    Running,
    /// Step completed successfully
    Completed,
    /// Step failed
    Failed,
    /// Step was skipped
    Skipped,
    /// Step was cancelled
    Cancelled,
}

/// Flow step definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowStep {
    /// Step ID
    pub id: String,
    /// Step name
    pub name: String,
    /// Function name to execute
    pub function_name: String,
    /// Dependencies (step IDs that must complete first)
    pub dependencies: Vec<String>,
    /// Step arguments
    pub args: Vec<u8>,
    /// Step configuration
    pub config: StepConfig,
    /// Current status
    pub status: StepStatus,
    /// Execution result (if completed)
    pub result: Option<Vec<u8>>,
    /// Error message (if failed)
    pub error: Option<String>,
    /// Retry count
    pub retry_count: usize,
    /// Start time
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// End time
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
}

/// Step-specific configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StepConfig {
    /// Maximum retries for this step
    pub max_retries: usize,
    /// Timeout for this step
    pub timeout_seconds: u64,
    /// Whether this step can run in parallel
    pub parallel: bool,
    /// Whether this step is optional
    pub optional: bool,
}

impl Default for StepConfig {
    fn default() -> Self {
        Self {
            max_retries: 3,
            timeout_seconds: 300,
            parallel: true,
            optional: false,
        }
    }
}

/// Flow execution context
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowExecutionContext {
    /// Execution ID
    pub execution_id: String,
    /// Flow configuration
    pub flow_config: DurableFlowConfig,
    /// Current flow state
    pub state: FlowState,
    /// All steps in the flow
    pub steps: HashMap<String, FlowStep>,
    /// Step execution order
    pub execution_order: Vec<String>,
    /// Shared flow state
    pub flow_state: HashMap<String, Vec<u8>>,
    /// Checkpoint data
    pub checkpoint: Option<FlowCheckpoint>,
    /// Start time
    pub start_time: chrono::DateTime<chrono::Utc>,
    /// End time
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// Current step index
    pub current_step_index: usize,
}

/// Flow checkpoint for persistence
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowCheckpoint {
    /// Checkpoint ID
    pub id: String,
    /// Execution ID
    pub execution_id: String,
    /// Checkpoint timestamp
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// Flow state at checkpoint
    pub flow_state: HashMap<String, Vec<u8>>,
    /// Completed steps
    pub completed_steps: Vec<String>,
    /// Current step
    pub current_step: Option<String>,
}

/// Flow execution request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowExecutionRequest {
    /// Flow name
    pub flow_name: String,
    /// Flow input arguments
    pub args: Vec<u8>,
    /// Flow configuration overrides
    pub config_overrides: Option<HashMap<String, serde_json::Value>>,
    /// Execution context
    pub context: HashMap<String, Vec<u8>>,
}

/// Flow execution response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowExecutionResponse {
    /// Execution ID
    pub execution_id: String,
    /// Success flag
    pub success: bool,
    /// Final result (if successful)
    pub result: Option<Vec<u8>>,
    /// Error message (if failed)
    pub error: Option<String>,
    /// Final flow state
    pub final_state: FlowState,
    /// Execution metrics
    pub metrics: FlowExecutionMetrics,
}

/// Flow execution metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowExecutionMetrics {
    /// Total execution time in milliseconds
    pub total_duration_ms: u64,
    /// Number of steps executed
    pub steps_executed: usize,
    /// Number of retries
    pub total_retries: usize,
    /// Number of checkpoints created
    pub checkpoints_created: usize,
    /// Peak memory usage (if available)
    pub peak_memory_bytes: Option<u64>,
}

/// Trait for flow step execution
#[async_trait]
pub trait FlowStepExecutor: Send + Sync {
    /// Execute a flow step
    async fn execute_step(
        &self,
        step: &FlowStep,
        context: &mut FlowExecutionContext,
        durable_context: &DurableContext,
    ) -> SdkResult<Vec<u8>>;
    
    /// Check if step can be executed (dependencies satisfied)
    fn can_execute_step(&self, step: &FlowStep, context: &FlowExecutionContext) -> bool;
    
    /// Get step function name
    fn get_function_name<'a>(&self, step: &'a FlowStep) -> &'a str;
}

/// Default step executor implementation
pub struct DefaultStepExecutor {
    /// Function registry for step execution
    function_handlers: Arc<RwLock<HashMap<String, Arc<dyn FlowStepHandler>>>>,
}

impl DefaultStepExecutor {
    pub fn new() -> Self {
        Self {
            function_handlers: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Register a step handler
    pub async fn register_handler(&self, function_name: String, handler: Arc<dyn FlowStepHandler>) {
        let mut handlers = self.function_handlers.write().await;
        handlers.insert(function_name, handler);
    }
}

#[async_trait]
impl FlowStepExecutor for DefaultStepExecutor {
    async fn execute_step(
        &self,
        step: &FlowStep,
        context: &mut FlowExecutionContext,
        durable_context: &DurableContext,
    ) -> SdkResult<Vec<u8>> {
        let handlers = self.function_handlers.read().await;
        
        if let Some(handler) = handlers.get(&step.function_name) {
            let step_context = FlowStepContext {
                step_id: step.id.clone(),
                execution_id: context.execution_id.clone(),
                flow_state: &mut context.flow_state,
                durable_context,
            };
            
            handler.execute(step.args.clone(), step_context).await
        } else {
            Err(SdkError::Configuration(format!(
                "No handler registered for function '{}'",
                step.function_name
            )))
        }
    }
    
    fn can_execute_step(&self, step: &FlowStep, context: &FlowExecutionContext) -> bool {
        // Check if all dependencies are completed
        for dep_id in &step.dependencies {
            if let Some(dep_step) = context.steps.get(dep_id) {
                if dep_step.status != StepStatus::Completed {
                    return false;
                }
            } else {
                // Dependency not found
                return false;
            }
        }
        true
    }
    
    fn get_function_name<'a>(&self, step: &'a FlowStep) -> &'a str {
        &step.function_name
    }
}

/// Context for flow step execution
pub struct FlowStepContext<'a> {
    /// Step ID
    pub step_id: String,
    /// Execution ID
    pub execution_id: String,
    /// Shared flow state
    pub flow_state: &'a mut HashMap<String, Vec<u8>>,
    /// Durable context for external calls
    pub durable_context: &'a DurableContext,
}

impl<'a> FlowStepContext<'a> {
    /// Get value from flow state
    pub fn get_state(&self, key: &str) -> Option<&Vec<u8>> {
        self.flow_state.get(key)
    }
    
    /// Set value in flow state
    pub fn set_state(&mut self, key: String, value: Vec<u8>) {
        self.flow_state.insert(key, value);
    }
    
    /// Make a durable call through the context
    pub async fn call(&self, service: &str, method: &str, _args: Vec<u8>) -> SdkResult<Vec<u8>> {
        // Delegate to durable context
        // This would call the actual durable context implementation
        Ok(format!("mock_call_{}_{}", service, method).into_bytes())
    }
}

/// Trait for flow step handlers
#[async_trait]
pub trait FlowStepHandler: Send + Sync {
    /// Execute the step
    async fn execute(&self, args: Vec<u8>, context: FlowStepContext<'_>) -> SdkResult<Vec<u8>>;
}

/// Durable flow engine for orchestrating multi-step processes
pub struct DurableFlowEngine {
    /// Engine configuration
    config: DurableFlowConfig,
    /// Step executor
    step_executor: Arc<dyn FlowStepExecutor>,
    /// State manager for persistence
    state_manager: Arc<dyn StateManager>,
    /// Active flow executions
    active_flows: Arc<RwLock<HashMap<String, Arc<Mutex<FlowExecutionContext>>>>>,
}

impl DurableFlowEngine {
    /// Create a new durable flow engine
    pub fn new(
        config: DurableFlowConfig,
        step_executor: Arc<dyn FlowStepExecutor>,
        state_manager: Arc<dyn StateManager>,
    ) -> Self {
        Self {
            config,
            step_executor,
            state_manager,
            active_flows: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Start a new flow execution
    pub async fn start_flow(&self, request: FlowExecutionRequest) -> SdkResult<String> {
        let execution_id = Uuid::new_v4().to_string();
        
        // Create execution context
        let mut context = FlowExecutionContext {
            execution_id: execution_id.clone(),
            flow_config: self.config.clone(),
            state: FlowState::Starting,
            steps: HashMap::new(),
            execution_order: Vec::new(),
            flow_state: HashMap::new(),
            checkpoint: None,
            start_time: chrono::Utc::now(),
            end_time: None,
            current_step_index: 0,
        };
        
        // Load flow definition (this would come from registry)
        let flow_definition = self.load_flow_definition(&request.flow_name).await?;
        context.steps = flow_definition.steps;
        context.execution_order = flow_definition.execution_order;
        
        // Store execution context
        let context_mutex = Arc::new(Mutex::new(context));
        {
            let mut active_flows = self.active_flows.write().await;
            active_flows.insert(execution_id.clone(), context_mutex.clone());
        }
        
        // Start execution in background
        let engine = self.clone_for_execution();
        let exec_id = execution_id.clone();
        tokio::spawn(async move {
            if let Err(e) = engine.execute_flow(exec_id.clone()).await {
                eprintln!("Flow execution {} failed: {}", exec_id, e);
            }
        });
        
        Ok(execution_id)
    }
    
    /// Execute a flow
    async fn execute_flow(&self, execution_id: String) -> SdkResult<()> {
        let context_mutex = {
            let active_flows = self.active_flows.read().await;
            active_flows.get(&execution_id).cloned()
                .ok_or_else(|| SdkError::Configuration(format!("Flow execution {} not found", execution_id)))?
        };
        
        // Create mock durable context (this would be injected in real usage)
        // For now, we'll use a placeholder since DurableContext requires more parameters
        let _durable_context = self.create_mock_context(execution_id.clone());
        
        loop {
            let (next_steps, _flow_complete) = {
                let mut context = context_mutex.lock().await;
                
                // Update state to running
                if context.state == FlowState::Starting {
                    context.state = FlowState::Running;
                }
                
                // Check for completion
                if self.is_flow_complete(&context) {
                    context.state = FlowState::Completed;
                    context.end_time = Some(chrono::Utc::now());
                    break;
                }
                
                // Get next executable steps
                let next_steps = self.get_next_executable_steps(&context);
                (next_steps, false)
            };
            
            if next_steps.is_empty() {
                // No more steps to execute, check if we're waiting or done
                break;
            }
            
            // Execute steps (potentially in parallel)  
            let mut step_futures = Vec::new();
            for step_id in next_steps {
                let context_mutex = context_mutex.clone();
                let step_executor = self.step_executor.clone();
                let execution_id = {
                    let context = context_mutex.lock().await;
                    context.execution_id.clone()
                };
                let durable_context = self.create_mock_context(execution_id);
                let engine = self.clone_for_execution();
                
                let future = async move {
                    engine.execute_single_step(step_id, context_mutex, step_executor, durable_context).await
                };
                step_futures.push(future);
            }
            
            // Wait for all steps to complete
            let results = futures::future::join_all(step_futures).await;
            
            // Handle results and update context
            for result in results {
                if let Err(e) = result {
                    eprintln!("Step execution failed: {}", e);
                    // Handle step failure (could trigger retries, etc.)
                }
            }
            
            // Create checkpoint if needed
            {
                let context = context_mutex.lock().await;
                if self.should_create_checkpoint(&context) {
                    self.create_checkpoint(&context).await?;
                }
            }
        }
        
        // Clean up active flow
        {
            let mut active_flows = self.active_flows.write().await;
            active_flows.remove(&execution_id);
        }
        
        Ok(())
    }
    
    /// Execute a single step
    async fn execute_single_step(
        &self,
        step_id: String,
        context_mutex: Arc<Mutex<FlowExecutionContext>>,
        step_executor: Arc<dyn FlowStepExecutor>,
        durable_context: DurableContext,
    ) -> SdkResult<()> {
        // Get step and update status
        let step = {
            let mut context = context_mutex.lock().await;
            
            if let Some(step) = context.steps.get_mut(&step_id) {
                step.status = StepStatus::Running;
                step.start_time = Some(chrono::Utc::now());
                step.clone()
            } else {
                return Err(SdkError::Configuration(format!("Step {} not found", step_id)));
            }
        };
        
        // Execute the step
        let result = {
            let mut context = context_mutex.lock().await;
            step_executor.execute_step(&step, &mut context, &durable_context).await
        };
        
        // Update step with result
        {
            let mut context = context_mutex.lock().await;
            if let Some(step) = context.steps.get_mut(&step_id) {
                match result {
                    Ok(output) => {
                        step.status = StepStatus::Completed;
                        step.result = Some(output);
                        step.end_time = Some(chrono::Utc::now());
                    }
                    Err(e) => {
                        step.retry_count += 1;
                        if step.retry_count >= step.config.max_retries {
                            step.status = StepStatus::Failed;
                            step.error = Some(e.to_string());
                            step.end_time = Some(chrono::Utc::now());
                        } else {
                            // Reset to pending for retry
                            step.status = StepStatus::Pending;
                        }
                    }
                }
            }
        }
        
        Ok(())
    }
    
    /// Check if flow is complete
    fn is_flow_complete(&self, context: &FlowExecutionContext) -> bool {
        context.steps.values().all(|step| {
            matches!(step.status, StepStatus::Completed | StepStatus::Skipped | StepStatus::Failed)
        })
    }
    
    /// Get next executable steps
    fn get_next_executable_steps(&self, context: &FlowExecutionContext) -> Vec<String> {
        let mut executable_steps = Vec::new();
        
        for (step_id, step) in &context.steps {
            if step.status == StepStatus::Pending && 
               self.step_executor.can_execute_step(step, context) {
                executable_steps.push(step_id.clone());
                
                // Limit concurrent steps
                if executable_steps.len() >= self.config.max_concurrent_steps {
                    break;
                }
            }
        }
        
        executable_steps
    }
    
    /// Check if checkpoint should be created
    fn should_create_checkpoint(&self, context: &FlowExecutionContext) -> bool {
        let completed_steps = context.steps.values()
            .filter(|step| step.status == StepStatus::Completed)
            .count();
            
        completed_steps > 0 && completed_steps % self.config.checkpoint_interval == 0
    }
    
    /// Create a checkpoint
    async fn create_checkpoint(&self, context: &FlowExecutionContext) -> SdkResult<()> {
        let checkpoint = FlowCheckpoint {
            id: Uuid::new_v4().to_string(),
            execution_id: context.execution_id.clone(),
            timestamp: chrono::Utc::now(),
            flow_state: context.flow_state.clone(),
            completed_steps: context.steps.iter()
                .filter(|(_, step)| step.status == StepStatus::Completed)
                .map(|(id, _)| id.clone())
                .collect(),
            current_step: context.steps.iter()
                .find(|(_, step)| step.status == StepStatus::Running)
                .map(|(id, _)| id.clone()),
        };
        
        let checkpoint_key = format!("flow:checkpoint:{}:{}", context.execution_id, checkpoint.id);
        let checkpoint_data = serde_json::to_vec(&checkpoint)
            .map_err(|e| SdkError::Serialization(e.to_string()))?;
            
        self.state_manager.set(&checkpoint_key, checkpoint_data).await?;
        
        Ok(())
    }
    
    /// Load flow definition (placeholder - would load from registry)
    async fn load_flow_definition(&self, flow_name: &str) -> SdkResult<FlowDefinition> {
        // This would load from a flow registry
        // For now, return a mock definition
        Ok(FlowDefinition {
            name: flow_name.to_string(),
            steps: HashMap::new(),
            execution_order: Vec::new(),
        })
    }
    
    /// Clone for execution (to avoid self borrowing issues)
    fn clone_for_execution(&self) -> DurableFlowEngine {
        DurableFlowEngine {
            config: self.config.clone(),
            step_executor: self.step_executor.clone(),
            state_manager: self.state_manager.clone(),
            active_flows: self.active_flows.clone(),
        }
    }
    
    /// Create a mock context for testing (real implementation would inject proper context)
    fn create_mock_context(&self, execution_id: String) -> DurableContext {
        // This is a placeholder - in real implementation, DurableContext would be properly injected
        // For now, we'll create a minimal mock that satisfies the compiler
        DurableContext::mock_for_testing(execution_id)
    }
}

/// Flow definition structure
#[derive(Debug, Clone)]
pub struct FlowDefinition {
    /// Flow name
    pub name: String,
    /// Flow steps
    pub steps: HashMap<String, FlowStep>,
    /// Execution order
    pub execution_order: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::state::InMemoryStateManager;
    use std::sync::Arc;
    
    // Mock step handler for testing
    struct MockStepHandler {
        output: String,
    }
    
    #[async_trait]
    impl FlowStepHandler for MockStepHandler {
        async fn execute(&self, _args: Vec<u8>, _context: FlowStepContext<'_>) -> SdkResult<Vec<u8>> {
            Ok(self.output.clone().into_bytes())
        }
    }
    
    #[tokio::test]
    async fn test_flow_config_creation() {
        let config = DurableFlowConfig {
            name: "test_flow".to_string(),
            version: "1.0.0".to_string(),
            checkpoint_interval: 2,
            max_retries: 5,
            step_timeout_seconds: 600,
            max_concurrent_steps: 5,
            deterministic: true,
        };
        
        assert_eq!(config.name, "test_flow");
        assert_eq!(config.version, "1.0.0");
        assert_eq!(config.checkpoint_interval, 2);
        assert_eq!(config.max_retries, 5);
        assert_eq!(config.step_timeout_seconds, 600);
        assert_eq!(config.max_concurrent_steps, 5);
        assert!(config.deterministic);
    }
    
    #[tokio::test]
    async fn test_step_executor_registration() {
        let executor = DefaultStepExecutor::new();
        let handler = Arc::new(MockStepHandler {
            output: "test_output".to_string(),
        });
        
        executor.register_handler("test_function".to_string(), handler).await;
        
        // Verify handler was registered
        let handlers = executor.function_handlers.read().await;
        assert!(handlers.contains_key("test_function"));
    }
    
    #[tokio::test]
    async fn test_flow_step_creation() {
        let step = FlowStep {
            id: "step_1".to_string(),
            name: "Test Step".to_string(),
            function_name: "test_function".to_string(),
            dependencies: vec![],
            args: b"test_args".to_vec(),
            config: StepConfig::default(),
            status: StepStatus::Pending,
            result: None,
            error: None,
            retry_count: 0,
            start_time: None,
            end_time: None,
        };
        
        assert_eq!(step.id, "step_1");
        assert_eq!(step.name, "Test Step");
        assert_eq!(step.function_name, "test_function");
        assert_eq!(step.status, StepStatus::Pending);
        assert_eq!(step.retry_count, 0);
    }
    
    #[tokio::test]
    async fn test_flow_execution_context() {
        let config = DurableFlowConfig::default();
        let execution_id = "test_execution".to_string();
        
        let context = FlowExecutionContext {
            execution_id: execution_id.clone(),
            flow_config: config.clone(),
            state: FlowState::Starting,
            steps: HashMap::new(),
            execution_order: Vec::new(),
            flow_state: HashMap::new(),
            checkpoint: None,
            start_time: chrono::Utc::now(),
            end_time: None,
            current_step_index: 0,
        };
        
        assert_eq!(context.execution_id, execution_id);
        assert_eq!(context.state, FlowState::Starting);
        assert!(context.steps.is_empty());
        assert!(context.execution_order.is_empty());
    }
    
    #[tokio::test]
    async fn test_flow_engine_creation() {
        let config = DurableFlowConfig::default();
        let step_executor = Arc::new(DefaultStepExecutor::new());
        let state_manager = Arc::new(InMemoryStateManager::new());
        
        let engine = DurableFlowEngine::new(config.clone(), step_executor, state_manager);
        
        assert_eq!(engine.config.name, config.name);
        assert_eq!(engine.config.version, config.version);
    }
    
    #[tokio::test]
    async fn test_checkpoint_creation() {
        let checkpoint = FlowCheckpoint {
            id: "checkpoint_1".to_string(),
            execution_id: "exec_1".to_string(),
            timestamp: chrono::Utc::now(),
            flow_state: HashMap::new(),
            completed_steps: vec!["step_1".to_string(), "step_2".to_string()],
            current_step: Some("step_3".to_string()),
        };
        
        assert_eq!(checkpoint.id, "checkpoint_1");
        assert_eq!(checkpoint.execution_id, "exec_1");
        assert_eq!(checkpoint.completed_steps.len(), 2);
        assert_eq!(checkpoint.current_step, Some("step_3".to_string()));
    }
    
    #[tokio::test]
    async fn test_flow_state_transitions() {
        let states = vec![
            FlowState::Starting,
            FlowState::Running,
            FlowState::Suspended,
            FlowState::Completed,
            FlowState::Failed,
            FlowState::Cancelled,
        ];
        
        for state in states {
            // Test serialization/deserialization
            let serialized = serde_json::to_string(&state).unwrap();
            let deserialized: FlowState = serde_json::from_str(&serialized).unwrap();
            assert_eq!(state, deserialized);
        }
    }
    
    #[tokio::test]
    async fn test_step_status_transitions() {
        let statuses = vec![
            StepStatus::Pending,
            StepStatus::Running,
            StepStatus::Completed,
            StepStatus::Failed,
            StepStatus::Skipped,
            StepStatus::Cancelled,
        ];
        
        for status in statuses {
            // Test serialization/deserialization
            let serialized = serde_json::to_string(&status).unwrap();
            let deserialized: StepStatus = serde_json::from_str(&serialized).unwrap();
            assert_eq!(status, deserialized);
        }
    }
}