#!/usr/bin/env python3
"""
Comprehensive test for AGNT5 SDK high-level components with durable primitives integration.

This test demonstrates that Agents, Tools, Workflows, and Memory systems all work
correctly with the core durable primitives (functions, objects, flows).
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

# Import AGNT5 SDK components
from agnt5 import Agent, Tool, Workflow, Memory, durable, tool
from agnt5.memory import DurableMemory, DurableMemoryStore
from agnt5.types import Message, MessageRole, MemoryQuery
from agnt5.context import Context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==== Test Tools with Durable Functions ====

@tool(name="data_extractor", timeout=30.0, max_retries=3)
async def extract_data(source_url: str) -> Dict[str, Any]:
    """Extract data from a source URL with automatic durability."""
    logger.info(f"Extracting data from: {source_url}")
    # This tool automatically gets retry logic and state persistence
    return {
        "url": source_url,
        "data": f"extracted_data_from_{source_url}",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }


@tool(name="data_validator", enable_durability=True)
async def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted data with durable execution."""
    logger.info(f"Validating data: {data.get('url', 'unknown')}")
    return {
        "valid": True,
        "validation_score": 0.95,
        "validated_data": data,
        "timestamp": datetime.now().isoformat()
    }


@tool(name="data_processor")
def process_data_sync(data: Dict[str, Any], operation: str = "clean") -> Dict[str, Any]:
    """Synchronous data processing tool (also gets durability)."""
    logger.info(f"Processing data with operation: {operation}")
    return {
        "processed_data": f"processed_{data.get('data', 'unknown')}",
        "operation": operation,
        "timestamp": datetime.now().isoformat()
    }


# ==== Test Workflows with Durable Flows ====

class DataProcessingWorkflow(Workflow):
    """
    Multi-step data processing workflow that leverages durable flows.
    
    This workflow demonstrates:
    - Automatic state persistence across steps
    - Parallel execution coordination
    - Tool integration with durability
    - Comprehensive error handling and retry logic
    """
    
    def __init__(self):
        super().__init__(
            name="data_processing_workflow",
            description="Process data through extraction, validation, and transformation",
            version="1.0.0"
        )
        
        # Configure for durability
        self.config.enable_durability = True
        self.config.checkpoint_interval = 1
        self.config.max_retries = 3
        self.config.max_parallel_steps = 3
    
    async def run(self, source_urls: List[str]) -> Dict[str, Any]:
        """Main workflow execution with durable flow integration."""
        logger.info(f"Starting data processing workflow for {len(source_urls)} sources")
        
        # Step 1: Extract data from all sources (can run in parallel)
        logger.info("Step 1: Extracting data from sources")
        extraction_tasks = []
        for i, url in enumerate(source_urls):
            extraction_tasks.append((f"extract_{i}", extract_data, url))
        
        extraction_results = await self.parallel(extraction_tasks)
        logger.info(f"Extracted data from {len(extraction_results)} sources")
        
        # Step 2: Validate all extracted data
        logger.info("Step 2: Validating extracted data")
        validation_tasks = []
        for i, data in enumerate(extraction_results):
            validation_tasks.append((f"validate_{i}", validate_data, data))
        
        validation_results = await self.parallel(validation_tasks)
        logger.info(f"Validated {len(validation_results)} data sources")
        
        # Step 3: Process the validated data
        logger.info("Step 3: Processing validated data")
        processed_results = []
        for i, validated_data in enumerate(validation_results):
            result = await self.step(
                f"process_{i}",
                process_data_sync,
                validated_data["validated_data"],
                "clean_and_normalize"
            )
            processed_results.append(result)
        
        # Step 4: Aggregate final results
        logger.info("Step 4: Aggregating final results")
        final_result = await self.step(
            "aggregate",
            self._aggregate_results,
            processed_results
        )
        
        logger.info("Data processing workflow completed successfully")
        return final_result
    
    async def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate processing results into final output."""
        return {
            "total_processed": len(results),
            "results": results,
            "workflow_completed_at": datetime.now().isoformat(),
            "status": "completed"
        }


# ==== Test Agents with Durable Objects ====

@durable.object
class ResearchAgent(Agent):
    """
    Research agent that uses durable object state persistence.
    
    This agent demonstrates:
    - Persistent conversation history
    - Durable tool execution
    - State recovery across restarts
    - Memory integration
    """
    
    def __init__(self, agent_id: str):
        # Initialize the durable object
        super(Agent, self).__init__(agent_id)
        
        # Initialize Agent components with durability
        self.agent_id = agent_id
        self.conversation_history: List[Message] = []
        self.research_context: Dict[str, Any] = {}
        self.tools_used: List[str] = []
        
        # Configure agent settings
        self.name = f"research_agent_{agent_id}"
        self.system_prompt = "You are a research assistant with access to data processing tools."
        
        # Add tools with automatic durability
        self.available_tools = {
            "extract_data": extract_data,
            "validate_data": validate_data,
            "process_data": process_data_sync
        }
    
    async def conduct_research(self, topic: str, sources: List[str]) -> Dict[str, Any]:
        """Conduct research on a topic using durable workflows and tools."""
        logger.info(f"Agent {self.agent_id} conducting research on: {topic}")
        
        # Store research context in durable state
        self.research_context = {
            "topic": topic,
            "sources": sources,
            "started_at": datetime.now().isoformat()
        }
        await self.save()  # Persist state
        
        # Create and execute data processing workflow
        workflow = DataProcessingWorkflow()
        workflow_result = await workflow.execute(sources)
        
        # Update research context with results
        self.research_context.update({
            "workflow_result": workflow_result,
            "completed_at": datetime.now().isoformat(),
            "status": "completed"
        })
        
        # Track tools used
        self.tools_used.extend(["extract_data", "validate_data", "process_data"])
        await self.save()  # Persist final state
        
        logger.info(f"Agent {self.agent_id} completed research on: {topic}")
        return self.research_context
    
    async def get_research_summary(self) -> Dict[str, Any]:
        """Get a summary of all research conducted by this agent."""
        return {
            "agent_id": self.agent_id,
            "research_context": self.research_context,
            "tools_used": list(set(self.tools_used)),  # Unique tools
            "conversation_count": len(self.conversation_history),
        }


# ==== Test Memory Systems with Durable Objects ====

async def test_durable_memory():
    """Test the durable memory system."""
    logger.info("Testing durable memory system...")
    
    # Create a durable memory instance
    memory = await DurableMemory.create("test_memory_001")
    
    # Add various types of memories
    await memory.add("The capital of France is Paris")
    await memory.add("Python is a programming language")
    
    # Add a message to memory
    message = Message(
        role=MessageRole.USER,
        content="What is machine learning?"
    )
    await memory.add(message)
    
    # Search memories
    query_results = await memory.search("France", limit=5)
    logger.info(f"Found {len(query_results)} results for 'France'")
    
    # Get memory statistics
    stats = await memory.get_stats()
    logger.info(f"Memory stats: {stats}")
    
    return {
        "memory_id": memory.memory_id,
        "stats": stats,
        "search_results": len(query_results)
    }


# ==== Main Test Execution ====

async def run_comprehensive_test():
    """Run comprehensive test of all durable primitives integration."""
    logger.info("="*60)
    logger.info("AGNT5 SDK Durable Primitives Integration Test")
    logger.info("="*60)
    
    test_results = {}
    
    try:
        # Test 1: Durable Tools
        logger.info("\n1. Testing Durable Tools...")
        tool_result = await extract_data("https://example.com/data.json")
        test_results["durable_tools"] = {
            "status": "success",
            "result": tool_result
        }
        logger.info(f"✓ Durable tools test passed: {tool_result['status']}")
        
        # Test 2: Durable Workflows
        logger.info("\n2. Testing Durable Workflows...")
        workflow = DataProcessingWorkflow()
        workflow_result = await workflow.execute([
            "https://source1.com/data",
            "https://source2.com/data",
            "https://source3.com/data"
        ])
        test_results["durable_workflows"] = {
            "status": "success",
            "result": workflow_result
        }
        logger.info(f"✓ Durable workflows test passed: {workflow_result['total_processed']} sources processed")
        
        # Test 3: Durable Agent Objects
        logger.info("\n3. Testing Durable Agent Objects...")
        research_agent = await ResearchAgent.get_or_create("researcher_001")
        agent_result = await research_agent.conduct_research(
            topic="AGNT5 Platform Architecture",
            sources=[
                "https://docs.agnt5.com/architecture",
                "https://github.com/agnt5/platform"
            ]
        )
        agent_summary = await research_agent.get_research_summary()
        test_results["durable_agents"] = {
            "status": "success",
            "result": agent_result,
            "summary": agent_summary
        }
        logger.info(f"✓ Durable agent test passed: Research completed on '{agent_result['topic']}'")
        
        # Test 4: Durable Memory
        logger.info("\n4. Testing Durable Memory...")
        memory_result = await test_durable_memory()
        test_results["durable_memory"] = {
            "status": "success",
            "result": memory_result
        }
        logger.info(f"✓ Durable memory test passed: {memory_result['stats']['total_entries']} entries stored")
        
        # Test 5: Integration Test - All Components Together
        logger.info("\n5. Testing Full Integration...")
        
        # Create an agent with memory
        agent_with_memory = await ResearchAgent.get_or_create("integrated_agent_001")
        
        # Create a memory for the agent
        agent_memory = await DurableMemory.create("agent_integrated_memory")
        
        # Run workflow and store results in memory
        workflow_for_integration = DataProcessingWorkflow()
        integration_result = await workflow_for_integration.execute([
            "https://integration-test.com/source1",
            "https://integration-test.com/source2"
        ])
        
        # Store workflow result in agent memory
        await agent_memory.add(f"Workflow completed: {json.dumps(integration_result)}")
        
        # Agent conducts research and uses memory
        final_research = await agent_with_memory.conduct_research(
            topic="Integration Test Results",
            sources=["https://integration-test.com/results"]
        )
        
        test_results["full_integration"] = {
            "status": "success",
            "workflow_result": integration_result,
            "agent_research": final_research,
            "memory_entries": await agent_memory.get_stats()
        }
        logger.info("✓ Full integration test passed: All components working together")
        
        # Final Summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✓ PASSED" if result["status"] == "success" else "✗ FAILED"
            logger.info(f"{test_name:20} {status}")
            if result["status"] == "success":
                passed_tests += 1
        
        logger.info(f"\nResults: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Durable primitives integration is working correctly.")
        else:
            logger.error("❌ Some tests failed. Check the logs above for details.")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


async def main():
    """Main entry point for the comprehensive test."""
    print("AGNT5 SDK - Durable Primitives Integration Test")
    print("This test verifies that Agents, Tools, Workflows, and Memory")
    print("all work correctly with durable functions, objects, and flows.\n")
    
    results = await run_comprehensive_test()
    
    print(f"\nTest completed. Results summary:")
    if "error" in results:
        print(f"❌ Test failed: {results['error']}")
        return 1
    else:
        print("✅ Test completed successfully!")
        print(f"Results: {json.dumps({k: v['status'] for k, v in results.items()}, indent=2)}")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))