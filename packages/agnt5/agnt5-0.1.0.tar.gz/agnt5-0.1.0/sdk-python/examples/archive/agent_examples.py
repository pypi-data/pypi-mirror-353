#!/usr/bin/env python3
"""
Comprehensive Agent Examples for AGNT5 SDK

This example demonstrates various agent patterns and use cases:
1. Basic Agent Usage
2. Agent with Tools
3. Multi-Provider Agents
4. Agent with Memory
5. Agent Reflection and Self-Improvement
6. Multi-Agent Coordination
7. Agent with Durable State
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from agnt5 import Agent, Memory, Tool, tool
from agnt5.durable import durable
from agnt5.llm import LanguageModelType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# 1. BASIC AGENT USAGE
# =============================================================================


async def demo_basic_agent():
    """Demonstrate basic agent creation and usage."""
    print("\n🤖 1. Basic Agent Usage")
    print("=" * 40)

    # Simple agent with different models
    agents = {
        "claude": Agent(name="claude-assistant", model="anthropic/claude-3-5-sonnet", system_prompt="You are Claude, a helpful AI assistant. Be concise and friendly."),
        "gpt": Agent(name="gpt-assistant", model="openai/gpt-4o", system_prompt="You are GPT, a helpful AI assistant. Be direct and informative."),
        "gemini": Agent(name="gemini-assistant", model="google/gemini-1.5-pro", system_prompt="You are Gemini, a helpful AI assistant. Be thorough and analytical."),
    }

    question = "What is the capital of France and why is it important?"

    for name, agent in agents.items():
        try:
            print(f"\n  {name.upper()} Response:")
            response = await agent.run(question)
            print(f"    {response.content[:150]}...")
        except Exception as e:
            print(f"    ❌ {name} failed: {e}")


# =============================================================================
# 2. AGENT WITH TOOLS
# =============================================================================


@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Mock implementation
    return f"Search results for '{query}': [Mock results - this would call a real search API]"


@tool
def calculate(expression: str) -> str:
    """Calculate mathematical expressions safely."""
    try:
        # Simple safe evaluation for demo
        result = eval(expression.replace("^", "**"))
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    # Mock implementation
    return f"Weather in {location}: 72°F, Sunny with light clouds"


async def demo_agent_with_tools():
    """Demonstrate agent using tools."""
    print("\n🔧 2. Agent with Tools")
    print("=" * 40)

    # Create agent with tools
    research_agent = Agent(
        name="research-assistant",
        model="anthropic/claude-3-5-sonnet",
        tools=[search_web, calculate, get_weather],
        system_prompt="You are a research assistant. Use tools when needed to answer questions accurately.",
    )

    # Test different types of queries that require tools
    queries = [
        "What's 15 * 23 + 47?",
        "Search for information about quantum computing",
        "What's the weather like in San Francisco?",
        "Calculate 2^10 and search for information about binary numbers",
    ]

    for query in queries:
        try:
            print(f"\n  Query: {query}")
            response = await research_agent.run(query)
            print(f"  Response: {response.content[:200]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")


# =============================================================================
# 3. MULTI-PROVIDER AGENT COORDINATION
# =============================================================================


async def demo_multi_provider_coordination():
    """Demonstrate coordination between agents from different providers."""
    print("\n🌐 3. Multi-Provider Agent Coordination")
    print("=" * 40)

    # Different specialized agents
    creative_agent = Agent(name="creative-writer", model="anthropic/claude-3-5-sonnet", system_prompt="You are a creative writer. Focus on storytelling and narrative.")

    technical_agent = Agent(name="technical-analyst", model="openai/gpt-4o", system_prompt="You are a technical analyst. Focus on factual, structured analysis.")

    research_agent = Agent(name="researcher", model="google/gemini-1.5-pro", system_prompt="You are a researcher. Focus on gathering and synthesizing information.")

    # Collaborative task: Create a product description
    product = "AI-powered smart garden system"

    try:
        # Step 1: Research phase
        print(f"\n  📚 Research Phase (Gemini):")
        research_prompt = f"Research the market and technology for {product}. What are the key features and benefits?"
        research_result = await research_agent.run(research_prompt)
        print(f"    {research_result.content[:200]}...")

        # Step 2: Technical analysis
        print(f"\n  🔬 Technical Analysis (GPT):")
        technical_prompt = f"Based on this research: {research_result.content[:500]}... Provide a technical specification for {product}"
        technical_result = await technical_agent.run(technical_prompt)
        print(f"    {technical_result.content[:200]}...")

        # Step 3: Creative writing
        print(f"\n  ✍️ Creative Writing (Claude):")
        creative_prompt = f"Create an engaging product description for {product} based on: {technical_result.content[:500]}..."
        creative_result = await creative_agent.run(creative_prompt)
        print(f"    {creative_result.content[:200]}...")

    except Exception as e:
        print(f"  ❌ Coordination failed: {e}")


# =============================================================================
# 4. AGENT WITH MEMORY
# =============================================================================


async def demo_agent_with_memory():
    """Demonstrate agent with persistent memory."""
    print("\n🧠 4. Agent with Memory")
    print("=" * 40)

    # Create agent with memory
    memory_agent = Agent(
        name="memory-assistant",
        model="anthropic/claude-3-5-sonnet",
        memory=Memory(),
        system_prompt="You are a personal assistant with memory. Remember important details about our conversations.",
    )

    # Conversation sequence
    conversations = [
        "Hi, I'm John and I work as a software engineer at TechCorp.",
        "I'm working on a Python project using FastAPI.",
        "My favorite programming language is Python, but I'm learning Rust.",
        "What programming languages do I like and where do I work?",
        "Can you help me with my FastAPI project?",
    ]

    for i, message in enumerate(conversations, 1):
        try:
            print(f"\n  Turn {i}: {message}")
            response = await memory_agent.run(message)
            print(f"  Response: {response.content[:150]}...")
        except Exception as e:
            print(f"  ❌ Turn {i} failed: {e}")


# =============================================================================
# 5. AGENT REFLECTION AND SELF-IMPROVEMENT
# =============================================================================


async def demo_agent_reflection():
    """Demonstrate agent reflection and self-improvement."""
    print("\n🪞 5. Agent Reflection and Self-Improvement")
    print("=" * 40)

    reflective_agent = Agent(name="reflective-assistant", model="anthropic/claude-3-5-sonnet", system_prompt="You are a thoughtful assistant that reflects on your responses.")

    # Initial response
    query = "Explain machine learning in simple terms."
    print(f"\n  Query: {query}")

    try:
        # Get initial response
        initial_response = await reflective_agent.run(query)
        print(f"  Initial Response: {initial_response.content[:150]}...")

        # Reflect on the response
        print(f"\n  🤔 Reflecting on response quality...")
        reflection = await reflective_agent.reflect_on_response(user_query=query, agent_response=initial_response.content, level="analytical")
        print(f"  Reflection Score: {reflection.get('overall_score', 'N/A')}")
        print(f"  Key Insights: {reflection.get('insights', [])[:2]}")

        # Generate improved response
        print(f"\n  📈 Generating improved response...")
        improved_response = await reflective_agent.improve_response(
            original_query=query, original_response=initial_response.content, feedback="Make it more beginner-friendly with examples"
        )
        print(f"  Improved Response: {improved_response[:150]}...")

        # Self-evaluation
        print(f"\n  📊 Self-evaluation...")
        evaluation = await reflective_agent.self_evaluate()
        print(f"  Self-evaluation insights: {len(evaluation.get('insights', []))} points")

    except Exception as e:
        print(f"  ❌ Reflection failed: {e}")


# =============================================================================
# 6. MULTI-AGENT WORKFLOW
# =============================================================================


@dataclass
class Task:
    """Simple task structure for multi-agent workflows."""

    id: str
    description: str
    assigned_to: str = None
    status: str = "pending"
    result: str = None


async def demo_multi_agent_workflow():
    """Demonstrate multi-agent workflow coordination."""
    print("\n👥 6. Multi-Agent Workflow")
    print("=" * 40)

    # Create specialized agents
    planner_agent = Agent(name="planner", model="openai/gpt-4o", system_prompt="You are a project planner. Break down complex tasks into steps.")

    coder_agent = Agent(name="coder", model="anthropic/claude-3-5-sonnet", system_prompt="You are a senior developer. Write clean, efficient code.")

    reviewer_agent = Agent(name="reviewer", model="google/gemini-1.5-pro", system_prompt="You are a code reviewer. Provide constructive feedback.")

    # Workflow: Build a simple Python function
    project = "Create a Python function to calculate factorial"

    try:
        # Step 1: Planning
        print(f"\n  📋 Planning Phase:")
        plan_prompt = f"Create a development plan for: {project}. List the key steps."
        plan = await planner_agent.run(plan_prompt)
        print(f"    Plan: {plan.content[:200]}...")

        # Step 2: Implementation
        print(f"\n  💻 Implementation Phase:")
        code_prompt = f"Implement this plan: {plan.content[:300]}... Write the Python code."
        code = await coder_agent.run(code_prompt)
        print(f"    Code: {code.content[:200]}...")

        # Step 3: Review
        print(f"\n  🔍 Review Phase:")
        review_prompt = f"Review this code: {code.content[:500]}... Provide feedback and suggestions."
        review = await reviewer_agent.run(review_prompt)
        print(f"    Review: {review.content[:200]}...")

        print(f"\n  ✅ Multi-agent workflow completed!")

    except Exception as e:
        print(f"  ❌ Workflow failed: {e}")


# =============================================================================
# 7. DURABLE AGENT WITH STATE PERSISTENCE
# =============================================================================


@durable.object
class AgentSession:
    """Durable object to maintain agent session state."""

    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.session_id = session_id
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_preferences = {}
        self.context = {}

    async def add_interaction(self, user_message: str, agent_response: str):
        """Add an interaction to the session history."""
        interaction = {
            "timestamp": "2024-01-01T00:00:00Z",  # Would be actual timestamp
            "user": user_message,
            "agent": agent_response,
        }
        self.conversation_history.append(interaction)
        await self.save()

    async def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences."""
        self.user_preferences.update(preferences)
        await self.save()

    async def get_context_summary(self) -> str:
        """Get a summary of the conversation context."""
        if not self.conversation_history:
            return "No previous conversation."

        recent_interactions = self.conversation_history[-3:]  # Last 3 interactions
        summary = "Recent conversation:\n"
        for interaction in recent_interactions:
            summary += f"User: {interaction['user'][:50]}...\n"
            summary += f"Agent: {interaction['agent'][:50]}...\n"

        return summary


@durable.function
async def create_durable_agent_session(ctx, session_id: str, model: str) -> Dict[str, Any]:
    """Create a durable agent session."""
    session = await ctx.get_object(AgentSession, session_id)

    agent = Agent(name=f"durable-agent-{session_id}", model=model, system_prompt="You are a helpful assistant with persistent memory across sessions.")

    return {"session_id": session_id, "agent_model": model, "status": "created"}


async def demo_durable_agent():
    """Demonstrate durable agent with persistent state."""
    print("\n💾 7. Durable Agent with State Persistence")
    print("=" * 40)

    session_id = "user-session-123"

    try:
        # Create durable session
        print(f"  Creating durable session: {session_id}")
        session_info = await create_durable_agent_session(None, session_id, "anthropic/claude-3-5-sonnet")
        print(f"    ✅ Session created: {session_info}")

        # Simulate conversation with state persistence
        print(f"\n  💬 Simulating persistent conversation:")

        # This would typically be integrated with the actual agent
        # For demo purposes, we'll show the concept
        session = await AgentSession.get_or_create(session_id)

        # Simulate interactions
        await session.add_interaction("Hello, I'm interested in learning Python", "Great! I'd be happy to help you learn Python. What's your programming background?")

        await session.add_interaction("I'm a complete beginner", "Perfect! Let's start with the basics. Python is a great first language because...")

        # Update preferences
        await session.update_preferences({"language": "python", "level": "beginner", "learning_style": "hands-on"})

        # Get context summary
        context = await session.get_context_summary()
        print(f"    Context Summary: {context[:150]}...")

        print(f"    ✅ Durable state maintained across interactions")

    except Exception as e:
        print(f"  ❌ Durable agent demo failed: {e}")


# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================


async def main():
    """Run all agent examples."""
    print("🚀 AGNT5 Agent Examples")
    print("=" * 60)
    print("Demonstrating various agent patterns and capabilities:")
    print("- Basic usage with different providers")
    print("- Tool integration and function calling")
    print("- Multi-provider coordination")
    print("- Memory and context management")
    print("- Reflection and self-improvement")
    print("- Multi-agent workflows")
    print("- Durable state persistence")

    try:
        await demo_basic_agent()
        await demo_agent_with_tools()
        await demo_multi_provider_coordination()
        await demo_agent_with_memory()
        await demo_agent_reflection()
        await demo_multi_agent_workflow()
        await demo_durable_agent()

        print("\n" + "=" * 60)
        print("✨ All agent examples completed successfully!")
        print("📚 Key takeaways:")
        print("  • Use provider/model format for future-proof model selection")
        print("  • Agents can use tools for enhanced capabilities")
        print("  • Multi-provider coordination enables specialized workflows")
        print("  • Memory enables context-aware conversations")
        print("  • Reflection improves response quality over time")
        print("  • Multi-agent workflows handle complex tasks")
        print("  • Durable state ensures persistence across failures")

    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
