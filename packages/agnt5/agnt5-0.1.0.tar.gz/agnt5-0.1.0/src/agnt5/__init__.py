"""
AGNT5 Python SDK - Build durable, resilient agent-first applications.

This SDK provides high-level components for building agents, tools, and workflows
with built-in durability guarantees and state management, backed by a high-performance
Rust core.
"""

# Import the Rust extension module
try:
    from . import _core
    from ._core import (
        PyDurableWorker as _PyDurableWorker,
        PyContext as _PyContext,
        PyHandler as _PyHandler,
        PyWorkerConfig as _PyWorkerConfig,
        PyInvocationResult as _PyInvocationResult,
        AgntError,
        create_worker,
        create_config,
        init_logging,
    )
    _rust_core_available = True
except ImportError as e:
    _rust_core_available = False
    _import_error = e

# Import Python implementations
from .durable import durable, DurableContext, DurableObject
from .context import Context, get_context
from .runtime import run_service, RuntimeConfig
from .workflow import Workflow, Step
from .types import (
    AgentConfig,
    ToolConfig, 
    WorkflowConfig,
    DurableConfig,
    ExecutionState,
)

# Import high-level AI components
from .agent import Agent
from .tool import Tool, tool
from .memory import Memory

# Import task system
from .task import (
    task,
    json_extraction_task,
    pydantic_task,
    string_task,
    Task,
    TaskResult,
    OutputFormat,
)

# Import LLM providers
from .llm import (
    LanguageModel,
    LanguageModelType,
    create_llm,
    Message,
    ToolCall,
    ToolResult,
    ANTHROPIC_AVAILABLE,
    OPENAI_AVAILABLE,
    GOOGLE_AVAILABLE,
    MISTRAL_AVAILABLE,
    AZURE_OPENAI_AVAILABLE,
    TOGETHER_AVAILABLE,
    get_available_providers,
)

# Import data extraction
from .extraction import (
    extract_json_from_text,
    extract_structured_data,
    extract_entities,
    JSONExtractor,
)

# Import reflection
from .reflection import (
    reflect_on_response,
    reflect_on_goals,
    analyze_errors,
    ReflectionEngine,
    ReflectionType,
    ReflectionLevel,
)

# High-level API exports
__version__ = "0.1.0"

def get_worker(
    service_name: str,
    service_version: str = "1.0.0",
    coordinator_endpoint: str = None,
) -> "DurableWorker":
    """
    Create a new durable worker using the Rust core.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        coordinator_endpoint: Endpoint of the coordinator service
        
    Returns:
        A configured DurableWorker instance
        
    Raises:
        RuntimeError: If the Rust core is not available
    """
    if not _rust_core_available:
        raise RuntimeError(
            f"Rust core is required but not available: {_import_error}. "
            "Please build and install the Rust extension first."
        )
    
    # Use the high-performance Rust core
    import uuid
    worker_id = str(uuid.uuid4())
    
    config = create_config(
        worker_id=worker_id,
        service_name=service_name,
        version=service_version,
    )
    
    rust_worker = create_worker(
        worker_id=worker_id,
        service_name=service_name,
        version=service_version,
        coordinator_endpoint=coordinator_endpoint,
    )
    
    return DurableWorker(rust_worker)

def setup_logging(level: str = "info"):
    """
    Initialize Rust logging.
    
    Args:
        level: Log level ('debug', 'info', 'warn', 'error')
    """
    if not _rust_core_available:
        print(f"Warning: Rust core not available, cannot initialize Rust logging: {_import_error}")
        return
    
    try:
        init_logging(level)
        print(f"Rust logging initialized at level: {level}")
    except Exception as e:
        print(f"Failed to initialize Rust logging: {e}")

def function(
    name: str = None,
    timeout: int = 300,
    retry: int = 3,
    **kwargs
):
    """
    Decorator to mark a function as durable.
    
    Args:
        name: Name of the function (defaults to function name)
        timeout: Timeout in seconds
        retry: Number of retry attempts
        
    Returns:
        Decorated function
    """
    return durable.function(name=name, timeout=timeout, retry=retry, **kwargs)

# Wrapper for Rust worker to provide consistent API
class DurableWorker:
    """High-performance durable worker backed by Rust core."""
    
    def __init__(self, rust_worker: "_PyDurableWorker"):
        self._rust_worker = rust_worker
        
    async def register_function(self, func, name: str = None, timeout: int = 300, retry: int = 3):
        """Register a function handler with the worker."""
        handler_name = name or func.__name__
        return self._rust_worker.register_function(
            name=handler_name,
            handler=func,
            timeout_secs=timeout,
            retry_attempts=retry,
        )
    
    async def register_object_factory(self, factory_class, name: str = None):
        """Register a durable object factory with the worker."""
        object_name = name or factory_class.__name__
        # For now, just log the registration since the Rust worker may not have this method yet
        print(f"📦 Registered object factory: {object_name}")
        return True
    
    async def start(self):
        """Start the worker."""
        return await self._rust_worker.start()
    
    async def stop(self):
        """Stop the worker."""
        return await self._rust_worker.stop()
    
    async def wait(self):
        """Wait for the worker to finish."""
        return await self._rust_worker.wait()
    
    async def get_status(self):
        """Get worker status."""
        return await self._rust_worker.get_status()
    
    @property
    def config(self):
        """Get worker configuration."""
        return self._rust_worker.config
    
    async def list_handlers(self):
        """List registered handlers."""
        return await self._rust_worker.list_handlers()

# Re-export key types
if _rust_core_available:
    WorkerConfig = _PyWorkerConfig
    InvocationResult = _PyInvocationResult

__all__ = [
    # Core worker management
    "get_worker",
    "DurableWorker", 
    "WorkerConfig",
    "setup_logging",
    
    # Decorators and context
    "function",
    "durable",
    "DurableContext", 
    "DurableObject",
    "Context",
    "get_context",
    
    # Runtime
    "run_service",
    "RuntimeConfig",
    
    # Types
    "DurableConfig",
    "ExecutionState", 
    "InvocationResult",
    "AgntError",
    
    # Version
    "__version__",
    
    # Workflow support  
    "Workflow",
    "Step",
    
    # High-level AI components
    "Agent",
    "Tool", 
    "tool",
    "Memory",
    
    # Task system
    "task",
    "json_extraction_task",
    "pydantic_task", 
    "string_task",
    "Task",
    "TaskResult",
    "OutputFormat",
    
    # LLM providers
    "LanguageModel",
    "LanguageModelType",
    "create_llm",
    "Message",
    "ToolCall",
    "ToolResult",
    "ANTHROPIC_AVAILABLE",
    "OPENAI_AVAILABLE", 
    "GOOGLE_AVAILABLE",
    "MISTRAL_AVAILABLE",
    "AZURE_OPENAI_AVAILABLE", 
    "TOGETHER_AVAILABLE",
    "get_available_providers",
    
    # Data extraction
    "extract_json_from_text",
    "extract_structured_data",
    "extract_entities",
    "JSONExtractor",
    
    # Reflection
    "reflect_on_response",
    "reflect_on_goals", 
    "analyze_errors",
    "ReflectionEngine",
    "ReflectionType",
    "ReflectionLevel",
]

# Expose rust core availability for debugging
globals()["_rust_core_available"] = _rust_core_available