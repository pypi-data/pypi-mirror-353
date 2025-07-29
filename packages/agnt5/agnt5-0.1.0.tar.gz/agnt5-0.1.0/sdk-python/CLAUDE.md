# CLAUDE.md - AGNT5 Python SDK

This file provides guidance to Claude Code when working with the AGNT5 Python SDK, which enables building durable, resilient agent-first applications with a three-layer progressive disclosure design.

## SDK Overview

The AGNT5 Python SDK is a hybrid Python/Rust framework that provides:
- **High-level AI components**: Agents, Tools, Workflows for rapid development
- **Memory systems**: Working, episodic, semantic, and procedural memory
- **Durable primitives**: Low-level building blocks with exactly-once guarantees
- **Rust integration**: High-performance core via PyO3 bindings for optimal performance

## Architecture

### Multi-Language Integration
- **Python API Layer** (`src/agnt5/`): High-level Python APIs and decorators
- **Rust Bridge** (`rust-src/`): PyO3-based integration with SDK-Core (../sdk-core)
- **SDK-Core Integration**: Connection to AGNT5 runtime via gRPC and Protocol Buffers
- **Maturin Build System**: Seamless Python wheel packaging with Rust extensions

### Key Directories
```
sdk-python/
├── src/agnt5/           # Python API layer
│   ├── __init__.py      # Main exports and Rust core integration
│   ├── agent.py         # High-level Agent class
│   ├── durable.py       # Durable primitives (@function, @flow, @object)
│   ├── context.py       # Context API for all operations
│   ├── runtime.py       # Runtime integration and service management
│   ├── workflow.py      # Workflow orchestration
│   ├── memory.py        # Memory system implementations
│   ├── tool.py          # Tool definitions and decorators
│   ├── task.py          # Task extraction and processing
│   ├── types.py         # Type definitions and data models
│   └── llm/             # LLM provider integrations
├── rust-src/            # Rust bridge implementation
│   ├── lib.rs           # PyO3 module exports
│   ├── worker.rs        # Worker lifecycle management
│   ├── context.rs       # Context implementation
│   └── handlers.rs      # Function/object invocation handlers
├── examples/            # Example applications and benchmarks
└── pyproject.toml       # Python packaging and dependencies
```

## Development Patterns

### Layer 1: High-Level Components (Most Common)

**Creating Agents**
```python
from agnt5 import Agent, Tool

# Simple agent with memory
agent = Agent(
    name="assistant",
    instructions="You are a helpful AI assistant",
    tools=[search_tool, analysis_tool],
    memory=True,
    human_in_loop=True
)

response = await agent.run("user query")
```

**Building Tools**
```python
from agnt5 import Tool, tool

# Decorator approach
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return search_api(query)

# Class-based approach
search_tool = Tool(
    name="web_search",
    function=search_web,
    retry=3,
    timeout=30,
    description="Search web for current information"
)
```

**Workflow Orchestration**
```python
from agnt5 import Workflow, Step

workflow = Workflow([
    Step("extract", extract_data),
    Step("validate", validate_data),
    Step("store", store_data)
])

result = await workflow.run(input_data)
```

### Layer 2: Memory Systems

**Working Memory**
```python
from agnt5.memory import WorkingMemory

working_memory = WorkingMemory(capacity=1000)
await working_memory.store("user_preferences", {"theme": "dark"})
preferences = await working_memory.get("user_preferences")
```

**Episodic Memory**
```python
from agnt5.memory import EpisodicMemory

episodic_memory = EpisodicMemory()
await episodic_memory.remember("conversation", {
    "user": "How do I deploy my app?",
    "assistant": "Here are the deployment steps...",
    "timestamp": "2024-01-15T10:30:00Z"
})
```

### Layer 3: Durable Primitives (Power Users)

**@durable.function - Single reliable operation**
```python
from agnt5.durable import function

@function
async def reliable_api_call(ctx, endpoint: str, data: dict):
    """Function that survives failures with automatic retries."""
    return await ctx.call("external_service", endpoint, data)
```

**@durable.flow - Multi-step processes with state**
```python
from agnt5.durable import flow

@flow
async def complex_workflow(ctx, input_data):
    """Workflow that maintains state across failures."""
    step1_result = await ctx.call(process_step1, input_data)
    step2_result = await ctx.call(process_step2, step1_result)
    return await ctx.call(finalize_step, step2_result)
```

**@durable.object - Persistent state with serial execution**
```python
from agnt5.durable import object

@object
class AgentMemory:
    """Persistent object with thread-safe state management."""
    def __init__(self):
        self.context = {}
        self.history = []
    
    async def update(self, new_context):
        # Thread-safe, persistent across restarts
        self.context.update(new_context)
        self.history.append(new_context)
```

## Context API Patterns

All AGNT5 durable primitives provide a unified context API (`ctx`):

```python
@function
async def example_function(ctx, data):
    # Durable service calls
    result = await ctx.call(external_service, data)
    
    # Time delays (durable across restarts)
    await ctx.sleep(30)
    
    # Wait for events (human approval, webhooks, etc.)
    approval = await ctx.wait_for_event("approval_123", timeout=3600)
    
    # Parallel execution
    results = await ctx.spawn([
        (task1, args1),
        (task2, args2),
        (task3, args3)
    ])
    
    # Execution-scoped state management
    await ctx.state.set("progress", {"current": 3, "total": 10})
    progress = await ctx.state.get("progress")
    
    # Access shared durable objects
    memory = await ctx.get_object(AgentMemory, "user_123")
    
    # Built-in AI capabilities
    response = await ctx.chat(messages)
    embeddings = await ctx.embed(text)
    
    return result
```

## Common Development Commands

`uv` package and project manager is used for development. The sdk-core rust core is integrated into the `sdk-python` project using maturin python toolchain.

### Local Setup
```bash
# Download the packages and create the environment
uv sync

# Compile rust shared object using maturin and build the package as well for development
cd sdk/sdk-python
uv run maturin develop

# Build release wheel
uv run maturin build --release
```

Docker containers are used for local development. Python sdk based benchmark application is used for all the testing needs, it can be found at `sdk/sdk-python/examples/agnt5-python-bench`

### Docker Development Commands (from project root)
```bash
# Build Python SDK and add to uv virtual env in agnt5-python-bench container
just sdk-python-build

# Rebuild the agnt5-python-bench Docker image
just sdk-python-rebuild

# Run integration tests in the agnt5-python-bench container
just sdk-python-test

# Restart the agnt5-python-bench container instance
just sdk-python-restart
```

### Testing
```bash
# Run Python tests
uv run pytest tests/ -v

# Run specific test suite
uv run pytest tests/test_agent.py::test_agent_creation

# Run with coverage
uv run pytest tests/ --cov=agnt5 --cov-report=html

# Test async functionality
uv run pytest tests/ -k "async" --asyncio-mode=auto
```

### Development Tools
```bash
# Format code with ruff
uv tool install ruff # install the tool using uv
ruff check src/ tests/

# Type checking using pyright
uv tool install pyright
pyright

# Build documentation
sphinx-build docs/ docs/_build/
```

### Rust Development
```bash
# Build Rust components
cd rust-src/
cargo build --release

# Run Rust tests
cargo test

# Check Rust formatting
cargo fmt --check
cargo clippy
```


## Configuration and Environment

### Environment Variables
```bash
# Service configuration
export AGNT5_SERVICE_NAME="my-python-service"
export AGNT5_SERVICE_VERSION="1.0.0"

# If running inside a docker container
export AGNT5_RUNTIME_ENDPOINT="http://agnt5-runtime:8081"

# If runnig outside in local development
export AGNT5_RUNTIME_ENDPOINT="http://localhost:8081"


# Logging and observability
export AGNT5_LOG_LEVEL="INFO"
export AGNT5_TRACE_ENABLED="true"
export AGNT5_METRICS_ENABLED="true"

# Development settings
export AGNT5_DEV_MODE="true"
export AGNT5_HOT_RELOAD="true"
```

### Runtime Configuration
```python
from agnt5.runtime import RuntimeConfig

config = RuntimeConfig(
    service_name="my-service",
    runtime_endpoint="http://agnt5-runtime:8081",
    service_version="1.0.0",
    reconnect_attempts=5,
    reconnect_delay=2.0
)
```

## Worker Registration and Service Management

### Service Registration
```python
from agnt5 import get_worker, setup_logging

async def main():
    # Initialize logging
    setup_logging("info")
    
    # Create worker
    worker = get_worker(
        service_name="customer-support",
        service_version="1.0.0",
        coordinator_endpoint="http://agnt5-runtime:8081"
    )
    
    # Register handlers
    await worker.register_function(handle_customer_request, "customer_service")
    await worker.register_function(process_order_workflow, "process_order")
    await worker.register_object_factory(CustomerSession, "customer_session")
    
    # Start the worker
    await worker.start()
    await worker.wait()
```

### Example Application Structure
The benchmark application in `examples/agnt5-python-bench/` demonstrates proper structure:
- `agents/`: Agent implementations (customer_service.py, technical_support.py)
- `workflows/`: Durable workflow definitions (order_processing.py, issue_resolution.py)
- `objects/`: Durable object implementations (customer_session.py, order_tracker.py)
- `main.py`: Worker registration and service startup

## LLM Integration

### Provider Support
The SDK supports multiple LLM providers via `src/agnt5/llm/`:
- Anthropic (`anthropic.py`)
- OpenAI (`openai.py`)
- Google (`google.py`)
- Azure OpenAI (`azure.py`)
- Mistral (`mistral.py`)
- Together AI (`together.py`)

### Using LLM Providers
```python
from agnt5.llm import create_llm, LanguageModelType

# Create model instance
llm = create_llm(
    model_type=LanguageModelType.ANTHROPIC,
    model_name="claude-3-sonnet-20240229",
    api_key="your-api-key"
)

# Use in agent
agent = Agent(
    name="assistant",
    instructions="You are helpful",
    llm=llm
)
```

## Testing Patterns

### Unit Testing with Mock Context
```python
import pytest
from agnt5.testing import MockContext, MockAgent

async def test_agent_behavior():
    agent = Agent(name="test", instructions="Be helpful")
    
    with MockContext() as ctx:
        response = await agent.run("test query")
        assert "helpful" in response.lower()

async def test_durable_function():
    @function
    async def test_fn(ctx, data):
        return await ctx.call("service", "method", data)
    
    with MockContext() as ctx:
        ctx.mock_call("service", "method", return_value="mocked")
        result = await test_fn(ctx, {"test": "data"})
        assert result == "mocked"
```

### Integration Testing
```python
async def test_full_workflow():
    workflow = Workflow([
        Step("extract", extract_data),
        Step("validate", validate_data)
    ])
    
    result = await workflow.run(test_input)
    assert result["status"] == "success"
```

## Error Handling and Resilience

### Automatic Retry with Backoff
```python
from agnt5.durable import ExponentialBackoff

@function(retry_policy=ExponentialBackoff(max_attempts=5))
async def flaky_operation(ctx, data):
    """Automatic retry with exponential backoff."""
    return await ctx.call("unreliable_service", data)
```

### Custom Error Handling
```python
@flow
async def robust_workflow(ctx, input_data):
    try:
        return await ctx.call(primary_processor, input_data)
    except ServiceUnavailableError:
        # Fallback processing
        return await ctx.call(backup_processor, input_data)
```

## Performance Considerations

### Rust Core Integration
- **High Performance**: The SDK automatically uses the Rust core when available
- **Fallback**: Gracefully falls back to HTTP communication if Rust core is unavailable
- **Check availability**: Use `agnt5._rust_core_available` to check if Rust core is loaded

### Optimization Tips
1. **Use SDK-Core**: Install Rust extension for optimal performance
2. **Batch Operations**: Group multiple calls using `ctx.spawn()`
3. **Memory Management**: Configure appropriate cache sizes
4. **Async Patterns**: Use async/await throughout your code

## Deployment

### Docker Integration
Example Dockerfile for Python SDK applications:
```dockerfile
FROM python:3.11-slim

# Install Rust for building extensions
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install dependencies
COPY pyproject.toml .
RUN pip install -e ".[dev]"

# Build application
COPY . .
RUN maturin build --release
```

### Platform Deployment
```bash
# Deploy to AGNT5 Platform
agnt5 deploy --service my-python-service --image my-service:latest

# Monitor service
agnt5 logs --service my-python-service
agnt5 monitor --service my-python-service
```

## Troubleshooting

### Common Issues

**Rust Core Not Available**
```
WARNING: SDK-Core extension not available, falling back to HTTP communication
```
- Install Rust toolchain: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Rebuild extension: `maturin develop`
- Check PyO3 compatibility with Python version

**Connection Errors**
```
ERROR: Failed to connect to runtime at http://localhost:8080
```
- Ensure AGNT5 runtime is running: `just up` from project root
- Check endpoint configuration in `RuntimeConfig`
- Verify network connectivity and firewall settings

**Import Errors**
```
ImportError: cannot import name '_core' from 'agnt5'
```
- Rebuild Rust extension: `maturin develop`
- Check Python path and virtual environment
- Verify maturin installation: `pip install maturin`

### Debug Mode
```python
import agnt5
agnt5.setup_logging("DEBUG")

# Enable execution tracing
@function(trace=True)
async def traced_function(ctx, data):
    return await ctx.call("service", data)
```

## Integration with AGNT5 Platform

### Service Communication
- Uses Protocol Buffers for type-safe communication
- Generated types from `../../protos/gen/`
- Automatic serialization/deserialization of Python objects

### Observability
```python
# Automatic metrics collection
agent = Agent(
    name="monitored_agent",
    metrics=True,
    tracing=True
)

# Custom metrics in functions
@function
async def custom_operation(ctx, data):
    ctx.metrics.increment("custom_operation.calls")
    start_time = time.time()
    
    result = await ctx.call("service", data)
    
    ctx.metrics.histogram(
        "custom_operation.duration",
        time.time() - start_time
    )
    return result
```

## File Organization

### Important Files to Monitor
- `src/agnt5/__init__.py`: Main exports and Rust integration
- `src/agnt5/durable.py`: Core durable primitives implementation
- `src/agnt5/runtime.py`: Runtime integration and service lifecycle
- `rust-src/lib.rs`: PyO3 module exports and Rust integration
- `pyproject.toml`: Python packaging, dependencies, and build configuration
- `Cargo.toml`: Rust dependencies and build settings
- `examples/agnt5-python-bench/main.py`: Reference implementation for worker registration

### Development Workflow
1. Make changes to Python code in `src/agnt5/`
2. Update Rust bridge code in `rust-src/` if needed
3. Rebuild extension: `maturin develop`
4. Run tests: `pytest tests/`
5. Test with examples: `cd examples/agnt5-python-bench && python main.py`

This SDK provides a seamless bridge between high-level Python development and high-performance Rust execution, enabling developers to build sophisticated agent applications with durability guarantees and automatic failure recovery.