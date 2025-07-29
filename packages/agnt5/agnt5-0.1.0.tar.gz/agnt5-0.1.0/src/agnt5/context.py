"""
Context management for the AGNT5 SDK.

Provides execution context for agents, tools, and workflows with
support for distributed tracing, state management, and error handling.
"""

from typing import Any, Dict, Optional, List, Union, TypeVar, ContextManager, Generic, Type
from contextvars import ContextVar
from contextlib import contextmanager
import uuid
from datetime import datetime
import logging
from dataclasses import dataclass, field

from .types import ExecutionContext, ExecutionState, Message


logger = logging.getLogger(__name__)

# Context variable for the current execution context
_current_context: ContextVar[Optional["Context"]] = ContextVar("agnt5_context", default=None)

T = TypeVar('T')


@dataclass
class Context:
    """
    Execution context for AGNT5 operations with durable primitives integration.
    
    Provides access to:
    - Execution metadata (ID, timestamps, state)
    - Distributed tracing information
    - Shared state and variables
    - Error handling and recovery
    - Durable function calls via ctx.call()
    - Durable sleep via ctx.sleep()
    - Durable object access via ctx.get_object()
    
    Example:
        ```python
        from agnt5 import Context, get_context
        
        # Get current context
        ctx = get_context()
        
        # Make durable service calls
        result = await ctx.call("data_service", "process", input_data)
        
        # Durable sleep
        await ctx.sleep(30)
        
        # Access durable objects
        memory = await ctx.get_object(AgentMemory, "user_123")
        
        # Store state
        await ctx.set("user_id", "123")
        user_id = await ctx.get("user_id")
        ```
    """
    
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    name: Optional[str] = None
    
    # Execution state
    state: ExecutionState = ExecutionState.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # State storage
    _state: Dict[str, Any] = field(default_factory=dict, init=False)
    
    # Conversation history (for agents)
    _messages: List[Message] = field(default_factory=list, init=False)
    
    # Error information
    error: Optional[Exception] = None
    error_count: int = 0
    
    def __post_init__(self):
        """Initialize context after creation."""
        if self.state == ExecutionState.RUNNING and not self.started_at:
            self.started_at = datetime.utcnow()
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in the context state with durable persistence.
        
        Args:
            key: State key
            value: State value
        """
        from .durable import _runtime_client
        
        if _runtime_client:
            await _runtime_client.save_state(key, value)
        else:
            self._state[key] = value
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the context state with durable persistence.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        from .durable import _runtime_client
        
        if _runtime_client:
            return await _runtime_client.load_state(key, default)
        else:
            return self._state.get(key, default)
    
    async def update(self, **kwargs) -> None:
        """Update multiple state values with durable persistence."""
        for key, value in kwargs.items():
            await self.set(key, value)
    
    async def clear(self) -> None:
        """Clear all state values with durable persistence."""
        from .durable import _runtime_client
        
        if _runtime_client:
            for key in list(self._state.keys()):
                await _runtime_client.delete_state(key)
        else:
            self._state.clear()
    
    @property
    def state_dict(self) -> Dict[str, Any]:
        """Get a copy of the state dictionary."""
        return self._state.copy()
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation history."""
        self._messages.append(message)
    
    def get_messages(self) -> List[Message]:
        """Get the conversation history."""
        return self._messages.copy()
    
    def clear_messages(self) -> None:
        """Clear the conversation history."""
        self._messages.clear()
    
    def create_child(self, name: str) -> "Context":
        """
        Create a child context.
        
        Args:
            name: Name for the child context
            
        Returns:
            Child context
        """
        child = Context(
            execution_id=str(uuid.uuid4()),
            parent_id=self.execution_id,
            name=name,
            state=ExecutionState.PENDING,
            metadata=self.metadata.copy(),
        )
        
        # Copy parent state
        child._state = self._state.copy()
        
        return child
    
    def record_error(self, error: Exception) -> None:
        """Record an error in the context."""
        self.error = error
        self.error_count += 1
        logger.error(f"Error in context {self.execution_id}: {error}")
    
    async def call(self, service: str, method: str, *args, **kwargs) -> Any:
        """
        Make a durable external service call via the runtime.
        
        Args:
            service: Service name
            method: Method name
            *args: Method arguments
            **kwargs: Method keyword arguments
            
        Returns:
            Service response
        """
        from .durable import _runtime_client
        
        if _runtime_client:
            return await _runtime_client.call_service(service, method, *args, **kwargs)
        else:
            # Fallback to mock response for testing
            logger.info(f"Mock service call: {service}.{method}")
            return f"mock_response_from_{service}_{method}"
    
    async def sleep(self, seconds: float) -> None:
        """
        Durable sleep that survives restarts.
        
        Args:
            seconds: Duration to sleep in seconds
        """
        from .durable import _runtime_client
        import asyncio
        
        if _runtime_client:
            await _runtime_client.durable_sleep(seconds)
        else:
            # Fallback for testing
            logger.info(f"Mock durable sleep: {seconds} seconds")
            await asyncio.sleep(seconds)
    
    async def get_object(self, object_class: Type[Any], object_id: str) -> Any:
        """
        Get or create a durable object instance.
        
        Args:
            object_class: The durable object class
            object_id: Unique identifier for the object instance
            
        Returns:
            Durable object instance
        """
        from .durable import _runtime_client
        
        if _runtime_client:
            return await _runtime_client.get_object(object_class, object_id)
        else:
            # Fallback: create object directly
            return await object_class.get_or_create(object_id)
    
    def mark_completed(self, success: bool = True) -> None:
        """Mark the context as completed."""
        self.completed_at = datetime.utcnow()
        self.state = ExecutionState.COMPLETED if success else ExecutionState.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "execution_id": self.execution_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "state": self.state.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "state_data": self._state,
            "error": str(self.error) if self.error else None,
            "error_count": self.error_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        """Create context from dictionary."""
        ctx = cls(
            execution_id=data["execution_id"],
            parent_id=data.get("parent_id"),
            name=data.get("name"),
            state=ExecutionState(data["state"]),
            metadata=data.get("metadata", {}),
        )
        
        # Restore timestamps
        if data.get("started_at"):
            ctx.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            ctx.completed_at = datetime.fromisoformat(data["completed_at"])
        
        # Restore state
        ctx._state = data.get("state_data", {})
        
        # Restore error info
        ctx.error_count = data.get("error_count", 0)
        
        return ctx


def get_context() -> Context:
    """
    Get the current execution context.
    
    Returns:
        Current context or creates a new one if none exists
    """
    ctx = _current_context.get()
    if ctx is None:
        ctx = Context()
        _current_context.set(ctx)
    return ctx


def set_context(ctx: Context) -> None:
    """
    Set the current execution context.
    
    Args:
        ctx: Context to set as current
    """
    _current_context.set(ctx)


@contextmanager
def use_context(ctx: Context) -> ContextManager[Context]:
    """
    Context manager to temporarily use a specific context.
    
    Example:
        ```python
        ctx = Context(name="my-operation")
        
        with use_context(ctx):
            # All operations here use ctx
            agent = Agent("my-agent")
            await agent.run("Hello")
        ```
    """
    previous = _current_context.get()
    _current_context.set(ctx)
    
    try:
        yield ctx
    finally:
        _current_context.set(previous)


@contextmanager
def create_context(
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> ContextManager[Context]:
    """
    Create and use a new context.
    
    Example:
        ```python
        with create_context("data-processing") as ctx:
            # Operations in this context
            ctx.set("batch_size", 100)
            process_data()
        ```
    """
    ctx = Context(
        name=name,
        metadata=metadata or {},
        state=ExecutionState.RUNNING,
    )
    
    with use_context(ctx):
        yield ctx


class ContextualValue(Generic[T]):
    """
    A value that is bound to the current context.
    
    Example:
        ```python
        # Define a contextual value
        current_user = ContextualValue[str]("current_user")
        
        # Set in context
        with create_context("request") as ctx:
            current_user.set("alice")
            
            # Get from anywhere in the call stack
            user = current_user.get()  # "alice"
        ```
    """
    
    def __init__(self, key: str, default: Optional[T] = None):
        """Initialize a contextual value."""
        self.key = key
        self.default = default
    
    def get(self) -> Optional[T]:
        """Get the value from the current context."""
        ctx = get_context()
        return ctx.get(self.key, self.default)
    
    def set(self, value: T) -> None:
        """Set the value in the current context."""
        ctx = get_context()
        ctx.set(self.key, value)
    
    def clear(self) -> None:
        """Clear the value from the current context."""
        ctx = get_context()
        if self.key in ctx._state:
            del ctx._state[self.key]


# Common contextual values
current_agent = ContextualValue[str]("current_agent")
current_workflow = ContextualValue[str]("current_workflow")
current_user = ContextualValue[str]("current_user")
current_tenant = ContextualValue[str]("current_tenant")