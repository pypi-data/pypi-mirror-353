"""
Example demonstrating the new dynamic model registry system.

This example shows how to use capability-based model selection
without hardcoding model names, making the code future-proof
as new models are released.
"""

import asyncio
import os
from agnt5 import Agent
from agnt5.llm import get_model_registry, ModelCapability


async def demo_capability_based_selection():
    """Demonstrate capability-based model selection."""
    
    print("🤖 AGNT5 Dynamic Model Registry Demo\n")
    
    # Get the model registry
    registry = get_model_registry()
    
    # 1. Show available providers and models
    print("📋 Available Providers:")
    for provider in registry.list_providers():
        models = registry.list_models(provider=provider)
        print(f"  {provider}: {len(models)} models")
    print()
    
    # 2. Create agents using capability-based aliases
    print("🚀 Creating agents with capability-based model selection:\n")
    
    # Fast agent for quick responses
    fast_agent = Agent(
        name="quick-assistant",
        model="fastest",  # Will resolve to fastest available model
        system_prompt="You are a quick response assistant."
    )
    print(f"Fast Agent: {fast_agent.llm.model_name} (provider: {fast_agent.llm.provider_name})")
    
    # Reasoning agent for complex tasks
    reasoning_agent = Agent(
        name="reasoning-assistant", 
        model="best-reasoning",  # Will resolve to best reasoning model
        system_prompt="You are an expert at logical reasoning and analysis."
    )
    print(f"Reasoning Agent: {reasoning_agent.llm.model_name} (provider: {reasoning_agent.llm.provider_name})")
    
    # Coding agent
    coding_agent = Agent(
        name="coding-assistant",
        model="best-coding",  # Will resolve to best coding model
        system_prompt="You are an expert programmer."
    )
    print(f"Coding Agent: {coding_agent.llm.model_name} (provider: {coding_agent.llm.provider_name})")
    
    # Budget-conscious agent
    budget_agent = Agent(
        name="budget-assistant",
        model="most-affordable",  # Will resolve to cheapest model
        system_prompt="You are a helpful but cost-effective assistant."
    )
    print(f"Budget Agent: {budget_agent.llm.model_name} (provider: {budget_agent.llm.provider_name})")
    
    print()
    
    # 3. Provider-specific latest models
    print("🔄 Provider-specific latest models:")
    
    providers = ["claude-latest", "gpt-latest", "gemini-latest", "mistral-latest"]
    for provider_alias in providers:
        try:
            agent = Agent(name=f"test-{provider_alias}", model=provider_alias)
            print(f"  {provider_alias}: {agent.llm.model_name}")
        except Exception as e:
            print(f"  {provider_alias}: Not available ({e})")
    
    print()
    
    # 4. Demonstrate model capabilities checking
    print("🎯 Model Capabilities Analysis:")
    
    # Find models with specific capabilities
    vision_models = registry.find_models_by_capability(ModelCapability.VISION)
    print(f"Vision-capable models: {len(vision_models)}")
    for model in vision_models[:3]:  # Show first 3
        print(f"  - {model.name} ({model.provider})")
    
    tool_models = registry.find_models_by_capability(ModelCapability.TOOL_CALLING)
    print(f"Tool-calling models: {len(tool_models)}")
    
    long_context_models = registry.find_models_by_capability(ModelCapability.LONG_CONTEXT)
    print(f"Long context models: {len(long_context_models)}")
    
    print()
    
    # 5. Dynamic model registration (for new models)
    print("➕ Dynamic Model Registration:")
    
    # Register a hypothetical new model
    new_model = registry.register_dynamic_model(
        name="hypothetical-new-model-v2",
        provider="new_provider",
        tier=registry.ModelTier.EXPERIMENTAL,
        capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING],
        aliases=["new-latest", "experimental-best"]
    )
    print(f"Registered: {new_model.name} with aliases {new_model.aliases}")
    
    # Now we can use the new model via its alias
    try:
        new_agent = Agent(name="experimental", model="new-latest")
        print(f"Created agent with new model: {new_agent.llm.model_name}")
    except Exception as e:
        print(f"New model agent creation failed (expected): {e}")
    
    print()
    
    # 6. Demonstrate actual model usage
    print("💬 Testing model responses:")
    
    # Use the fast agent for a quick query
    try:
        response = await fast_agent.run("What is 2+2?")
        print(f"Fast Agent Response: {response.content[:100]}...")
    except Exception as e:
        print(f"Fast agent failed: {e}")
    
    print("\n✅ Demo complete!")


async def demo_configuration_management():
    """Show how to manage model configurations."""
    
    print("\n⚙️  Configuration Management Demo\n")
    
    registry = get_model_registry()
    
    # Show model details
    print("📊 Model Information:")
    
    models_to_check = ["claude-latest", "gpt-fast", "best-reasoning"]
    
    for model_alias in models_to_check:
        model_info = registry.resolve_model(model_alias)
        if model_info:
            print(f"\n{model_alias} -> {model_info.name}")
            print(f"  Provider: {model_info.provider}")
            print(f"  Tier: {model_info.tier.value}")
            print(f"  Context Length: {model_info.context_length:,}" if model_info.context_length else "  Context Length: Unknown")
            print(f"  Supports Tools: {model_info.supports_tools}")
            print(f"  Supports Vision: {model_info.supports_vision}")
            print(f"  Capabilities: {', '.join(cap.value for cap in model_info.capabilities)}")
    
    # Show configuration file location
    print(f"\n📄 Configuration file: {registry.config_path}")
    print("💡 Tip: Edit this file to add new models or update capabilities without changing code!")


if __name__ == "__main__":
    # Run the demos
    asyncio.run(demo_capability_based_selection())
    asyncio.run(demo_configuration_management())
    
    print("\n" + "="*70)
    print("🎉 Key Benefits of the Dynamic Model Registry:")
    print("="*70)
    print("✅ No hardcoded model names in your code")
    print("✅ Capability-based model selection")
    print("✅ Automatic resolution of provider-specific 'latest' models")
    print("✅ Easy configuration updates via JSON file")
    print("✅ Forward compatibility with new models")
    print("✅ Intelligent fallback handling")
    print("✅ Runtime model discovery (future feature)")
    print("="*70)