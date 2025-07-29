"""
Agent implementation for the AGNT5 SDK.

Agents are the primary building blocks for conversational AI applications.
They manage conversations, tool usage, and state persistence.
"""

from typing import List, Optional, Union, AsyncIterator, Dict, Any, Callable
import asyncio
from dataclasses import dataclass, field
import json
import logging
import time

from .types import (
    AgentConfig,
    ExecutionContext,
    ExecutionState,
)
from .tool import Tool
from .context import Context, get_context
from .memory import Memory
from .durable import durable
from .tracing import (
    trace_agent_run, span, traced, 
    set_span_attribute, add_span_event, log, TraceLevel,
    trace_tool_call, trace_llm_call, trace_memory_operation
)
from .llm import (
    LanguageModel,
    LanguageModelType,
    LanguageModelResponse,
    Message,
    Role as MessageRole,
    ToolCall,
    ToolResult,
    TokenUsage,
    create_llm,
    LLMError,
)


logger = logging.getLogger(__name__)


class MockLanguageModel(LanguageModel):
    """Mock LLM for testing and fallback."""
    
    def __init__(self, model: str, system_prompt: Optional[str] = None):
        # Create a mock model type
        super().__init__(
            llm_model=LanguageModelType.GPT_4O,  # Default mock model
            system_prompt=system_prompt
        )
        self.mock_model = model
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    @property
    def model_name(self) -> str:
        return self.mock_model
    
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stream: bool = False,
        **kwargs
    ) -> Union[LanguageModelResponse, AsyncIterator[LanguageModelResponse]]:
        """Generate a mock response."""
        if stream:
            return self._mock_stream_response(messages, tools)
        else:
            return self._mock_single_response(messages, tools)
    
    async def _mock_single_response(self, messages: List[Message], tools: Optional[List[Dict[str, Any]]] = None) -> LanguageModelResponse:
        """Generate a single mock response."""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        last_message = messages[-1] if messages else None
        user_content = last_message.content if last_message else "Hello"
        
        # Generate a mock response based on the input
        mock_response = f"This is a mock response to: {user_content[:50]}..." if len(str(user_content)) > 50 else f"This is a mock response to: {user_content}"
        
        # If tools are available, sometimes generate a mock tool call
        tool_calls = None
        if tools and len(tools) > 0 and "search" in str(user_content).lower():
            tool_calls = [ToolCall(
                id="mock_tool_call_123",
                name=tools[0]["name"],
                arguments={"query": str(user_content)[:100]}
            )]
            mock_response = "I'll search for that information."
        
        return LanguageModelResponse(
            message=mock_response,
            usage=TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70),
            tool_calls=tool_calls,
            model=self.mock_model,
            finish_reason="stop"
        )
    
    async def _mock_stream_response(self, messages: List[Message], tools: Optional[List[Dict[str, Any]]] = None) -> AsyncIterator[LanguageModelResponse]:
        """Generate a streaming mock response."""
        response_text = await self._mock_single_response(messages, tools)
        words = response_text.message.split()
        
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield LanguageModelResponse(
                message=word + " " if i < len(words) - 1 else word,
                usage=TokenUsage(),
                model=self.mock_model
            )
    
    def convert_messages_to_provider_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert messages to mock format."""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
    
    def convert_tools_to_provider_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to mock format."""
        return tools


class Agent:
    """
    High-level agent that orchestrates conversations and tool usage.
    
    Example:
        ```python
        from agnt5 import Agent, Tool
        
        # Define a tool
        @tool
        def search_web(query: str) -> str:
            return f"Results for: {query}"
        
        # Create an agent
        agent = Agent(
            name="research-assistant",
            tools=[search_web],
            system_prompt="You are a helpful research assistant."
        )
        
        # Run the agent
        response = await agent.run("Find information about AGNT5")
        ```
    """
    
    def __init__(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Union[Tool, Callable]]] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[Memory] = None,
        config: Optional[AgentConfig] = None,
        llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        **llm_kwargs,
    ):
        """Initialize an Agent."""
        if config:
            self.config = config
        else:
            self.config = AgentConfig(
                name=name,
                description=description,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools or [],
                system_prompt=system_prompt,
            )
        
        self.memory = memory or Memory()
        self._tools: Dict[str, Tool] = {}
        self._conversation: List[Message] = []
        self._execution_context: Optional[ExecutionContext] = None
        
        # Initialize LLM provider
        self._llm = self._initialize_llm(
            model=model,
            provider=llm_provider,
            api_key=api_key,
            system_prompt=system_prompt,
            **llm_kwargs
        )
        
        # Register tools
        for tool in self.config.tools:
            if isinstance(tool, Tool):
                self._tools[tool.name] = tool
            elif callable(tool):
                # Convert function to Tool
                from .tool import tool as tool_decorator
                wrapped_tool = tool_decorator(tool)
                self._tools[wrapped_tool.name] = wrapped_tool
    
    def _initialize_llm(
        self,
        model: str,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LanguageModel:
        """Initialize the LLM provider using provider/model format."""
        try:
            # Parse the model string using LanguageModelType
            model_type = LanguageModelType.from_string(model)
            
            # Use explicit provider if given, otherwise use detected provider
            resolved_provider = provider or model_type.get_provider()
            resolved_model = model_type.value
            
            logger.info(f"Using model '{resolved_model}' with provider '{resolved_provider}'")
            
            # Create LLM instance
            return create_llm(
                provider=resolved_provider,
                model=resolved_model,
                api_key=api_key,
                system_prompt=system_prompt,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM provider {resolved_provider}: {e}")
            logger.info("Falling back to mock LLM for testing")
            return MockLanguageModel(model=model, system_prompt=system_prompt)
    
    @property
    def name(self) -> str:
        return self.config.name
    
    @property
    def tools(self) -> Dict[str, Tool]:
        return self._tools
    
    @property
    def llm(self) -> LanguageModel:
        """Get the LLM instance."""
        return self._llm
    
    def add_tool(self, tool: Union[Tool, Callable]) -> None:
        """Add a tool to the agent."""
        if isinstance(tool, Tool):
            self._tools[tool.name] = tool
        elif callable(tool):
            from .tool import tool as tool_decorator
            wrapped_tool = tool_decorator(tool)
            self._tools[wrapped_tool.name] = wrapped_tool
    
    async def run(
        self,
        message: Union[str, Message],
        *,
        context: Optional[Context] = None,
        stream: bool = False,
    ) -> Union[Message, AsyncIterator[Message]]:
        """
        Run the agent with a message with comprehensive OpenAI-style tracing.
        
        Args:
            message: Input message (string or Message object)
            context: Optional execution context
            stream: Whether to stream responses
            
        Returns:
            Response message or async iterator of messages if streaming
        """
        with trace_agent_run(self.name) as trace_obj:
            # Set trace metadata
            trace_obj.metadata.update({
                "agent.system_prompt": self.config.system_prompt[:100] + "..." if self.config.system_prompt and len(self.config.system_prompt) > 100 else self.config.system_prompt,
                "agent.tools_count": len(self._tools),
                "agent.memory_enabled": self.memory is not None,
                "agent.model": self.config.model,
                "agent.temperature": self.config.temperature,
                "agent.durability_enabled": getattr(self.config, 'enable_durability', False),
            })
            
            with span("agent.run") as agent_span:
                # Set span attributes
                agent_span.set_attribute("agent.name", self.name)
                agent_span.set_attribute("agent.model", self.config.model)
                agent_span.set_attribute("agent.temperature", self.config.temperature)
                agent_span.set_attribute("stream.enabled", stream)
                
                # Convert string to Message if needed
                if isinstance(message, str):
                    message = Message(
                        role=MessageRole.USER,
                        content=message,
                    )
                
                agent_span.set_attribute("input.length", len(message.content))
                agent_span.set_attribute("input.role", message.role.value)
                agent_span.set_attribute("tools.available", list(self._tools.keys()))
                
                # Log start event
                agent_span.add_event("agent.execution.started", {
                    "query_preview": message.content[:50] + "..." if len(message.content) > 50 else message.content,
                    "tools_available": list(self._tools.keys()),
                    "conversation_length": len(self._conversation)
                })
                
                try:
                    # Get or create context
                    ctx = context or get_context()
                    
                    # Add to conversation history
                    self._conversation.append(message)
                    
                    # Store in memory if enabled
                    if self.memory:
                        with trace_memory_operation("add", "conversation"):
                            await self.memory.add(message)
                    
                    # Create durable execution
                    if getattr(self.config, 'enable_durability', False):
                        result = await self._run_durable(message, ctx, stream)
                    else:
                        result = await self._run_direct(message, ctx, stream)
                    
                    # Log success
                    agent_span.set_attribute("execution.status", "success")
                    if isinstance(result, Message):
                        agent_span.set_attribute("response.length", len(result.content))
                        agent_span.add_event("agent.execution.completed", {
                            "response_preview": result.content[:50] + "..." if len(result.content) > 50 else result.content,
                            "response_role": result.role.value
                        })
                    else:
                        agent_span.set_attribute("response.type", "stream")
                        agent_span.add_event("agent.execution.streaming", {
                            "stream_enabled": True
                        })
                    
                    return result
                    
                except Exception as e:
                    # Handle error
                    agent_span.set_error(e)
                    agent_span.add_event("agent.execution.failed", {
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    })
                    log(TraceLevel.ERROR, f"Agent execution failed: {e}", 
                        agent_name=self.name, error_type=type(e).__name__)
                    raise
    
    @durable.function
    async def _run_durable(
        self,
        message: Message,
        context: Context,
        stream: bool,
    ) -> Union[Message, AsyncIterator[Message]]:
        """Run with durability guarantees."""
        # Implementation would integrate with the durable runtime
        # For now, delegate to direct execution
        return await self._run_direct(message, context, stream)
    
    async def _run_direct(
        self,
        message: Message,
        context: Context,
        stream: bool,
    ) -> Union[Message, AsyncIterator[Message]]:
        """Direct execution without durability with detailed tracing."""
        
        with span("agent.execution.direct") as execution_span:
            execution_span.set_attribute("execution.type", "direct")
            execution_span.set_attribute("execution.stream", stream)
            
            # Prepare messages for LLM
            with span("agent.prepare_messages") as prep_span:
                messages = self._prepare_messages()
                prep_span.set_attribute("messages.count", len(messages))
                prep_span.set_attribute("conversation.length", len(self._conversation))
            
            # Call LLM with tracing
            response = await self._call_llm_with_tracing(messages, stream)
            
            if stream:
                execution_span.set_attribute("response.type", "stream")
                return self._stream_response(response)
            else:
                # Process tool calls if any
                if response.tool_calls:
                    execution_span.set_attribute("tools.called", True)
                    execution_span.set_attribute("tools.count", len(response.tool_calls))
                    
                    tool_results = await self._execute_tools_with_tracing(response.tool_calls)
                    
                    # Add tool results to conversation
                    for result in tool_results:
                        tool_message = Message(
                            role=MessageRole.TOOL,
                            content=json.dumps(result.output),
                            tool_call_id=result.tool_call_id,
                        )
                        self._conversation.append(tool_message)
                    
                    # Get final response after tool execution
                    with span("agent.final_llm_call") as final_span:
                        messages = self._prepare_messages()
                        final_span.set_attribute("messages.count", len(messages))
                        final_span.set_attribute("after_tools", True)
                        response = await self._call_llm_with_tracing(messages, False)
                else:
                    execution_span.set_attribute("tools.called", False)
                
                # Add response to conversation
                self._conversation.append(response)
                
                # Store in memory
                if self.memory:
                    with trace_memory_operation("add", "response"):
                        await self.memory.add(response)
                
                execution_span.set_attribute("response.length", len(response.content))
                execution_span.set_attribute("response.role", response.role.value)
                
                return response
    
    def _prepare_messages(self) -> List[Dict[str, Any]]:
        """Prepare messages for LLM API."""
        messages = []
        
        # Add system prompt
        if self.config.system_prompt:
            messages.append({
                "role": "system",
                "content": self.config.system_prompt,
            })
        
        # Add conversation history
        for msg in self._conversation:
            msg_dict = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                msg_dict["name"] = msg.name
            if msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            
            messages.append(msg_dict)
        
        return messages
    
    async def _call_llm_with_tracing(
        self,
        messages: List[Dict[str, Any]],
        stream: bool,
    ) -> Message:
        """Call the LLM API with comprehensive tracing."""
        # Calculate prompt length for tracing
        prompt_length = sum(len(str(msg.get("content", ""))) for msg in messages)
        
        with trace_llm_call(self.config.model, prompt_length) as llm_span:
            llm_span.set_attribute("llm.temperature", self.config.temperature)
            llm_span.set_attribute("llm.max_tokens", self.config.max_tokens or 0)
            llm_span.set_attribute("llm.stream", stream)
            llm_span.set_attribute("llm.messages_count", len(messages))
            llm_span.set_attribute("llm.provider", self._llm.provider_name)
            
            llm_span.add_event("llm.request.started", {
                "model": self.config.model,
                "prompt_length": prompt_length,
                "temperature": self.config.temperature,
                "provider": self._llm.provider_name
            })
            
            start_time = time.time()
            
            try:
                # Convert messages to LLM format
                llm_messages = self._convert_to_llm_messages(messages)
                
                # Prepare tools for LLM
                tools = self._prepare_tools_for_llm() if self._tools else None
                
                # Call the actual LLM
                response = await self._llm.generate(
                    messages=llm_messages,
                    tools=tools,
                    max_tokens=self.config.max_tokens or 1024,
                    temperature=self.config.temperature,
                    stream=stream,
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Convert LLM response back to Message
                message = Message(
                    role=MessageRole.ASSISTANT,
                    content=response.message,
                    tool_calls=response.tool_calls,
                )
                
                llm_span.set_attribute("llm.response.length", len(response.message))
                llm_span.set_attribute("llm.duration_ms", duration_ms)
                llm_span.set_attribute("llm.status", "success")
                llm_span.set_attribute("llm.tokens.prompt", response.usage.prompt_tokens)
                llm_span.set_attribute("llm.tokens.completion", response.usage.completion_tokens)
                llm_span.set_attribute("llm.tokens.total", response.usage.total_tokens)
                
                if response.tool_calls:
                    llm_span.set_attribute("llm.tool_calls.count", len(response.tool_calls))
                
                llm_span.add_event("llm.request.completed", {
                    "response_length": len(response.message),
                    "duration_ms": duration_ms,
                    "tokens_prompt": response.usage.prompt_tokens,
                    "tokens_completion": response.usage.completion_tokens,
                    "tokens_total": response.usage.total_tokens,
                    "tool_calls": len(response.tool_calls) if response.tool_calls else 0,
                })
                
                return message
                
            except LLMError as e:
                duration_ms = (time.time() - start_time) * 1000
                
                llm_span.set_error(e)
                llm_span.set_attribute("llm.duration_ms", duration_ms)
                llm_span.set_attribute("llm.status", "error")
                
                llm_span.add_event("llm.request.failed", {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": duration_ms,
                    "provider": e.provider,
                })
                
                log(TraceLevel.ERROR, f"LLM call failed: {e}", 
                    model=self.config.model, provider=e.provider, error_type=type(e).__name__)
                
                raise
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                llm_span.set_error(e)
                llm_span.set_attribute("llm.duration_ms", duration_ms)
                llm_span.set_attribute("llm.status", "error")
                
                llm_span.add_event("llm.request.failed", {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": duration_ms
                })
                
                log(TraceLevel.ERROR, f"LLM call failed: {e}", 
                    model=self.config.model, error_type=type(e).__name__)
                
                raise
    
    def _convert_to_llm_messages(self, messages: List[Dict[str, Any]]) -> List[Message]:
        """Convert agent messages to LLM Message format."""
        llm_messages = []
        
        for msg in messages:
            role_str = msg.get("role", "user")
            if role_str == "system":
                role = MessageRole.SYSTEM
            elif role_str == "user":
                role = MessageRole.USER
            elif role_str == "assistant":
                role = MessageRole.ASSISTANT
            elif role_str == "tool":
                role = MessageRole.TOOL
            else:
                role = MessageRole.USER  # Default fallback
            
            # Convert tool calls if present
            tool_calls = None
            if msg.get("tool_calls"):
                tool_calls = [
                    ToolCall(
                        id=tc["id"],
                        name=tc["function"]["name"],
                        arguments=json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"]
                    )
                    for tc in msg["tool_calls"]
                ]
            
            message = Message(
                role=role,
                content=msg.get("content", ""),
                name=msg.get("name"),
                tool_calls=tool_calls,
                tool_call_id=msg.get("tool_call_id"),
            )
            
            llm_messages.append(message)
        
        return llm_messages
    
    def _prepare_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Prepare tools in the format expected by LLM providers."""
        tools = []
        
        for tool in self._tools.values():
            # Create tool schema
            tool_schema = {
                "name": tool.name,
                "description": tool.description or f"Tool: {tool.name}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add tool parameters if available
            if hasattr(tool, 'parameters') and tool.parameters:
                tool_schema["parameters"] = tool.parameters
            elif hasattr(tool, 'config') and hasattr(tool.config, 'parameters'):
                tool_schema["parameters"] = tool.config.parameters
            
            tools.append(tool_schema)
        
        return tools
    
    async def _call_llm(
        self,
        messages: List[Dict[str, Any]],
        stream: bool,
    ) -> Message:
        """Call the LLM API (legacy method for backward compatibility)."""
        return await self._call_llm_with_tracing(messages, stream)
    
    async def _stream_response(
        self,
        response: Any,
    ) -> AsyncIterator[Message]:
        """Stream response messages."""
        # Placeholder implementation
        yield Message(
            role=MessageRole.ASSISTANT,
            content="Streaming not yet implemented.",
        )
    
    async def _execute_tools_with_tracing(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute tool calls with comprehensive tracing."""
        results = []
        
        with span("agent.tools.execute") as tools_span:
            tools_span.set_attribute("tools.count", len(tool_calls))
            tools_span.add_event("tools.execution.started", {
                "tool_calls": [call.name for call in tool_calls],
                "total_count": len(tool_calls)
            })
            
            for i, call in enumerate(tool_calls):
                with trace_tool_call(call.name) as tool_span:
                    tool_span.set_attribute("tool.name", call.name)
                    tool_span.set_attribute("tool.index", i)
                    tool_span.set_attribute("tool.call_id", call.id)
                    tool_span.set_attribute("tool.arguments_count", len(call.arguments))
                    
                    tool = self._tools.get(call.name)
                    if not tool:
                        error_msg = f"Tool '{call.name}' not found"
                        tool_span.set_attribute("tool.status", "not_found")
                        tool_span.add_event("tool.execution.failed", {
                            "error_type": "ToolNotFound",
                            "error_message": error_msg,
                            "available_tools": list(self._tools.keys())
                        })
                        
                        results.append(ToolResult(
                            tool_call_id=call.id,
                            output=None,
                            error=error_msg,
                        ))
                        continue
                    
                    tool_span.add_event("tool.execution.started", {
                        "tool_name": call.name,
                        "arguments": str(call.arguments)[:200] + "..." if len(str(call.arguments)) > 200 else str(call.arguments)
                    })
                    
                    start_time = time.time()
                    
                    try:
                        # Execute tool
                        output = await tool.invoke(**call.arguments)
                        duration_ms = (time.time() - start_time) * 1000
                        
                        tool_span.set_attribute("tool.status", "success")
                        tool_span.set_attribute("tool.duration_ms", duration_ms)
                        tool_span.set_attribute("tool.output_length", len(str(output)) if output else 0)
                        
                        tool_span.add_event("tool.execution.completed", {
                            "result_type": type(output).__name__,
                            "result_preview": str(output)[:100] + "..." if len(str(output)) > 100 else str(output),
                            "duration_ms": duration_ms
                        })
                        
                        results.append(ToolResult(
                            tool_call_id=call.id,
                            output=output,
                        ))
                        
                    except Exception as e:
                        duration_ms = (time.time() - start_time) * 1000
                        
                        tool_span.set_error(e)
                        tool_span.set_attribute("tool.status", "error")
                        tool_span.set_attribute("tool.duration_ms", duration_ms)
                        
                        tool_span.add_event("tool.execution.failed", {
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "duration_ms": duration_ms
                        })
                        
                        logger.error(f"Tool execution failed: {e}")
                        log(TraceLevel.ERROR, f"Tool {call.name} failed: {e}", 
                            tool_name=call.name, error_type=type(e).__name__)
                        
                        results.append(ToolResult(
                            tool_call_id=call.id,
                            output=None,
                            error=str(e),
                        ))
            
            # Record overall tool execution results
            successful_tools = sum(1 for result in results if result.error is None)
            failed_tools = len(results) - successful_tools
            
            tools_span.set_attribute("tools.successful", successful_tools)
            tools_span.set_attribute("tools.failed", failed_tools)
            tools_span.add_event("tools.execution.completed", {
                "total_executed": len(results),
                "successful": successful_tools,
                "failed": failed_tools
            })
        
        return results
    
    async def _execute_tools(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute tool calls (legacy method for backward compatibility)."""
        return await self._execute_tools_with_tracing(tool_calls)
    
    @traced("agent.clear_conversation")
    async def clear_conversation(self) -> None:
        """Clear the conversation history and persist state."""
        with span("agent.conversation.clear") as clear_span:
            conversation_length = len(self._conversation)
            clear_span.set_attribute("conversation.length_before", conversation_length)
            
            self._conversation.clear()
            
            clear_span.set_attribute("conversation.length_after", 0)
            clear_span.add_event("conversation.cleared", {
                "messages_removed": conversation_length
            })
            
            # Save state with tracing
            await self._save_with_tracing()
            
            log(TraceLevel.INFO, f"Cleared conversation with {conversation_length} messages", 
                agent_name=self.name, messages_removed=conversation_length)
    
    def get_conversation(self) -> List[Message]:
        """Get the conversation history."""
        return self._conversation.copy()
    
    @traced("agent.save_state")
    async def save_state(self) -> Dict[str, Any]:
        """Save agent state for persistence with tracing."""
        with span("agent.state.save") as save_span:
            save_span.set_attribute("agent.name", self.name)
            save_span.set_attribute("conversation.length", len(self._conversation))
            save_span.set_attribute("memory.enabled", self.memory is not None)
            
            save_span.add_event("state.serialization.started")
            
            # Serialize conversation
            conversation_data = []
            for msg in self._conversation:
                msg_data = {
                    "role": msg.role.value,
                    "content": msg.content,
                    "name": msg.name,
                    "tool_calls": [tc.__dict__ for tc in msg.tool_calls] if msg.tool_calls else None,
                    "tool_call_id": msg.tool_call_id,
                    "metadata": msg.metadata,
                    "timestamp": msg.timestamp.isoformat(),
                }
                conversation_data.append(msg_data)
            
            # Export memory if available
            memory_data = None
            if self.memory:
                with trace_memory_operation("export", "full_state"):
                    memory_data = await self.memory.export()
            
            state = {
                "config": self.config.__dict__,
                "conversation": conversation_data,
                "memory": memory_data,
            }
            
            # Calculate state size for monitoring
            state_size = len(str(state))
            save_span.set_attribute("state.size_bytes", state_size)
            save_span.add_event("state.serialization.completed", {
                "state_size_bytes": state_size,
                "conversation_messages": len(conversation_data),
                "memory_included": memory_data is not None
            })
            
            log(TraceLevel.INFO, f"Saved agent state: {state_size} bytes", 
                agent_name=self.name, state_size=state_size)
            
            return state
    
    @traced("agent.load_state")
    async def load_state(self, state: Dict[str, Any]) -> None:
        """Load agent state from persistence with tracing."""
        with span("agent.state.load") as load_span:
            state_size = len(str(state))
            load_span.set_attribute("agent.name", self.name)
            load_span.set_attribute("state.size_bytes", state_size)
            
            conversation_data = state.get("conversation", [])
            load_span.set_attribute("conversation.messages_to_load", len(conversation_data))
            load_span.set_attribute("memory.data_present", "memory" in state and state["memory"] is not None)
            
            load_span.add_event("state.deserialization.started", {
                "state_size_bytes": state_size,
                "conversation_messages": len(conversation_data)
            })
            
            # Restore conversation
            with span("agent.conversation.restore") as conv_span:
                self._conversation.clear()
                for i, msg_data in enumerate(conversation_data):
                    try:
                        msg = Message(
                            role=MessageRole(msg_data["role"]),
                            content=msg_data["content"],
                            name=msg_data.get("name"),
                            tool_call_id=msg_data.get("tool_call_id"),
                            metadata=msg_data.get("metadata", {}),
                        )
                        if msg_data.get("tool_calls"):
                            msg.tool_calls = [
                                ToolCall(**tc) for tc in msg_data["tool_calls"]
                            ]
                        self._conversation.append(msg)
                    except Exception as e:
                        conv_span.add_event("message.restore.failed", {
                            "message_index": i,
                            "error": str(e)
                        })
                        log(TraceLevel.WARN, f"Failed to restore message {i}: {e}", 
                            agent_name=self.name, message_index=i)
                        
                conv_span.set_attribute("messages.restored", len(self._conversation))
            
            # Restore memory
            if self.memory and state.get("memory"):
                with trace_memory_operation("import", "full_state"):
                    await self.memory.import_data(state["memory"])
            
            load_span.add_event("state.deserialization.completed", {
                "conversation_messages_restored": len(self._conversation),
                "memory_restored": self.memory is not None and state.get("memory") is not None
            })
            
            log(TraceLevel.INFO, f"Loaded agent state: {len(self._conversation)} messages", 
                agent_name=self.name, messages_restored=len(self._conversation))
    
    async def _save_with_tracing(self) -> None:
        """Save agent state with tracing (placeholder for actual persistence)."""
        with span("agent.save") as save_span:
            # This would call actual persistence layer
            save_span.add_event("save.placeholder", {
                "note": "Actual persistence implementation pending"
            })
            # For now, just simulate save operation
            await asyncio.sleep(0.01)
    
    # Reflection capabilities
    async def reflect_on_response(
        self,
        user_query: str,
        agent_response: str,
        level: str = "analytical"
    ) -> Dict[str, Any]:
        """
        Reflect on the quality of a response.
        
        Args:
            user_query: The original user query
            agent_response: The agent's response
            level: Reflection level ('surface', 'analytical', 'metacognitive')
            
        Returns:
            Reflection results with scores and insights
        """
        from .reflection import reflect_on_response
        
        with trace_agent_run(f"{self.name}_reflection") as trace_obj:
            trace_obj.metadata.update({
                "reflection.type": "response_quality",
                "reflection.level": level,
                "agent.name": self.name,
            })
            
            return await reflect_on_response(
                user_query=user_query,
                agent_response=agent_response,
                level=level,
                agent=self
            )
    
    async def reflect_on_conversation(self, level: str = "analytical") -> Dict[str, Any]:
        """
        Reflect on the entire conversation so far.
        
        Args:
            level: Reflection level
            
        Returns:
            Reflection results for the conversation
        """
        if not self._conversation:
            return {
                "insights": ["No conversation to reflect on"],
                "improvements": ["Start a conversation first"],
                "overall_score": 0.0
            }
        
        # Get the last user message and agent response
        user_messages = [msg for msg in self._conversation if msg.role == MessageRole.USER]
        agent_messages = [msg for msg in self._conversation if msg.role == MessageRole.ASSISTANT]
        
        if not user_messages or not agent_messages:
            return {
                "insights": ["Incomplete conversation"],
                "improvements": ["Complete the conversation cycle"],
                "overall_score": 2.0
            }
        
        # Reflect on the last exchange
        last_user_msg = user_messages[-1].content
        last_agent_msg = agent_messages[-1].content
        
        return await self.reflect_on_response(
            user_query=str(last_user_msg),
            agent_response=str(last_agent_msg),
            level=level
        )
    
    async def self_evaluate(self, criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform self-evaluation based on recent performance.
        
        Args:
            criteria: Optional list of criteria to evaluate
            
        Returns:
            Self-evaluation results
        """
        from .reflection import ReflectionEngine, ReflectionType, ReflectionLevel
        
        engine = ReflectionEngine()
        
        # Gather context from recent conversation
        context = {
            "conversation_length": len(self._conversation),
            "tools_available": list(self._tools.keys()),
            "model": self.config.model,
            "recent_messages": [
                {"role": msg.role.value, "content": str(msg.content)[:200]}
                for msg in self._conversation[-5:]  # Last 5 messages
            ]
        }
        
        # Perform performance reflection
        result = await engine.reflect(
            ReflectionType.PERFORMANCE_REVIEW,
            ReflectionLevel.METACOGNITIVE,
            context,
            agent=self
        )
        
        return result.to_dict()
    
    async def improve_response(
        self,
        original_query: str,
        original_response: str,
        feedback: Optional[str] = None
    ) -> str:
        """
        Generate an improved response based on reflection.
        
        Args:
            original_query: The original user query
            original_response: The original response
            feedback: Optional user feedback
            
        Returns:
            Improved response
        """
        # First, reflect on the original response
        reflection = await self.reflect_on_response(
            user_query=original_query,
            agent_response=original_response,
            level="analytical"
        )
        
        # Build improvement prompt
        improvements = reflection.get("improvements", [])
        insights = reflection.get("insights", [])
        
        improvement_prompt = f"""Based on reflection, please provide an improved response to the original query.

Original Query: {original_query}
Original Response: {original_response}

Reflection Insights:
{chr(10).join(f"- {insight}" for insight in insights)}

Suggested Improvements:
{chr(10).join(f"- {improvement}" for improvement in improvements)}

{f"User Feedback: {feedback}" if feedback else ""}

Please provide an improved response that addresses the identified issues:"""
        
        # Generate improved response
        response = await self.run(improvement_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def learn_from_error(self, error_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Learn from an error by analyzing what went wrong.
        
        Args:
            error_description: Description of the error
            context: Optional context where the error occurred
            
        Returns:
            Learning insights and prevention strategies
        """
        from .reflection import analyze_errors
        
        return await analyze_errors(
            errors=[error_description],
            attempted_solutions=[context] if context else [],
            level="metacognitive",
            agent=self
        )