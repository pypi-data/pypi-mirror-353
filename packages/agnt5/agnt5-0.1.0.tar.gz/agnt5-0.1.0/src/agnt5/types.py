"""
Type definitions for the AGNT5 SDK.
"""

from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


class ExecutionState(Enum):
    """State of a durable execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageRole(Enum):
    """Role of a message in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """Represents a message in an agent conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List["ToolCall"]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolCall:
    """Represents a tool invocation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool_call_id: str
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Configuration for an Agent."""
    name: str
    description: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: List[Union["Tool", Callable]] = field(default_factory=list)
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Durability settings
    enable_durability: bool = True
    checkpoint_interval: int = 10  # Checkpoint every N messages
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ToolConfig:
    """Configuration for a Tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution settings
    timeout: Optional[float] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_durability: bool = True


@dataclass
class WorkflowConfig:
    """Configuration for a Workflow."""
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Durability settings
    enable_durability: bool = True
    checkpoint_on_step: bool = True
    max_parallel_steps: int = 10
    timeout: Optional[float] = None


@dataclass
class DurableConfig:
    """Configuration for durable functions and objects."""
    name: str
    version: str = "1.0.0"
    
    # Execution settings
    deterministic: bool = True
    idempotent: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    
    # State management
    checkpoint_interval: Optional[int] = None
    state_retention_days: int = 30
    
    # Concurrency
    max_concurrent_executions: Optional[int] = None
    rate_limit: Optional[int] = None  # Per second


@dataclass
class ExecutionContext:
    """Context for a durable execution."""
    execution_id: str
    workflow_id: Optional[str] = None
    parent_execution_id: Optional[str] = None
    state: ExecutionState = ExecutionState.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Retry information
    attempt: int = 1
    last_error: Optional[str] = None
    
    # Checkpoint data
    last_checkpoint: Optional[datetime] = None
    checkpoint_data: Optional[Dict[str, Any]] = None


T = TypeVar('T')


class DurablePromise(Generic[T]):
    """A promise for durable async operations."""
    def __init__(self, execution_id: str, result_type: type[T]):
        self.execution_id = execution_id
        self.result_type = result_type
        self._result: Optional[T] = None
        self._error: Optional[Exception] = None
        self._completed = False
    
    @property
    def is_completed(self) -> bool:
        return self._completed
    
    def get(self, timeout: Optional[float] = None) -> T:
        """Get the result, blocking if necessary."""
        if self._error:
            raise self._error
        if not self._completed:
            raise RuntimeError("Promise not yet resolved")
        return self._result
    
    async def wait(self, timeout: Optional[float] = None) -> T:
        """Async wait for the result."""
        # Implementation would integrate with the runtime
        return self.get(timeout)


@dataclass
class MemoryEntry:
    """An entry in agent memory."""
    content: Any
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    
    def access(self):
        """Mark this entry as accessed."""
        self.accessed_at = datetime.now(timezone.utc)
        self.access_count += 1


@dataclass
class MemoryQuery:
    """Query for searching memory."""
    query: Optional[str] = None
    embedding: Optional[List[float]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10
    include_metadata: bool = True
    similarity_threshold: float = 0.7