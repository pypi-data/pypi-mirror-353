"""
Anthropic Claude integration for AGNT5 SDK.

Provides integration with Anthropic's Claude models including proper message conversion,
tool calling, and streaming support.
"""

import json
import os
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .base import (
    LanguageModel,
    LanguageModelResponse,
    LanguageModelType,
    LLMError,
    Message,
    Role,
    TokenUsage,
    ToolCall,
)

try:
    import anthropic
    from anthropic.types import (
        ContentBlock,
        MessageParam,
        TextBlock,
        ToolUseBlock,
    )
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicError(LLMError):
    """Anthropic-specific errors."""
    pass


class AnthropicLanguageModel(LanguageModel):
    """
    Anthropic Claude language model implementation.
    
    Supports all Claude models with proper message conversion, tool calling,
    and streaming capabilities.
    """
    
    def __init__(
        self,
        llm_model: LanguageModelType,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        if not ANTHROPIC_AVAILABLE:
            raise AnthropicError("Anthropic library not installed. Install with: pip install anthropic")
        
        super().__init__(llm_model, system_prompt, **kwargs)
        
        # Get API key
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise AnthropicError("Anthropic API key required. Set ANTHROPIC_API_KEY or pass api_key parameter")
        
        # Initialize client
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        
        # Validate model is supported by Anthropic
        if not self.model_name.startswith("claude"):
            raise AnthropicError(f"Model {self.model_name} is not an Anthropic model")
    
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
        """Generate response using Anthropic Claude."""
        try:
            # Validate and prepare messages
            self.validate_messages(messages)
            prepared_messages = self.prepare_system_message(messages)
            
            # Convert to Anthropic format
            anthropic_messages = self.convert_messages_to_provider_format(prepared_messages)
            
            # Extract system message if present
            system_message = None
            if anthropic_messages and anthropic_messages[0].get("role") == "system":
                system_message = anthropic_messages[0]["content"]
                anthropic_messages = anthropic_messages[1:]
            
            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
            
            if system_message:
                request_params["system"] = system_message
            
            if tools:
                request_params["tools"] = self.convert_tools_to_provider_format(tools)
            
            # Add any additional parameters
            request_params.update(kwargs)
            
            if stream:
                return self._generate_stream(**request_params)
            else:
                return await self._generate_single(**request_params)
                
        except anthropic.APIError as e:
            raise AnthropicError(f"Anthropic API error: {e}", provider="anthropic", model=self.model_name) from e
        except Exception as e:
            raise AnthropicError(f"Unexpected error: {e}", provider="anthropic", model=self.model_name) from e
    
    async def _generate_single(self, **request_params) -> LanguageModelResponse:
        """Generate a single response."""
        response = await self.client.messages.create(**request_params)
        
        # Extract text content and tool calls
        response_text = ""
        tool_calls = []
        
        for content_block in response.content:
            if isinstance(content_block, TextBlock):
                response_text += content_block.text
            elif isinstance(content_block, ToolUseBlock):
                tool_calls.append(ToolCall(
                    id=content_block.id,
                    name=content_block.name,
                    arguments=content_block.input
                ))
        
        # Calculate token usage
        usage = TokenUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens
        )
        
        return LanguageModelResponse(
            message=response_text,
            usage=usage,
            tool_calls=tool_calls if tool_calls else None,
            model=response.model,
            finish_reason=response.stop_reason,
            metadata={"response_id": response.id}
        )
    
    async def _generate_stream(self, **request_params) -> AsyncIterator[LanguageModelResponse]:
        """Generate streaming response."""
        request_params["stream"] = True
        
        async with self.client.messages.stream(**request_params) as stream:
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    if hasattr(chunk.delta, "text"):
                        yield LanguageModelResponse(
                            message=chunk.delta.text,
                            usage=TokenUsage(),
                            model=self.model_name
                        )
                elif chunk.type == "message_start":
                    # Initial message metadata
                    yield LanguageModelResponse(
                        message="",
                        usage=TokenUsage(),
                        model=chunk.message.model,
                        metadata={"message_id": chunk.message.id}
                    )
    
    def convert_messages_to_provider_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal messages to Anthropic format."""
        anthropic_messages = []
        
        for message in messages:
            # Handle system messages
            if message.role == Role.SYSTEM:
                anthropic_messages.append({
                    "role": "system",
                    "content": message.content if isinstance(message.content, str) else str(message.content)
                })
                continue
            
            # Convert role
            if message.role == Role.USER:
                role = "user"
            elif message.role == Role.ASSISTANT:
                role = "assistant"
            elif message.role == Role.TOOL:
                # Tool results are handled as user messages with tool_result content
                role = "user"
            else:
                continue  # Skip unsupported roles
            
            # Prepare content
            if isinstance(message.content, str):
                content = message.content
            elif isinstance(message.content, list):
                content = self._convert_content_blocks(message.content)
            else:
                content = str(message.content)
            
            anthropic_message = {
                "role": role,
                "content": content
            }
            
            # Handle tool calls for assistant messages
            if message.tool_calls and message.role == Role.ASSISTANT:
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                elif not isinstance(content, list):
                    content = [{"type": "text", "text": str(content)}]
                
                # Add tool use blocks
                for tool_call in message.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tool_call.id,
                        "name": tool_call.name,
                        "input": tool_call.arguments
                    })
                
                anthropic_message["content"] = content
            
            # Handle tool results
            if message.tool_call_id:
                anthropic_message["content"] = [{
                    "type": "tool_result",
                    "tool_use_id": message.tool_call_id,
                    "content": content if isinstance(content, str) else str(content)
                }]
            
            anthropic_messages.append(anthropic_message)
        
        return anthropic_messages
    
    def _convert_content_blocks(self, content_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert content blocks to Anthropic format."""
        converted_blocks = []
        
        for block in content_blocks:
            if isinstance(block, str):
                converted_blocks.append({"type": "text", "text": block})
            elif isinstance(block, dict):
                block_type = block.get("type", "text")
                
                if block_type == "text":
                    converted_blocks.append({
                        "type": "text",
                        "text": block.get("text", str(block))
                    })
                elif block_type == "image":
                    # Handle image blocks
                    converted_blocks.append({
                        "type": "image",
                        "source": block.get("source", {})
                    })
                else:
                    # Convert unknown blocks to text
                    converted_blocks.append({
                        "type": "text", 
                        "text": str(block)
                    })
            else:
                converted_blocks.append({"type": "text", "text": str(block)})
        
        return converted_blocks
    
    def convert_tools_to_provider_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Anthropic format."""
        anthropic_tools = []
        
        for tool in tools:
            if "function" in tool:
                # OpenAI-style tool format
                func = tool["function"]
                anthropic_tool = {
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {})
                }
            else:
                # Direct Anthropic format or simple format
                anthropic_tool = {
                    "name": tool.get("name", "unknown"),
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("input_schema", tool.get("parameters", {}))
                }
            
            anthropic_tools.append(anthropic_tool)
        
        return anthropic_tools
    
    def extract_tool_calls_from_response(self, response: Any) -> List[ToolCall]:
        """Extract tool calls from Anthropic response."""
        tool_calls = []
        
        if hasattr(response, "content"):
            for content_block in response.content:
                if isinstance(content_block, ToolUseBlock):
                    tool_calls.append(ToolCall(
                        id=content_block.id,
                        name=content_block.name,
                        arguments=content_block.input
                    ))
        
        return tool_calls