"""
Together AI integration for AGNT5 SDK.

Provides integration with Together AI's models using OpenAI-compatible API
for various open-source models including Llama, Mixtral, Qwen, and more.
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


class TogetherAIError(LLMError):
    """Together AI-specific errors."""
    pass


class TogetherAILanguageModel(LanguageModel):
    """
    Together AI language model implementation using OpenAI-compatible API.
    
    Supports various open-source models hosted on Together AI including
    Llama, Mixtral, Qwen, and other popular models.
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
            raise TogetherAIError("OpenAI library not installed. Install with: pip install openai")
        
        super().__init__(llm_model, system_prompt, **kwargs)
        
        # Get API key
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise TogetherAIError("Together AI API key required. Set TOGETHER_API_KEY or pass api_key parameter")
        
        # Set base URL for Together AI API
        self.base_url = base_url or "https://api.together.xyz/v1"
        
        # Initialize client with Together AI endpoint
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Validate model is supported by Together AI
        if not (self.model_name.startswith("meta-llama") or 
                self.model_name.startswith("mistralai") or 
                self.model_name.startswith("Qwen") or
                "/" in self.model_name):  # Together uses namespace/model format
            raise TogetherAIError(f"Model {self.model_name} is not a recognized Together AI model")
    
    @property
    def provider_name(self) -> str:
        return "together"
    
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
        """Generate response using Together AI."""
        try:
            # Validate and prepare messages
            self.validate_messages(messages)
            prepared_messages = self.prepare_system_message(messages)
            
            # Convert to OpenAI format (Together AI API is compatible)
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
            
            # Together AI supports tools for some models
            if tools and self._supports_tools():
                request_params["tools"] = self.convert_tools_to_provider_format(tools)
                request_params["tool_choice"] = "auto"
            
            # Add any additional parameters
            request_params.update(kwargs)
            
            if stream:
                return self._generate_stream(**request_params)
            else:
                return await self._generate_single(**request_params)
                
        except openai.APIError as e:
            # Handle Together AI-specific API errors
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                raise TogetherAIError(f"Together AI authentication error: {e}", provider="together", model=self.model_name) from e
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise TogetherAIError(f"Together AI rate limit error: {e}", provider="together", model=self.model_name) from e
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                raise TogetherAIError(f"Together AI model not found: {e}. Available models: https://docs.together.ai/docs/inference-models", provider="together", model=self.model_name) from e
            else:
                raise TogetherAIError(f"Together AI API error: {e}", provider="together", model=self.model_name) from e
        except Exception as e:
            raise TogetherAIError(f"Unexpected error: {e}", provider="together", model=self.model_name) from e
    
    def _supports_tools(self) -> bool:
        """Check if the current model supports tool calling."""
        # Tool support varies by model on Together AI
        # Generally, newer instruct models support tools
        tool_supported_models = [
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", 
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "mistralai/Mixtral-8x22B-Instruct-v0.1",
        ]
        
        return (self.model_name in tool_supported_models or 
                "instruct" in self.model_name.lower())
    
    async def _generate_single(self, **request_params) -> LanguageModelResponse:
        """Generate a single response."""
        response = await self.client.chat.completions.create(**request_params)
        
        message = response.choices[0].message
        
        # Extract text content
        response_text = message.content or ""
        
        # Extract tool calls (if supported)
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
            metadata={
                "response_id": response.id,
                "provider": "together",
                "supports_tools": self._supports_tools()
            }
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
                
                # Handle tool calls (if supported)
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
        """Convert internal messages to OpenAI/Together AI format."""
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
            
            # Handle tool calls for assistant messages (if supported)
            if message.tool_calls and message.role == Role.ASSISTANT and self._supports_tools():
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
        """Convert content blocks to OpenAI/Together AI format."""
        # For simple text-only blocks, return as string
        if len(content_blocks) == 1 and content_blocks[0].get("type") == "text":
            return content_blocks[0].get("text", str(content_blocks[0]))
        
        # For complex content, return as structured blocks
        # Note: Together AI primarily supports text, limited multimodal support
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
                elif block_type == "image_url" and self._supports_vision():
                    # Some Together AI models support vision
                    converted_blocks.append({
                        "type": "image_url",
                        "image_url": block.get("image_url", {})
                    })
                else:
                    # Convert unknown/unsupported blocks to text
                    converted_blocks.append({
                        "type": "text", 
                        "text": f"[{block_type.upper()}]: {str(block)}"
                    })
            else:
                converted_blocks.append({"type": "text", "text": str(block)})
        
        return converted_blocks
    
    def _supports_vision(self) -> bool:
        """Check if the current model supports vision/image input."""
        vision_models = [
            "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        ]
        return self.model_name in vision_models
    
    def convert_tools_to_provider_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI/Together AI format."""
        if not self._supports_tools():
            return []
        
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
        """Extract tool calls from Together AI response."""
        if not self._supports_tools():
            return []
        
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