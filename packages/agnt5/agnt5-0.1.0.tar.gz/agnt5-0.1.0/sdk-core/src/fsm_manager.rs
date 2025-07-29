use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{Duration, Instant};
use std::future::Future;
use std::pin::Pin;

use crate::invocation_fsm::{InvocationFSM, InvocationState, InvocationEvent, SuspendReason, FSMError};
use crate::durable_context::FSMManager;

/// Configuration for FSM Manager
#[derive(Clone)]
pub struct FSMManagerConfig {
    pub default_max_retries: u32,
    pub cleanup_completed_after: Duration,
    pub cleanup_failed_after: Duration,
    pub max_concurrent_invocations: usize,
    pub cleanup_interval: Duration,
}

impl Default for FSMManagerConfig {
    fn default() -> Self {
        Self {
            default_max_retries: 3,
            cleanup_completed_after: Duration::from_secs(300), // 5 minutes
            cleanup_failed_after: Duration::from_secs(3600),   // 1 hour
            max_concurrent_invocations: 1000,
            cleanup_interval: Duration::from_secs(60),         // 1 minute
        }
    }
}

/// Statistics about current invocations
#[derive(Debug, Default)]
pub struct FSMStats {
    pub total: usize,
    pub created: usize,
    pub running: usize,
    pub suspended_await: usize,
    pub suspended_sleep: usize,
    pub suspended_event: usize,
    pub completed: usize,
    pub failed: usize,
    pub recovery: usize,
}

/// Manages multiple invocation state machines
pub struct FSMManagerImpl {
    invocations: Arc<RwLock<HashMap<String, InvocationFSM>>>,
    config: FSMManagerConfig,
    last_cleanup: Arc<RwLock<Instant>>,
}

impl FSMManagerImpl {
    pub fn new(config: FSMManagerConfig) -> Self {
        Self {
            invocations: Arc::new(RwLock::new(HashMap::new())),
            config,
            last_cleanup: Arc::new(RwLock::new(Instant::now())),
        }
    }
    
    /// Create a new invocation FSM
    pub async fn create_invocation(&self, invocation_id: String, handler_name: String) -> Result<(), FSMError> {
        let mut invocations = self.invocations.write().unwrap();
        
        if invocations.len() >= self.config.max_concurrent_invocations {
            return Err(FSMError::TooManyInvocations);
        }
        
        let fsm = InvocationFSM::new(invocation_id.clone(), handler_name, self.config.default_max_retries);
        invocations.insert(invocation_id, fsm);
        
        Ok(())
    }
    
    /// Get all invocations in a specific state
    pub async fn get_invocations_in_state(&self, target_state: fn(&InvocationState) -> bool) -> Vec<String> {
        let invocations = self.invocations.read().unwrap();
        invocations.iter()
            .filter(|(_, fsm)| target_state(&fsm.state))
            .map(|(id, _)| id.clone())
            .collect()
    }
    
    /// Get all suspended invocations that can be resumed
    pub async fn get_resumable_invocations(&self) -> Vec<(String, SuspendReason)> {
        let invocations = self.invocations.read().unwrap();
        invocations.iter()
            .filter_map(|(id, fsm)| {
                if fsm.is_suspended() {
                    fsm.suspension_reason().map(|reason| (id.clone(), reason))
                } else {
                    None
                }
            })
            .collect()
    }
    
    /// Get invocations that need recovery
    pub async fn get_recovery_invocations(&self) -> Vec<String> {
        self.get_invocations_in_state(|state| matches!(state, InvocationState::Recovery)).await
    }
    
    /// Get invocations that can be retried
    pub async fn get_retryable_invocations(&self) -> Vec<String> {
        let invocations = self.invocations.read().unwrap();
        invocations.iter()
            .filter_map(|(id, fsm)| {
                if fsm.can_retry() {
                    Some(id.clone())
                } else {
                    None
                }
            })
            .collect()
    }
    
    /// Mark all non-terminal invocations for recovery due to connection failure
    pub async fn mark_all_for_recovery(&self) -> Result<usize, FSMError> {
        let mut invocations = self.invocations.write().unwrap();
        let mut marked_count = 0;
        
        for (_, fsm) in invocations.iter_mut() {
            if !fsm.is_terminal() {
                fsm.transition(InvocationEvent::MarkForRecovery)?;
                marked_count += 1;
            }
        }
        
        Ok(marked_count)
    }
    
    /// Mark specific invocations for recovery
    pub async fn mark_invocations_for_recovery(&self, invocation_ids: &[String]) -> Result<usize, FSMError> {
        let mut invocations = self.invocations.write().unwrap();
        let mut marked_count = 0;
        
        for invocation_id in invocation_ids {
            if let Some(fsm) = invocations.get_mut(invocation_id) {
                if !fsm.is_terminal() {
                    fsm.transition(InvocationEvent::MarkForRecovery)?;
                    marked_count += 1;
                }
            }
        }
        
        Ok(marked_count)
    }
    
    /// Retry failed invocations that are eligible for retry
    pub async fn retry_failed_invocations(&self) -> Result<usize, FSMError> {
        let retryable = self.get_retryable_invocations().await;
        let mut retry_count = 0;
        
        for invocation_id in retryable {
            match self.transition(&invocation_id, InvocationEvent::Retry).await {
                Ok(_) => retry_count += 1,
                Err(e) => {
                    tracing::warn!("Failed to retry invocation {}: {}", invocation_id, e);
                }
            }
        }
        
        Ok(retry_count)
    }
    
    /// Cleanup completed and old failed invocations
    pub async fn cleanup_old_invocations(&self) -> usize {
        let mut invocations = self.invocations.write().unwrap();
        let now = Instant::now();
        let mut removed_count = 0;
        
        invocations.retain(|_, fsm| {
            let should_remove = match &fsm.state {
                InvocationState::Completed { .. } => {
                    now.duration_since(fsm.last_activity) > self.config.cleanup_completed_after
                },
                InvocationState::Failed { retry_count, .. } if *retry_count >= fsm.max_retries => {
                    now.duration_since(fsm.last_activity) > self.config.cleanup_failed_after
                },
                _ => false,
            };
            
            if should_remove {
                removed_count += 1;
                tracing::debug!("Cleaning up old invocation: {}", fsm.invocation_id);
            }
            
            !should_remove
        });
        
        // Update last cleanup time
        *self.last_cleanup.write().unwrap() = now;
        
        removed_count
    }
    
    /// Run automatic cleanup if enough time has passed
    pub async fn maybe_cleanup(&self) -> usize {
        let last_cleanup = *self.last_cleanup.read().unwrap();
        if Instant::now().duration_since(last_cleanup) >= self.config.cleanup_interval {
            self.cleanup_old_invocations().await
        } else {
            0
        }
    }
    
    /// Get statistics about current invocations
    pub async fn get_stats(&self) -> FSMStats {
        let invocations = self.invocations.read().unwrap();
        let mut stats = FSMStats::default();
        
        for fsm in invocations.values() {
            match &fsm.state {
                InvocationState::Created => stats.created += 1,
                InvocationState::Running => stats.running += 1,
                InvocationState::SuspendedAwait { .. } => stats.suspended_await += 1,
                InvocationState::SuspendedSleep { .. } => stats.suspended_sleep += 1,
                InvocationState::SuspendedEvent { .. } => stats.suspended_event += 1,
                InvocationState::Completed { .. } => stats.completed += 1,
                InvocationState::Failed { .. } => stats.failed += 1,
                InvocationState::Recovery => stats.recovery += 1,
            }
        }
        
        stats.total = invocations.len();
        stats
    }
    
    /// Get detailed information about a specific invocation
    pub async fn get_invocation_info(&self, invocation_id: &str) -> Option<InvocationInfo> {
        let invocations = self.invocations.read().unwrap();
        invocations.get(invocation_id).map(|fsm| InvocationInfo {
            invocation_id: fsm.invocation_id.clone(),
            handler_name: fsm.handler_name.clone(),
            state: fsm.state.clone(),
            current_step: fsm.current_step,
            created_at: fsm.created_at,
            last_activity: fsm.last_activity,
            retry_count: fsm.retry_count,
            max_retries: fsm.max_retries,
            can_retry: fsm.can_retry(),
            is_suspended: fsm.is_suspended(),
            is_terminal: fsm.is_terminal(),
            suspension_reason: fsm.suspension_reason(),
        })
    }
    
    /// Get all invocation information for debugging/monitoring
    pub async fn get_all_invocations(&self) -> Vec<InvocationInfo> {
        let invocations = self.invocations.read().unwrap();
        invocations.values()
            .map(|fsm| InvocationInfo {
                invocation_id: fsm.invocation_id.clone(),
                handler_name: fsm.handler_name.clone(),
                state: fsm.state.clone(),
                current_step: fsm.current_step,
                created_at: fsm.created_at,
                last_activity: fsm.last_activity,
                retry_count: fsm.retry_count,
                max_retries: fsm.max_retries,
                can_retry: fsm.can_retry(),
                is_suspended: fsm.is_suspended(),
                is_terminal: fsm.is_terminal(),
                suspension_reason: fsm.suspension_reason(),
            })
            .collect()
    }
    
    /// Remove a specific invocation (useful for testing or manual cleanup)
    pub async fn remove_invocation(&self, invocation_id: &str) -> bool {
        self.invocations.write().unwrap().remove(invocation_id).is_some()
    }
    
    /// Check if the manager is healthy (not over capacity)
    pub async fn is_healthy(&self) -> bool {
        let invocations = self.invocations.read().unwrap();
        invocations.len() < self.config.max_concurrent_invocations
    }
}

impl FSMManager for FSMManagerImpl {
    fn transition(&self, invocation_id: &str, event: InvocationEvent) -> Pin<Box<dyn Future<Output = Result<InvocationState, FSMError>> + Send + '_>> {
        let invocation_id = invocation_id.to_string();
        
        Box::pin(async move {
            let mut invocations = self.invocations.write().unwrap();
            
            let fsm = invocations.get_mut(&invocation_id)
                .ok_or_else(|| FSMError::InvocationNotFound { invocation_id: invocation_id.clone() })?;
            
            let result = fsm.transition(event);
            
            // FIXME: Note: Automatic cleanup should be handled by a separate background task
            // or triggered explicitly to avoid thread safety issues
            
            result
        })
    }

    fn get_state(&self, invocation_id: &str) -> Pin<Box<dyn Future<Output = Option<InvocationState>> + Send + '_>> {
        let invocation_id = invocation_id.to_string();
        
        Box::pin(async move {
            let invocations = self.invocations.read().unwrap();
            invocations.get(&invocation_id).map(|fsm| fsm.state.clone())
        })
    }
}

/// Detailed information about an invocation for monitoring
#[derive(Debug, Clone)]
pub struct InvocationInfo {
    pub invocation_id: String,
    pub handler_name: String,
    pub state: InvocationState,
    pub current_step: usize,
    pub created_at: Instant,
    pub last_activity: Instant,
    pub retry_count: u32,
    pub max_retries: u32,
    pub can_retry: bool,
    pub is_suspended: bool,
    pub is_terminal: bool,
    pub suspension_reason: Option<SuspendReason>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time::{sleep, Duration};

    #[tokio::test]
    async fn test_fsm_manager_creation() {
        let config = FSMManagerConfig::default();
        let manager = FSMManagerImpl::new(config);
        
        // Test creating an invocation
        let result = manager.create_invocation("test_inv".to_string(), "test_handler".to_string()).await;
        assert!(result.is_ok());
        
        // Test getting state
        let state = manager.get_state("test_inv").await;
        assert_eq!(state, Some(InvocationState::Created));
    }

    #[tokio::test]
    async fn test_fsm_manager_transitions() {
        let config = FSMManagerConfig::default();
        let manager = FSMManagerImpl::new(config);
        
        // Create invocation
        manager.create_invocation("test_inv".to_string(), "test_handler".to_string()).await.unwrap();
        
        // Test transition from Created to Running
        let result = manager.transition("test_inv", InvocationEvent::Start).await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), InvocationState::Running);
        
        // Test suspension
        let result = manager.transition("test_inv", InvocationEvent::Suspend {
            reason: SuspendReason::ServiceCall { promise_id: "promise_1".to_string() }
        }).await;
        assert!(result.is_ok());
        assert!(matches!(result.unwrap(), InvocationState::SuspendedAwait { .. }));
        
        // Test resume
        let result = manager.transition("test_inv", InvocationEvent::Resume { result: None }).await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), InvocationState::Running);
        
        // Test completion
        let result = manager.transition("test_inv", InvocationEvent::Complete {
            result: b"success".to_vec()
        }).await;
        assert!(result.is_ok());
        assert!(matches!(result.unwrap(), InvocationState::Completed { .. }));
    }

    #[tokio::test]
    async fn test_fsm_manager_recovery() {
        let config = FSMManagerConfig::default();
        let manager = FSMManagerImpl::new(config);
        
        // Create multiple invocations
        manager.create_invocation("inv1".to_string(), "handler1".to_string()).await.unwrap();
        manager.create_invocation("inv2".to_string(), "handler2".to_string()).await.unwrap();
        
        // Start them
        manager.transition("inv1", InvocationEvent::Start).await.unwrap();
        manager.transition("inv2", InvocationEvent::Start).await.unwrap();
        
        // Mark all for recovery
        let marked = manager.mark_all_for_recovery().await.unwrap();
        assert_eq!(marked, 2);
        
        // Verify they're in recovery state
        let recovery_invocations = manager.get_recovery_invocations().await;
        assert_eq!(recovery_invocations.len(), 2);
        assert!(recovery_invocations.contains(&"inv1".to_string()));
        assert!(recovery_invocations.contains(&"inv2".to_string()));
    }

    #[tokio::test]
    async fn test_fsm_manager_retry_logic() {
        let config = FSMManagerConfig {
            default_max_retries: 2,
            ..Default::default()
        };
        let manager = FSMManagerImpl::new(config);
        
        // Create and start invocation
        manager.create_invocation("test_inv".to_string(), "test_handler".to_string()).await.unwrap();
        manager.transition("test_inv", InvocationEvent::Start).await.unwrap();
        
        // Fail the invocation
        manager.transition("test_inv", InvocationEvent::Fail { 
            error: "test error".to_string() 
        }).await.unwrap();
        
        // Should be retryable
        let retryable = manager.get_retryable_invocations().await;
        assert_eq!(retryable.len(), 1);
        assert_eq!(retryable[0], "test_inv");
        
        // Retry
        let retry_count = manager.retry_failed_invocations().await.unwrap();
        assert_eq!(retry_count, 1);
        
        // Should be running again
        let state = manager.get_state("test_inv").await;
        assert_eq!(state, Some(InvocationState::Running));
    }

    #[tokio::test]
    async fn test_fsm_manager_stats() {
        let config = FSMManagerConfig::default();
        let manager = FSMManagerImpl::new(config);
        
        // Create invocations in different states
        manager.create_invocation("created".to_string(), "handler".to_string()).await.unwrap();
        
        manager.create_invocation("running".to_string(), "handler".to_string()).await.unwrap();
        manager.transition("running", InvocationEvent::Start).await.unwrap();
        
        manager.create_invocation("suspended".to_string(), "handler".to_string()).await.unwrap();
        manager.transition("suspended", InvocationEvent::Start).await.unwrap();
        manager.transition("suspended", InvocationEvent::Suspend {
            reason: SuspendReason::ServiceCall { promise_id: "promise".to_string() }
        }).await.unwrap();
        
        manager.create_invocation("completed".to_string(), "handler".to_string()).await.unwrap();
        manager.transition("completed", InvocationEvent::Start).await.unwrap();
        manager.transition("completed", InvocationEvent::Complete {
            result: b"done".to_vec()
        }).await.unwrap();
        
        // Get stats
        let stats = manager.get_stats().await;
        assert_eq!(stats.total, 4);
        assert_eq!(stats.created, 1);
        assert_eq!(stats.running, 1);
        assert_eq!(stats.suspended_await, 1);
        assert_eq!(stats.completed, 1);
    }

    #[tokio::test]
    async fn test_fsm_manager_cleanup() {
        let config = FSMManagerConfig {
            cleanup_completed_after: Duration::from_millis(10),
            cleanup_failed_after: Duration::from_millis(10),
            ..Default::default()
        };
        let manager = FSMManagerImpl::new(config);
        
        // Create and complete an invocation
        manager.create_invocation("completed".to_string(), "handler".to_string()).await.unwrap();
        manager.transition("completed", InvocationEvent::Start).await.unwrap();
        manager.transition("completed", InvocationEvent::Complete {
            result: b"done".to_vec()
        }).await.unwrap();
        
        // Wait a bit to ensure cleanup time has passed
        sleep(Duration::from_millis(20)).await;
        
        // Run cleanup
        let cleaned = manager.cleanup_old_invocations().await;
        assert_eq!(cleaned, 1);
        
        // Verify invocation was removed
        let stats = manager.get_stats().await;
        assert_eq!(stats.total, 0);
    }

    #[tokio::test]
    async fn test_fsm_manager_capacity_limits() {
        let config = FSMManagerConfig {
            max_concurrent_invocations: 2,
            ..Default::default()
        };
        let manager = FSMManagerImpl::new(config);
        
        // Create invocations up to limit
        assert!(manager.create_invocation("inv1".to_string(), "handler".to_string()).await.is_ok());
        assert!(manager.create_invocation("inv2".to_string(), "handler".to_string()).await.is_ok());
        
        // Should fail to create more
        let result = manager.create_invocation("inv3".to_string(), "handler".to_string()).await;
        assert!(matches!(result, Err(FSMError::TooManyInvocations)));
        
        // Should not be healthy
        assert!(!manager.is_healthy().await);
    }

    #[tokio::test]
    async fn test_fsm_manager_invocation_info() {
        let config = FSMManagerConfig::default();
        let manager = FSMManagerImpl::new(config);
        
        // Create invocation
        manager.create_invocation("test_inv".to_string(), "test_handler".to_string()).await.unwrap();
        
        // Get info
        let info = manager.get_invocation_info("test_inv").await;
        assert!(info.is_some());
        
        let info = info.unwrap();
        assert_eq!(info.invocation_id, "test_inv");
        assert_eq!(info.handler_name, "test_handler");
        assert_eq!(info.state, InvocationState::Created);
        assert_eq!(info.retry_count, 0);
        assert!(!info.is_suspended);
        assert!(!info.is_terminal);
    }
}