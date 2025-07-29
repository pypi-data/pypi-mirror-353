"""
Google Gemini integration for AGNT5 SDK.

Provides integration with Google's Gemini models including proper message conversion,
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
    import google.generativeai as genai
    from google.generativeai.types import (
        GenerateContentResponse,
        Content,
        Part,
        FunctionCall,
        FunctionResponse,
    )
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    # Define placeholder types for type hints when Google SDK is not available
    Content = Any
    Part = Any
    FunctionCall = Any
    FunctionResponse = Any
    GenerateContentResponse = Any


class GoogleError(LLMError):
    """Google Gemini-specific errors."""
    pass


class GoogleLanguageModel(LanguageModel):
    """
    Google Gemini language model implementation.
    
    Supports all Gemini models with proper message conversion, tool calling,
    and streaming capabilities.
    """
    
    def __init__(
        self,
        llm_model: LanguageModelType,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        if not GOOGLE_AVAILABLE:
            raise GoogleError("Google AI library not installed. Install with: pip install google-generativeai")
        
        super().__init__(llm_model, system_prompt, **kwargs)
        
        # Get API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise GoogleError("Google API key required. Set GOOGLE_API_KEY or pass api_key parameter")
        
        # Configure the client
        genai.configure(api_key=self.api_key)
        
        # Validate model is supported by Google
        if not self.model_name.startswith("gemini"):
            raise GoogleError(f"Model {self.model_name} is not a Google Gemini model")
        
        # Initialize the model
        self.model = genai.GenerativeModel(self.model_name)
    
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
        """Generate response using Google Gemini."""
        try:
            # Validate and prepare messages
            self.validate_messages(messages)
            prepared_messages = self.prepare_system_message(messages)
            
            # Convert to Gemini format
            gemini_contents = self.convert_messages_to_provider_format(prepared_messages)
            
            # Prepare generation config
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
            generation_config.update(kwargs)
            
            # Prepare tools if provided
            gemini_tools = None
            if tools:
                gemini_tools = self.convert_tools_to_provider_format(tools)
            
            if stream:
                return self._generate_stream(gemini_contents, generation_config, gemini_tools)
            else:
                return await self._generate_single(gemini_contents, generation_config, gemini_tools)
                
        except Exception as e:
            # Handle various Google AI exceptions
            error_msg = str(e)
            if "API_KEY" in error_msg.upper():
                raise GoogleError(f"Google API authentication error: {e}", provider="google", model=self.model_name) from e
            elif "QUOTA" in error_msg.upper() or "RATE_LIMIT" in error_msg.upper():
                raise GoogleError(f"Google API quota/rate limit error: {e}", provider="google", model=self.model_name) from e
            else:
                raise GoogleError(f"Google API error: {e}", provider="google", model=self.model_name) from e
    
    async def _generate_single(
        self, 
        contents: List[Content], 
        generation_config: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LanguageModelResponse:
        """Generate a single response."""
        try:
            # Create generation arguments
            generate_kwargs = {
                "contents": contents,
                "generation_config": generation_config,
            }
            
            if tools:
                generate_kwargs["tools"] = tools
            
            # Generate content
            response = self.model.generate_content(**generate_kwargs)
            
            # Extract text content
            response_text = ""
            tool_calls = []
            
            if response.candidates:
                candidate = response.candidates[0]
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
                    elif hasattr(part, 'function_call') and part.function_call:
                        # Extract function call
                        func_call = part.function_call
                        tool_calls.append(ToolCall(
                            id=f"call_{hash(func_call.name)}",  # Generate ID since Gemini doesn't provide one
                            name=func_call.name,
                            arguments=dict(func_call.args) if func_call.args else {}
                        ))
            
            # Calculate token usage (Gemini provides usage in response)
            usage = TokenUsage()
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = TokenUsage(
                    prompt_tokens=response.usage_metadata.prompt_token_count,
                    completion_tokens=response.usage_metadata.candidates_token_count,
                    total_tokens=response.usage_metadata.total_token_count
                )
            
            return LanguageModelResponse(
                message=response_text,
                usage=usage,
                tool_calls=tool_calls if tool_calls else None,
                model=self.model_name,
                finish_reason=getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None,
                metadata={
                    "safety_ratings": getattr(response.candidates[0], 'safety_ratings', []) if response.candidates else []
                }
            )
            
        except Exception as e:
            raise GoogleError(f"Error generating single response: {e}", provider="google", model=self.model_name) from e
    
    async def _generate_stream(
        self, 
        contents: List[Content], 
        generation_config: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[LanguageModelResponse]:
        """Generate streaming response."""
        try:
            # Create generation arguments
            generate_kwargs = {
                "contents": contents,
                "generation_config": generation_config,
                "stream": True,
            }
            
            if tools:
                generate_kwargs["tools"] = tools
            
            # Generate streaming content
            response_stream = self.model.generate_content(**generate_kwargs)
            
            for chunk in response_stream:
                if chunk.candidates:
                    candidate = chunk.candidates[0]
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield LanguageModelResponse(
                                message=part.text,
                                usage=TokenUsage(),
                                model=self.model_name
                            )
                        elif hasattr(part, 'function_call') and part.function_call:
                            # Handle function calls in streaming
                            func_call = part.function_call
                            yield LanguageModelResponse(
                                message="",
                                usage=TokenUsage(),
                                tool_calls=[ToolCall(
                                    id=f"call_{hash(func_call.name)}",
                                    name=func_call.name,
                                    arguments=dict(func_call.args) if func_call.args else {}
                                )],
                                model=self.model_name
                            )
                            
        except Exception as e:
            raise GoogleError(f"Error generating streaming response: {e}", provider="google", model=self.model_name) from e
    
    def convert_messages_to_provider_format(self, messages: List[Message]) -> List[Content]:
        """Convert internal messages to Gemini Content format."""
        contents = []
        system_instruction = None
        
        for message in messages:
            # Handle system messages separately
            if message.role == Role.SYSTEM:
                system_instruction = message.content
                continue
            
            # Convert role
            if message.role == Role.USER:
                role = "user"
            elif message.role == Role.ASSISTANT:
                role = "model"  # Gemini uses "model" instead of "assistant"
            elif message.role == Role.TOOL:
                # Tool results are handled as function responses
                role = "function"
            else:
                continue  # Skip unsupported roles
            
            # Prepare content parts
            parts = []
            
            if isinstance(message.content, str):
                if message.content:  # Only add non-empty content
                    parts.append(Part(text=message.content))
            elif isinstance(message.content, list):
                parts.extend(self._convert_content_blocks(message.content))
            
            # Handle tool calls for assistant messages
            if message.tool_calls and message.role == Role.ASSISTANT:
                for tool_call in message.tool_calls:
                    parts.append(Part(
                        function_call=FunctionCall(
                            name=tool_call.name,
                            args=tool_call.arguments
                        )
                    ))
            
            # Handle tool results
            if message.tool_call_id and message.role == Role.TOOL:
                # Tool results in Gemini are handled as function responses
                parts.append(Part(
                    function_response=FunctionResponse(
                        name=f"function_{message.tool_call_id}",  # Reconstruct function name
                        response={"result": message.content}
                    )
                ))
            
            if parts:  # Only add content if there are parts
                contents.append(Content(role=role, parts=parts))
        
        # Add system instruction to the model if present
        if system_instruction and contents:
            # Prepend system instruction as user message (Gemini pattern)
            system_content = Content(
                role="user",
                parts=[Part(text=f"System: {system_instruction}")]
            )
            contents.insert(0, system_content)
        
        return contents
    
    def _convert_content_blocks(self, content_blocks: List[Dict[str, Any]]) -> List[Part]:
        """Convert content blocks to Gemini Part format."""
        parts = []
        
        for block in content_blocks:
            if isinstance(block, str):
                parts.append(Part(text=block))
            elif isinstance(block, dict):
                block_type = block.get("type", "text")
                
                if block_type == "text":
                    text_content = block.get("text", str(block))
                    if text_content:
                        parts.append(Part(text=text_content))
                elif block_type == "image" or block_type == "image_url":
                    # Handle image content (Gemini supports images)
                    # This would require additional image processing
                    # For now, convert to text description
                    image_desc = block.get("alt_text", "Image content")
                    parts.append(Part(text=f"[Image: {image_desc}]"))
                else:
                    # Convert unknown blocks to text
                    parts.append(Part(text=str(block)))
            else:
                parts.append(Part(text=str(block)))
        
        return parts
    
    def convert_tools_to_provider_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Gemini function format."""
        gemini_functions = []
        
        for tool in tools:
            if "function" in tool:
                # OpenAI-style tool format
                func = tool["function"]
                gemini_function = {
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters", {})
                }
            else:
                # Direct format or simple format
                gemini_function = {
                    "name": tool.get("name", "unknown"),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", tool.get("input_schema", {}))
                }
            
            gemini_functions.append(gemini_function)
        
        # Wrap functions in the expected Gemini tools format
        return [{"function_declarations": gemini_functions}]
    
    def extract_tool_calls_from_response(self, response: Any) -> List[ToolCall]:
        """Extract tool calls from Gemini response."""
        tool_calls = []
        
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    func_call = part.function_call
                    tool_calls.append(ToolCall(
                        id=f"call_{hash(func_call.name)}",
                        name=func_call.name,
                        arguments=dict(func_call.args) if func_call.args else {}
                    ))
        
        return tool_calls