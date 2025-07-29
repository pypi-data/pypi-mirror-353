#!/usr/bin/env python3
"""
Direct connection test using sdk-core client directly.
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Testing direct sdk-core connection from Python...")
    
    try:
        # Import the Rust extension directly
        import agnt5._core as sdk_core
        
        logger.info("Creating WorkerCoordinatorClient...")
        client = sdk_core.WorkerCoordinatorClient("http://localhost:8081")
        
        logger.info("Starting worker stream...")
        stream = client.start_worker_stream()
        
        logger.info("Stream started successfully!")
        
        # Let it run briefly
        await asyncio.sleep(1)
        
        logger.info("Done!")
        
    except ImportError as e:
        logger.error(f"SDK-Core extension not available: {e}")
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())