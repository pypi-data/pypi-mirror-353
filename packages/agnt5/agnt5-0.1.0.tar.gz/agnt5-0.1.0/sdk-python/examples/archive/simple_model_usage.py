"""
Simple model usage with provider/model format.

This example shows the clean, straightforward way to specify models
using the provider/model format or simple auto-detection.
"""

import asyncio
from agnt5 import Agent


async def demo_simple_model_usage():
    """Demonstrate simple model usage patterns."""
    
    print("🤖 AGNT5 Simple Model Usage Demo\n")
    
    # Method 1: Explicit provider/model format (recommended for clarity)
    print("📝 Method 1: Explicit provider/model format")
    agents = [
        Agent(name="claude", model="anthropic/claude-3-5-sonnet"),
        Agent(name="gpt", model="openai/gpt-4o"),
        Agent(name="gemini", model="google/gemini-1.5-pro"),
        Agent(name="mistral", model="mistral/mistral-large-latest"),
        Agent(name="llama", model="together/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"),
    ]
    
    for agent in agents:
        print(f"  {agent.name}: {agent.llm.model_name} (provider: {agent.llm.provider_name})")
    
    print()
    
    # Method 2: Auto-detection (works but less explicit)
    print("🔍 Method 2: Auto-detection from model name")
    auto_agents = [
        Agent(name="claude-auto", model="claude-3-5-sonnet"),
        Agent(name="gpt-auto", model="gpt-4o"),
        Agent(name="gemini-auto", model="gemini-1.5-pro"),
        Agent(name="mistral-auto", model="mistral-large-latest"),
    ]
    
    for agent in auto_agents:
        print(f"  {agent.name}: {agent.llm.model_name} (detected: {agent.llm.provider_name})")
    
    print()
    
    # Method 3: Any model name - future proof
    print("🚀 Method 3: Future-proof with any model name")
    future_agents = [
        Agent(name="new-claude", model="anthropic/claude-4-opus"),  # Hypothetical future model
        Agent(name="new-gpt", model="openai/gpt-5"),               # Hypothetical future model
        Agent(name="new-provider", model="newai/amazing-model"),   # Hypothetical new provider
    ]
    
    for agent in future_agents:
        print(f"  {agent.name}: {agent.llm.model_name} (provider: {agent.llm.provider_name})")
    
    print()
    
    # Method 4: Test actual conversation
    print("💬 Testing actual conversation:")
    
    try:
        # Use a simple model for testing
        test_agent = Agent(
            name="test-agent",
            model="anthropic/claude-3-5-haiku",  # Fast and affordable for testing
            system_prompt="You are a helpful assistant. Be concise."
        )
        
        response = await test_agent.run("What is 2+2? Answer in one sentence.")
        print(f"  Agent Response: {response.content}")
        
    except Exception as e:
        print(f"  Test failed (likely no API key): {e}")
    
    print("\n✅ Demo complete!")


def demo_model_parsing():
    """Show how the model parsing works."""
    
    print("\n🔧 Model Parsing Demo\n")
    
    from agnt5.llm.base import LanguageModelType
    
    test_cases = [
        "anthropic/claude-3-5-sonnet",
        "openai/gpt-4o",
        "google/gemini-1.5-pro", 
        "mistral/mistral-large-latest",
        "together/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "claude-3-5-sonnet",  # Auto-detection
        "gpt-4o",             # Auto-detection
        "gemini-1.5-pro",     # Auto-detection
        "newai/future-model", # Unknown provider
        "unknown-model",      # Unknown model
    ]
    
    print("Model String → Provider | Model")
    print("-" * 50)
    
    for model_string in test_cases:
        model_type = LanguageModelType.from_string(model_string)
        print(f"{model_string:<35} → {model_type.provider:<10} | {model_type.model}")


if __name__ == "__main__":
    # Run the demos
    asyncio.run(demo_simple_model_usage())
    demo_model_parsing()
    
    print("\n" + "="*60)
    print("🎉 Key Benefits of Provider/Model Format:")
    print("="*60)
    print("✅ Clear and explicit: 'anthropic/claude-3-5-sonnet'")
    print("✅ Future-proof: Works with any new model/provider")
    print("✅ No configuration files needed")
    print("✅ Auto-detection fallback for convenience")
    print("✅ Simple to understand and debug")
    print("✅ Works with existing and future models")
    print("="*60)