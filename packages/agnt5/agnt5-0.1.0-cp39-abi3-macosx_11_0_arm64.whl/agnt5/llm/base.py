"""
Base classes and interfaces for LLM provider integration.

Defines the common interface that all LLM providers must implement,
along with shared types and utilities.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from datetime import datetime


class Role(Enum):
    """Message roles in conversations."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class LanguageModelType:
    """
    Simple model type that parses provider/model format.
    
    Supports formats:
    - "provider/model" (e.g., "anthropic/claude-3-5-sonnet")
    - "model" (auto-detects provider, e.g., "gpt-4o")
    """
    
    def __init__(self, model_string: str):
        """
        Initialize with a model string.
        
        Args:
            model_string: Either "provider/model" or just "model"
        """
        self.original = model_string
        
        if "/" in model_string:
            # Format: "provider/model"
            self._provider, self.value = model_string.split("/", 1)
        else:
            # Format: "model" - auto-detect provider
            self.value = model_string
            self._provider = self._detect_provider(model_string)
    
    @classmethod
    def from_string(cls, model_string: str) -> "LanguageModelType":
        """Create LanguageModelType from string."""
        return cls(model_string)
    
    def _detect_provider(self, model_name: str) -> str:
        """Auto-detect provider from model name."""
        model_lower = model_name.lower()
        
        # Claude models
        if any(keyword in model_lower for keyword in ["claude", "sonnet", "haiku", "opus"]):
            return "anthropic"
        
        # OpenAI models
        elif model_lower.startswith("gpt"):
            return "openai"
        
        # Google models
        elif model_lower.startswith("gemini"):
            return "google"
        
        # Mistral models
        elif any(model_lower.startswith(prefix) for prefix in ["mistral", "codestral"]):
            return "mistral"
        
        # Together AI models (usually have namespace/model format, but handle edge cases)
        elif any(keyword in model_lower for keyword in ["llama", "mixtral", "qwen"]) or model_name.count("/") > 0:
            return "together"
        
        # Default to OpenAI for unknown models
        else:
            return "openai"
    
    def get_provider(self) -> str:
        """Get the provider name for this model."""
        return self._provider
    
    @property
    def provider(self) -> str:
        """Provider property for easy access."""
        return self._provider
    
    @property
    def model(self) -> str:
        """Model name property for easy access."""
        return self.value
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"LanguageModelType('{self.original}' -> provider='{self._provider}', model='{self.value}')"
    
    def __eq__(self, other):
        if isinstance(other, LanguageModelType):
            return self.value == other.value and self._provider == other._provider
        elif isinstance(other, str):
            return self.value == other or self.original == other
        return False
    
    def __hash__(self):
        return hash((self._provider, self.value))


@dataclass
class TokenUsage:
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ToolCall:
    """Represents a tool call made by the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """Represents the result of a tool call."""
    tool_call_id: str
    output: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: Role
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LanguageModelResponse:
    """Response from a language model."""
    message: str
    usage: TokenUsage
    tool_calls: Optional[List[ToolCall]] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    
    def __init__(self, message: str, provider: str = None, model: str = None, **kwargs):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.model = model
        self.metadata = kwargs


class LanguageModel(ABC):
    """
    Abstract base class for all language model providers.
    
    Provides a unified interface for different LLM providers with support for:
    - Text generation with tool calling
    - Streaming responses
    - Message format conversion
    - Error handling
    """
    
    def __init__(
        self,
        llm_model: LanguageModelType,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        self.llm_model = llm_model
        self.system_prompt = system_prompt
        self.config = kwargs
        
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self.llm_model.get_provider()
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.llm_model.value
    
    @abstractmethod
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
        """
        Generate a response from the language model.
        
        Args:
            messages: List of conversation messages
            tools: Optional list of available tools
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
            **kwargs: Provider-specific parameters
            
        Returns:
            LanguageModelResponse or async iterator for streaming
        """
        pass
    
    @abstractmethod
    def convert_messages_to_provider_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal message format to provider-specific format."""
        pass
    
    @abstractmethod
    def convert_tools_to_provider_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert internal tool format to provider-specific format."""
        pass
    
    def prepare_system_message(self, messages: List[Message]) -> List[Message]:
        """Prepare system message for the conversation."""
        if not self.system_prompt:
            return messages
            
        # Check if system message already exists
        if messages and messages[0].role == Role.SYSTEM:
            # Merge with existing system message
            existing_content = messages[0].content
            if isinstance(existing_content, str):
                combined_content = f"{self.system_prompt}\n\n{existing_content}"
            else:
                combined_content = self.system_prompt
            
            messages[0].content = combined_content
            return messages
        else:
            # Add new system message
            system_message = Message(role=Role.SYSTEM, content=self.system_prompt)
            return [system_message] + messages
    
    def validate_messages(self, messages: List[Message]) -> None:
        """Validate message format and content."""
        if not messages:
            raise LLMError("No messages provided", provider=self.provider_name)
        
        for i, message in enumerate(messages):
            if not isinstance(message.role, Role):
                raise LLMError(f"Invalid role at message {i}: {message.role}", provider=self.provider_name)
            
            if not message.content and not message.tool_calls:
                raise LLMError(f"Empty content at message {i}", provider=self.provider_name)
    
    def extract_tool_calls_from_response(self, response: Any) -> List[ToolCall]:
        """Extract tool calls from provider response."""
        # Default implementation - override in subclasses
        return []
    
    async def generate_with_retry(
        self,
        messages: List[Message],
        max_retries: int = 3,
        **kwargs
    ) -> LanguageModelResponse:
        """Generate response with automatic retry on failure."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = await self.generate(messages, **kwargs)
                if isinstance(result, AsyncIterator):
                    # Convert streaming to single response for retry logic
                    response_text = ""
                    async for chunk in result:
                        response_text += chunk.message
                    return LanguageModelResponse(
                        message=response_text,
                        usage=TokenUsage(),
                        model=self.model_name
                    )
                return result
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Exponential backoff
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue
                break
        
        raise LLMError(
            f"Failed after {max_retries + 1} attempts: {last_error}",
            provider=self.provider_name,
            model=self.model_name
        ) from last_error