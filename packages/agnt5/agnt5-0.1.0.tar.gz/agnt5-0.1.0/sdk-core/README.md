# AGNT5 SDK-Core

The AGNT5 SDK-Core is a Rust library that provides the foundational communication layer for building durable, resilient agent-first applications. It handles protocol buffer communication, worker management, and low-level runtime interactions with the AGNT5 platform.

## Overview

SDK-Core serves as the communication bridge between user applications and the AGNT5 durable runtime. It provides:

- **Type-safe Protocol Buffer bindings** for all AGNT5 runtime services
- **Worker management** with automatic registration and lifecycle handling  
- **Message serialization/deserialization** with JSON and binary support
- **State management** for durable function execution
- **Type-safe wrappers** for complex protocol operations

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Code     │    │   SDK-Core       │    │ AGNT5 Runtime   │
│                 │    │                  │    │                 │
│ @durable.fn     │◄──►│ DurableWorker    │◄──►│ WorkerCoordinator│
│ Handler Impl    │    │ StateManager     │    │ Gateway Service │
│                 │    │ MessageSerializer│    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Current Implementation Status

### ✅ Completed Features

- **Protocol Buffer Integration (1.1)**
  - Build system for automatic protobuf compilation
  - Generated Rust bindings for `worker_coordinator.proto` and `gateway.proto`
  - Type-safe wrappers for all protocol messages

### 🚧 In Progress

- **Worker Communication Layer (1.2)** - Next phase
  - Bidirectional streaming client implementation
  - Connection lifecycle management
  - Message routing and serialization

## Usage Examples

### Basic Worker Setup

```rust
use agnt5_sdk_core::*;

// Create worker configuration
let config = WorkerConfig::new(
    "my-service".to_string(),
    "1.0.0".to_string()
);

// Create gRPC client
let client_config = ClientConfig::default();
let client = WorkerCoordinatorClient::new(client_config).await?;

// Create state manager (in-memory for development)
let state_manager = Arc::new(InMemoryStateManager::new());

// Create worker
let mut worker = DurableWorker::new(config, client, state_manager);

// Register a handler
#[async_trait::async_trait]
impl Handler for MyHandler {
    async fn invoke(&self, ctx: InvocationContext, input: Vec<u8>) -> SdkResult<Vec<u8>> {
        // Your business logic here
        let result = process_input(input).await?;
        Ok(result)
    }
}

worker.register_handler("my_handler".to_string(), Arc::new(MyHandler)).await;

// Start the worker
worker.start().await?;
```

### Type-Safe Message Construction

```rust
use agnt5_sdk_core::*;

// Build service registration with builder pattern
let registration = ServiceRegistrationBuilder::new(
    "order-processor".to_string(),
    "1.0.0".to_string()
)
.with_handler("process_order".to_string())
.with_handler("cancel_order".to_string())
.with_endpoint("localhost:8080".to_string())
.with_service_type(ServiceType::Function)
.with_metadata("env".to_string(), "production".to_string())
.build();

// Create state operations
let state_op = StateOperationRequest::Set {
    key: "order_status".to_string(),
    value: b"processing".to_vec(),
};

// Build service messages
let msg_builder = ServiceMessageBuilder::new("inv-123".to_string());
let response_msg = msg_builder.response(b"success".to_vec(), true);
let state_msg = msg_builder.clone().state_operation(state_op);

// Create external service calls
let service_call = ServiceCallBuilder::new(
    "payment-service".to_string(),
    "process_payment".to_string(),
    b"payment_data".to_vec(),
)
.with_object_key("user-456".to_string())
.build();
```

### Message Serialization

```rust
use agnt5_sdk_core::*;

// JSON serialization (default)
let serializer = JsonSerializer;

#[derive(Serialize, Deserialize)]
struct OrderData {
    order_id: String,
    amount: f64,
    items: Vec<String>,
}

let order = OrderData {
    order_id: "ord-123".to_string(),
    amount: 99.99,
    items: vec!["item1".to_string(), "item2".to_string()],
};

// Serialize for transmission
let bytes = serializer.serialize(&order)?;

// Deserialize from runtime
let received_order: OrderData = serializer.deserialize(&bytes)?;
```

### State Management

```rust
use agnt5_sdk_core::*;

// In-memory state manager (for development/testing)
let state_manager = InMemoryStateManager::new();

// Store state
state_manager.set("progress", b"step_2_complete".to_vec()).await?;

// Retrieve state
if let Some(progress) = state_manager.get("progress").await? {
    let status = String::from_utf8(progress)?;
    println!("Current progress: {}", status);
}

// Delete state
state_manager.delete("temp_data").await?;

// Remote state manager (for production)
let remote_state = RemoteStateManager::new("invocation-id-123".to_string());
// Note: Remote state manager requires bidirectional streaming (coming in 1.2)
```

## Protocol Buffer Messages

The SDK-Core provides access to all AGNT5 protocol buffer types:

### Service Registration
```rust
// Register a service with the runtime
let registration = ServiceRegistration {
    service_name: "my-service".to_string(),
    version: "1.0.0".to_string(),
    handlers: vec!["handler1".to_string(), "handler2".to_string()],
    endpoint: "worker-123".to_string(),
    protocol_version: "1.0".to_string(),
    supported_protocol_versions: vec!["1.0".to_string()],
    service_type: ServiceType::Function as i32,
    metadata: HashMap::new(),
};
```

### Runtime Messages
```rust
// Messages received from runtime
match RuntimeMessageType::from_runtime_message(msg)? {
    (invocation_id, RuntimeMessageType::InvocationStart { 
        service_name, handler_name, input_data, metadata 
    }) => {
        // Handle new invocation
        process_invocation(invocation_id, handler_name, input_data).await?;
    },
    (invocation_id, RuntimeMessageType::JournalEntry { entry_type }) => {
        // Handle journal replay during recovery
        replay_journal_entry(invocation_id, entry_type).await?;
    },
    (invocation_id, RuntimeMessageType::InvocationComplete { success, message }) => {
        // Handle invocation completion
        cleanup_invocation(invocation_id, success).await?;
    },
    (invocation_id, RuntimeMessageType::SuspensionComplete { 
        promise_id, result_data, error 
    }) => {
        // Handle promise resolution
        resolve_promise(promise_id, result_data, error).await?;
    },
}
```

## Configuration

### Client Configuration
```rust
let config = ClientConfig {
    gateway_endpoint: "http://localhost:8080".to_string(),
    worker_coordinator_endpoint: "http://localhost:8081".to_string(),
    timeout_seconds: 30,
    retry_attempts: 3,
};
```

### Worker Configuration
```rust
let worker_config = WorkerConfig {
    service_name: "my-service".to_string(),
    version: "1.0.0".to_string(),
    worker_id: "worker-unique-id".to_string(),
    max_concurrent_invocations: 10,
    heartbeat_interval_seconds: 30,
};
```

## Error Handling

SDK-Core provides comprehensive error types:

```rust
use agnt5_sdk_core::SdkError;

match result {
    Err(SdkError::Grpc(status)) => {
        eprintln!("gRPC error: {}", status);
    },
    Err(SdkError::Connection(msg)) => {
        eprintln!("Connection error: {}", msg);
    },
    Err(SdkError::Serialization(err)) => {
        eprintln!("Serialization error: {}", err);
    },
    Err(SdkError::State(msg)) => {
        eprintln!("State management error: {}", msg);
    },
    Err(SdkError::Invocation(msg)) => {
        eprintln!("Invocation error: {}", msg);
    },
    Ok(result) => {
        // Handle success
    },
}
```

## Testing

Run the test suite:

```bash
cargo test
```

Example tests are included for all wrapper types:

```rust
#[tokio::test]
async fn test_worker_lifecycle() {
    let config = WorkerConfig::new("test-service".to_string(), "1.0".to_string());
    let client = MockWorkerCoordinatorClient::new();
    let state_manager = Arc::new(InMemoryStateManager::new());
    
    let worker = DurableWorker::new(config, client, state_manager);
    
    // Test handler registration
    worker.register_handler("test_handler".to_string(), Arc::new(TestHandler)).await;
    
    // Note: Full lifecycle testing requires bidirectional streaming (1.2)
}
```

## Development

### Building

```bash
# Build the library
cargo build

# Build with release optimizations
cargo build --release

# Build and run tests
cargo test
```

### Protocol Buffer Updates

When protocol buffer definitions change:

1. The build system automatically regenerates Rust bindings
2. Update wrapper types in `src/wrappers.rs` if needed
3. Run tests to ensure compatibility

### Adding New Features

1. Add new modules to `src/`
2. Export public APIs in `src/lib.rs`
3. Add comprehensive tests
4. Update this README with usage examples

## Dependencies

### Core Dependencies
- **tonic** - gRPC client/server framework
- **prost** - Protocol Buffer implementation
- **tokio** - Async runtime
- **serde** - Serialization framework
- **anyhow** - Error handling
- **uuid** - Unique identifier generation

### Build Dependencies
- **tonic-build** - Protocol Buffer compilation

## Upcoming Features (Phase 1.2)

The next implementation phase will add:

- **Bidirectional Streaming**: Full `WorkerCoordinatorService.InvokeHandler` implementation
- **Connection Management**: Automatic reconnection and graceful shutdown
- **Message Routing**: Complete request/response handling
- **Promise Management**: Suspension and resumption support
- **Journal Replay**: State recovery during failures

## Contributing

1. Follow Rust naming conventions and formatting
2. Add comprehensive tests for new features  
3. Update documentation and examples
4. Ensure all builds pass: `cargo build && cargo test`

## License

This project is part of the AGNT5 Platform. See the main repository for license information.