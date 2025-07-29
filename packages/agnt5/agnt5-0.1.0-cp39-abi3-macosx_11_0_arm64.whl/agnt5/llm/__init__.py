"""
LLM provider integrations for AGNT5 SDK.

Provides unified interface for different LLM providers (Anthropic, OpenAI, etc.)
with consistent message handling, tool calling, and streaming support.
"""

from .base import (
    LanguageModel,
    LanguageModelResponse,
    LanguageModelType,
    Message,
    Role,
    TokenUsage,
    ToolCall,
    ToolResult,
    LLMError,
)

# Model registry is available but not exported by default
# Users can import directly if needed: from agnt5.llm.model_registry import ...

try:
    from .anthropic import AnthropicLanguageModel
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from .openai import OpenAILanguageModel
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from .google import GoogleLanguageModel
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from .mistral import MistralLanguageModel
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

try:
    from .azure import AzureOpenAILanguageModel
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

try:
    from .together import TogetherAILanguageModel
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False

__all__ = [
    # Base classes
    "LanguageModel",
    "LanguageModelResponse", 
    "LanguageModelType",
    "Message",
    "Role",
    "TokenUsage",
    "ToolCall",
    "ToolResult",
    "LLMError",
    
    # Factory function
    "create_llm",
    
    # Provider availability flags
    "ANTHROPIC_AVAILABLE",
    "OPENAI_AVAILABLE", 
    "GOOGLE_AVAILABLE",
    "MISTRAL_AVAILABLE",
    "AZURE_OPENAI_AVAILABLE",
    "TOGETHER_AVAILABLE",
]

# Conditionally export providers
if ANTHROPIC_AVAILABLE:
    __all__.append("AnthropicLanguageModel")

if OPENAI_AVAILABLE:
    __all__.append("OpenAILanguageModel")

if GOOGLE_AVAILABLE:
    __all__.append("GoogleLanguageModel")

if MISTRAL_AVAILABLE:
    __all__.append("MistralLanguageModel")

if AZURE_OPENAI_AVAILABLE:
    __all__.append("AzureOpenAILanguageModel")

if TOGETHER_AVAILABLE:
    __all__.append("TogetherAILanguageModel")


def get_available_providers():
    """Get list of available LLM providers."""
    providers = []
    if ANTHROPIC_AVAILABLE:
        providers.append("anthropic")
    if OPENAI_AVAILABLE:
        providers.append("openai")
    if GOOGLE_AVAILABLE:
        providers.append("google")
    if MISTRAL_AVAILABLE:
        providers.append("mistral")
    if AZURE_OPENAI_AVAILABLE:
        providers.append("azure_openai")
    if TOGETHER_AVAILABLE:
        providers.append("together")
    return providers


def create_llm(provider: str, model: str, **kwargs) -> LanguageModel:
    """
    Factory function to create LLM instances.
    
    Args:
        provider: Provider name ('anthropic', 'openai')
        model: Model name
        **kwargs: Provider-specific configuration
        
    Returns:
        LanguageModel instance
        
    Raises:
        ValueError: If provider is not available
    """
    if provider == "anthropic":
        if not ANTHROPIC_AVAILABLE:
            raise ValueError("Anthropic provider not available. Install: pip install anthropic")
        return AnthropicLanguageModel(
            llm_model=LanguageModelType.from_string(model),
            **kwargs
        )
    elif provider == "openai":
        if not OPENAI_AVAILABLE:
            raise ValueError("OpenAI provider not available. Install: pip install openai")
        return OpenAILanguageModel(
            llm_model=LanguageModelType.from_string(model),
            **kwargs
        )
    elif provider == "google":
        if not GOOGLE_AVAILABLE:
            raise ValueError("Google provider not available. Install: pip install google-generativeai")
        return GoogleLanguageModel(
            llm_model=LanguageModelType.from_string(model),
            **kwargs
        )
    elif provider == "mistral":
        if not MISTRAL_AVAILABLE:
            raise ValueError("Mistral provider not available. Install: pip install openai")
        return MistralLanguageModel(
            llm_model=LanguageModelType.from_string(model),
            **kwargs
        )
    elif provider == "azure_openai":
        if not AZURE_OPENAI_AVAILABLE:
            raise ValueError("Azure OpenAI provider not available. Install: pip install openai")
        return AzureOpenAILanguageModel(
            llm_model=LanguageModelType.from_string(model),
            **kwargs
        )
    elif provider == "together":
        if not TOGETHER_AVAILABLE:
            raise ValueError("Together AI provider not available. Install: pip install openai")
        return TogetherAILanguageModel(
            llm_model=LanguageModelType.from_string(model),
            **kwargs
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Available: {get_available_providers()}")