"""
Durable execution primitives for the AGNT5 SDK.

Provides decorators and base classes for creating durable functions,
flows, and objects that survive failures and maintain state.
This is a thin wrapper around the Rust SDK-Core for high performance.
"""

from typing import Any, Callable, Optional, TypeVar, Union, Dict, List, Type
import functools
import inspect
import asyncio
import logging
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, asdict

from .types import DurableConfig, DurablePromise
from .context import get_context

logger = logging.getLogger(__name__)

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Global registry for durable functions, flows, and objects
_function_registry: Dict[str, "DurableFunction"] = {}
_flow_registry: Dict[str, "DurableFlow"] = {}
_object_registry: Dict[str, Type["DurableObject"]] = {}
_service_registry: Dict[str, "DurableService"] = {}
_runtime_client = None  # Will be set by SDK-Core integration


@dataclass
class InvocationRequest:
    """Request for function invocation from runtime."""
    invocation_id: str
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    context: Dict[str, Any]


@dataclass
class InvocationResponse:
    """Response for function invocation to runtime."""
    invocation_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    state_changes: Optional[Dict[str, Any]] = None


class DurableContext:
    """
    Durable execution context with runtime integration via SDK-Core.
    
    Provides APIs for:
    - External service calls via ctx.call()
    - Durable sleep via ctx.sleep() 
    - State management via ctx.state
    - Object access via ctx.get_object()
    """
    
    def __init__(self, invocation_id: str, context_data: Dict[str, Any]):
        self.invocation_id = invocation_id
        self.execution_id = context_data.get("execution_id", str(uuid.uuid4()))
        self.function_name = context_data.get("function_name", "")
        self._state: Dict[str, Any] = context_data.get("state", {})
        self._runtime_client = _runtime_client
    
    async def call(self, service: str, method: str, *args, **kwargs) -> Any:
        """Make a durable external service call via SDK-Core."""
        if self._runtime_client:
            return await self._runtime_client.durable_call(service, method, args, kwargs)
        else:
            # Fallback for local testing with realistic mock responses
            logger.info(f"Durable call: {service}.{method} with args={args}, kwargs={kwargs}")
            return self._generate_mock_response(service, method, args, kwargs)
    
    def _generate_mock_response(self, service: str, method: str, args: tuple, kwargs: dict) -> Any:
        """Generate realistic mock responses for testing."""
        # Data extractor service
        if service == "data_extractor" and method == "extract":
            return {
                "data": f"mock_data_from_{args[0].get('url', 'unknown')}" if args and isinstance(args[0], dict) else "mock_data",
                "size": 1024,
                "format": "json",
                "extracted_at": "2024-01-01T00:00:00Z"
            }
        
        # Data validator service
        elif service == "data_validator" and method == "validate":
            return {
                "valid": True,
                "score": 0.95,
                "issues": [],
                "validated_at": "2024-01-01T00:00:00Z"
            }
        
        # Data cleaner service
        elif service == "data_cleaner" and method == "clean":
            return {
                "cleaned_data": "cleaned_" + str(args[0]) if args else "cleaned_data",
                "transformations_applied": ["trim_whitespace", "normalize_encoding"],
                "cleaned_at": "2024-01-01T00:00:00Z"
            }
        
        # Data transformer service
        elif service == "data_transformer":
            transform_type = args[0].get("type", method) if args and isinstance(args[0], dict) else method
            return {
                "transformed_data": f"transformed_data_{transform_type}",
                "transformation_type": transform_type,
                "records_processed": 100,
                "transformed_at": "2024-01-01T00:00:00Z"
            }
        
        # Data aggregator service
        elif service == "data_aggregator" and method == "aggregate":
            return {
                "aggregated_data": "final_aggregated_result",
                "size": 5120,
                "records_count": 300,
                "aggregation_method": "merge_and_dedupe",
                "aggregated_at": "2024-01-01T00:00:00Z"
            }
        
        # Data storage service
        elif service == "data_storage" and method == "store":
            return {
                "success": True,
                "location": "database://processed_data/table_123",
                "record_id": "REC-789",
                "stored_at": "2024-01-01T00:00:00Z"
            }
        
        # Search service
        elif service == "search_service" and method == "search":
            query = args[0].get("query", "default") if args and isinstance(args[0], dict) else "default"
            max_results = args[0].get("max_results", 10) if args and isinstance(args[0], dict) else 10
            
            sources = []
            for i in range(max_results):
                sources.append({
                    "title": f"Source {i+1} for {query}",
                    "url": f"https://example.com/source_{i+1}",
                    "content": f"Content related to {query} from source {i+1}",
                    "metadata": {
                        "author": f"Author {i+1}",
                        "published_date": "2024-01-01",
                        "source_type": "academic" if i % 2 == 0 else "general"
                    }
                })
            return sources
        
        # Analysis service
        elif service == "analysis_service" and method == "analyze":
            content = args[0].get("content", "") if args and isinstance(args[0], dict) else ""
            return {
                "summary": f"Analysis summary of content (length: {len(content)})",
                "key_points": [
                    "Key finding 1",
                    "Key finding 2", 
                    "Key finding 3"
                ],
                "relevance_score": 0.85,
                "sentiment": "neutral",
                "analyzed_at": "2024-01-01T00:00:00Z"
            }
        
        # Synthesis service
        elif service == "synthesis_service" and method == "synthesize":
            return {
                "key_findings": [
                    "Finding 1: Important insight discovered",
                    "Finding 2: Significant pattern identified",
                    "Finding 3: Notable correlation found"
                ],
                "conclusions": [
                    "Conclusion 1: Evidence supports hypothesis",
                    "Conclusion 2: Further research recommended"
                ],
                "confidence_score": 0.88,
                "synthesized_at": "2024-01-01T00:00:00Z"
            }
        
        # Report generator service
        elif service == "report_generator" and method == "generate":
            topic = args[0].get("topic", "Unknown") if args and isinstance(args[0], dict) else "Unknown"
            return {
                "report_id": "RPT-12345",
                "title": f"Research Report: {topic}",
                "content": f"Comprehensive report on {topic} with detailed findings and analysis.",
                "format": "markdown",
                "pages": 15,
                "generated_at": "2024-01-01T00:00:00Z"
            }
        
        # Order service
        elif service == "order_service" and method == "validate":
            return {
                "valid": True,
                "validation_id": "VAL-123",
                "validated_at": "2024-01-01T00:00:00Z"
            }
        
        # Inventory service
        elif service == "inventory_service":
            if method == "reserve":
                return {
                    "success": True,
                    "reservation_id": f"RES-{args[0].get('product_id', 'UNKNOWN')}-123" if args and isinstance(args[0], dict) else "RES-123",
                    "quantity_reserved": args[0].get('quantity', 1) if args and isinstance(args[0], dict) else 1,
                    "reserved_at": "2024-01-01T00:00:00Z"
                }
            elif method in ["release", "confirm"]:
                return {
                    "success": True,
                    "processed_at": "2024-01-01T00:00:00Z"
                }
        
        # Payment service
        elif service == "payment_service" and method == "charge":
            return {
                "success": True,
                "payment_id": "PAY-78901",
                "transaction_id": "TXN-45678",
                "amount_charged": args[0].get('amount', 0) if args and isinstance(args[0], dict) else 0,
                "charged_at": "2024-01-01T00:00:00Z"
            }
        
        # Fulfillment service
        elif service == "fulfillment_service" and method == "create_shipment":
            return {
                "success": True,
                "shipment_id": "SHIP-56789",
                "tracking_number": "TRK-ABCDEF123456",
                "estimated_delivery": "2024-01-08T00:00:00Z",
                "carrier": "FedEx",
                "created_at": "2024-01-01T00:00:00Z"
            }
        
        # Notification service
        elif service == "notification_service" and method == "send_confirmation":
            return {
                "success": True,
                "notification_id": "NOT-12345",
                "sent_at": "2024-01-01T00:00:00Z"
            }
        
        # Default fallback
        else:
            return {
                "service": service,
                "method": method,
                "mock": True,
                "response": f"mock_response_from_{service}_{method}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    async def sleep(self, seconds: float) -> None:
        """Durable sleep that survives restarts via SDK-Core."""
        if self._runtime_client:
            await self._runtime_client.durable_sleep(seconds)
        else:
            # Fallback for local testing
            logger.info(f"Durable sleep: {seconds} seconds")
            await asyncio.sleep(seconds)
    
    @property
    def state(self) -> "StateManager":
        """Access execution-scoped state."""
        return StateManager(self._state, self._runtime_client)
    
    async def get_object(self, object_class: Type[T], object_id: str) -> T:
        """Get or create a durable object via SDK-Core."""
        if self._runtime_client:
            return await self._runtime_client.get_object(object_class.__name__, object_id)
        else:
            # Fallback for local testing
            return await object_class.get_or_create(object_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for persistence."""
        return {
            "invocation_id": self.invocation_id,
            "execution_id": self.execution_id,
            "function_name": self.function_name,
            "state": self._state,
        }


class StateManager:
    """Manages execution-scoped state via SDK-Core."""
    
    def __init__(self, state_dict: Dict[str, Any], runtime_client=None):
        self._state = state_dict
        self._runtime_client = runtime_client
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        if self._runtime_client:
            return await self._runtime_client.get_state(key, default)
        return self._state.get(key, default)
    
    async def set(self, key: str, value: Any) -> None:
        """Set a state value."""
        if self._runtime_client:
            await self._runtime_client.set_state(key, value)
        else:
            self._state[key] = value
    
    async def delete(self, key: str) -> None:
        """Delete a state value."""
        if self._runtime_client:
            await self._runtime_client.delete_state(key)
        else:
            self._state.pop(key, None)
    
    def keys(self) -> List[str]:
        """Get all state keys."""
        return list(self._state.keys())


class DurableFunction:
    """
    A durable function that maintains state across failures.
    Delegates execution to SDK-Core for high performance.
    """
    
    def __init__(self, func: Callable, config: Optional[DurableConfig] = None):
        """Initialize a durable function."""
        self.func = func
        self.is_async = inspect.iscoroutinefunction(func)
        
        # Configuration
        if config:
            self.config = config
        else:
            self.config = DurableConfig(
                name=func.__name__,
                version="1.0.0",
            )
        
        # Register the function
        _function_registry[self.config.name] = self
        
        # Preserve function metadata
        functools.update_wrapper(self, func)
    
    async def invoke(self, request: InvocationRequest) -> InvocationResponse:
        """
        Invoke the durable function with runtime request.
        Called by SDK-Core when runtime sends invocation.
        """
        try:
            # Create durable context from request
            ctx = DurableContext(request.invocation_id, request.context)
            
            # Prepare arguments - inject context as first parameter
            args = [ctx] + request.args
            
            # Execute the function
            if self.is_async:
                result = await self.func(*args, **request.kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self.func, *args, **request.kwargs)
            
            # Return successful response
            return InvocationResponse(
                invocation_id=request.invocation_id,
                success=True,
                result=result,
                state_changes=ctx.to_dict(),
            )
            
        except Exception as e:
            logger.error(f"Error executing durable function '{self.config.name}': {e}")
            return InvocationResponse(
                invocation_id=request.invocation_id,
                success=False,
                error=str(e),
            )
    
    async def __call__(self, *args, **kwargs) -> Any:
        """Direct call for local testing (bypasses runtime)."""
        # Create mock request for local execution
        request = InvocationRequest(
            invocation_id=str(uuid.uuid4()),
            function_name=self.config.name,
            args=list(args),
            kwargs=kwargs,
            context={
                "execution_id": str(uuid.uuid4()),
                "function_name": self.config.name,
            }
        )
        
        response = await self.invoke(request)
        if response.success:
            return response.result
        else:
            raise RuntimeError(response.error)


class DurableFlow:
    """
    A durable flow that orchestrates multiple steps via SDK-Core.
    
    Durable flows provide:
    - Multi-step process coordination with shared state
    - Automatic checkpointing and recovery
    - Parallel execution of independent steps
    - Error handling and retry logic
    - Integration with the Rust flow engine
    
    Example:
        ```python
        @durable.flow
        async def research_workflow(ctx, topic):
            # Step 1: Search for sources
            sources = await ctx.call(search_sources, topic)
            await ctx.state.set("sources", sources)
            
            # Step 2: Analyze each source (can run in parallel)
            analyses = []
            for source in sources:
                analysis = await ctx.call(analyze_source, source)
                analyses.append(analysis)
            
            # Step 3: Synthesize results
            await ctx.state.set("analyses", analyses)
            report = await ctx.call(generate_report, analyses)
            
            return report
        ```
    """
    
    def __init__(self, func: Callable, config: Optional[DurableConfig] = None):
        """Initialize a durable flow."""
        self.func = func
        self.is_async = inspect.iscoroutinefunction(func)
        
        # Configuration with flow-specific defaults
        if config:
            self.config = config
        else:
            self.config = DurableConfig(
                name=func.__name__,
                version="1.0.0",
                checkpoint_interval=1,  # Checkpoint after each step by default
                deterministic=True,     # Flows should be deterministic
            )
        
        # Register the flow as a function but track it as a flow
        self._durable_func = DurableFunction(self._flow_wrapper, self.config)
        
        # Register in flow registry
        _flow_registry[self.config.name] = self
        
        # Preserve function metadata
        functools.update_wrapper(self, func)
    
    async def _flow_wrapper(self, ctx: DurableContext, *args, **kwargs) -> Any:
        """
        Wrapper that executes the flow function with enhanced context.
        
        This wrapper provides flow-specific functionality like:
        - Step tracking and checkpointing
        - Shared state management
        - Parallel execution coordination
        """
        # Initialize flow execution context in shared state
        flow_state = {
            "flow_name": self.config.name,
            "execution_id": ctx.execution_id,
            "current_step": 0,
            "completed_steps": [],
            "step_results": {},
            "flow_config": {
                "checkpoint_interval": getattr(self.config, 'checkpoint_interval', 1),
                "max_retries": self.config.max_retries,
                "deterministic": self.config.deterministic,
            }
        }
        
        # Store initial flow state
        await ctx.state.set("__flow_state__", flow_state)
        
        try:
            # Execute the actual flow function
            if self.is_async:
                result = await self.func(ctx, *args, **kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self.func, ctx, *args, **kwargs)
            
            # Mark flow as completed
            flow_state["status"] = "completed"
            flow_state["result"] = result
            await ctx.state.set("__flow_state__", flow_state)
            
            return result
            
        except Exception as e:
            # Mark flow as failed
            flow_state["status"] = "failed"
            flow_state["error"] = str(e)
            await ctx.state.set("__flow_state__", flow_state)
            raise
    
    async def invoke(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke the durable flow via the function wrapper."""
        return await self._durable_func.invoke(request)
    
    async def __call__(self, *args, **kwargs) -> Any:
        """Execute the durable flow."""
        return await self._durable_func(*args, **kwargs)
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the current status of a flow execution."""
        if _runtime_client:
            return await _runtime_client.get_flow_status(self.config.name, execution_id)
        else:
            # Fallback for local testing
            return {
                "execution_id": execution_id,
                "flow_name": self.config.name,
                "status": "unknown",
                "current_step": 0,
                "completed_steps": [],
            }
    
    async def resume_execution(self, execution_id: str) -> Any:
        """Resume a suspended flow execution."""
        if _runtime_client:
            return await _runtime_client.resume_flow(self.config.name, execution_id)
        else:
            raise RuntimeError("Flow resumption requires runtime client integration")
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running flow execution."""
        if _runtime_client:
            return await _runtime_client.cancel_flow(self.config.name, execution_id)
        else:
            # Fallback for local testing
            logger.info(f"Mock cancellation of flow {self.config.name} execution {execution_id}")
            return True


class DurableObject:
    """
    Base class for durable objects that maintain state.
    
    Durable objects provide:
    - Automatic state persistence via SDK-Core
    - Serialized access per object instance
    - Method invocation routing
    - Virtual object management
    
    Example:
        ```python
        @durable.object
        class ShoppingCart:
            def __init__(self, user_id: str):
                self.user_id = user_id
                self.items = []
            
            async def add_item(self, item_id: str, quantity: int):
                self.items.append({"id": item_id, "qty": quantity})
                await self.save()
            
            async def checkout(self, ctx: DurableContext):
                total = await ctx.call("pricing_service", "calculate_total", self.items)
                order = await ctx.call("order_service", "create_order", {
                    "user_id": self.user_id,
                    "items": self.items,
                    "total": total
                })
                self.items = []
                await self.save()
                return order
        ```
    """
    
    def __init__(self, object_id: str):
        """Initialize a durable object."""
        self.object_id = object_id
        self._version = 0
        from datetime import timezone
        self._last_saved = datetime.now(timezone.utc)
        self._methods: Dict[str, Callable] = {}
        
        # Register all public methods as invokable
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_') and name not in ['save', 'get_or_create']:
                self._methods[name] = method
    
    @classmethod
    async def get_or_create(cls, object_id: str) -> "DurableObject":
        """Get an existing object or create a new one via SDK-Core."""
        if _runtime_client:
            return await _runtime_client.get_or_create_object(cls.__name__, object_id)
        
        # Fallback for local testing
        state = await cls._load_state(object_id)
        if state:
            obj = cls(object_id)
            await obj._restore_state(state)
            return obj
        else:
            obj = cls(object_id)
            await obj.save()
            return obj
    
    async def invoke_method(self, method_name: str, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        """Invoke a method on this object."""
        if method_name not in self._methods:
            raise ValueError(f"Method '{method_name}' not found on object {self.object_id}")
        
        method = self._methods[method_name]
        if inspect.iscoroutinefunction(method):
            result = await method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)
        
        # Auto-save after method execution
        await self.save()
        return result
    
    async def save(self) -> None:
        """Save the object state via SDK-Core."""
        if _runtime_client:
            state = await self._get_state()
            await _runtime_client.save_object_state(self.__class__.__name__, self.object_id, state)
        else:
            # Fallback for local testing
            state = await self._get_state()
            await self._save_state(self.object_id, state)
        
        self._version += 1
        from datetime import timezone
        self._last_saved = datetime.now(timezone.utc)
    
    async def _get_state(self) -> Dict[str, Any]:
        """Get the current state for serialization."""
        state = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and not callable(value):
                try:
                    # Try to serialize the value
                    json.dumps(value, default=str)
                    state[key] = value
                except (TypeError, ValueError):
                    # Skip non-serializable values
                    logger.warning(f"Skipping non-serializable attribute '{key}' in object {self.object_id}")
        
        state['_version'] = self._version
        state['_last_saved'] = self._last_saved.isoformat()
        return state
    
    async def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore state from serialization."""
        for key, value in state.items():
            if key == '_last_saved':
                self._last_saved = datetime.fromisoformat(value)
            else:
                setattr(self, key, value)
    
    @classmethod
    async def _load_state(cls, object_id: str) -> Optional[Dict[str, Any]]:
        """Load state from storage via SDK-Core (fallback)."""
        if _runtime_client:
            return await _runtime_client.load_object_state(cls.__name__, object_id)
        return None
    
    @classmethod
    async def _save_state(cls, object_id: str, state: Dict[str, Any]) -> None:
        """Save state to storage via SDK-Core (fallback)."""
        # This is a fallback - normally save() method calls SDK-Core directly
        pass


class DurableService:
    """Service that registers and manages durable functions and objects."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.functions: Dict[str, DurableFunction] = {}
        self.objects: Dict[str, Type[DurableObject]] = {}
        
        # Register in global registry
        _service_registry[name] = self
    
    def add_function(self, func: DurableFunction) -> None:
        """Add a function to this service."""
        self.functions[func.config.name] = func
    
    def add_object(self, object_class: Type[DurableObject]) -> None:
        """Add an object class to this service."""
        self.objects[object_class.__name__] = object_class
    
    async def handle_invocation(self, request: InvocationRequest) -> InvocationResponse:
        """Handle function invocation from runtime."""
        if request.function_name in self.functions:
            func = self.functions[request.function_name]
            return await func.invoke(request)
        else:
            return InvocationResponse(
                invocation_id=request.invocation_id,
                success=False,
                error=f"Function '{request.function_name}' not found in service '{self.name}'",
            )
    
    def get_service_config(self) -> Dict[str, Any]:
        """Get service configuration for registration with SDK-Core."""
        return {
            "name": self.name,
            "version": self.version,
            "functions": [
                {
                    "name": func.config.name,
                    "version": func.config.version,
                    "deterministic": func.config.deterministic,
                    "idempotent": func.config.idempotent,
                    "max_retries": func.config.max_retries,
                    "timeout": func.config.timeout,
                }
                for func in self.functions.values()
            ],
            "objects": [
                {
                    "name": obj.__name__,
                    "methods": [
                        name for name, _ in inspect.getmembers(obj, predicate=inspect.isfunction)
                        if not name.startswith('_') and name not in ['save', 'get_or_create']
                    ]
                }
                for obj in self.objects.values()
            ]
        }


class DurableNamespace:
    """Namespace for durable primitives."""
    
    def __init__(self):
        self._current_service: Optional[DurableService] = None
    
    def service(self, name: str, version: str = "1.0.0") -> DurableService:
        """Create or get a durable service."""
        if name in _service_registry:
            return _service_registry[name]
        return DurableService(name, version)
    
    @staticmethod
    def function(
        func: Optional[F] = None,
        *,
        name: Optional[str] = None,
        version: str = "1.0.0",
        deterministic: bool = True,
        idempotent: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        service: Optional[str] = None,
    ) -> Union[DurableFunction, Callable[[F], DurableFunction]]:
        """Decorator to create a durable function."""
        def decorator(f: F) -> DurableFunction:
            config = DurableConfig(
                name=name or f.__name__,
                version=version,
                deterministic=deterministic,
                idempotent=idempotent,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=timeout,
            )
            
            durable_func = DurableFunction(f, config)
            
            # Add to service if specified
            if service:
                svc = durable.service(service)
                svc.add_function(durable_func)
            
            return durable_func
        
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    @staticmethod
    def flow(
        func: Optional[F] = None,
        *,
        name: Optional[str] = None,
        version: str = "1.0.0",
        checkpoint_interval: int = 1,
        max_retries: int = 3,
        max_concurrent_steps: int = 10,
        deterministic: bool = True,
        timeout: Optional[float] = None,
        service: Optional[str] = None,
    ) -> Union[DurableFlow, Callable[[F], DurableFlow]]:
        """
        Decorator to create a durable flow.
        
        Args:
            func: The function to wrap as a durable flow
            name: Flow name (defaults to function name)
            version: Flow version
            checkpoint_interval: Steps between checkpoints
            max_retries: Maximum retry attempts per step
            max_concurrent_steps: Maximum parallel steps
            deterministic: Whether execution should be deterministic
            timeout: Timeout per step in seconds
            service: Service to register the flow with
            
        Returns:
            DurableFlow instance or decorator
            
        Example:
            ```python
            @durable.flow(checkpoint_interval=2, max_concurrent_steps=5)
            async def data_pipeline(ctx, input_data):
                # Step 1: Extract data
                extracted = await ctx.call(extract_service, "extract", input_data)
                await ctx.state.set("extracted", extracted)
                
                # Step 2: Transform data (checkpointed here due to interval=2)
                transformed = await ctx.call(transform_service, "transform", extracted)
                await ctx.state.set("transformed", transformed)
                
                # Step 3: Load data
                result = await ctx.call(load_service, "load", transformed)
                return result
            ```
        """
        def decorator(f: F) -> DurableFlow:
            config = DurableConfig(
                name=name or f.__name__,
                version=version,
                checkpoint_interval=checkpoint_interval,
                max_retries=max_retries,
                deterministic=deterministic,
                timeout=timeout,
                max_concurrent_executions=max_concurrent_steps,
            )
            
            durable_flow = DurableFlow(f, config)
            
            # Add to service if specified
            if service:
                svc = durable.service(service)
                svc.add_function(durable_flow._durable_func)
            
            return durable_flow
        
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    @staticmethod
    def object(cls: Optional[Type[T]] = None, *, service: Optional[str] = None) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
        """Decorator to create a durable object class."""
        def decorator(c: Type[T]) -> Type[T]:
            # Ensure class inherits from DurableObject
            if not issubclass(c, DurableObject):
                # Create a new class that inherits from both
                class DurableClass(c, DurableObject):
                    pass
                
                # Copy class attributes
                for attr, value in c.__dict__.items():
                    if not attr.startswith('__'):
                        setattr(DurableClass, attr, value)
                
                # Update class name and module
                DurableClass.__name__ = c.__name__
                DurableClass.__module__ = c.__module__
                
                final_class = DurableClass
            else:
                final_class = c
            
            # Register in global registry
            _object_registry[final_class.__name__] = final_class
            
            # Add to service if specified
            if service:
                svc = durable.service(service)
                svc.add_object(final_class)
            
            return final_class
        
        if cls is None:
            return decorator
        else:
            return decorator(cls)
    
    @staticmethod
    async def sleep(seconds: float) -> None:
        """Durable sleep that survives restarts via SDK-Core."""
        if _runtime_client:
            await _runtime_client.durable_sleep(seconds)
        else:
            logger.info(f"Durable sleep: {seconds} seconds")
            await asyncio.sleep(seconds)
    
    @staticmethod
    def promise(result_type: Type[T]) -> DurablePromise[T]:
        """Create a durable promise."""
        ctx = get_context()
        return DurablePromise(ctx.execution_id, result_type)
    
    def get_all_services(self) -> List[DurableService]:
        """Get all registered services."""
        return list(_service_registry.values())
    
    def get_all_functions(self) -> List[DurableFunction]:
        """Get all registered functions."""
        return list(_function_registry.values())
    
    def get_all_objects(self) -> List[Type[DurableObject]]:
        """Get all registered object classes."""
        return list(_object_registry.values())
    
    def get_all_flows(self) -> List[DurableFlow]:
        """Get all registered flows."""
        return list(_flow_registry.values())
    
    def get_flow(self, name: str) -> Optional[DurableFlow]:
        """Get a specific flow by name."""
        return _flow_registry.get(name)
    
    async def list_active_flows(self) -> List[Dict[str, Any]]:
        """List all currently active flow executions."""
        if _runtime_client:
            return await _runtime_client.list_active_flows()
        else:
            # Fallback for local testing
            return [
                {
                    "flow_name": flow.config.name,
                    "execution_id": "mock_execution",
                    "status": "running",
                    "started_at": datetime.now().isoformat(),
                }
                for flow in _flow_registry.values()
            ]


# Integration functions for SDK-Core
async def handle_invocation_from_runtime(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle function invocation from runtime via SDK-Core."""
    try:
        request = InvocationRequest(
            invocation_id=request_data["invocation_id"],
            function_name=request_data["function_name"],
            args=request_data.get("args", []),
            kwargs=request_data.get("kwargs", {}),
            context=request_data.get("context", {}),
        )
        
        # Find the function or flow
        if request.function_name in _function_registry:
            func = _function_registry[request.function_name]
            response = await func.invoke(request)
        elif request.function_name in _flow_registry:
            flow = _flow_registry[request.function_name]
            response = await flow.invoke(request)
        else:
            response = InvocationResponse(
                invocation_id=request.invocation_id,
                success=False,
                error=f"Function or flow '{request.function_name}' not found",
            )
        
        return asdict(response)
        
    except Exception as e:
        logger.error(f"Error handling invocation: {e}")
        return {
            "invocation_id": request_data.get("invocation_id", "unknown"),
            "success": False,
            "error": str(e),
        }


def get_service_registration_data() -> Dict[str, Any]:
    """Get service registration data for SDK-Core."""
    return {
        "services": [svc.get_service_config() for svc in _service_registry.values()],
        "functions": [
            {
                "name": func.config.name,
                "version": func.config.version,
                "type": "function",
                "deterministic": func.config.deterministic,
                "idempotent": func.config.idempotent,
                "max_retries": func.config.max_retries,
                "timeout": func.config.timeout,
            }
            for func in _function_registry.values()
        ],
        "flows": [
            {
                "name": flow.config.name,
                "version": flow.config.version,
                "type": "flow",
                "deterministic": flow.config.deterministic,
                "checkpoint_interval": flow.config.checkpoint_interval,
                "max_retries": flow.config.max_retries,
                "timeout": flow.config.timeout,
                "max_concurrent_steps": flow.config.max_concurrent_executions,
            }
            for flow in _flow_registry.values()
        ],
        "objects": [
            {
                "name": obj.__name__,
                "type": "object",
                "methods": [
                    name for name, _ in inspect.getmembers(obj, predicate=inspect.isfunction)
                    if not name.startswith('_') and name not in ['save', 'get_or_create']
                ]
            }
            for obj in _object_registry.values()
        ]
    }


def set_runtime_client(client):
    """Set the runtime client for SDK-Core integration."""
    global _runtime_client
    _runtime_client = client


# Create the durable namespace instance
durable = DurableNamespace()