# AGNT5 SDK Examples

This directory contains comprehensive examples demonstrating the capabilities of the AGNT5 Python SDK. The examples are organized by functionality and complexity, from basic usage to advanced durable workflows.

## 📁 Example Categories

### 🤖 Agent Examples
**File:** `agent_examples.py`

Demonstrates various agent patterns and capabilities:

- **Basic Agent Usage**: Simple agents with different LLM providers
- **Agent with Tools**: Function calling and tool integration
- **Multi-Provider Coordination**: Agents from different providers working together
- **Agent with Memory**: Persistent conversation context
- **Agent Reflection**: Self-evaluation and improvement
- **Multi-Agent Workflows**: Collaborative task completion
- **Durable Agents**: State persistence across failures

```bash
python examples/agent_examples.py
```

### 📋 Task Examples
**File:** `task_examples.py`

Shows structured task creation and execution:

- **Basic Tasks**: String and JSON output formatting
- **JSON Extraction**: Structured data extraction from text
- **Pydantic Models**: Type-safe structured output
- **String Processing**: Text generation and transformation
- **Task Chaining**: Complex workflows with multiple tasks
- **Error Handling**: Robust validation and retry logic
- **Agent-Task Integration**: Combining agents with tasks
- **Durable Tasks**: Persistent task workflows

```bash
python examples/task_examples.py
```

### 🏗️ Durable Examples

#### Order Processing
**File:** `order_processing.py`

Complete e-commerce order processing workflow:
- Order validation with external services
- Payment processing with retry logic
- Shipment creation and tracking
- Customer notifications
- State persistence and recovery

#### Shopping Cart
**File:** `shopping_cart_example.py`

Durable object example with shopping cart:
- User-specific cart state
- Concurrent access handling
- Persistent state across restarts
- Checkout workflow integration

#### Enhanced APIs
**File:** `updated_apis_demo.py`

Integration between high-level APIs and durable primitives:
- Context API with durable state
- Workflow execution as durable flows
- Seamless API integration

### 🔧 Model Management Examples

#### Simple Model Usage
**File:** `simple_model_usage.py`

Demonstrates the clean provider/model format:
- Explicit provider/model syntax
- Auto-detection fallback
- Future-proof model handling
- Multiple provider usage

#### Dynamic Model Usage
**File:** `dynamic_model_usage.py`

Advanced model registry features:
- Capability-based model selection
- Configuration-driven management
- Runtime model discovery

## 🚀 Quick Start

### Prerequisites

1. **Install Dependencies**:
```bash
pip install agnt5
# Optional: Install provider-specific libraries
pip install anthropic openai google-generativeai
```

2. **Set API Keys**:
```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export MISTRAL_API_KEY="your-key-here"
export TOGETHER_API_KEY="your-key-here"
```

### Running Examples

Most examples can be run directly and will gracefully handle missing API keys:

```bash
# Basic agent usage
python examples/agent_examples.py

# Task demonstrations  
python examples/task_examples.py

# Model management
python examples/simple_model_usage.py

# Durable workflows
python examples/order_processing.py
python examples/shopping_cart_example.py
```

## 📚 Example Patterns

### Basic Agent Creation

```python
from agnt5 import Agent

# Explicit provider/model (recommended)
agent = Agent(
    name="assistant",
    model="anthropic/claude-3-5-sonnet",
    system_prompt="You are a helpful assistant."
)

# Auto-detection
agent = Agent(
    name="assistant", 
    model="gpt-4o",  # Auto-detects OpenAI
    system_prompt="You are a helpful assistant."
)
```

### Tool Integration

```python
from agnt5 import Agent, tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

agent = Agent(
    name="research-agent",
    model="anthropic/claude-3-5-sonnet",
    tools=[search_web],
    system_prompt="Use tools to answer questions."
)
```

### Task Creation

```python
from agnt5 import task, json_extraction_task, pydantic_task
from agnt5.task import OutputFormat
from pydantic import BaseModel

# Basic task
@task(output_format=OutputFormat.STRING)
async def summarize_text(text: str) -> str:
    agent = Agent(model="anthropic/claude-3-5-sonnet")
    response = await agent.run(f"Summarize: {text}")
    return response.content

# JSON extraction
@json_extraction_task
async def extract_data(text: str) -> dict:
    agent = Agent(model="openai/gpt-4o")
    response = await agent.run(f"Extract structured data: {text}")
    return response.content

# Pydantic validation
class Person(BaseModel):
    name: str
    age: int

@pydantic_task(model=Person)
async def extract_person(text: str) -> Person:
    agent = Agent(model="google/gemini-1.5-pro")
    response = await agent.run(f"Extract person info: {text}")
    return response.content
```

### Durable Workflows

```python
from agnt5.durable import durable, DurableContext

@durable.function
async def process_order(ctx: DurableContext, order_data: dict) -> dict:
    # Validate order
    validation = await ctx.call("validation_service", "validate", order_data)
    await ctx.state.set("validated", True)
    
    # Process payment
    payment = await ctx.call("payment_service", "charge", order_data)
    await ctx.state.set("payment_id", payment["id"])
    
    # Create shipment
    shipment = await ctx.call("shipping_service", "create", order_data)
    
    return {
        "order_id": order_data["id"],
        "status": "completed",
        "payment_id": payment["id"],
        "tracking": shipment["tracking_number"]
    }

@durable.object
class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences = {}
        self.conversation_history = []
    
    async def update_preferences(self, prefs: dict):
        self.preferences.update(prefs)
        await self.save()
```

## 🔍 Example Details

### Agent Examples (`agent_examples.py`)

1. **Basic Agent Usage**: Different LLM providers (Claude, GPT, Gemini)
2. **Agent with Tools**: Web search, calculator, weather tools
3. **Multi-Provider Coordination**: Research → Analysis → Creative writing pipeline
4. **Agent with Memory**: Persistent conversation context
5. **Agent Reflection**: Self-evaluation and response improvement
6. **Multi-Agent Workflow**: Planning → Coding → Review workflow
7. **Durable Agent**: Session state persistence with durable objects

### Task Examples (`task_examples.py`)

1. **Basic Tasks**: Text summarization and sentiment analysis
2. **JSON Extraction**: Contact info and fact extraction
3. **Pydantic Models**: Product reviews and meeting agendas
4. **String Processing**: Creative writing and concept explanation
5. **Task Chaining**: Research → Summary → Analysis pipeline
6. **Error Handling**: Robust validation and retry logic
7. **Agent-Task Integration**: Orchestrated content creation
8. **Durable Tasks**: Persistent multi-stage workflows

### Durable Examples

#### Order Processing (`order_processing.py`)
- Complete e-commerce workflow
- External service integration
- State persistence and recovery
- Error handling and retries

#### Shopping Cart (`shopping_cart_example.py`)
- Durable object patterns
- Concurrent access handling
- User-specific state management
- Integration with external services

## 🛠️ Development Tips

### Running Without API Keys

Most examples include fallback modes and mock implementations:

```python
# Examples will show mock responses if API keys are missing
python examples/agent_examples.py
# Output: Using mock LLM for testing
```

### Debugging

Enable debug logging to see detailed execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Customization

Examples are designed to be easily customizable:

1. **Change Models**: Update model strings in agent creation
2. **Add Tools**: Create new `@tool` functions and add to agents
3. **Modify Prompts**: Update system prompts for different behaviors
4. **Extend Tasks**: Add new task functions with different output formats

### Production Usage

For production deployment:

1. **Set Proper API Keys**: Use environment variables or secret management
2. **Enable Durable Runtime**: Deploy with AGNT5 runtime for full durability
3. **Add Error Handling**: Implement comprehensive error handling
4. **Monitor Performance**: Use built-in tracing and metrics

## 📖 Additional Resources

- **[Simple Model Usage Guide](SIMPLE_MODEL_USAGE.md)**: Clean provider/model format
- **[SDK Documentation](../README.md)**: Complete SDK documentation
- **[Durable Runtime](../../core/durable-runtime/README.md)**: Runtime deployment guide

## 🤝 Contributing

When adding new examples:

1. **Follow Patterns**: Use consistent structure and error handling
2. **Add Documentation**: Include clear docstrings and comments
3. **Test Thoroughly**: Ensure examples work with and without API keys
4. **Update README**: Add new examples to this README

## 📝 License

These examples are part of the AGNT5 Platform and are subject to the same license terms.