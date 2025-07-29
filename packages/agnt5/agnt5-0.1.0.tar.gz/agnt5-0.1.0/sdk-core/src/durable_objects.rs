//! Durable Objects support for the AGNT5 SDK Core
//! 
//! Provides virtual object management with:
//! - Object key routing and sharding
//! - Serialized access per object instance
//! - State persistence and recovery
//! - Method invocation handling

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{RwLock, Mutex};
use serde::{Deserialize, Serialize};
use async_trait::async_trait;

use crate::error::{SdkError, SdkResult};
use crate::worker::StateManager;

/// Configuration for durable objects
#[derive(Debug, Clone)]
pub struct DurableObjectConfig {
    /// Maximum number of object instances to keep in memory
    pub max_cached_objects: usize,
    /// TTL for inactive objects in seconds
    pub object_ttl_seconds: u64,
    /// Number of virtual shards for object routing
    pub shard_count: usize,
}

impl Default for DurableObjectConfig {
    fn default() -> Self {
        Self {
            max_cached_objects: 10000,
            object_ttl_seconds: 3600, // 1 hour
            shard_count: 256,
        }
    }
}

/// Object key for routing and identification
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ObjectKey {
    /// Object class name
    pub class_name: String,
    /// Object instance ID
    pub object_id: String,
    /// Generated routing key for consistent hashing
    pub routing_key: String,
}

impl ObjectKey {
    /// Create a new object key
    pub fn new(class_name: String, object_id: String) -> Self {
        let combined = format!("{}:{}", class_name, object_id);
        let routing_key = format!("{}#{:x}#{}", 
            class_name,
            crc32fast::hash(combined.as_bytes()) & 0xFFFF,
            object_id
        );
        
        Self {
            class_name,
            object_id,
            routing_key,
        }
    }
    
    /// Get shard ID for this object key
    pub fn shard_id(&self, shard_count: usize) -> usize {
        let hash = crc32fast::hash(self.routing_key.as_bytes());
        (hash as usize) % shard_count
    }
}

/// Method invocation request for durable objects
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObjectMethodInvocation {
    /// Object key
    pub object_key: ObjectKey,
    /// Method name to invoke
    pub method_name: String,
    /// Serialized arguments
    pub args: Vec<u8>,
    /// Invocation ID for tracking
    pub invocation_id: String,
}

/// Method invocation response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObjectMethodResponse {
    /// Invocation ID
    pub invocation_id: String,
    /// Success flag
    pub success: bool,
    /// Serialized result (if successful)
    pub result: Option<Vec<u8>>,
    /// Error message (if failed)
    pub error: Option<String>,
    /// Updated object state
    pub state_changes: Option<Vec<u8>>,
}

/// Trait for durable object implementations
#[async_trait]
pub trait DurableObject: Send + Sync {
    /// Get object class name
    fn class_name(&self) -> &str;
    
    /// Get object ID
    fn object_id(&self) -> &str;
    
    /// Invoke a method on this object
    async fn invoke_method(&mut self, method_name: &str, args: Vec<u8>) -> SdkResult<Vec<u8>>;
    
    /// Serialize object state
    async fn get_state(&self) -> SdkResult<Vec<u8>>;
    
    /// Restore object from state
    async fn restore_state(&mut self, state: Vec<u8>) -> SdkResult<()>;
    
    /// Save object state (called automatically after method invocation)
    async fn save(&self, state_manager: Arc<dyn StateManager>) -> SdkResult<()>;
}

/// Object instance wrapper with metadata
struct ObjectInstance {
    /// The actual object
    object: Box<dyn DurableObject>,
    /// Last access timestamp
    last_accessed: std::time::Instant,
    /// Access lock for serialized method execution
    access_lock: Arc<Mutex<()>>,
}

impl ObjectInstance {
    fn new(object: Box<dyn DurableObject>) -> Self {
        Self {
            object,
            last_accessed: std::time::Instant::now(),
            access_lock: Arc::new(Mutex::new(())),
        }
    }
    
    fn touch(&mut self) {
        self.last_accessed = std::time::Instant::now();
    }
}

/// Factory trait for creating durable objects
#[async_trait]
pub trait DurableObjectFactory: Send + Sync {
    /// Create a new object instance
    async fn create_object(&self, object_id: String) -> SdkResult<Box<dyn DurableObject>>;
    
    /// Get the class name this factory creates
    fn class_name(&self) -> &str;
}

/// Router for managing durable object instances and routing
pub struct DurableObjectRouter {
    /// Configuration
    config: DurableObjectConfig,
    /// Object factories by class name
    factories: RwLock<HashMap<String, Arc<dyn DurableObjectFactory>>>,
    /// Active object instances
    objects: RwLock<HashMap<ObjectKey, ObjectInstance>>,
    /// State manager for persistence
    state_manager: Arc<dyn StateManager>,
    /// Routing cache
    routing_cache: RwLock<HashMap<String, usize>>,
}

impl DurableObjectRouter {
    /// Create a new durable object router
    pub fn new(config: DurableObjectConfig, state_manager: Arc<dyn StateManager>) -> Self {
        Self {
            config,
            factories: RwLock::new(HashMap::new()),
            objects: RwLock::new(HashMap::new()),
            state_manager,
            routing_cache: RwLock::new(HashMap::new()),
        }
    }
    
    /// Register a factory for creating objects of a specific class
    pub async fn register_factory(&self, factory: Arc<dyn DurableObjectFactory>) {
        let class_name = factory.class_name().to_string();
        let mut factories = self.factories.write().await;
        factories.insert(class_name, factory);
    }
    
    /// Get or create a durable object
    pub async fn get_object(&self, class_name: &str, object_id: &str) -> SdkResult<ObjectKey> {
        let object_key = ObjectKey::new(class_name.to_string(), object_id.to_string());
        
        // Check if object already exists in memory
        {
            let objects = self.objects.read().await;
            if objects.contains_key(&object_key) {
                return Ok(object_key);
            }
        }
        
        // Object not in memory, create it
        let mut objects = self.objects.write().await;
        
        // Double-check pattern
        if objects.contains_key(&object_key) {
            return Ok(object_key);
        }
        
        // Get factory for this class
        let factory = {
            let factories = self.factories.read().await;
            factories.get(class_name)
                .cloned()
                .ok_or_else(|| SdkError::Configuration(
                    format!("No factory registered for class '{}'", class_name)
                ))?
        };
        
        // Try to load existing state
        let state_key = format!("object:{}:{}", class_name, object_id);
        let existing_state = self.state_manager.get(&state_key).await?;
        
        // Create object instance
        let mut object = factory.create_object(object_id.to_string()).await?;
        
        // Restore state if it exists
        if let Some(state) = existing_state {
            object.restore_state(state).await?;
        }
        
        // Store in memory
        let instance = ObjectInstance::new(object);
        objects.insert(object_key.clone(), instance);
        
        // Cleanup old objects if needed
        self.cleanup_objects(&mut objects).await;
        
        Ok(object_key)
    }
    
    /// Invoke a method on a durable object
    pub async fn invoke_method(&self, invocation: ObjectMethodInvocation) -> SdkResult<ObjectMethodResponse> {
        let object_key = &invocation.object_key;
        
        // Ensure object exists
        self.get_object(&object_key.class_name, &object_key.object_id).await?;
        
        // Get object instance
        let (access_lock, object_exists) = {
            let objects = self.objects.read().await;
            if let Some(instance) = objects.get(object_key) {
                (instance.access_lock.clone(), true)
            } else {
                (Arc::new(Mutex::new(())), false)
            }
        };
        
        if !object_exists {
            return Ok(ObjectMethodResponse {
                invocation_id: invocation.invocation_id,
                success: false,
                result: None,
                error: Some("Object not found".to_string()),
                state_changes: None,
            });
        }
        
        // Serialize access to this object
        let _lock = access_lock.lock().await;
        
        // Execute method with exclusive access
        let result = {
            let mut objects = self.objects.write().await;
            if let Some(instance) = objects.get_mut(object_key) {
                instance.touch();
                instance.object.invoke_method(&invocation.method_name, invocation.args).await
            } else {
                return Ok(ObjectMethodResponse {
                    invocation_id: invocation.invocation_id,
                    success: false,
                    result: None,
                    error: Some("Object disappeared during invocation".to_string()),
                    state_changes: None,
                });
            }
        };
        
        match result {
            Ok(response_data) => {
                // Save object state
                let state_changes = {
                    let objects = self.objects.read().await;
                    if let Some(instance) = objects.get(object_key) {
                        match instance.object.save(self.state_manager.clone()).await {
                            Ok(()) => instance.object.get_state().await.ok(),
                            Err(_) => None,
                        }
                    } else {
                        None
                    }
                };
                
                Ok(ObjectMethodResponse {
                    invocation_id: invocation.invocation_id,
                    success: true,
                    result: Some(response_data),
                    error: None,
                    state_changes,
                })
            }
            Err(e) => {
                Ok(ObjectMethodResponse {
                    invocation_id: invocation.invocation_id,
                    success: false,
                    result: None,
                    error: Some(e.to_string()),
                    state_changes: None,
                })
            }
        }
    }
    
    /// Get shard ID for an object key
    pub async fn get_shard_id(&self, object_key: &ObjectKey) -> usize {
        let routing_key = &object_key.routing_key;
        
        // Check cache first
        {
            let cache = self.routing_cache.read().await;
            if let Some(&shard_id) = cache.get(routing_key) {
                return shard_id;
            }
        }
        
        // Calculate and cache shard ID
        let shard_id = object_key.shard_id(self.config.shard_count);
        let mut cache = self.routing_cache.write().await;
        cache.insert(routing_key.clone(), shard_id);
        
        shard_id
    }
    
    /// Cleanup old objects from memory
    async fn cleanup_objects(&self, objects: &mut HashMap<ObjectKey, ObjectInstance>) {
        if objects.len() <= self.config.max_cached_objects {
            return;
        }
        
        let ttl = std::time::Duration::from_secs(self.config.object_ttl_seconds);
        let now = std::time::Instant::now();
        
        // Remove expired objects
        objects.retain(|_key, instance| {
            now.duration_since(instance.last_accessed) < ttl
        });
        
        // If still too many, remove oldest
        if objects.len() > self.config.max_cached_objects {
            let mut keys_to_remove = Vec::new();
            {
                let mut objects_by_age: Vec<_> = objects.iter().collect();
                objects_by_age.sort_by_key(|(_, instance)| instance.last_accessed);
                
                let to_remove = objects.len() - self.config.max_cached_objects;
                for (key, _) in objects_by_age.into_iter().take(to_remove) {
                    keys_to_remove.push(key.clone());
                }
            }
            
            for key in keys_to_remove {
                objects.remove(&key);
            }
        }
    }
    
    /// Get statistics about object usage
    pub async fn get_stats(&self) -> ObjectRouterStats {
        let objects = self.objects.read().await;
        let factories = self.factories.read().await;
        let routing_cache = self.routing_cache.read().await;
        
        ObjectRouterStats {
            active_objects: objects.len(),
            registered_factories: factories.len(),
            routing_cache_size: routing_cache.len(),
            max_cached_objects: self.config.max_cached_objects,
            shard_count: self.config.shard_count,
        }
    }
}

/// Statistics about the object router
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObjectRouterStats {
    /// Number of active objects in memory
    pub active_objects: usize,
    /// Number of registered object factories
    pub registered_factories: usize,
    /// Size of routing cache
    pub routing_cache_size: usize,
    /// Maximum cached objects configuration
    pub max_cached_objects: usize,
    /// Number of shards for routing
    pub shard_count: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::state::InMemoryStateManager;
    
    // Test durable object implementation
    struct TestCounter {
        object_id: String,
        count: i32,
    }
    
    #[async_trait]
    impl DurableObject for TestCounter {
        fn class_name(&self) -> &str {
            "TestCounter"
        }
        
        fn object_id(&self) -> &str {
            &self.object_id
        }
        
        async fn invoke_method(&mut self, method_name: &str, args: Vec<u8>) -> SdkResult<Vec<u8>> {
            match method_name {
                "increment" => {
                    self.count += 1;
                    Ok(self.count.to_string().into_bytes())
                }
                "get" => {
                    Ok(self.count.to_string().into_bytes())
                }
                "add" => {
                    let amount: i32 = String::from_utf8(args).unwrap().parse().unwrap();
                    self.count += amount;
                    Ok(self.count.to_string().into_bytes())
                }
                _ => Err(SdkError::Invocation(format!("Unknown method: {}", method_name)))
            }
        }
        
        async fn get_state(&self) -> SdkResult<Vec<u8>> {
            Ok(self.count.to_string().into_bytes())
        }
        
        async fn restore_state(&mut self, state: Vec<u8>) -> SdkResult<()> {
            self.count = String::from_utf8(state).unwrap().parse().unwrap();
            Ok(())
        }
        
        async fn save(&self, state_manager: Arc<dyn StateManager>) -> SdkResult<()> {
            let state_key = format!("object:{}:{}", self.class_name(), self.object_id());
            let state = self.get_state().await?;
            state_manager.set(&state_key, state).await
        }
    }
    
    // Test factory
    struct TestCounterFactory;
    
    #[async_trait]
    impl DurableObjectFactory for TestCounterFactory {
        async fn create_object(&self, object_id: String) -> SdkResult<Box<dyn DurableObject>> {
            Ok(Box::new(TestCounter { object_id, count: 0 }))
        }
        
        fn class_name(&self) -> &str {
            "TestCounter"
        }
    }
    
    #[tokio::test]
    async fn test_object_key_creation() {
        let key = ObjectKey::new("TestClass".to_string(), "test-id".to_string());
        
        assert_eq!(key.class_name, "TestClass");
        assert_eq!(key.object_id, "test-id");
        assert!(key.routing_key.contains("TestClass"));
        assert!(key.routing_key.contains("test-id"));
        
        // Test shard ID calculation
        let shard_id = key.shard_id(256);
        assert!(shard_id < 256);
    }
    
    #[tokio::test]
    async fn test_durable_object_router() {
        let config = DurableObjectConfig::default();
        let state_manager = Arc::new(InMemoryStateManager::new());
        let router = DurableObjectRouter::new(config, state_manager);
        
        // Register factory
        let factory = Arc::new(TestCounterFactory);
        router.register_factory(factory).await;
        
        // Get object
        let object_key = router.get_object("TestCounter", "test-1").await.unwrap();
        assert_eq!(object_key.class_name, "TestCounter");
        assert_eq!(object_key.object_id, "test-1");
        
        // Invoke methods
        let invocation = ObjectMethodInvocation {
            object_key: object_key.clone(),
            method_name: "increment".to_string(),
            args: vec![],
            invocation_id: "inv-1".to_string(),
        };
        
        let response = router.invoke_method(invocation).await.unwrap();
        assert!(response.success);
        assert_eq!(String::from_utf8(response.result.unwrap()).unwrap(), "1");
        
        // Invoke increment again
        let invocation2 = ObjectMethodInvocation {
            object_key: object_key.clone(),
            method_name: "increment".to_string(),
            args: vec![],
            invocation_id: "inv-2".to_string(),
        };
        
        let response2 = router.invoke_method(invocation2).await.unwrap();
        assert!(response2.success);
        assert_eq!(String::from_utf8(response2.result.unwrap()).unwrap(), "2");
        
        // Test add method with args
        let invocation3 = ObjectMethodInvocation {
            object_key: object_key.clone(),
            method_name: "add".to_string(),
            args: "5".as_bytes().to_vec(),
            invocation_id: "inv-3".to_string(),
        };
        
        let response3 = router.invoke_method(invocation3).await.unwrap();
        assert!(response3.success);
        assert_eq!(String::from_utf8(response3.result.unwrap()).unwrap(), "7");
    }
    
    #[tokio::test]
    async fn test_object_persistence() {
        let config = DurableObjectConfig::default();
        let state_manager = Arc::new(InMemoryStateManager::new());
        let router = DurableObjectRouter::new(config, state_manager.clone());
        
        // Register factory
        let factory = Arc::new(TestCounterFactory);
        router.register_factory(factory).await;
        
        // Create and use object
        let object_key = router.get_object("TestCounter", "persistent-test").await.unwrap();
        
        let invocation = ObjectMethodInvocation {
            object_key: object_key.clone(),
            method_name: "add".to_string(),
            args: "10".as_bytes().to_vec(),
            invocation_id: "inv-1".to_string(),
        };
        
        let response = router.invoke_method(invocation).await.unwrap();
        assert!(response.success);
        assert_eq!(String::from_utf8(response.result.unwrap()).unwrap(), "10");
        
        // Create new router with same state manager (simulating restart)
        let config2 = DurableObjectConfig::default();
        let router2 = DurableObjectRouter::new(config2, state_manager);
        
        let factory2 = Arc::new(TestCounterFactory);
        router2.register_factory(factory2).await;
        
        // Get same object - should restore state
        let object_key2 = router2.get_object("TestCounter", "persistent-test").await.unwrap();
        
        let invocation2 = ObjectMethodInvocation {
            object_key: object_key2,
            method_name: "get".to_string(),
            args: vec![],
            invocation_id: "inv-2".to_string(),
        };
        
        let response2 = router2.invoke_method(invocation2).await.unwrap();
        assert!(response2.success);
        assert_eq!(String::from_utf8(response2.result.unwrap()).unwrap(), "10");
    }
    
    #[tokio::test]
    async fn test_router_stats() {
        let config = DurableObjectConfig::default();
        let state_manager = Arc::new(InMemoryStateManager::new());
        let router = DurableObjectRouter::new(config, state_manager);
        
        // Register factory
        let factory = Arc::new(TestCounterFactory);
        router.register_factory(factory).await;
        
        // Create some objects
        router.get_object("TestCounter", "obj-1").await.unwrap();
        router.get_object("TestCounter", "obj-2").await.unwrap();
        
        let stats = router.get_stats().await;
        assert_eq!(stats.active_objects, 2);
        assert_eq!(stats.registered_factories, 1);
        assert_eq!(stats.shard_count, 256);
    }
}