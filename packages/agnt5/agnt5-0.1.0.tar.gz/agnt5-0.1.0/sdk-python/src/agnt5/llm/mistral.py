"""
Mistral AI integration for AGNT5 SDK.

Provides integration with Mistral's models using OpenAI-compatible API
including proper message conversion, tool calling, and streaming support.
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
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class MistralError(LLMError):
    """Mistral-specific errors."""
    pass


class MistralLanguageModel(LanguageModel):
    """
    Mistral AI language model implementation using OpenAI-compatible API.
    
    Supports all Mistral models with proper message conversion, tool calling,
    and streaming capabilities.
    """
    
    def __init__(
        self,
        llm_model: LanguageModelType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        if not OPENAI_AVAILABLE:
            raise MistralError("OpenAI library not installed. Install with: pip install openai")
        
        super().__init__(llm_model, system_prompt, **kwargs)
        
        # Get API key
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise MistralError("Mistral API key required. Set MISTRAL_API_KEY or pass api_key parameter")
        
        # Set base URL for Mistral API
        self.base_url = base_url or "https://api.mistral.ai/v1"
        
        # Initialize client with Mistral endpoint
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Validate model is supported by Mistral
        if not any(self.model_name.startswith(prefix) for prefix in 
                  ["mistral", "open-mistral", "open-mixtral", "codestral"]):
            raise MistralError(f"Model {self.model_name} is not a Mistral model")
    
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
        """Generate response using Mistral AI."""
        try:
            # Validate and prepare messages
            self.validate_messages(messages)
            prepared_messages = self.prepare_system_message(messages)
            
            # Convert to OpenAI format (Mistral API is compatible)
            openai_messages = self.convert_messages_to_provider_format(prepared_messages)
            
            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": openai_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": stream,
            }
            
            if tools:
                request_params["tools"] = self.convert_tools_to_provider_format(tools)
                request_params["tool_choice"] = "auto"
            
            # Add any additional parameters
            request_params.update(kwargs)
            
            if stream:
                return self._generate_stream(**request_params)
            else:
                return await self._generate_single(**request_params)
                
        except openai.APIError as e:
            # Handle Mistral-specific API errors
            error_msg = str(e)
            if "authentication" in error_msg.lower():
                raise MistralError(f"Mistral API authentication error: {e}", provider="mistral", model=self.model_name) from e
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise MistralError(f"Mistral API rate limit error: {e}", provider="mistral", model=self.model_name) from e
            else:
                raise MistralError(f"Mistral API error: {e}", provider="mistral", model=self.model_name) from e
        except Exception as e:
            raise MistralError(f"Unexpected error: {e}", provider="mistral", model=self.model_name) from e
    
    async def _generate_single(self, **request_params) -> LanguageModelResponse:
        """Generate a single response."""
        response = await self.client.chat.completions.create(**request_params)
        
        message = response.choices[0].message
        
        # Extract text content
        response_text = message.content or ""
        
        # Extract tool calls
        tool_calls = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.type == "function":
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {"raw_arguments": tool_call.function.arguments}
                    
                    tool_calls.append(ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=arguments
                    ))
        
        # Calculate token usage
        usage = TokenUsage()
        if response.usage:
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
        
        return LanguageModelResponse(
            message=response_text,
            usage=usage,
            tool_calls=tool_calls if tool_calls else None,
            model=response.model,
            finish_reason=response.choices[0].finish_reason,
            metadata={"response_id": response.id}
        )
    
    async def _generate_stream(self, **request_params) -> AsyncIterator[LanguageModelResponse]:
        """Generate streaming response."""
        stream = await self.client.chat.completions.create(**request_params)
        
        async for chunk in stream:
            if chunk.choices:
                choice = chunk.choices[0]
                
                # Handle content delta
                if choice.delta.content:
                    yield LanguageModelResponse(
                        message=choice.delta.content,
                        usage=TokenUsage(),
                        model=chunk.model
                    )
                
                # Handle tool calls
                if choice.delta.tool_calls:
                    for tool_call_delta in choice.delta.tool_calls:
                        if tool_call_delta.function:
                            # Note: In streaming, tool calls come in pieces
                            # This is a simplified version - full implementation would
                            # need to accumulate the complete tool call
                            yield LanguageModelResponse(
                                message="",
                                usage=TokenUsage(),
                                model=chunk.model,
                                metadata={"tool_call_delta": tool_call_delta}
                            )
    
    def convert_messages_to_provider_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal messages to OpenAI/Mistral format."""
        openai_messages = []
        
        for message in messages:
            # Convert role
            if message.role == Role.SYSTEM:
                role = "system"
            elif message.role == Role.USER:
                role = "user"
            elif message.role == Role.ASSISTANT:
                role = "assistant"
            elif message.role == Role.TOOL:
                role = "tool"
            else:
                continue  # Skip unsupported roles
            
            # Prepare content
            if isinstance(message.content, str):
                content = message.content
            elif isinstance(message.content, list):
                content = self._convert_content_blocks(message.content)
            else:
                content = str(message.content)
            
            openai_message = {
                "role": role,
                "content": content
            }
            
            # Add name if present
            if message.name:
                openai_message["name"] = message.name
            
            # Handle tool calls for assistant messages
            if message.tool_calls and message.role == Role.ASSISTANT:
                openai_message["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.arguments)
                        }
                    }
                    for tool_call in message.tool_calls
                ]
            
            # Handle tool call ID for tool messages
            if message.tool_call_id:
                openai_message["tool_call_id"] = message.tool_call_id
            
            openai_messages.append(openai_message)
        
        return openai_messages
    
    def _convert_content_blocks(self, content_blocks: List[Dict[str, Any]]) -> Union[str, List[Dict[str, Any]]]:
        """Convert content blocks to OpenAI/Mistral format."""
        # For simple text-only blocks, return as string
        if len(content_blocks) == 1 and content_blocks[0].get("type") == "text":
            return content_blocks[0].get("text", str(content_blocks[0]))
        
        # For complex content, return as structured blocks
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
                else:
                    # Convert unknown blocks to text (Mistral doesn't support images yet)
                    converted_blocks.append({
                        "type": "text", 
                        "text": str(block)
                    })
            else:
                converted_blocks.append({"type": "text", "text": str(block)})
        
        return converted_blocks
    
    def convert_tools_to_provider_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI/Mistral format."""
        openai_tools = []
        
        for tool in tools:
            if "function" in tool:
                # Already in OpenAI format
                openai_tools.append(tool)
            else:
                # Convert from simple format
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.get("name", "unknown"),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", tool.get("input_schema", {}))
                    }
                }
                openai_tools.append(openai_tool)
        
        return openai_tools
    
    def extract_tool_calls_from_response(self, response: Any) -> List[ToolCall]:
        """Extract tool calls from Mistral response."""
        tool_calls = []
        
        if hasattr(response, "choices") and response.choices:
            message = response.choices[0].message
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.type == "function":
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {"raw_arguments": tool_call.function.arguments}
                        
                        tool_calls.append(ToolCall(
                            id=tool_call.id,
                            name=tool_call.function.name,
                            arguments=arguments
                        ))
        
        return tool_calls