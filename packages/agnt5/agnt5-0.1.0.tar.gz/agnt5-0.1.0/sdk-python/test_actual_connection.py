#!/usr/bin/env python3
"""
Simple test that actually calls worker.start() to test real connection.
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import agnt5

async def main():
    logger.info("Creating worker...")
    
    worker = agnt5.get_worker(
        service_name="connection_test",
        service_version="1.0.0", 
        coordinator_endpoint="http://localhost:8081"
    )
    
    # Register a simple function
    async def test_func(_ctx, data):
        return {"result": "test"}
    
    await worker.register_function(test_func, name="test_func", timeout=30, retry=3)
    
    logger.info("Service is starting...")
    logger.info("Connecting to runtime at http://localhost:8081")
    await worker.start()
    
    logger.info("Service started successfully - connection established")
    logger.info("Worker started - sleeping 2 seconds...")
    await asyncio.sleep(2)
    
    await worker.stop()
    logger.info("Service stopped successfully")
    
    logger.info("Done!")

if __name__ == "__main__":
    asyncio.run(main())