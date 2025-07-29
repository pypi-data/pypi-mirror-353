"""
Dynamic model registry for LLM providers.

This module provides a future-proof way to handle model discovery and management
without hardcoding model names. It supports:
1. Dynamic model discovery via API calls
2. Configuration-based model definitions
3. Capability-based model selection
4. Automatic fallback and aliasing
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelCapability(Enum):
    """Model capabilities for intelligent selection."""
    TEXT_GENERATION = "text_generation"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"
    MULTILINGUAL = "multilingual"
    FAST_INFERENCE = "fast_inference"
    COST_EFFICIENT = "cost_efficient"


class ModelTier(Enum):
    """Model performance/cost tiers."""
    FLAGSHIP = "flagship"        # Best performance, highest cost
    PERFORMANCE = "performance"  # High performance, moderate cost
    BALANCED = "balanced"        # Good performance, reasonable cost
    EFFICIENT = "efficient"      # Fast inference, low cost
    EXPERIMENTAL = "experimental" # Beta/preview models


@dataclass
class ModelInfo:
    """Comprehensive model information."""
    name: str
    provider: str
    tier: ModelTier
    capabilities: Set[ModelCapability]
    context_length: Optional[int] = None
    max_output_tokens: Optional[int] = None
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_vision: bool = False
    deprecated: bool = False
    aliases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ModelRegistry:
    """
    Dynamic model registry with automatic discovery and configuration.
    
    This registry supports multiple strategies for model management:
    1. Static configuration from files
    2. Dynamic discovery via provider APIs
    3. Capability-based selection
    4. Automatic fallback handling
    """
    
    def __init__(self, config_path: Optional[str] = None, cache_ttl: int = 3600):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "models.json"
        )
        self.cache_ttl = cache_ttl  # Cache TTL in seconds
        self._models: Dict[str, ModelInfo] = {}
        self._aliases: Dict[str, str] = {}
        self._capabilities_cache: Dict[ModelCapability, List[str]] = {}
        self._last_refresh = None
        
        # Load initial configuration
        self._load_static_config()
    
    def _load_static_config(self):
        """Load static model configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self._parse_config(config)
            else:
                # Create default configuration
                self._create_default_config()
        except Exception as e:
            logger.warning(f"Failed to load model config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default model configuration with capability-based aliases."""
        default_models = {
            # Anthropic models
            "anthropic": {
                "claude-3-5-sonnet-latest": {
                    "tier": "flagship",
                    "capabilities": ["text_generation", "tool_calling", "vision", "reasoning", "analysis"],
                    "aliases": ["claude-latest", "best-reasoning"],
                    "context_length": 200000,
                    "supports_tools": True,
                    "supports_vision": True
                },
                "claude-3-5-haiku-latest": {
                    "tier": "efficient", 
                    "capabilities": ["text_generation", "tool_calling", "fast_inference"],
                    "aliases": ["claude-fast", "fastest"],
                    "context_length": 200000,
                    "supports_tools": True
                }
            },
            # OpenAI models
            "openai": {
                "gpt-4o": {
                    "tier": "flagship",
                    "capabilities": ["text_generation", "tool_calling", "vision", "reasoning", "analysis"],
                    "aliases": ["gpt-latest", "best-multimodal"],
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_vision": True
                },
                "gpt-4o-mini": {
                    "tier": "efficient",
                    "capabilities": ["text_generation", "tool_calling", "fast_inference", "cost_efficient"],
                    "aliases": ["gpt-fast", "most-affordable"],
                    "context_length": 128000,
                    "supports_tools": True
                }
            },
            # Google models
            "google": {
                "gemini-1.5-pro": {
                    "tier": "flagship",
                    "capabilities": ["text_generation", "tool_calling", "vision", "long_context"],
                    "aliases": ["gemini-latest"],
                    "context_length": 2000000,
                    "supports_tools": True,
                    "supports_vision": True
                },
                "gemini-1.5-flash": {
                    "tier": "efficient",
                    "capabilities": ["text_generation", "tool_calling", "fast_inference"],
                    "aliases": ["gemini-fast"],
                    "context_length": 1000000,
                    "supports_tools": True
                }
            },
            # Mistral models
            "mistral": {
                "mistral-large-latest": {
                    "tier": "flagship",
                    "capabilities": ["text_generation", "tool_calling", "reasoning", "multilingual"],
                    "aliases": ["mistral-latest"],
                    "supports_tools": True
                },
                "mistral-small-latest": {
                    "tier": "efficient",
                    "capabilities": ["text_generation", "fast_inference", "cost_efficient"],
                    "aliases": ["mistral-fast"]
                }
            },
            # Together AI models (dynamic patterns)
            "together": {
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": {
                    "tier": "performance",
                    "capabilities": ["text_generation", "tool_calling", "reasoning"],
                    "aliases": ["llama-latest"],
                    "supports_tools": True
                },
                "mistralai/Mixtral-8x7B-Instruct-v0.1": {
                    "tier": "balanced",
                    "capabilities": ["text_generation", "tool_calling", "multilingual"],
                    "aliases": ["mixtral-latest"],
                    "supports_tools": True
                }
            }
        }
        
        self._parse_config(default_models)
    
    def _parse_config(self, config: Dict[str, Any]):
        """Parse configuration and populate model registry."""
        self._models.clear()
        self._aliases.clear()
        
        for provider, models in config.items():
            for model_name, model_config in models.items():
                # Convert capabilities from strings to enum
                capabilities = set()
                for cap_str in model_config.get("capabilities", []):
                    try:
                        capabilities.add(ModelCapability(cap_str))
                    except ValueError:
                        logger.warning(f"Unknown capability: {cap_str}")
                
                # Create ModelInfo
                model_info = ModelInfo(
                    name=model_name,
                    provider=provider,
                    tier=ModelTier(model_config.get("tier", "balanced")),
                    capabilities=capabilities,
                    context_length=model_config.get("context_length"),
                    max_output_tokens=model_config.get("max_output_tokens"),
                    supports_streaming=model_config.get("supports_streaming", True),
                    supports_tools=model_config.get("supports_tools", False),
                    supports_vision=model_config.get("supports_vision", False),
                    deprecated=model_config.get("deprecated", False),
                    aliases=model_config.get("aliases", []),
                    metadata=model_config.get("metadata", {})
                )
                
                self._models[model_name] = model_info
                
                # Register aliases
                for alias in model_info.aliases:
                    self._aliases[alias] = model_name
        
        self._last_refresh = datetime.utcnow()
        logger.info(f"Loaded {len(self._models)} models with {len(self._aliases)} aliases")
    
    async def refresh_models(self, force: bool = False):
        """Refresh model information from providers."""
        if not force and self._last_refresh:
            elapsed = datetime.utcnow() - self._last_refresh
            if elapsed.total_seconds() < self.cache_ttl:
                return
        
        logger.info("Refreshing model registry from providers...")
        
        # Attempt to fetch latest models from each provider
        tasks = []
        if self._should_refresh_provider("anthropic"):
            tasks.append(self._refresh_anthropic_models())
        if self._should_refresh_provider("openai"):
            tasks.append(self._refresh_openai_models())
        if self._should_refresh_provider("google"):
            tasks.append(self._refresh_google_models())
        
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
                self._last_refresh = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Failed to refresh some providers: {e}")
    
    def _should_refresh_provider(self, provider: str) -> bool:
        """Check if provider should be refreshed (has API key, etc.)."""
        api_key_vars = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "google": "GOOGLE_API_KEY"
        }
        return os.getenv(api_key_vars.get(provider, "")) is not None
    
    async def _refresh_anthropic_models(self):
        """Refresh Anthropic models (placeholder - would call actual API)."""
        # In a real implementation, this would call Anthropic's API
        # to get the latest model list and capabilities
        logger.debug("Refreshing Anthropic models...")
    
    async def _refresh_openai_models(self):
        """Refresh OpenAI models (placeholder - would call actual API)."""
        # In a real implementation, this would call OpenAI's API
        logger.debug("Refreshing OpenAI models...")
    
    async def _refresh_google_models(self):
        """Refresh Google models (placeholder - would call actual API)."""
        # In a real implementation, this would call Google's API
        logger.debug("Refreshing Google models...")
    
    def resolve_model(self, model_identifier: str) -> Optional[ModelInfo]:
        """
        Resolve a model identifier to actual model information.
        
        Args:
            model_identifier: Can be:
                - Exact model name (e.g., "gpt-4o")
                - Alias (e.g., "gpt-latest", "fastest")
                - Capability (e.g., "best-reasoning")
                
        Returns:
            ModelInfo if found, None otherwise
        """
        # Exact match first
        if model_identifier in self._models:
            return self._models[model_identifier]
        
        # Check aliases
        if model_identifier in self._aliases:
            actual_name = self._aliases[model_identifier]
            return self._models.get(actual_name)
        
        # Fuzzy matching for flexibility
        return self._fuzzy_match(model_identifier)
    
    def _fuzzy_match(self, identifier: str) -> Optional[ModelInfo]:
        """Attempt fuzzy matching for unknown identifiers."""
        identifier_lower = identifier.lower()
        
        # Provider-based matching
        if "claude" in identifier_lower:
            return self._find_best_model_for_provider("anthropic")
        elif "gpt" in identifier_lower:
            return self._find_best_model_for_provider("openai")
        elif "gemini" in identifier_lower:
            return self._find_best_model_for_provider("google")
        elif "mistral" in identifier_lower:
            return self._find_best_model_for_provider("mistral")
        elif "llama" in identifier_lower or "meta-llama" in identifier_lower:
            return self._find_best_model_for_provider("together")
        
        return None
    
    def _find_best_model_for_provider(self, provider: str) -> Optional[ModelInfo]:
        """Find the best model for a given provider."""
        provider_models = [m for m in self._models.values() if m.provider == provider and not m.deprecated]
        
        if not provider_models:
            return None
        
        # Prefer flagship tier, then performance, then balanced
        tier_order = [ModelTier.FLAGSHIP, ModelTier.PERFORMANCE, ModelTier.BALANCED, ModelTier.EFFICIENT]
        
        for tier in tier_order:
            tier_models = [m for m in provider_models if m.tier == tier]
            if tier_models:
                return tier_models[0]  # Return first match
        
        return provider_models[0]  # Fallback to any model
    
    def find_models_by_capability(self, capability: ModelCapability, provider: Optional[str] = None) -> List[ModelInfo]:
        """Find models that support a specific capability."""
        models = []
        for model in self._models.values():
            if capability in model.capabilities and not model.deprecated:
                if provider is None or model.provider == provider:
                    models.append(model)
        
        # Sort by tier (flagship first)
        tier_order = {ModelTier.FLAGSHIP: 0, ModelTier.PERFORMANCE: 1, ModelTier.BALANCED: 2, ModelTier.EFFICIENT: 3}
        models.sort(key=lambda m: tier_order.get(m.tier, 999))
        
        return models
    
    def get_fastest_model(self, provider: Optional[str] = None) -> Optional[ModelInfo]:
        """Get the fastest model available."""
        fast_models = self.find_models_by_capability(ModelCapability.FAST_INFERENCE, provider)
        return fast_models[0] if fast_models else None
    
    def get_most_capable_model(self, provider: Optional[str] = None) -> Optional[ModelInfo]:
        """Get the most capable model available."""
        all_models = [m for m in self._models.values() if not m.deprecated]
        if provider:
            all_models = [m for m in all_models if m.provider == provider]
        
        if not all_models:
            return None
        
        # Score models by number of capabilities and tier
        def score_model(model: ModelInfo) -> int:
            tier_score = {ModelTier.FLAGSHIP: 100, ModelTier.PERFORMANCE: 80, ModelTier.BALANCED: 60, ModelTier.EFFICIENT: 40}
            return len(model.capabilities) * 10 + tier_score.get(model.tier, 0)
        
        return max(all_models, key=score_model)
    
    def get_cheapest_model(self, provider: Optional[str] = None) -> Optional[ModelInfo]:
        """Get the most cost-efficient model."""
        cheap_models = self.find_models_by_capability(ModelCapability.COST_EFFICIENT, provider)
        return cheap_models[0] if cheap_models else None
    
    def list_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(set(model.provider for model in self._models.values()))
    
    def list_models(self, provider: Optional[str] = None, include_deprecated: bool = False) -> List[ModelInfo]:
        """List all available models."""
        models = list(self._models.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if not include_deprecated:
            models = [m for m in models if not m.deprecated]
        
        return models
    
    def get_model_by_name(self, name: str) -> Optional[ModelInfo]:
        """Get model by exact name."""
        return self._models.get(name)
    
    def register_dynamic_model(self, name: str, provider: str, **kwargs) -> ModelInfo:
        """Register a new model dynamically."""
        model_info = ModelInfo(
            name=name,
            provider=provider,
            tier=kwargs.get("tier", ModelTier.EXPERIMENTAL),
            capabilities=set(kwargs.get("capabilities", [ModelCapability.TEXT_GENERATION])),
            **{k: v for k, v in kwargs.items() if k not in ["tier", "capabilities"]}
        )
        
        self._models[name] = model_info
        
        # Register aliases if provided
        for alias in model_info.aliases:
            self._aliases[alias] = name
        
        logger.info(f"Registered dynamic model: {name}")
        return model_info


# Global registry instance
_registry = None

def get_model_registry() -> ModelRegistry:
    """Get the global model registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


def resolve_model_name(identifier: str) -> str:
    """
    Resolve any model identifier to an actual model name.
    
    This is the main entry point for model resolution.
    """
    registry = get_model_registry()
    model_info = registry.resolve_model(identifier)
    
    if model_info:
        return model_info.name
    else:
        # If we can't resolve it, return as-is and let the provider handle it
        # This allows for forward compatibility with new models
        logger.warning(f"Unknown model identifier '{identifier}', using as-is")
        return identifier


def get_provider_for_model(model_name: str) -> Optional[str]:
    """Get the provider name for a model."""
    registry = get_model_registry()
    model_info = registry.resolve_model(model_name)
    return model_info.provider if model_info else None


def supports_capability(model_name: str, capability: ModelCapability) -> bool:
    """Check if a model supports a specific capability."""
    registry = get_model_registry()
    model_info = registry.resolve_model(model_name)
    return model_info and capability in model_info.capabilities