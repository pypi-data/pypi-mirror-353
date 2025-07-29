"""
Testing utilities for the AGNT5 SDK.

Provides test helpers, mocks, and fixtures for testing agents,
tools, and workflows in isolation.
"""

from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator
import asyncio
from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager
import json
import logging
from datetime import datetime

from .types import (
    Message,
    MessageRole,
    ToolCall,
    ToolResult,
    ExecutionContext,
    ExecutionState,
)
from .agent import Agent
from .tool import Tool
from .workflow import Workflow
from .context import Context, create_context
from .memory import Memory, InMemoryStore


logger = logging.getLogger(__name__)


class MockLLM:
    """
    Mock LLM for testing agents without real API calls.
    
    Example:
        ```python
        from agnt5.testing import MockLLM, TestAgent
        
        # Create mock LLM with predefined responses
        mock_llm = MockLLM(responses=[
            "Hello! How can I help you?",
            ToolCall(name="search", arguments={"query": "weather"}),
            "The weather is sunny today.",
        ])
        
        # Use in test
        agent = TestAgent("my-agent", llm=mock_llm)
        response = await agent.run("What's the weather?")
        ```
    """
    
    def __init__(
        self,
        responses: Optional[List[Union[str, ToolCall, List[ToolCall]]]] = None,
        default_response: str = "Mock response",
    ):
        """Initialize mock LLM."""
        self.responses = responses or []
        self.default_response = default_response
        self.call_count = 0
        self.call_history: List[Dict[str, Any]] = []
    
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Message:
        """Mock completion method."""
        # Record call
        self.call_history.append({
            "messages": messages,
            "tools": tools,
            "kwargs": kwargs,
            "timestamp": datetime.utcnow(),
        })
        
        # Get response
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            response = self.default_response
        
        self.call_count += 1
        
        # Convert response to Message
        if isinstance(response, str):
            return Message(
                role=MessageRole.ASSISTANT,
                content=response,
            )
        elif isinstance(response, ToolCall):
            return Message(
                role=MessageRole.ASSISTANT,
                content="",
                tool_calls=[response],
            )
        elif isinstance(response, list) and all(isinstance(tc, ToolCall) for tc in response):
            return Message(
                role=MessageRole.ASSISTANT,
                content="",
                tool_calls=response,
            )
        else:
            return Message(
                role=MessageRole.ASSISTANT,
                content=str(response),
            )
    
    def reset(self):
        """Reset the mock."""
        self.call_count = 0
        self.call_history.clear()


class TestAgent(Agent):
    """
    Test-friendly agent with mock LLM support.
    
    Example:
        ```python
        from agnt5.testing import TestAgent
        
        # Create test agent
        agent = TestAgent(
            "test-agent",
            responses=["Hello!", "How are you?"],
        )
        
        # Test conversation
        response1 = await agent.run("Hi")
        assert response1.content == "Hello!"
        
        response2 = await agent.run("What's up?")
        assert response2.content == "How are you?"
        ```
    """
    
    def __init__(
        self,
        name: str,
        *,
        llm: Optional[MockLLM] = None,
        responses: Optional[List[Union[str, ToolCall]]] = None,
        **kwargs,
    ):
        """Initialize test agent."""
        super().__init__(name, **kwargs)
        
        # Set up mock LLM
        if llm:
            self.llm = llm
        else:
            self.llm = MockLLM(responses=responses)
    
    async def _call_llm(
        self,
        messages: List[Dict[str, Any]],
        stream: bool,
    ) -> Message:
        """Override to use mock LLM."""
        return await self.llm.complete(messages, tools=list(self._tools.values()))


class MockTool(Tool):
    """
    Mock tool for testing.
    
    Example:
        ```python
        from agnt5.testing import MockTool
        
        # Create mock tool
        tool = MockTool(
            name="calculator",
            return_value=42,
        )
        
        # Use in tests
        result = await tool.invoke(a=10, b=32)
        assert result == 42
        assert tool.call_count == 1
        assert tool.last_args == {"a": 10, "b": 32}
        ```
    """
    
    def __init__(
        self,
        name: str,
        *,
        return_value: Any = None,
        side_effect: Optional[Callable] = None,
        raises: Optional[Exception] = None,
    ):
        """Initialize mock tool."""
        async def mock_func(**kwargs):
            return None
        
        super().__init__(mock_func, name=name)
        
        self.return_value = return_value
        self.side_effect = side_effect
        self.raises = raises
        self.call_count = 0
        self.call_history: List[Dict[str, Any]] = []
        self.last_args: Optional[Dict[str, Any]] = None
    
    async def invoke(self, **kwargs) -> Any:
        """Mock invoke method."""
        # Record call
        self.call_count += 1
        self.last_args = kwargs
        self.call_history.append({
            "args": kwargs,
            "timestamp": datetime.utcnow(),
        })
        
        # Handle exceptions
        if self.raises:
            raise self.raises
        
        # Handle side effect
        if self.side_effect:
            if asyncio.iscoroutinefunction(self.side_effect):
                return await self.side_effect(**kwargs)
            else:
                return self.side_effect(**kwargs)
        
        # Return configured value
        return self.return_value
    
    def reset(self):
        """Reset the mock."""
        self.call_count = 0
        self.call_history.clear()
        self.last_args = None


class TestWorkflow(Workflow):
    """
    Test-friendly workflow with step tracking.
    
    Example:
        ```python
        from agnt5.testing import TestWorkflow
        
        class MyWorkflow(TestWorkflow):
            async def run(self, data: str) -> str:
                step1 = await self.step("process", lambda: data.upper())
                step2 = await self.step("validate", lambda: len(step1) > 0)
                return step1 if step2 else ""
        
        # Test workflow
        workflow = MyWorkflow("test-workflow")
        result = await workflow.execute("hello")
        
        assert result == "HELLO"
        assert workflow.executed_steps == ["process", "validate"]
        assert workflow.get_step_result("process") == "HELLO"
        ```
    """
    
    def __init__(self, name: str, **kwargs):
        """Initialize test workflow."""
        super().__init__(name, **kwargs)
        self.executed_steps: List[str] = []
        self.step_errors: Dict[str, Exception] = {}
    
    async def step(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Track step execution."""
        self.executed_steps.append(name)
        
        try:
            return await super().step(name, func, *args, **kwargs)
        except Exception as e:
            self.step_errors[name] = e
            raise
    
    def assert_steps_executed(self, expected_steps: List[str]):
        """Assert that specific steps were executed in order."""
        assert self.executed_steps == expected_steps, \
            f"Expected steps {expected_steps}, but got {self.executed_steps}"
    
    def assert_step_succeeded(self, step_name: str):
        """Assert that a step succeeded."""
        assert step_name in self.executed_steps, \
            f"Step '{step_name}' was not executed"
        assert step_name not in self.step_errors, \
            f"Step '{step_name}' failed with error: {self.step_errors.get(step_name)}"


@asynccontextmanager
async def test_context(
    name: str = "test",
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for test contexts.
    
    Example:
        ```python
        from agnt5.testing import test_context
        
        async with test_context("my-test") as ctx:
            ctx.set("user_id", "test-user")
            
            agent = Agent("test-agent")
            response = await agent.run("Hello")
        ```
    """
    async with create_context(name, metadata) as ctx:
        # Set up test context
        ctx.metadata["test"] = True
        ctx.metadata["test_started_at"] = datetime.utcnow()
        
        yield ctx
        
        # Clean up
        ctx.metadata["test_completed_at"] = datetime.utcnow()


class MemoryFixture:
    """
    Test fixture for memory operations.
    
    Example:
        ```python
        from agnt5.testing import MemoryFixture
        
        # Create fixture with test data
        memory_fixture = MemoryFixture()
        memory = await memory_fixture.with_entries([
            "User's name is Alice",
            "User likes Python",
            {"type": "preference", "value": "dark_mode"},
        ])
        
        # Use in tests
        results = await memory.search("name")
        assert len(results) == 1
        assert "Alice" in results[0].content
        ```
    """
    
    def __init__(self):
        """Initialize memory fixture."""
        self.memory = Memory(store=InMemoryStore())
    
    async def with_entries(self, entries: List[Any]) -> Memory:
        """Create memory with predefined entries."""
        for entry in entries:
            await self.memory.add(entry)
        return self.memory
    
    async def with_messages(self, messages: List[Union[str, Message]]) -> Memory:
        """Create memory with message history."""
        for msg in messages:
            if isinstance(msg, str):
                msg = Message(
                    role=MessageRole.USER,
                    content=msg,
                )
            await self.memory.add(msg)
        return self.memory


def assert_tool_called(tool: Union[Tool, MockTool], times: int = 1):
    """
    Assert that a tool was called a specific number of times.
    
    Example:
        ```python
        from agnt5.testing import MockTool, assert_tool_called
        
        tool = MockTool("search", return_value="results")
        await tool.invoke(query="test")
        
        assert_tool_called(tool, times=1)
        ```
    """
    if isinstance(tool, MockTool):
        assert tool.call_count == times, \
            f"Expected tool '{tool.name}' to be called {times} times, but was called {tool.call_count} times"
    else:
        logger.warning("assert_tool_called only works with MockTool instances")


def assert_message_content(message: Message, expected_content: str):
    """
    Assert that a message contains expected content.
    
    Example:
        ```python
        from agnt5.testing import assert_message_content
        
        message = Message(role=MessageRole.ASSISTANT, content="Hello, world!")
        assert_message_content(message, "Hello")
        ```
    """
    assert expected_content in message.content, \
        f"Expected message to contain '{expected_content}', but got '{message.content}'"


async def run_until_complete(
    agent: Agent,
    max_turns: int = 10,
    stop_on: Optional[Callable[[Message], bool]] = None,
) -> List[Message]:
    """
    Run agent conversation until completion or max turns.
    
    Example:
        ```python
        from agnt5.testing import run_until_complete
        
        agent = TestAgent("assistant")
        
        # Run until agent says "goodbye"
        messages = await run_until_complete(
            agent,
            stop_on=lambda msg: "goodbye" in msg.content.lower()
        )
        ```
    """
    messages = []
    
    for i in range(max_turns):
        # Create user message
        user_msg = Message(
            role=MessageRole.USER,
            content=f"Message {i+1}",
        )
        
        # Get agent response
        response = await agent.run(user_msg)
        messages.append(response)
        
        # Check stop condition
        if stop_on and stop_on(response):
            break
    
    return messages