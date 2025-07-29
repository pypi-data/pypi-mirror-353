#!/usr/bin/env python3
"""
Test with persistent connection for grpcurl testing.
"""

import asyncio
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import agnt5

# Global worker for cleanup
worker = None

async def main():
    global worker
    logger.info("Creating persistent worker...")
    
    worker = agnt5.get_worker(
        service_name="test_service", 
        service_version="1.0.0",
        coordinator_endpoint="http://localhost:8081"
    )
    
    # Register a simple function
    async def test_function(ctx, data):
        logger.info(f"✅ Python function called with data: {data}")
        return {"result": "success", "handler": "test_function", "data": data}
    
    await worker.register_function(test_function, name="test_function", timeout=30, retry=3)
    logger.info("✅ Function registered: test_function")
    
    logger.info("🚀 Starting worker...")
    await worker.start()
    
    logger.info("🔄 Worker is running persistently. Press Ctrl+C to stop.")
    logger.info("🧪 Test with: grpcurl -plaintext -d '{\"serviceName\": \"test_service\", \"handlerName\": \"test_function\", \"inputData\": \"eyJ0ZXN0IjogInZhbHVlIn0=\"}' localhost:8080 api.v1.GatewayService/InvokeFunction")
    
    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal, shutting down...")
        await worker.stop()
        logger.info("✅ Worker stopped")

def signal_handler(signum, frame):
    logger.info("🛑 Signal received, shutting down...")
    if worker:
        # Create new event loop for cleanup since we might be in a signal handler
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(worker.stop())
            loop.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("✅ Shutdown complete")