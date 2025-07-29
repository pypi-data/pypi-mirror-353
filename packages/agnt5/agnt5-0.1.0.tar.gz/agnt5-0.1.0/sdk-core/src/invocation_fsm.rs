use std::time::{Duration, Instant};
use thiserror::Error;

/// Finite State Machine for managing invocation lifecycle
#[derive(Debug, Clone, PartialEq)]
pub enum InvocationState {
    /// Initial state when invocation is created
    Created,
    /// Invocation is currently executing
    Running,
    /// Suspended waiting for external service call
    SuspendedAwait { promise_id: String },
    /// Suspended waiting for timer
    SuspendedSleep { wake_time: Instant },
    /// Suspended waiting for external event
    SuspendedEvent { event_id: String },
    /// Invocation completed successfully
    Completed { result: Vec<u8> },
    /// Invocation failed with error
    Failed { error: String, retry_count: u32 },
    /// Marked for recovery after connection failure
    Recovery,
}

/// State transition events
#[derive(Debug, Clone)]
pub enum InvocationEvent {
    Start,
    Suspend { reason: SuspendReason },
    Resume { result: Option<Vec<u8>> },
    Complete { result: Vec<u8> },
    Fail { error: String },
    Retry,
    MarkForRecovery,
}

#[derive(Debug, Clone)]
pub enum SuspendReason {
    ServiceCall { promise_id: String },
    Sleep { duration: Duration },
    Event { event_id: String },
}

/// Invocation FSM with state management
pub struct InvocationFSM {
    pub invocation_id: String,
    pub state: InvocationState,
    pub handler_name: String,
    pub current_step: usize,
    pub created_at: Instant,
    pub last_activity: Instant,
    pub retry_count: u32,
    pub max_retries: u32,
}

impl InvocationFSM {
    pub fn new(invocation_id: String, handler_name: String, max_retries: u32) -> Self {
        let now = Instant::now();
        Self {
            invocation_id,
            state: InvocationState::Created,
            handler_name,
            current_step: 0,
            created_at: now,
            last_activity: now,
            retry_count: 0,
            max_retries,
        }
    }
    
    /// Process state transition event
    pub fn transition(&mut self, event: InvocationEvent) -> Result<InvocationState, FSMError> {
        let new_state = match (&self.state, &event) {
            // Valid transitions from Created
            (InvocationState::Created, InvocationEvent::Start) => InvocationState::Running,
            
            // Valid transitions from Running
            (InvocationState::Running, InvocationEvent::Suspend { reason }) => {
                match reason {
                    SuspendReason::ServiceCall { promise_id } => 
                        InvocationState::SuspendedAwait { promise_id: promise_id.clone() },
                    SuspendReason::Sleep { duration } => 
                        InvocationState::SuspendedSleep { wake_time: Instant::now() + *duration },
                    SuspendReason::Event { event_id } => 
                        InvocationState::SuspendedEvent { event_id: event_id.clone() },
                }
            },
            (InvocationState::Running, InvocationEvent::Complete { result }) => 
                InvocationState::Completed { result: result.clone() },
            (InvocationState::Running, InvocationEvent::Fail { error }) => 
                InvocationState::Failed { error: error.clone(), retry_count: self.retry_count },
            
            // Valid transitions from Suspended states
            (InvocationState::SuspendedAwait { .. }, InvocationEvent::Resume { .. }) => InvocationState::Running,
            (InvocationState::SuspendedSleep { .. }, InvocationEvent::Resume { .. }) => InvocationState::Running,
            (InvocationState::SuspendedEvent { .. }, InvocationEvent::Resume { .. }) => InvocationState::Running,
            
            // Recovery transitions
            (_, InvocationEvent::MarkForRecovery) => InvocationState::Recovery,
            (InvocationState::Recovery, InvocationEvent::Start) => InvocationState::Running,
            
            // Retry transitions
            (InvocationState::Failed { .. }, InvocationEvent::Retry) if self.retry_count < self.max_retries => {
                self.retry_count += 1;
                InvocationState::Running
            },
            
            // Invalid transitions
            _ => return Err(FSMError::InvalidTransition {
                from: self.state.clone(),
                event: event.clone(),
            }),
        };
        
        self.state = new_state.clone();
        self.last_activity = Instant::now();
        
        tracing::debug!("Invocation {} transitioned to {:?}", self.invocation_id, new_state);
        Ok(new_state)
    }
    
    /// Check if invocation can be retried
    pub fn can_retry(&self) -> bool {
        matches!(self.state, InvocationState::Failed { .. }) && self.retry_count < self.max_retries
    }
    
    /// Check if invocation is in a suspended state
    pub fn is_suspended(&self) -> bool {
        matches!(self.state, 
            InvocationState::SuspendedAwait { .. } | 
            InvocationState::SuspendedSleep { .. } | 
            InvocationState::SuspendedEvent { .. }
        )
    }
    
    /// Check if invocation is terminal (completed or failed beyond retry)
    pub fn is_terminal(&self) -> bool {
        match &self.state {
            InvocationState::Completed { .. } => true,
            InvocationState::Failed { retry_count, .. } => *retry_count >= self.max_retries,
            _ => false,
        }
    }
    
    /// Get current suspension reason if suspended
    pub fn suspension_reason(&self) -> Option<SuspendReason> {
        match &self.state {
            InvocationState::SuspendedAwait { promise_id } => 
                Some(SuspendReason::ServiceCall { promise_id: promise_id.clone() }),
            InvocationState::SuspendedSleep { wake_time } => {
                let duration = wake_time.duration_since(Instant::now());
                Some(SuspendReason::Sleep { duration })
            },
            InvocationState::SuspendedEvent { event_id } => 
                Some(SuspendReason::Event { event_id: event_id.clone() }),
            _ => None,
        }
    }
}

#[derive(Debug, Error)]
pub enum FSMError {
    #[error("Invalid state transition from {from:?} with event {event:?}")]
    InvalidTransition { from: InvocationState, event: InvocationEvent },
    
    #[error("Invocation {invocation_id} not found")]
    InvocationNotFound { invocation_id: String },
    
    #[error("Too many concurrent invocations")]
    TooManyInvocations,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fsm_creation() {
        let fsm = InvocationFSM::new("test_inv".to_string(), "test_handler".to_string(), 3);
        assert_eq!(fsm.state, InvocationState::Created);
        assert_eq!(fsm.invocation_id, "test_inv");
        assert_eq!(fsm.handler_name, "test_handler");
        assert_eq!(fsm.retry_count, 0);
        assert_eq!(fsm.max_retries, 3);
    }

    #[test]
    fn test_valid_transitions() {
        let mut fsm = InvocationFSM::new("test".to_string(), "handler".to_string(), 3);
        
        // Created -> Running
        let result = fsm.transition(InvocationEvent::Start);
        assert!(result.is_ok());
        assert_eq!(fsm.state, InvocationState::Running);
        
        // Running -> SuspendedAwait
        let result = fsm.transition(InvocationEvent::Suspend {
            reason: SuspendReason::ServiceCall { promise_id: "promise_1".to_string() }
        });
        assert!(result.is_ok());
        assert!(matches!(fsm.state, InvocationState::SuspendedAwait { .. }));
        
        // SuspendedAwait -> Running
        let result = fsm.transition(InvocationEvent::Resume { result: None });
        assert!(result.is_ok());
        assert_eq!(fsm.state, InvocationState::Running);
        
        // Running -> Completed
        let result = fsm.transition(InvocationEvent::Complete {
            result: b"success".to_vec()
        });
        assert!(result.is_ok());
        assert!(matches!(fsm.state, InvocationState::Completed { .. }));
    }

    #[test]
    fn test_invalid_transitions() {
        let mut fsm = InvocationFSM::new("test".to_string(), "handler".to_string(), 3);
        
        // Cannot complete from Created state
        let result = fsm.transition(InvocationEvent::Complete {
            result: b"success".to_vec()
        });
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), FSMError::InvalidTransition { .. }));
    }

    #[test]
    fn test_retry_logic() {
        let mut fsm = InvocationFSM::new("test".to_string(), "handler".to_string(), 2);
        
        // Start -> Running -> Failed
        fsm.transition(InvocationEvent::Start).unwrap();
        fsm.transition(InvocationEvent::Fail { error: "test error".to_string() }).unwrap();
        
        assert!(fsm.can_retry());
        
        // Retry 1
        let result = fsm.transition(InvocationEvent::Retry);
        assert!(result.is_ok());
        assert_eq!(fsm.state, InvocationState::Running);
        assert_eq!(fsm.retry_count, 1);
        
        // Fail again
        fsm.transition(InvocationEvent::Fail { error: "test error 2".to_string() }).unwrap();
        assert!(fsm.can_retry());
        
        // Retry 2 (last retry)
        fsm.transition(InvocationEvent::Retry).unwrap();
        assert_eq!(fsm.retry_count, 2);
        
        // Fail again - no more retries
        fsm.transition(InvocationEvent::Fail { error: "test error 3".to_string() }).unwrap();
        assert!(!fsm.can_retry());
        assert!(fsm.is_terminal());
        
        // Cannot retry anymore
        let result = fsm.transition(InvocationEvent::Retry);
        assert!(result.is_err());
    }

    #[test]
    fn test_recovery_transitions() {
        let mut fsm = InvocationFSM::new("test".to_string(), "handler".to_string(), 3);
        
        // Start execution
        fsm.transition(InvocationEvent::Start).unwrap();
        assert_eq!(fsm.state, InvocationState::Running);
        
        // Mark for recovery
        let result = fsm.transition(InvocationEvent::MarkForRecovery);
        assert!(result.is_ok());
        assert_eq!(fsm.state, InvocationState::Recovery);
        
        // Restart from recovery
        let result = fsm.transition(InvocationEvent::Start);
        assert!(result.is_ok());
        assert_eq!(fsm.state, InvocationState::Running);
    }

    #[test]
    fn test_suspension_states() {
        let mut fsm = InvocationFSM::new("test".to_string(), "handler".to_string(), 3);
        
        fsm.transition(InvocationEvent::Start).unwrap();
        
        // Test service call suspension
        fsm.transition(InvocationEvent::Suspend {
            reason: SuspendReason::ServiceCall { promise_id: "promise_1".to_string() }
        }).unwrap();
        
        assert!(fsm.is_suspended());
        let reason = fsm.suspension_reason().unwrap();
        assert!(matches!(reason, SuspendReason::ServiceCall { .. }));
        
        // Resume
        fsm.transition(InvocationEvent::Resume { result: None }).unwrap();
        assert!(!fsm.is_suspended());
        
        // Test sleep suspension
        fsm.transition(InvocationEvent::Suspend {
            reason: SuspendReason::Sleep { duration: Duration::from_secs(5) }
        }).unwrap();
        
        assert!(fsm.is_suspended());
        let reason = fsm.suspension_reason().unwrap();
        assert!(matches!(reason, SuspendReason::Sleep { .. }));
    }
}