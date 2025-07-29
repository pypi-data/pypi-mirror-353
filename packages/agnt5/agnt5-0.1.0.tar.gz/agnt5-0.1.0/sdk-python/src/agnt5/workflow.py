"""
Workflow implementation for the AGNT5 SDK.

Workflows orchestrate complex multi-step processes with durability guarantees.
They support parallel execution, error handling, and state management.
"""

from typing import (
    Any, Callable, Dict, List, Optional, Union, TypeVar, Generic,
    AsyncIterator, Tuple, Set
)
import asyncio
from dataclasses import dataclass, field
import inspect
import logging
from datetime import datetime
import json

from .types import (
    WorkflowConfig,
    ExecutionContext,
    ExecutionState,
    DurablePromise,
)
from .context import Context, get_context
from .durable import durable, DurableContext
# from .agent import Agent  # Commented out to avoid dependency issues
# from .tool import Tool    # Commented out to avoid dependency issues


logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class Step:
    """Represents a step in a workflow."""
    name: str
    func: Callable
    args: Tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    result: Optional[Any] = None
    error: Optional[Exception] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0


class Workflow:
    """
    Orchestrates complex multi-step processes with durability.
    
    Example:
        ```python
        from agnt5 import Workflow, Agent
        
        class DataProcessingWorkflow(Workflow):
            '''Process data through multiple stages.'''
            
            async def run(self, data: List[str]) -> Dict[str, Any]:
                # Step 1: Validate data
                validated = await self.step("validate", self.validate_data, data)
                
                # Step 2: Process in parallel
                results = await self.parallel([
                    ("analyze", self.analyze_data, validated),
                    ("transform", self.transform_data, validated),
                ])
                
                # Step 3: Combine results
                final = await self.step("combine", self.combine_results, results)
                
                return final
            
            async def validate_data(self, data: List[str]) -> List[str]:
                # Validation logic
                return [d for d in data if d]
            
            async def analyze_data(self, data: List[str]) -> Dict[str, Any]:
                # Analysis logic
                return {"count": len(data), "unique": len(set(data))}
            
            async def transform_data(self, data: List[str]) -> List[str]:
                # Transformation logic
                return [d.upper() for d in data]
            
            async def combine_results(self, results: List[Any]) -> Dict[str, Any]:
                # Combine parallel results
                return {
                    "analysis": results[0],
                    "transformed": results[1],
                }
        
        # Use the workflow
        workflow = DataProcessingWorkflow(name="data-processor")
        result = await workflow.execute(["hello", "world"])
        ```
    """
    
    def __init__(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        version: str = "1.0.0",
        config: Optional[WorkflowConfig] = None,
    ):
        """Initialize a Workflow."""
        if config:
            self.config = config
        else:
            self.config = WorkflowConfig(
                name=name,
                description=description or inspect.getdoc(self.__class__) or f"Workflow: {name}",
                version=version,
            )
        
        self._steps: Dict[str, Step] = {}
        self._execution_context: Optional[ExecutionContext] = None
        self._agents: Dict[str, Agent] = {}
        self._tools: Dict[str, Tool] = {}
    
    @property
    def name(self) -> str:
        return self.config.name
    
    def add_agent(self, agent) -> None:
        """Add an agent to the workflow."""
        self._agents[agent.name] = agent
    
    def add_tool(self, tool) -> None:
        """Add a tool to the workflow."""
        self._tools[tool.name] = tool
    
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the workflow.
        
        Args:
            *args: Positional arguments for the run method
            **kwargs: Keyword arguments for the run method
            
        Returns:
            Workflow result
        """
        ctx = get_context()
        
        # Create execution context
        self._execution_context = ExecutionContext(
            execution_id=ctx.execution_id,
            workflow_id=self.name,
            state=ExecutionState.RUNNING,
            started_at=datetime.utcnow(),
        )
        
        try:
            # Execute with durability if enabled (use durable flow)
            if self.config.enable_durability:
                result = await self._execute_as_durable_flow(*args, **kwargs)
            else:
                result = await self._execute_direct(*args, **kwargs)
            
            # Mark as completed
            self._execution_context.state = ExecutionState.COMPLETED
            self._execution_context.completed_at = datetime.utcnow()
            
            return result
            
        except Exception as e:
            # Mark as failed
            self._execution_context.state = ExecutionState.FAILED
            self._execution_context.completed_at = datetime.utcnow()
            self._execution_context.last_error = str(e)
            raise
    
    async def _execute_as_durable_flow(self, *args, **kwargs) -> Any:
        """
        Execute as a durable flow with comprehensive state management and recovery.
        
        This creates a sophisticated durable flow that provides:
        - Automatic checkpointing at configurable intervals
        - Step-by-step state tracking and recovery
        - Parallel execution coordination
        - Tool and agent integration
        - Comprehensive error handling and retry logic
        """
        @durable.flow(
            name=f"workflow_{self.name}",
            checkpoint_interval=getattr(self.config, 'checkpoint_interval', 1),
            max_retries=getattr(self.config, 'max_retries', 3),
            max_concurrent_steps=getattr(self.config, 'max_parallel_steps', 5),
            deterministic=True,
            timeout=getattr(self.config, 'timeout', None),
        )
        async def comprehensive_workflow_flow(ctx: DurableContext, *flow_args, **flow_kwargs) -> Any:
            # Initialize comprehensive workflow state
            workflow_metadata = {
                "workflow_name": self.name,
                "workflow_version": getattr(self.config, 'version', '1.0.0'),
                "execution_id": ctx.execution_id,
                "started_at": datetime.utcnow().isoformat(),
                "input_args": flow_args,
                "input_kwargs": flow_kwargs,
                "config": {
                    "checkpoint_interval": getattr(self.config, 'checkpoint_interval', 1),
                    "max_retries": getattr(self.config, 'max_retries', 3),
                    "max_parallel_steps": getattr(self.config, 'max_parallel_steps', 5),
                    "enable_durability": getattr(self.config, 'enable_durability', True),
                }
            }
            
            await ctx.state.set("workflow_metadata", workflow_metadata)
            await ctx.state.set("current_step", 0)
            await ctx.state.set("completed_steps", [])
            await ctx.state.set("step_results", {})
            await ctx.state.set("workflow_status", "running")
            
            # Create enhanced workflow context
            workflow_ctx = EnhancedWorkflowDurableContext(ctx, self)
            
            try:
                # Execute the workflow with comprehensive tracking
                result = await self._run_with_enhanced_context(workflow_ctx, *flow_args, **flow_kwargs)
                
                # Mark workflow as completed
                workflow_metadata["completed_at"] = datetime.utcnow().isoformat()
                workflow_metadata["status"] = "completed"
                workflow_metadata["result"] = result
                
                await ctx.state.set("workflow_metadata", workflow_metadata)
                await ctx.state.set("workflow_status", "completed")
                await ctx.state.set("final_result", result)
                
                logger.info(f"Workflow '{self.name}' completed successfully")
                return result
                
            except Exception as e:
                # Handle workflow failure with comprehensive error tracking
                workflow_metadata["failed_at"] = datetime.utcnow().isoformat()
                workflow_metadata["status"] = "failed"
                workflow_metadata["error"] = str(e)
                workflow_metadata["error_type"] = type(e).__name__
                
                await ctx.state.set("workflow_metadata", workflow_metadata)
                await ctx.state.set("workflow_status", "failed")
                await ctx.state.set("workflow_error", {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "failed_at": datetime.utcnow().isoformat(),
                })
                
                logger.error(f"Workflow '{self.name}' failed: {e}")
                raise
        
        # Execute the comprehensive durable flow
        return await comprehensive_workflow_flow(*args, **kwargs)
    
    @durable.function
    async def _execute_durable(self, *args, **kwargs) -> Any:
        """Execute with durability guarantees (legacy method)."""
        return await self.run(*args, **kwargs)
    
    async def _execute_direct(self, *args, **kwargs) -> Any:
        """Direct execution without durability."""
        return await self.run(*args, **kwargs)
    
    async def run(self, *args, **kwargs) -> Any:
        """
        Main workflow logic. Override this in subclasses.
        
        Args:
            *args: Workflow arguments
            **kwargs: Workflow keyword arguments
            
        Returns:
            Workflow result
        """
        raise NotImplementedError("Subclasses must implement the run method")
    
    async def step(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a workflow step.
        
        Args:
            name: Step name
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Step result
        """
        # Create step
        step = Step(
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
        )
        
        # Store step
        self._steps[name] = step
        
        # Log step start
        logger.info(f"Starting step '{name}' in workflow '{self.name}'")
        step.started_at = datetime.utcnow()
        
        try:
            # Execute step
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
            
            # Store result
            step.result = result
            step.completed_at = datetime.utcnow()
            
            # Checkpoint if configured
            if self.config.checkpoint_on_step:
                await self._checkpoint()
            
            logger.info(f"Completed step '{name}' in workflow '{self.name}'")
            return result
            
        except Exception as e:
            # Store error
            step.error = e
            step.completed_at = datetime.utcnow()
            
            logger.error(f"Step '{name}' failed in workflow '{self.name}': {e}")
            
            # Retry if configured
            if step.retries < self.config.get("max_retries", 3):
                step.retries += 1
                logger.info(f"Retrying step '{name}' (attempt {step.retries})")
                return await self.step(name, func, *args, **kwargs)
            
            raise
    
    async def parallel(
        self,
        tasks: List[Tuple[str, Callable, ...]],
    ) -> List[Any]:
        """
        Execute multiple steps in parallel.
        
        Args:
            tasks: List of (name, func, *args) tuples
            
        Returns:
            List of results in the same order as tasks
        """
        # Create tasks
        async_tasks = []
        
        for task_spec in tasks:
            if len(task_spec) == 2:
                name, func = task_spec
                args = ()
            else:
                name, func, *args = task_spec
            
            # Create coroutine
            coro = self.step(name, func, *args)
            async_tasks.append(coro)
        
        # Execute in parallel with concurrency limit
        if self.config.max_parallel_steps:
            results = []
            for i in range(0, len(async_tasks), self.config.max_parallel_steps):
                batch = async_tasks[i:i + self.config.max_parallel_steps]
                batch_results = await asyncio.gather(*batch)
                results.extend(batch_results)
            return results
        else:
            return await asyncio.gather(*async_tasks)
    
    async def call_agent(
        self,
        agent_name: str,
        message: str,
        **kwargs,
    ) -> Any:
        """
        Call an agent within the workflow.
        
        Args:
            agent_name: Name of the agent
            message: Message to send
            **kwargs: Additional arguments
            
        Returns:
            Agent response
        """
        agent = self._agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in workflow")
        
        return await agent.run(message, **kwargs)
    
    async def call_tool(
        self,
        tool_name: str,
        **kwargs,
    ) -> Any:
        """
        Call a tool within the workflow.
        
        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments
            
        Returns:
            Tool result
        """
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in workflow")
        
        return await tool.invoke(**kwargs)
    
    async def wait(self, seconds: float) -> None:
        """Wait for a specified duration."""
        await asyncio.sleep(seconds)
    
    async def _checkpoint(self) -> None:
        """Save workflow state checkpoint."""
        if not self._execution_context:
            return
        
        checkpoint_data = {
            "steps": {
                name: {
                    "result": step.result,
                    "error": str(step.error) if step.error else None,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "retries": step.retries,
                }
                for name, step in self._steps.items()
            },
        }
        
        self._execution_context.checkpoint_data = checkpoint_data
        self._execution_context.last_checkpoint = datetime.utcnow()
        
        # TODO: Persist checkpoint to durable storage
    
    def get_step_result(self, name: str) -> Optional[Any]:
        """Get the result of a completed step."""
        step = self._steps.get(name)
        if step and step.result is not None:
            return step.result
        return None
    
    def get_execution_context(self) -> Optional[ExecutionContext]:
        """Get the current execution context."""
        return self._execution_context
    
    async def save_state(self) -> Dict[str, Any]:
        """Save workflow state for persistence."""
        return {
            "config": self.config.__dict__,
            "execution_context": self._execution_context.__dict__ if self._execution_context else None,
            "steps": {
                name: {
                    "name": step.name,
                    "result": step.result,
                    "error": str(step.error) if step.error else None,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "retries": step.retries,
                }
                for name, step in self._steps.items()
            },
        }
    
    async def load_state(self, state: Dict[str, Any]) -> None:
        """Load workflow state from persistence."""
        # Restore execution context
        if state.get("execution_context"):
            ctx_data = state["execution_context"]
            self._execution_context = ExecutionContext(**ctx_data)
        
        # Note: Step results would need to be restored based on the workflow's
        # specific implementation and replay logic


def workflow(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "1.0.0",
    enable_durability: bool = True,
) -> Union[Workflow, Callable]:
    """
    Decorator to create a workflow from a function.
    
    Example:
        ```python
        @workflow
        async def process_order(order_id: str) -> Dict[str, Any]:
            '''Process an order through multiple stages.'''
            # Workflow logic
            return {"status": "completed", "order_id": order_id}
        ```
    """
    def decorator(f: Callable) -> Workflow:
        # Create a workflow class from the function
        class FunctionWorkflow(Workflow):
            async def run(self, *args, **kwargs):
                return await f(*args, **kwargs)
        
        # Create instance
        workflow_name = name or f.__name__
        workflow_desc = description or inspect.getdoc(f) or f"Workflow: {workflow_name}"
        
        config = WorkflowConfig(
            name=workflow_name,
            description=workflow_desc,
            version=version,
            enable_durability=enable_durability,
        )
        
        return FunctionWorkflow(name=workflow_name, config=config)
    
    if func is None:
        # Called with arguments: @workflow(name="...", ...)
        return decorator
    else:
        # Called without arguments: @workflow
        return decorator(func)


class WorkflowDurableContext:
    """
    Bridge between Workflow and DurableContext to provide workflow-specific APIs.
    
    This class wraps a DurableContext and adds workflow-specific functionality
    like step tracking, parallel execution, and agent/tool integration.
    """
    
    def __init__(self, durable_ctx: DurableContext, workflow: Workflow):
        self.durable_ctx = durable_ctx
        self.workflow = workflow
        self.workflow._durable_context = durable_ctx
    
    async def call(self, service: str, method: str, *args, **kwargs) -> Any:
        """Make a durable service call."""
        return await self.durable_ctx.call(service, method, *args, **kwargs)
    
    async def sleep(self, seconds: float) -> None:
        """Durable sleep."""
        await self.durable_ctx.sleep(seconds)
    
    async def get_object(self, object_class, object_id: str):
        """Get a durable object."""
        return await self.durable_ctx.get_object(object_class, object_id)
    
    @property
    def state(self):
        """Access durable state."""
        return self.durable_ctx.state
    
    @property
    def execution_id(self) -> str:
        """Get execution ID."""
        return self.durable_ctx.execution_id
    
    async def step(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute a workflow step with durable state tracking."""
        return await self.workflow.step(name, func, *args, **kwargs)
    
    async def parallel(self, tasks: List[Tuple[str, Callable, ...]]) -> List[Any]:
        """Execute multiple steps in parallel with durable state tracking."""
        return await self.workflow.parallel(tasks)
    
    async def call_agent(self, agent_name: str, message: str, **kwargs) -> Any:
        """Call an agent within the workflow."""
        return await self.workflow.call_agent(agent_name, message, **kwargs)
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a tool within the workflow."""
        return await self.workflow.call_tool(tool_name, **kwargs)


# Add method to Workflow class for durable context execution
async def _run_with_durable_context(self, ctx: WorkflowDurableContext, *args, **kwargs) -> Any:
    """
    Execute the workflow run method with a durable context.
    
    This method replaces the original run method when executing as a durable flow.
    """
    return await self.run(*args, **kwargs)

# Enhanced method for Workflow class durable context execution
async def _run_with_enhanced_context(self, ctx, *args, **kwargs) -> Any:
    """
    Execute the workflow run method with an enhanced durable context.
    
    This method provides the workflow with full access to durable primitives
    and comprehensive state management.
    """
    # Store the enhanced context for use in step methods
    self._enhanced_context = ctx
    
    try:
        # Execute the workflow run method with enhanced context
        result = await self.run(*args, **kwargs)
        return result
    finally:
        # Clean up context reference
        if hasattr(self, '_enhanced_context'):
            delattr(self, '_enhanced_context')

# Monkey patch the enhanced method onto the Workflow class
Workflow._run_with_enhanced_context = _run_with_enhanced_context


class EnhancedWorkflowDurableContext:
    """
    Enhanced bridge between Workflow and DurableContext with advanced features.
    
    This context provides:
    - Comprehensive step tracking and state management
    - Advanced parallel execution with concurrency control
    - Integrated agent and tool management
    - Automatic checkpointing and recovery
    - Performance monitoring and metrics
    - Error handling and retry coordination
    """
    
    def __init__(self, durable_ctx: DurableContext, workflow):
        self.durable_ctx = durable_ctx
        self.workflow = workflow
        self.workflow._durable_context = durable_ctx
        self._step_counter = 0
        self._parallel_execution_slots = getattr(workflow.config, 'max_parallel_steps', 5)
    
    async def call(self, service: str, method: str, *args, **kwargs) -> Any:
        """Make a durable service call with workflow integration."""
        # Track service call in workflow state
        call_id = f"service_call_{self._step_counter}"
        self._step_counter += 1
        
        await self.durable_ctx.state.set(f"call_{call_id}", {
            "service": service,
            "method": method,
            "args": args,
            "kwargs": kwargs,
            "started_at": datetime.utcnow().isoformat(),
        })
        
        try:
            result = await self.durable_ctx.call(service, method, *args, **kwargs)
            await self.durable_ctx.state.set(f"call_{call_id}_result", {
                "result": result,
                "completed_at": datetime.utcnow().isoformat(),
                "status": "success",
            })
            return result
        except Exception as e:
            await self.durable_ctx.state.set(f"call_{call_id}_result", {
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat(),
                "status": "failed",
            })
            raise
    
    async def sleep(self, seconds: float) -> None:
        """Durable sleep with workflow state tracking."""
        sleep_id = f"sleep_{self._step_counter}"
        self._step_counter += 1
        
        await self.durable_ctx.state.set(f"sleep_{sleep_id}", {
            "duration": seconds,
            "started_at": datetime.utcnow().isoformat(),
        })
        
        await self.durable_ctx.sleep(seconds)
        
        await self.durable_ctx.state.set(f"sleep_{sleep_id}_completed", {
            "completed_at": datetime.utcnow().isoformat(),
        })
    
    async def get_object(self, object_class, object_id: str):
        """Get a durable object with workflow integration."""
        # Track object access
        access_id = f"object_access_{self._step_counter}"
        self._step_counter += 1
        
        await self.durable_ctx.state.set(f"object_{access_id}", {
            "object_class": object_class.__name__,
            "object_id": object_id,
            "accessed_at": datetime.utcnow().isoformat(),
        })
        
        return await self.durable_ctx.get_object(object_class, object_id)
    
    @property
    def state(self):
        """Access durable state with workflow enhancements."""
        return self.durable_ctx.state
    
    @property
    def execution_id(self) -> str:
        """Get execution ID."""
        return self.durable_ctx.execution_id
    
    async def step(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute a workflow step with comprehensive durable state tracking."""
        step_start_time = datetime.utcnow()
        
        # Update step tracking
        current_step = await self.state.get("current_step", 0)
        current_step += 1
        await self.state.set("current_step", current_step)
        
        # Store step metadata
        step_metadata = {
            "step_number": current_step,
            "step_name": name,
            "function_name": func.__name__ if hasattr(func, '__name__') else str(func),
            "started_at": step_start_time.isoformat(),
            "args": args,
            "kwargs": kwargs,
        }
        await self.state.set(f"step_{current_step}_metadata", step_metadata)
        
        try:
            # Execute the step through the workflow
            result = await self.workflow.step(name, func, *args, **kwargs)
            
            # Update completion tracking
            completed_steps = await self.state.get("completed_steps", [])
            completed_steps.append(name)
            await self.state.set("completed_steps", completed_steps)
            
            # Store step result
            step_results = await self.state.get("step_results", {})
            step_results[name] = result
            await self.state.set("step_results", step_results)
            
            # Update step completion metadata
            step_metadata["completed_at"] = datetime.utcnow().isoformat()
            step_metadata["duration_seconds"] = (datetime.utcnow() - step_start_time).total_seconds()
            step_metadata["status"] = "completed"
            await self.state.set(f"step_{current_step}_metadata", step_metadata)
            
            return result
            
        except Exception as e:
            # Track step failure
            step_metadata["failed_at"] = datetime.utcnow().isoformat()
            step_metadata["duration_seconds"] = (datetime.utcnow() - step_start_time).total_seconds()
            step_metadata["status"] = "failed"
            step_metadata["error"] = str(e)
            await self.state.set(f"step_{current_step}_metadata", step_metadata)
            raise
    
    async def parallel(self, tasks: List[Tuple[str, Callable, ...]]) -> List[Any]:
        """Execute multiple steps in parallel with advanced coordination."""
        parallel_execution_id = f"parallel_{self._step_counter}"
        self._step_counter += 1
        
        # Track parallel execution start
        parallel_metadata = {
            "execution_id": parallel_execution_id,
            "task_count": len(tasks),
            "started_at": datetime.utcnow().isoformat(),
            "tasks": [
                {
                    "name": task[0] if len(task) > 0 else f"task_{i}",
                    "function": task[1].__name__ if len(task) > 1 and hasattr(task[1], '__name__') else "unknown",
                    "args_count": len(task) - 2 if len(task) > 2 else 0,
                }
                for i, task in enumerate(tasks)
            ]
        }
        await self.state.set(f"parallel_{parallel_execution_id}", parallel_metadata)
        
        try:
            # Execute with concurrency control
            results = await self.workflow.parallel(tasks)
            
            # Track successful completion
            parallel_metadata["completed_at"] = datetime.utcnow().isoformat()
            parallel_metadata["duration_seconds"] = (
                datetime.utcnow() - datetime.fromisoformat(parallel_metadata["started_at"])
            ).total_seconds()
            parallel_metadata["status"] = "completed"
            parallel_metadata["results_count"] = len(results)
            
            await self.state.set(f"parallel_{parallel_execution_id}", parallel_metadata)
            return results
            
        except Exception as e:
            # Track parallel execution failure
            parallel_metadata["failed_at"] = datetime.utcnow().isoformat()
            parallel_metadata["duration_seconds"] = (
                datetime.utcnow() - datetime.fromisoformat(parallel_metadata["started_at"])
            ).total_seconds()
            parallel_metadata["status"] = "failed"
            parallel_metadata["error"] = str(e)
            
            await self.state.set(f"parallel_{parallel_execution_id}", parallel_metadata)
            raise
    
    async def call_agent(self, agent_name: str, message: str, **kwargs) -> Any:
        """Call an agent within the workflow with state tracking."""
        agent_call_id = f"agent_call_{self._step_counter}"
        self._step_counter += 1
        
        await self.state.set(f"agent_call_{agent_call_id}", {
            "agent_name": agent_name,
            "message": message,
            "kwargs": kwargs,
            "started_at": datetime.utcnow().isoformat(),
        })
        
        try:
            result = await self.workflow.call_agent(agent_name, message, **kwargs)
            await self.state.set(f"agent_call_{agent_call_id}_result", {
                "result": result,
                "completed_at": datetime.utcnow().isoformat(),
            })
            return result
        except Exception as e:
            await self.state.set(f"agent_call_{agent_call_id}_result", {
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat(),
            })
            raise
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a tool within the workflow with enhanced durability."""
        tool_call_id = f"tool_call_{self._step_counter}"
        self._step_counter += 1
        
        await self.state.set(f"tool_call_{tool_call_id}", {
            "tool_name": tool_name,
            "kwargs": kwargs,
            "started_at": datetime.utcnow().isoformat(),
        })
        
        try:
            # Use durable tool execution if available
            result = await self.workflow.call_tool(tool_name, **kwargs)
            await self.state.set(f"tool_call_{tool_call_id}_result", {
                "result": result,
                "completed_at": datetime.utcnow().isoformat(),
            })
            return result
        except Exception as e:
            await self.state.set(f"tool_call_{tool_call_id}_result", {
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat(),
            })
            raise
    
    async def get_workflow_progress(self) -> Dict[str, Any]:
        """Get comprehensive workflow progress information."""
        return {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow.name,
            "current_step": await self.state.get("current_step", 0),
            "completed_steps": await self.state.get("completed_steps", []),
            "workflow_status": await self.state.get("workflow_status", "unknown"),
            "step_results": await self.state.get("step_results", {}),
            "workflow_metadata": await self.state.get("workflow_metadata", {}),
        }


class WorkflowDurableContext(EnhancedWorkflowDurableContext):
    """
    Backward compatibility alias for the enhanced workflow context.
    
    This ensures existing code continues to work while providing
    access to all the new enhanced features.
    """
    pass


# Monkey patch the method onto the Workflow class
Workflow._run_with_durable_context = _run_with_durable_context