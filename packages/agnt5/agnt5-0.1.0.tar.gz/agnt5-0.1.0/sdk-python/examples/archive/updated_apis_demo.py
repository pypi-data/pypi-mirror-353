#!/usr/bin/env python3
"""
Demo showing how higher-order APIs now leverage durable primitives.

This example demonstrates:
- Context API now uses durable state and service calls
- Workflow execution automatically becomes a durable flow
- Integration between high-level and low-level APIs
"""

import asyncio
import logging
from agnt5 import durable
from agnt5.context import Context, create_context
from agnt5.workflow import Workflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example: Simple durable object for user preferences
@durable.object
class UserPreferences:
    def __init__(self, user_id: str):
        super().__init__(user_id)  # Call DurableObject.__init__
        self.user_id = user_id
        self.theme = "light"
        self.language = "en"
        self.notifications = True

    async def update_theme(self, theme: str):
        """Update user theme preference."""
        logger.info(f"Updating theme for user {self.user_id} to {theme}")
        self.theme = theme
        await self.save()

    async def get_preferences(self):
        """Get current preferences."""
        return {
            "user_id": self.user_id,
            "theme": self.theme,
            "language": self.language,
            "notifications": self.notifications
        }


async def process_user_data(data):
    """Simple processing function for workflow demo."""
    logger.info(f"Processing data: {data}")
    await asyncio.sleep(0.1)  # Simulate processing
    return {"processed": True, "result": f"processed_{data}"}


async def validate_data(data):
    """Simple validation function for workflow demo."""
    logger.info(f"Validating data: {data}")
    await asyncio.sleep(0.05)  # Simulate validation
    return data.get("valid", True)


class DataProcessingWorkflow(Workflow):
    """Enhanced workflow that uses durable primitives under the hood."""
    
    async def run(self, input_data):
        """
        This run method automatically becomes durable when enable_durability=True.
        The workflow execution is wrapped in a durable flow.
        """
        logger.info("Starting data processing workflow with enhanced durability")
        
        # Step 1: Validate input
        is_valid = await self.step("validate", validate_data, input_data)
        if not is_valid:
            raise ValueError("Invalid input data")
        
        # Step 2: Process data with durable context access
        ctx = self._durable_context if hasattr(self, '_durable_context') else None
        if ctx:
            # Make a durable service call via the context
            enhanced_data = await ctx.call("enhancement_service", "enhance", input_data)
            await ctx.state.set("enhanced_data", enhanced_data)
        else:
            enhanced_data = input_data
        
        # Step 3: Final processing
        result = await self.step("process", process_user_data, enhanced_data)
        
        return {
            "success": True,
            "input": input_data,
            "enhanced": enhanced_data,
            "result": result
        }


async def demo_enhanced_context():
    """Demonstrate enhanced Context API with durable primitives."""
    print("\n" + "=" * 50)
    print("Demo: Enhanced Context API")
    print("=" * 50)
    
    with create_context("context_demo") as ctx:
        logger.info(f"Created context: {ctx.execution_id}")
        
        # Test durable state management (async)
        await ctx.set("user_session", {"user_id": "12345", "login_time": "2024-01-01T10:00:00Z"})
        session = await ctx.get("user_session")
        logger.info(f"Retrieved session: {session}")
        
        # Test durable service call via context
        try:
            result = await ctx.call("user_service", "get_profile", user_id="12345")
            logger.info(f"Service call result: {result}")
        except Exception as e:
            logger.info(f"Service call (fallback mode): {e}")
        
        # Test durable object access via context
        user_prefs = await ctx.get_object(UserPreferences, "user_12345")
        prefs = await user_prefs.get_preferences()
        logger.info(f"User preferences: {prefs}")
        
        # Update preferences
        await user_prefs.update_theme("dark")
        updated_prefs = await user_prefs.get_preferences()
        logger.info(f"Updated preferences: {updated_prefs}")
        
        # Test durable sleep
        logger.info("Testing durable sleep (0.1 seconds)...")
        await ctx.sleep(0.1)
        logger.info("Durable sleep completed")


async def demo_enhanced_workflow():
    """Demonstrate enhanced Workflow that uses durable flow."""
    print("\n" + "=" * 50)
    print("Demo: Enhanced Workflow with Durable Flow")
    print("=" * 50)
    
    # Create workflow with durability enabled
    workflow = DataProcessingWorkflow(
        name="enhanced_workflow",
        config=type('Config', (), {
            'name': 'enhanced_workflow',
            'description': 'Workflow with durable flow integration',
            'version': '1.0.0',
            'enable_durability': True,
            'checkpoint_interval': 1,
            'max_retries': 3
        })()
    )
    
    # Execute workflow - this will automatically use durable flow
    input_data = {
        "data": "sample_input",
        "valid": True,
        "metadata": {"source": "demo", "timestamp": "2024-01-01T10:00:00Z"}
    }
    
    try:
        result = await workflow.execute(input_data)
        logger.info(f"Workflow result: {result}")
    except Exception as e:
        logger.error(f"Workflow error: {e}")


async def demo_direct_durable_primitives():
    """Demonstrate direct use of durable primitives."""
    print("\n" + "=" * 50)
    print("Demo: Direct Durable Primitives")
    print("=" * 50)
    
    # Show that registered durable flows are available
    flows = durable.get_all_flows()
    logger.info(f"Registered flows: {[f.config.name for f in flows]}")
    
    # Show registered durable functions
    functions = durable.get_all_functions()
    logger.info(f"Registered functions: {[f.config.name for f in functions]}")
    
    # Show registered durable objects
    objects = durable.get_all_objects()
    logger.info(f"Registered objects: {[obj.__name__ for obj in objects]}")


async def main():
    """Run all demonstrations."""
    print("AGNT5 Enhanced APIs Demonstration")
    print("=" * 50)
    print("Showing how higher-order APIs now leverage durable primitives:")
    print("- Context API uses durable state and service calls")
    print("- Workflow execution becomes durable flow automatically")
    print("- Seamless integration between high-level and low-level APIs")
    
    await demo_enhanced_context()
    await demo_enhanced_workflow()
    await demo_direct_durable_primitives()
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print("Higher-order APIs now provide durability out of the box.")


if __name__ == "__main__":
    asyncio.run(main())