"""
Tool implementation for the AGNT5 SDK.

Tools are functions that agents can call to perform specific tasks.
They support automatic schema generation, validation, and error handling.
"""

from typing import Callable, Any, Dict, Optional, List, Union, get_type_hints
import inspect
import asyncio
import functools
import json
from dataclasses import dataclass
import logging
from datetime import datetime

from .types import ToolConfig
from .context import get_context
from .durable import durable, DurableContext


logger = logging.getLogger(__name__)


class Tool:
    """
    A tool that can be called by agents.
    
    Example:
        ```python
        from agnt5 import Tool
        
        # Create a tool from a function
        def calculate_sum(a: int, b: int) -> int:
            '''Calculate the sum of two numbers.'''
            return a + b
        
        tool = Tool(calculate_sum)
        
        # Or use the decorator
        @tool
        def search_web(query: str) -> str:
            '''Search the web for information.'''
            return f"Results for: {query}"
        ```
    """
    
    def __init__(
        self,
        func: Callable,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[ToolConfig] = None,
    ):
        """Initialize a Tool."""
        self.func = func
        self.is_async = inspect.iscoroutinefunction(func)
        
        # Extract metadata from function
        self.name = name or func.__name__
        self.description = description or inspect.getdoc(func) or f"Tool: {self.name}"
        
        # Extract parameters schema
        self.parameters = self._extract_parameters()
        self.returns = self._extract_returns()
        
        # Configuration
        if config:
            self.config = config
        else:
            self.config = ToolConfig(
                name=self.name,
                description=self.description,
                parameters=self.parameters,
                returns=self.returns,
            )
    
    def _extract_parameters(self) -> Dict[str, Any]:
        """Extract parameter schema from function signature."""
        sig = inspect.signature(self.func)
        hints = get_type_hints(self.func)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            # Get type hint
            param_type = hints.get(param_name, Any)
            
            # Convert to JSON schema type
            schema_type = self._python_type_to_json_schema(param_type)
            properties[param_name] = schema_type
            
            # Check if required
            if param.default == param.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    
    def _extract_returns(self) -> Optional[Dict[str, Any]]:
        """Extract return type schema."""
        hints = get_type_hints(self.func)
        return_type = hints.get("return", Any)
        
        if return_type is None or return_type is type(None):
            return None
        
        return self._python_type_to_json_schema(return_type)
    
    def _python_type_to_json_schema(self, python_type: type) -> Dict[str, Any]:
        """Convert Python type to JSON schema."""
        # Handle basic types
        type_mapping = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
            Any: {"type": "any"},
        }
        
        # Handle Optional types
        origin = getattr(python_type, "__origin__", None)
        if origin is Union:
            args = python_type.__args__
            # Check if it's Optional (Union with None)
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                schema = self._python_type_to_json_schema(non_none_type)
                schema["nullable"] = True
                return schema
        
        # Handle List types
        if origin is list:
            args = getattr(python_type, "__args__", ())
            if args:
                item_type = args[0]
                return {
                    "type": "array",
                    "items": self._python_type_to_json_schema(item_type),
                }
        
        # Handle Dict types
        if origin is dict:
            return {"type": "object"}
        
        # Default mapping
        return type_mapping.get(python_type, {"type": "any"})
    
    async def invoke(self, **kwargs) -> Any:
        """
        Invoke the tool with the given arguments.
        
        This method provides automatic durability, retries, and state management.
        
        Args:
            **kwargs: Tool arguments
            
        Returns:
            Tool output
        """
        # Check if this is a durable tool (has durability enabled)
        if getattr(self.config, 'enable_durability', True):
            return await self._invoke_durable(kwargs)
        else:
            return await self._invoke_legacy(kwargs)
    
    async def invoke_durable(self, ctx: DurableContext, **kwargs) -> Any:
        """
        Invoke the tool with a durable context for enhanced state management.
        
        Args:
            ctx: Durable execution context
            **kwargs: Tool arguments
            
        Returns:
            Tool output
        """
        # Store tool invocation in durable state
        await ctx.state.set(f"tool_{self.name}_input", kwargs)
        await ctx.state.set(f"tool_{self.name}_started_at", datetime.now().isoformat())
        
        try:
            result = await self._invoke_durable(kwargs, ctx)
            await ctx.state.set(f"tool_{self.name}_result", result)
            await ctx.state.set(f"tool_{self.name}_completed_at", datetime.now().isoformat())
            return result
        except Exception as e:
            await ctx.state.set(f"tool_{self.name}_error", str(e))
            await ctx.state.set(f"tool_{self.name}_failed_at", datetime.now().isoformat())
            raise
    
    async def _invoke_durable(self, kwargs: Dict[str, Any], ctx: Optional[DurableContext] = None) -> Any:
        """
        Execute tool with full durability using durable function.
        """
        @durable.function(
            name=f"tool_{self.name}",
            max_retries=self.config.max_retries,
            timeout=self.config.timeout,
            deterministic=True,
        )
        async def durable_tool_execution(durable_ctx: DurableContext, tool_kwargs: Dict[str, Any]) -> Any:
            # Store execution metadata
            await durable_ctx.state.set("tool_name", self.name)
            await durable_ctx.state.set("tool_description", self.description)
            await durable_ctx.state.set("tool_input", tool_kwargs)
            await durable_ctx.state.set("execution_started", datetime.now().isoformat())
            
            # Validate arguments within durable context
            self._validate_arguments(tool_kwargs)
            
            # Execute the tool function
            try:
                if self.is_async:
                    result = await self.func(**tool_kwargs)
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: self.func(**tool_kwargs))
                
                # Store successful result
                await durable_ctx.state.set("tool_result", result)
                await durable_ctx.state.set("execution_completed", datetime.now().isoformat())
                await durable_ctx.state.set("execution_status", "success")
                
                logger.debug(f"Tool '{self.name}' completed successfully")
                return result
                
            except Exception as e:
                # Store error information
                await durable_ctx.state.set("tool_error", str(e))
                await durable_ctx.state.set("execution_failed", datetime.now().isoformat())
                await durable_ctx.state.set("execution_status", "failed")
                
                logger.error(f"Tool '{self.name}' failed: {e}")
                raise
        
        # Execute the durable function
        return await durable_tool_execution(kwargs)
    
    async def _invoke_legacy(self, kwargs: Dict[str, Any]) -> Any:
        """
        Legacy invocation method for backward compatibility.
        """
        ctx = get_context()
        
        # Validate arguments
        self._validate_arguments(kwargs)
        
        # Log invocation
        logger.debug(f"Invoking tool '{self.name}' with args: {kwargs}")
        
        try:
            # Execute with timeout if configured
            if self.config.timeout:
                return await self._invoke_with_timeout(kwargs)
            else:
                return await self._invoke_direct(kwargs)
        except Exception as e:
            logger.error(f"Tool '{self.name}' failed: {e}")
            
            # Retry if configured
            if self.config.max_retries > 1:
                return await self._invoke_with_retry(kwargs)
            else:
                raise
    
    async def _invoke_direct(self, kwargs: Dict[str, Any]) -> Any:
        """Direct invocation of the tool."""
        if self.is_async:
            return await self.func(**kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.func, **kwargs)
    
    async def _invoke_with_timeout(self, kwargs: Dict[str, Any]) -> Any:
        """Invoke with timeout."""
        try:
            return await asyncio.wait_for(
                self._invoke_direct(kwargs),
                timeout=self.config.timeout,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Tool '{self.name}' timed out after {self.config.timeout}s")
    
    async def _invoke_with_retry(self, kwargs: Dict[str, Any]) -> Any:
        """Invoke with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await self._invoke_with_timeout(kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    logger.warning(f"Tool '{self.name}' attempt {attempt + 1} failed, retrying...")
        
        raise last_error
    
    def _validate_arguments(self, kwargs: Dict[str, Any]) -> None:
        """Validate tool arguments against schema."""
        properties = self.parameters.get("properties", {})
        required = self.parameters.get("required", [])
        
        # Check required parameters
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Check for unknown parameters
        for key in kwargs:
            if key not in properties:
                raise ValueError(f"Unknown parameter: {key}")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get OpenAI function schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
    
    def __call__(self, **kwargs) -> Any:
        """Allow synchronous calling of the tool."""
        return asyncio.run(self.invoke(**kwargs))
    
    def __repr__(self) -> str:
        durability_status = "durable" if getattr(self.config, 'enable_durability', True) else "non-durable"
        return f"Tool(name='{self.name}', {durability_status}, retries={self.config.max_retries})"


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    timeout: Optional[float] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    enable_durability: bool = True,
) -> Union[Tool, Callable[[Callable], Tool]]:
    """
    Decorator to create a durable tool from a function.
    
    Tools created with this decorator automatically get:
    - Durability and state persistence
    - Automatic retries with exponential backoff
    - Timeout handling
    - Comprehensive logging and monitoring
    - Integration with durable flows and contexts
    
    Example:
        ```python
        @tool
        def calculate_sum(a: int, b: int) -> int:
            '''Calculate the sum of two numbers.'''
            return a + b
        
        @tool(name="web_search", timeout=30.0, max_retries=5)
        async def search(query: str) -> str:
            '''Search the web for information.'''
            # This tool will automatically retry on failures
            # and persist its state across interruptions
            return f"Results for: {query}"
        
        @tool(enable_durability=False)
        def simple_tool(value: str) -> str:
            '''A simple tool without durability (for backwards compatibility).'''
            return f"Processed: {value}"
        ```
    """
    def decorator(f: Callable) -> Tool:
        config = ToolConfig(
            name=name or f.__name__,
            description=description or inspect.getdoc(f) or f"Tool: {f.__name__}",
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            enable_durability=enable_durability,
        )
        
        tool_instance = Tool(f, config=config)
        
        # If durability is enabled, register as a durable function
        if enable_durability:
            # Create a durable function wrapper for the tool
            durable_func = durable.function(
                name=f"tool_{config.name}",
                max_retries=max_retries,
                timeout=timeout,
                deterministic=True,
            )(f)
            
            # Store reference to durable function in tool
            tool_instance._durable_func = durable_func
        
        return tool_instance
    
    if func is None:
        # Called with arguments: @tool(name="...", ...)
        return decorator
    else:
        # Called without arguments: @tool
        return decorator(func)


def durable_tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    timeout: Optional[float] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Union[Tool, Callable[[Callable], Tool]]:
    """
    Explicit decorator for creating durable tools.
    
    This is an alias for @tool with enable_durability=True (the default).
    Use this when you want to be explicit about durability.
    """
    return tool(
        func,
        name=name,
        description=description,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        enable_durability=True,
    )


class ToolKit:
    """
    A collection of related tools.
    
    Example:
        ```python
        from agnt5 import ToolKit
        
        class FileTools(ToolKit):
            '''Tools for file operations.'''
            
            @tool
            def read_file(self, path: str) -> str:
                '''Read contents of a file.'''
                with open(path, 'r') as f:
                    return f.read()
            
            @tool
            def write_file(self, path: str, content: str) -> None:
                '''Write content to a file.'''
                with open(path, 'w') as f:
                    f.write(content)
        
        # Use the toolkit
        file_tools = FileTools()
        tools = file_tools.get_tools()
        ```
    """
    
    def __init__(self):
        """Initialize the toolkit."""
        self._tools: Dict[str, Tool] = {}
        self._discover_tools()
    
    def _discover_tools(self) -> None:
        """Discover tools defined as methods."""
        for name in dir(self):
            if name.startswith("_"):
                continue
            
            attr = getattr(self, name)
            if isinstance(attr, Tool):
                self._tools[attr.name] = attr
            elif hasattr(attr, "__tool__"):
                # Method decorated with @tool
                tool_instance = attr.__tool__
                # Bind method to self
                bound_func = functools.partial(tool_instance.func, self)
                tool_instance.func = bound_func
                self._tools[tool_instance.name] = tool_instance
    
    def get_tools(self) -> List[Tool]:
        """Get all tools in this toolkit."""
        return list(self._tools.values())
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        return self._tools.get(name)
    
    def get_durable_tools(self) -> List[Tool]:
        """Get all durable tools in this toolkit."""
        return [
            tool for tool in self._tools.values() 
            if getattr(tool.config, 'enable_durability', True)
        ]
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI function schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]