#!/usr/bin/env python3
"""
Test script to verify that the Python SDK worker can start and register with the coordinator.
"""

import asyncio
import logging
import os
import sys

# Setup Python logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable Rust logging
os.environ.setdefault("RUST_LOG", "agnt5_sdk_core=info,agnt5_python=debug")


async def test_worker():
    """Test worker registration and startup."""
    try:
        # Import AGNT5 SDK
        import agnt5

        # Initialize Rust logging
        agnt5.setup_logging("debug")

        logger.info("Creating worker...")

        # Create worker
        worker = agnt5.get_worker(
            service_name="test_service",
            service_version="1.0.0",
            coordinator_endpoint="http://localhost:8081",  # Worker coordinator port
        )

        logger.info("Worker created successfully")

        # Register a simple test function
        async def test_function(_ctx, input_data):
            """A simple test function."""
            logger.info(f"Test function called with: {input_data}")
            return {"result": "success", "echo": input_data}

        logger.info("Registering test function...")
        await worker.register_function(test_function, name="test_function", timeout=30, retry=3)

        logger.info("Starting worker...")
        await worker.start()

        logger.info("Worker started successfully! Check the coordinator logs for registration details.")

        # Let it run for a few seconds to verify connection
        logger.info("Worker is running... Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Stopping worker...")

        logger.info("Stopping worker...")
        await worker.stop()

        logger.info("Worker stopped successfully")

    except Exception as e:
        logger.error(f"Error during worker test: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


async def main():
    """Main test runner."""
    logger.info("Starting worker registration test...")

    success = await test_worker()

    if success:
        logger.info("✅ Worker registration test passed!")
        sys.exit(0)
    else:
        logger.error("❌ Worker registration test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
