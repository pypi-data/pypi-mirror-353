use std::sync::{Arc, Mutex};
use std::time::Duration;
use crate::error::{SdkError, SdkResult};
use crate::invocation_fsm::{InvocationEvent, InvocationState, SuspendReason};
use crate::worker::StateManager;
use crate::pb::ServiceMessage;

/// Journal for recording operations during execution
pub struct Journal {
    pub entries: Vec<JournalEntry>,
    pub current_step: usize,
}

#[derive(Debug, Clone)]
pub enum JournalEntry {
    StateSet { step: usize, key: String, value: Vec<u8> },
    StateGet { step: usize, key: String, result: Option<Vec<u8>> },
    ServiceCall { 
        step: usize, 
        service: String, 
        method: String, 
        input: Vec<u8>, 
        result: Result<Vec<u8>, String> 
    },
    Sleep { step: usize, duration_ms: u64, completed: bool },
    Await { step: usize, promise_id: String, result: Option<Vec<u8>> },
}

impl Journal {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
            current_step: 0,
        }
    }

    pub fn record_state_set(&mut self, key: &str, value: &[u8]) -> usize {
        let step = self.current_step;
        self.entries.push(JournalEntry::StateSet {
            step,
            key: key.to_string(),
            value: value.to_vec(),
        });
        self.current_step += 1;
        step
    }

    pub fn record_state_get(&mut self, key: &str, result: Option<Vec<u8>>) -> usize {
        let step = self.current_step;
        self.entries.push(JournalEntry::StateGet {
            step,
            key: key.to_string(),
            result,
        });
        self.current_step += 1;
        step
    }
    
    pub fn record_service_call(&mut self, service: &str, method: &str, input: &[u8]) -> usize {
        let step = self.current_step;
        self.entries.push(JournalEntry::ServiceCall {
            step,
            service: service.to_string(),
            method: method.to_string(),
            input: input.to_vec(),
            result: Err("pending".to_string()), // Will be updated when result arrives
        });
        self.current_step += 1;
        step
    }
    
    pub fn update_service_result(&mut self, step: usize, result: &SdkResult<Vec<u8>>) {
        if let Some(JournalEntry::ServiceCall { result: entry_result, .. }) = self.entries.get_mut(step) {
            *entry_result = match result {
                Ok(data) => Ok(data.clone()),
                Err(e) => Err(e.to_string()),
            };
        }
    }

    pub fn record_sleep(&mut self, duration: Duration) -> usize {
        let step = self.current_step;
        self.entries.push(JournalEntry::Sleep {
            step,
            duration_ms: duration.as_millis() as u64,
            completed: false,
        });
        self.current_step += 1;
        step
    }

    pub fn mark_sleep_completed(&mut self, step: usize) {
        if let Some(JournalEntry::Sleep { completed, .. }) = self.entries.get_mut(step) {
            *completed = true;
        }
    }

    pub fn record_await(&mut self, promise_id: &str) -> usize {
        let step = self.current_step;
        self.entries.push(JournalEntry::Await {
            step,
            promise_id: promise_id.to_string(),
            result: None,
        });
        self.current_step += 1;
        step
    }

    pub fn update_await_result(&mut self, step: usize, result: Vec<u8>) {
        if let Some(JournalEntry::Await { result: entry_result, .. }) = self.entries.get_mut(step) {
            *entry_result = Some(result);
        }
    }
    
    /// Replay journal entries up to a specific step
    pub fn replay_to_step(&self, target_step: usize) -> Vec<&JournalEntry> {
        self.entries.iter()
            .filter(|entry| entry.step() <= target_step)
            .collect()
    }

    /// Get the latest journal entry
    pub fn last_entry(&self) -> Option<&JournalEntry> {
        self.entries.last()
    }

    /// Check if we're at a specific step during replay
    pub fn is_at_step(&self, step: usize) -> bool {
        self.current_step == step
    }
}

impl JournalEntry {
    pub fn step(&self) -> usize {
        match self {
            JournalEntry::StateSet { step, .. } => *step,
            JournalEntry::StateGet { step, .. } => *step,
            JournalEntry::ServiceCall { step, .. } => *step,
            JournalEntry::Sleep { step, .. } => *step,
            JournalEntry::Await { step, .. } => *step,
        }
    }

    pub fn is_completed(&self) -> bool {
        match self {
            JournalEntry::StateSet { .. } => true,
            JournalEntry::StateGet { .. } => true,
            JournalEntry::ServiceCall { result, .. } => result.is_ok(),
            JournalEntry::Sleep { completed, .. } => *completed,
            JournalEntry::Await { result, .. } => result.is_some(),
        }
    }
}

use std::future::Future;
use std::pin::Pin;

/// FSM Manager trait for state transitions
pub trait FSMManager: Send + Sync {
    fn transition(&self, invocation_id: &str, event: InvocationEvent) -> Pin<Box<dyn Future<Output = Result<InvocationState, crate::invocation_fsm::FSMError>> + Send + '_>>;
    fn get_state(&self, invocation_id: &str) -> Pin<Box<dyn Future<Output = Option<InvocationState>> + Send + '_>>;
}

/// Enhanced context that records all operations for replay
pub struct DurableContext {
    pub invocation_id: String,
    pub handler_name: String,
    pub state_manager: Arc<dyn StateManager>,
    pub journal: Arc<Mutex<Journal>>,
    pub fsm_manager: Arc<dyn FSMManager>,
    pub replay_mode: bool,
    pub current_step: usize,
    pub service_msg_tx: flume::Sender<ServiceMessage>,
}

impl DurableContext {
    pub fn new(
        invocation_id: String,
        handler_name: String,
        state_manager: Arc<dyn StateManager>,
        fsm_manager: Arc<dyn FSMManager>,
        service_msg_tx: flume::Sender<ServiceMessage>,
    ) -> Self {
        Self {
            invocation_id,
            handler_name,
            state_manager,
            journal: Arc::new(Mutex::new(Journal::new())),
            fsm_manager,
            replay_mode: false,
            current_step: 0,
            service_msg_tx,
        }
    }

    pub fn new_replay_mode(
        invocation_id: String,
        handler_name: String,
        state_manager: Arc<dyn StateManager>,
        fsm_manager: Arc<dyn FSMManager>,
        service_msg_tx: flume::Sender<ServiceMessage>,
        journal: Journal,
        current_step: usize,
    ) -> Self {
        Self {
            invocation_id,
            handler_name,
            state_manager,
            journal: Arc::new(Mutex::new(journal)),
            fsm_manager,
            replay_mode: true,
            current_step,
            service_msg_tx,
        }
    }
    
    /// Create a mock context for testing (should only be used in tests/flows)
    pub fn mock_for_testing(execution_id: String) -> Self {
        let (tx, _rx) = flume::unbounded();
        Self {
            invocation_id: execution_id.clone(),
            handler_name: "mock_handler".to_string(),
            state_manager: Arc::new(crate::state::InMemoryStateManager::new()),
            journal: Arc::new(Mutex::new(Journal::new())),
            fsm_manager: Arc::new(crate::fsm_manager::FSMManagerImpl::new(
                crate::fsm_manager::FSMManagerConfig::default()
            )),
            replay_mode: false,
            current_step: 0,
            service_msg_tx: tx,
        }
    }

    /// Durable state get operation with journaling
    pub async fn state_get(&mut self, key: &str) -> SdkResult<Option<Vec<u8>>> {
        if self.replay_mode {
            return self.replay_state_get(key).await;
        }
        
        let result = self.state_manager.get(key).await?;
        
        // Record the operation
        self.journal.lock().unwrap().record_state_get(key, result.clone());
        
        Ok(result)
    }

    /// Durable state set operation with journaling
    pub async fn state_set(&mut self, key: &str, value: Vec<u8>) -> SdkResult<()> {
        if self.replay_mode {
            return self.replay_state_set(key).await;
        }
        
        // Record the operation first
        self.journal.lock().unwrap().record_state_set(key, &value);
        
        // Then perform the actual operation
        self.state_manager.set(key, value).await
    }

    /// Durable external service call with FSM integration
    pub async fn call(&mut self, service: &str, method: &str, input: Vec<u8>) -> SdkResult<Vec<u8>> {
        if self.replay_mode {
            return self.replay_service_call().await;
        }
        
        // Record the call intent
        let call_id = self.journal.lock().unwrap().record_service_call(service, method, &input);
        let promise_id = format!("{}_{}", self.invocation_id, call_id);
        
        // Transition to suspended state
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Suspend {
            reason: SuspendReason::ServiceCall { promise_id: promise_id.clone() }
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        // Make the actual call (this will suspend the context)
        let result = self.make_service_call_and_suspend(service, method, input, promise_id).await;
        
        // On resume, transition back to running
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Resume {
            result: result.as_ref().ok().cloned()
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        // Record the result
        self.journal.lock().unwrap().update_service_result(call_id, &result);
        
        result
    }
    
    /// Durable sleep with FSM integration
    pub async fn sleep(&mut self, duration: Duration) -> SdkResult<()> {
        if self.replay_mode {
            return self.replay_sleep().await;
        }
        
        let sleep_id = self.journal.lock().unwrap().record_sleep(duration);
        
        // Transition to suspended sleep state
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Suspend {
            reason: SuspendReason::Sleep { duration }
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        // Request sleep (this will suspend the context)
        self.request_sleep_and_suspend(sleep_id, duration).await?;
        
        // On resume, transition back to running
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Resume {
            result: None
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        // Mark sleep as completed
        self.journal.lock().unwrap().mark_sleep_completed(sleep_id);
        
        Ok(())
    }
    
    /// Wait for external event with FSM integration
    pub async fn wait_for_event(&mut self, event_id: String, timeout: Option<Duration>) -> SdkResult<Vec<u8>> {
        if self.replay_mode {
            return self.replay_event_wait().await;
        }
        
        let await_id = self.journal.lock().unwrap().record_await(&event_id);
        
        // Transition to suspended event state
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Suspend {
            reason: SuspendReason::Event { event_id: event_id.clone() }
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        // Wait for event (this will suspend the context)
        let result = self.wait_for_event_and_suspend(event_id, timeout).await;
        
        // On resume, transition back to running
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Resume {
            result: result.as_ref().ok().cloned()
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        // Record the result
        if let Ok(ref data) = result {
            self.journal.lock().unwrap().update_await_result(await_id, data.clone());
        }
        
        result
    }
    
    /// Mark invocation as completed
    pub async fn complete(&mut self, result: Vec<u8>) -> SdkResult<()> {
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Complete {
            result: result.clone()
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        Ok(())
    }
    
    /// Mark invocation as failed
    pub async fn fail(&mut self, error: String) -> SdkResult<()> {
        self.fsm_manager.transition(&self.invocation_id, InvocationEvent::Fail {
            error
        }).await.map_err(|e| SdkError::InternalError(e.to_string()))?;
        
        Ok(())
    }
    
    /// Get current FSM state
    pub async fn get_state(&self) -> Option<InvocationState> {
        self.fsm_manager.get_state(&self.invocation_id).await
    }
    
    /// Check if invocation can be retried
    pub async fn can_retry(&self) -> bool {
        if let Some(state) = self.get_state().await {
            matches!(state, InvocationState::Failed { .. })
        } else {
            false
        }
    }

    /// Get current execution step
    pub fn current_step(&self) -> usize {
        self.current_step
    }

    /// Get journal entries for debugging
    pub fn get_journal_entries(&self) -> Vec<JournalEntry> {
        self.journal.lock().unwrap().entries.clone()
    }

    // Private helper methods for replay
    async fn replay_state_get(&mut self, key: &str) -> SdkResult<Option<Vec<u8>>> {
        let journal = self.journal.lock().unwrap();
        if let Some(entry) = journal.entries.get(self.current_step) {
            if let JournalEntry::StateGet { key: entry_key, result, .. } = entry {
                if entry_key == key {
                    self.current_step += 1;
                    return Ok(result.clone());
                }
            }
        }
        Err(SdkError::ReplayError(format!("Expected StateGet for key '{}' at step {}", key, self.current_step)))
    }

    async fn replay_state_set(&mut self, key: &str) -> SdkResult<()> {
        let journal = self.journal.lock().unwrap();
        if let Some(entry) = journal.entries.get(self.current_step) {
            if let JournalEntry::StateSet { key: entry_key, .. } = entry {
                if entry_key == key {
                    self.current_step += 1;
                    return Ok(());
                }
            }
        }
        Err(SdkError::ReplayError(format!("Expected StateSet for key '{}' at step {}", key, self.current_step)))
    }

    async fn replay_service_call(&mut self) -> SdkResult<Vec<u8>> {
        let journal = self.journal.lock().unwrap();
        if let Some(entry) = journal.entries.get(self.current_step) {
            if let JournalEntry::ServiceCall { result, .. } = entry {
                self.current_step += 1;
                return result.clone().map_err(|e| SdkError::ServiceCallError(e));
            }
        }
        Err(SdkError::ReplayError(format!("Expected ServiceCall at step {}", self.current_step)))
    }

    async fn replay_sleep(&mut self) -> SdkResult<()> {
        let journal = self.journal.lock().unwrap();
        if let Some(entry) = journal.entries.get(self.current_step) {
            if let JournalEntry::Sleep { completed, .. } = entry {
                if *completed {
                    self.current_step += 1;
                    return Ok(());
                }
            }
        }
        Err(SdkError::ReplayError(format!("Expected completed Sleep at step {}", self.current_step)))
    }

    async fn replay_event_wait(&mut self) -> SdkResult<Vec<u8>> {
        let journal = self.journal.lock().unwrap();
        if let Some(entry) = journal.entries.get(self.current_step) {
            if let JournalEntry::Await { result, .. } = entry {
                if let Some(data) = result {
                    self.current_step += 1;
                    return Ok(data.clone());
                }
            }
        }
        Err(SdkError::ReplayError(format!("Expected completed Await at step {}", self.current_step)))
    }

    // Private helper methods for actual operations
    async fn make_service_call_and_suspend(&self, service: &str, method: &str, input: Vec<u8>, promise_id: String) -> SdkResult<Vec<u8>> {
        // Create service call message
        let service_msg = ServiceMessage {
            invocation_id: self.invocation_id.clone(),
            message_type: Some(crate::pb::service_message::MessageType::ServiceCall(
                crate::pb::ServiceCall {
                    service_name: service.to_string(),
                    handler_name: method.to_string(),
                    input_data: input,
                    object_key: String::new(),
                    promise_id,
                }
            )),
        };

        // Send the message
        self.service_msg_tx.send_async(service_msg).await
            .map_err(|e| SdkError::InternalError(format!("Failed to send service call: {}", e)))?;

        // In a real implementation, this would suspend execution and wait for the response
        // For now, we'll simulate this with a placeholder
        Err(SdkError::SuspendedExecution("Waiting for service call response".to_string()))
    }

    async fn request_sleep_and_suspend(&self, sleep_id: usize, duration: Duration) -> SdkResult<()> {
        // Create sleep request message
        let service_msg = ServiceMessage {
            invocation_id: self.invocation_id.clone(),
            message_type: Some(crate::pb::service_message::MessageType::SleepRequest(
                crate::pb::SleepRequest {
                    duration_ms: duration.as_millis() as i64,
                    promise_id: sleep_id.to_string(),
                }
            )),
        };

        // Send the message
        self.service_msg_tx.send_async(service_msg).await
            .map_err(|e| SdkError::InternalError(format!("Failed to send sleep request: {}", e)))?;

        // In a real implementation, this would suspend execution and wait for the timer
        Err(SdkError::SuspendedExecution("Waiting for sleep to complete".to_string()))
    }

    async fn wait_for_event_and_suspend(&self, event_id: String, _timeout: Option<Duration>) -> SdkResult<Vec<u8>> {
        // Create await request message
        let service_msg = ServiceMessage {
            invocation_id: self.invocation_id.clone(),
            message_type: Some(crate::pb::service_message::MessageType::AwaitPromise(
                crate::pb::AwaitPromise {
                    promise_id: event_id,
                }
            )),
        };

        // Send the message
        self.service_msg_tx.send_async(service_msg).await
            .map_err(|e| SdkError::InternalError(format!("Failed to send await request: {}", e)))?;

        // In a real implementation, this would suspend execution and wait for the event
        Err(SdkError::SuspendedExecution("Waiting for event".to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use crate::invocation_fsm::FSMError;

    // Mock FSM Manager for testing
    struct MockFSMManager {
        states: Arc<Mutex<HashMap<String, InvocationState>>>,
    }

    impl MockFSMManager {
        fn new() -> Self {
            Self {
                states: Arc::new(Mutex::new(HashMap::new())),
            }
        }
    }

    impl FSMManager for MockFSMManager {
        fn transition(&self, invocation_id: &str, event: InvocationEvent) -> Pin<Box<dyn Future<Output = Result<InvocationState, FSMError>> + Send + '_>> {
            let states = Arc::clone(&self.states);
            let invocation_id = invocation_id.to_string();
            
            Box::pin(async move {
                let mut states = states.lock().unwrap();
                let current_state = states.get(&invocation_id).cloned().unwrap_or(InvocationState::Created);
                
                // Simple state transition logic for testing
                let new_state = match (&current_state, &event) {
                    (InvocationState::Created, InvocationEvent::Start) => InvocationState::Running,
                    (InvocationState::Running, InvocationEvent::Suspend { reason }) => {
                        match reason {
                            SuspendReason::ServiceCall { promise_id } => 
                                InvocationState::SuspendedAwait { promise_id: promise_id.clone() },
                            SuspendReason::Sleep { duration } => 
                                InvocationState::SuspendedSleep { wake_time: std::time::Instant::now() + *duration },
                            SuspendReason::Event { event_id } => 
                                InvocationState::SuspendedEvent { event_id: event_id.clone() },
                        }
                    },
                    (_, InvocationEvent::Resume { .. }) => InvocationState::Running,
                    (InvocationState::Running, InvocationEvent::Complete { result }) => 
                        InvocationState::Completed { result: result.clone() },
                    _ => return Err(FSMError::InvalidTransition { from: current_state, event }),
                };
                
                states.insert(invocation_id.to_string(), new_state.clone());
                Ok(new_state)
            })
        }

        fn get_state(&self, invocation_id: &str) -> Pin<Box<dyn Future<Output = Option<InvocationState>> + Send + '_>> {
            let states = Arc::clone(&self.states);
            let invocation_id = invocation_id.to_string();
            
            Box::pin(async move {
                states.lock().unwrap().get(&invocation_id).cloned()
            })
        }
    }

    // Mock State Manager for testing
    struct MockStateManager {
        data: Arc<Mutex<HashMap<String, Vec<u8>>>>,
    }

    impl MockStateManager {
        fn new() -> Self {
            Self {
                data: Arc::new(Mutex::new(HashMap::new())),
            }
        }
    }

    #[async_trait::async_trait]
    impl StateManager for MockStateManager {
        async fn get(&self, key: &str) -> SdkResult<Option<Vec<u8>>> {
            Ok(self.data.lock().unwrap().get(key).cloned())
        }

        async fn set(&self, key: &str, value: Vec<u8>) -> SdkResult<()> {
            self.data.lock().unwrap().insert(key.to_string(), value);
            Ok(())
        }

        async fn delete(&self, key: &str) -> SdkResult<()> {
            self.data.lock().unwrap().remove(key);
            Ok(())
        }
    }

    #[tokio::test]
    async fn test_journal_operations() {
        let mut journal = Journal::new();
        
        // Test state operations
        let step1 = journal.record_state_set("key1", b"value1");
        assert_eq!(step1, 0);
        assert_eq!(journal.current_step, 1);
        
        let step2 = journal.record_state_get("key1", Some(b"value1".to_vec()));
        assert_eq!(step2, 1);
        assert_eq!(journal.current_step, 2);
        
        // Test service call
        let step3 = journal.record_service_call("service", "method", b"input");
        assert_eq!(step3, 2);
        journal.update_service_result(step3, &Ok(b"output".to_vec()));
        
        // Verify entries
        assert_eq!(journal.entries.len(), 3);
        
        // Test replay
        let replay_entries = journal.replay_to_step(1);
        assert_eq!(replay_entries.len(), 2);
    }

    #[tokio::test]
    async fn test_durable_context_state_operations() {
        let (tx, _rx) = flume::unbounded();
        let state_manager = Arc::new(MockStateManager::new());
        let fsm_manager = Arc::new(MockFSMManager::new());
        
        let mut ctx = DurableContext::new(
            "test_inv".to_string(),
            "test_handler".to_string(),
            state_manager.clone(),
            fsm_manager,
            tx,
        );
        
        // Test state set
        ctx.state_set("test_key", b"test_value".to_vec()).await.unwrap();
        
        // Test state get
        let value = ctx.state_get("test_key").await.unwrap();
        assert_eq!(value, Some(b"test_value".to_vec()));
        
        // Verify journal recorded the operations
        let entries = ctx.get_journal_entries();
        assert_eq!(entries.len(), 2);
        
        match &entries[0] {
            JournalEntry::StateSet { key, value, .. } => {
                assert_eq!(key, "test_key");
                assert_eq!(value, b"test_value");
            },
            _ => panic!("Expected StateSet entry"),
        }
        
        match &entries[1] {
            JournalEntry::StateGet { key, result, .. } => {
                assert_eq!(key, "test_key");
                assert_eq!(result, &Some(b"test_value".to_vec()));
            },
            _ => panic!("Expected StateGet entry"),
        }
    }

    #[tokio::test]
    async fn test_durable_context_completion() {
        let (tx, _rx) = flume::unbounded();
        let state_manager = Arc::new(MockStateManager::new());
        let fsm_manager = Arc::new(MockFSMManager::new());
        
        let mut ctx = DurableContext::new(
            "test_inv".to_string(),
            "test_handler".to_string(),
            state_manager,
            fsm_manager.clone(),
            tx,
        );
        
        // Start the invocation
        fsm_manager.transition("test_inv", InvocationEvent::Start).await.unwrap();
        
        // Complete the invocation
        ctx.complete(b"result".to_vec()).await.unwrap();
        
        // Verify state
        let state = ctx.get_state().await.unwrap();
        assert!(matches!(state, InvocationState::Completed { .. }));
    }

    #[test]
    fn test_journal_entry_methods() {
        let entry = JournalEntry::StateSet {
            step: 5,
            key: "test".to_string(),
            value: vec![1, 2, 3],
        };
        
        assert_eq!(entry.step(), 5);
        assert!(entry.is_completed());
        
        let pending_call = JournalEntry::ServiceCall {
            step: 3,
            service: "test".to_string(),
            method: "test".to_string(),
            input: vec![],
            result: Err("pending".to_string()),
        };
        
        assert_eq!(pending_call.step(), 3);
        assert!(!pending_call.is_completed());
    }
}