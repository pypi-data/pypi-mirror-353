"""
Task system for AGNT5 SDK.

Provides @task decorator for creating structured, reusable operations with
validation, error handling, and integration with durable execution.
"""

import asyncio
import inspect
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_type_hints
from datetime import datetime
from enum import Enum

from .durable import durable
from .context import Context, get_context
from .tracing import trace_agent_run, span, traced, log, TraceLevel

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = "json"
    PYDANTIC = "pydantic"
    STRING = "string"
    RAW = "raw"


@dataclass
class TaskParameter:
    """Represents a task parameter with validation."""
    name: str
    type: Type
    description: Optional[str] = None
    required: bool = True
    default: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.__name__ if hasattr(self.type, '__name__') else str(self.type),
            "description": self.description,
            "required": self.required,
            "default": self.default
        }


@dataclass
class TaskConfig:
    """Configuration for a task."""
    name: str
    description: Optional[str] = None
    output_format: OutputFormat = OutputFormat.RAW
    output_schema: Optional[Dict[str, Any]] = None
    retry_count: int = 3
    timeout: Optional[float] = None
    enable_durability: bool = True
    parameters: List[TaskParameter] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "output_format": self.output_format.value,
            "output_schema": self.output_schema,
            "retry_count": self.retry_count,
            "timeout": self.timeout,
            "enable_durability": self.enable_durability,
            "parameters": [param.to_dict() for param in self.parameters]
        }


@dataclass
class TaskResult:
    """Result of task execution."""
    task_name: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_name": self.task_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time": self.execution_time
        }


class TaskRegistry:
    """Global registry for tasks."""
    _tasks: Dict[str, 'Task'] = {}
    
    @classmethod
    def register(cls, task: 'Task') -> None:
        """Register a task."""
        cls._tasks[task.config.name] = task
    
    @classmethod
    def get(cls, name: str) -> Optional['Task']:
        """Get a task by name."""
        return cls._tasks.get(name)
    
    @classmethod
    def list_tasks(cls) -> List[str]:
        """Get list of registered task names."""
        return list(cls._tasks.keys())
    
    @classmethod
    def get_all(cls) -> Dict[str, 'Task']:
        """Get all registered tasks."""
        return cls._tasks.copy()


class OutputValidator(ABC):
    """Base class for output validators."""
    
    @abstractmethod
    def validate(self, output: Any) -> Any:
        """Validate and potentially transform output."""
        pass


class JSONValidator(OutputValidator):
    """Validates and parses JSON output."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        self.schema = schema
    
    def validate(self, output: Any) -> Any:
        """Validate JSON output."""
        if isinstance(output, str):
            try:
                parsed = json.loads(output)
                return self._validate_schema(parsed) if self.schema else parsed
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON output: {e}")
        elif isinstance(output, (dict, list)):
            return self._validate_schema(output) if self.schema else output
        else:
            raise ValueError(f"Expected JSON-serializable output, got {type(output)}")
    
    def _validate_schema(self, data: Any) -> Any:
        """Basic schema validation (can be enhanced with jsonschema library)."""
        if not self.schema:
            return data
        
        # Basic type checking
        if "type" in self.schema:
            expected_type = self.schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                raise ValueError(f"Expected object, got {type(data)}")
            elif expected_type == "array" and not isinstance(data, list):
                raise ValueError(f"Expected array, got {type(data)}")
        
        # Check required properties for objects
        if isinstance(data, dict) and "properties" in self.schema:
            required = self.schema.get("required", [])
            for prop in required:
                if prop not in data:
                    raise ValueError(f"Missing required property: {prop}")
        
        return data


class PydanticValidator(OutputValidator):
    """Validates output using Pydantic models."""
    
    def __init__(self, model_class: Type):
        self.model_class = model_class
    
    def validate(self, output: Any) -> Any:
        """Validate using Pydantic model."""
        try:
            if isinstance(output, str):
                # Try to parse as JSON first
                try:
                    output = json.loads(output)
                except json.JSONDecodeError:
                    pass
            
            if isinstance(output, dict):
                return self.model_class(**output)
            else:
                return self.model_class(output)
        except Exception as e:
            raise ValueError(f"Failed to validate with {self.model_class.__name__}: {e}")


class Task:
    """
    A task represents a structured, reusable operation with validation and error handling.
    
    Tasks can be used for data extraction, processing, validation, and other operations
    that benefit from structured input/output and automatic retry mechanisms.
    """
    
    def __init__(self, config: TaskConfig, func: Callable):
        self.config = config
        self.func = func
        self._validator = self._create_validator()
        
        # Extract parameter information from function signature
        self._extract_parameters()
    
    def _create_validator(self) -> Optional[OutputValidator]:
        """Create appropriate validator based on configuration."""
        if self.config.output_format == OutputFormat.JSON:
            return JSONValidator(self.config.output_schema)
        elif self.config.output_format == OutputFormat.PYDANTIC and self.config.output_schema:
            # Output schema should contain the Pydantic model class
            model_class = self.config.output_schema.get("model_class")
            if model_class:
                return PydanticValidator(model_class)
        return None
    
    def _extract_parameters(self) -> None:
        """Extract parameter information from function signature."""
        try:
            sig = inspect.signature(self.func)
            
            # Try to get type hints, but handle forward references gracefully
            try:
                type_hints = get_type_hints(self.func)
            except (NameError, AttributeError):
                # Fall back to raw annotations if type hints can't be resolved
                type_hints = getattr(self.func, '__annotations__', {})
            
            parameters = []
            for param_name, param in sig.parameters.items():
                if param_name in ['self', 'cls']:
                    continue
                
                param_type = type_hints.get(param_name, str)
                required = param.default == inspect.Parameter.empty
                default = param.default if not required else None
                
                parameters.append(TaskParameter(
                    name=param_name,
                    type=param_type,
                    required=required,
                    default=default
                ))
            
            self.config.parameters = parameters
        except Exception as e:
            logger.warning(f"Failed to extract parameters for task {self.config.name}: {e}")
    
    async def run(self, *args, **kwargs) -> TaskResult:
        """Execute the task with validation and error handling."""
        task_result = TaskResult(
            task_name=self.config.name,
            status=TaskStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        with traced(f"task.{self.config.name}"):
            try:
                with span("task.execution") as task_span:
                    task_span.set_attribute("task.name", self.config.name)
                    task_span.set_attribute("task.durability", self.config.enable_durability)
                    task_span.set_attribute("task.output_format", self.config.output_format.value)
                    
                    # Execute with or without durability
                    if self.config.enable_durability:
                        output = await self._run_durable(*args, **kwargs)
                    else:
                        output = await self._run_direct(*args, **kwargs)
                    
                    # Validate output
                    if self._validator:
                        output = self._validator.validate(output)
                    
                    # Complete task
                    task_result.status = TaskStatus.COMPLETED
                    task_result.output = output
                    task_result.completed_at = datetime.utcnow()
                    task_result.execution_time = (
                        task_result.completed_at - task_result.started_at
                    ).total_seconds()
                    
                    task_span.set_attribute("task.status", "completed")
                    task_span.set_attribute("task.execution_time", task_result.execution_time)
                    
                    log(TraceLevel.INFO, f"Task {self.config.name} completed successfully",
                        task_name=self.config.name, execution_time=task_result.execution_time)
                    
                    return task_result
                    
            except Exception as e:
                task_result.status = TaskStatus.FAILED
                task_result.error = str(e)
                task_result.completed_at = datetime.utcnow()
                task_result.execution_time = (
                    task_result.completed_at - task_result.started_at
                ).total_seconds()
                
                logger.error(f"Task {self.config.name} failed: {e}")
                log(TraceLevel.ERROR, f"Task {self.config.name} failed: {e}",
                    task_name=self.config.name, error_type=type(e).__name__)
                
                return task_result
    
    @durable.function
    async def _run_durable(self, *args, **kwargs) -> Any:
        """Run task with durability guarantees."""
        return await self._run_direct(*args, **kwargs)
    
    async def _run_direct(self, *args, **kwargs) -> Any:
        """Run task directly without durability."""
        if inspect.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        else:
            # Run sync function in thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.func, *args, **kwargs)


def task(
    name: Optional[str] = None,
    description: Optional[str] = None,
    output_format: OutputFormat = OutputFormat.RAW,
    output_schema: Optional[Dict[str, Any]] = None,
    retry_count: int = 3,
    timeout: Optional[float] = None,
    enable_durability: bool = True,
) -> Callable:
    """
    Decorator to create a task from a function.
    
    Args:
        name: Task name (defaults to function name)
        description: Task description
        output_format: Expected output format (json, pydantic, string, raw)
        output_schema: Schema for output validation
        retry_count: Number of retry attempts on failure
        timeout: Execution timeout in seconds
        enable_durability: Whether to enable durable execution
        
    Example:
        ```python
        @task(name="extract_data", output_format=OutputFormat.JSON)
        def extract_json_data(text: str) -> dict:
            '''Extract structured data from text.'''
            # Processing logic
            return {"extracted": "data"}
        
        # Use the task
        result = await extract_json_data.run("input text")
        print(result.output)  # {"extracted": "data"}
        ```
    """
    def decorator(func: Callable) -> 'TaskFunction':
        task_name = name or func.__name__
        task_description = description or inspect.getdoc(func) or f"Task: {task_name}"
        
        config = TaskConfig(
            name=task_name,
            description=task_description,
            output_format=output_format,
            output_schema=output_schema,
            retry_count=retry_count,
            timeout=timeout,
            enable_durability=enable_durability
        )
        
        task_instance = Task(config, func)
        TaskRegistry.register(task_instance)
        
        # Create a wrapper that preserves the original function interface
        # but adds task capabilities
        return TaskFunction(task_instance, func)
    
    return decorator


class TaskFunction:
    """Wrapper that makes a task behave like a function while adding task capabilities."""
    
    def __init__(self, task: Task, original_func: Callable):
        self.task = task
        self.original_func = original_func
        self.__name__ = original_func.__name__
        self.__doc__ = original_func.__doc__
    
    async def __call__(self, *args, **kwargs) -> Any:
        """Direct function call returns just the output."""
        result = await self.task.run(*args, **kwargs)
        if result.status == TaskStatus.COMPLETED:
            return result.output
        else:
            raise RuntimeError(f"Task failed: {result.error}")
    
    async def run(self, *args, **kwargs) -> TaskResult:
        """Run as task and return full TaskResult."""
        return await self.task.run(*args, **kwargs)
    
    @property
    def config(self) -> TaskConfig:
        """Get task configuration."""
        return self.task.config
    
    def to_dict(self) -> Dict[str, Any]:
        """Export task configuration."""
        return self.task.config.to_dict()


# Convenience functions for common task types
def json_extraction_task(
    name: Optional[str] = None,
    description: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Callable:
    """Create a task for JSON data extraction."""
    return task(
        name=name,
        description=description,
        output_format=OutputFormat.JSON,
        output_schema=schema,
        **kwargs
    )


def pydantic_task(
    model_class: Type,
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> Callable:
    """Create a task with Pydantic output validation."""
    return task(
        name=name,
        description=description,
        output_format=OutputFormat.PYDANTIC,
        output_schema={"model_class": model_class},
        **kwargs
    )


def string_task(
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> Callable:
    """Create a task that returns string output."""
    return task(
        name=name,
        description=description,
        output_format=OutputFormat.STRING,
        **kwargs
    )