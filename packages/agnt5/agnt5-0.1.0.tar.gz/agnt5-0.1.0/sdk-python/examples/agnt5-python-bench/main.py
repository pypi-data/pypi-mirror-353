#!/usr/bin/env python3
"""
AGNT5 Python Benchmark Application - Worker Registration

Main entry point for the customer support platform worker.
Registers all durable functions, objects, and workflows with the AGNT5 runtime.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the SDK to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agnt5 import get_worker, setup_logging
from agnt5.runtime import RuntimeConfig

# Import application components
from agents.customer_service import CustomerServiceAgent, handle_customer_request
from agents.technical_support import TechnicalSupportAgent, handle_technical_request
from agents.order_management import OrderManagementAgent, handle_order_request
from agents.analytics_agent import AnalyticsAgent, process_analytics

from workflows.order_processing import process_order_workflow
from workflows.issue_resolution import resolve_issue_workflow
from workflows.reporting_pipeline import generate_reports_workflow

from objects.customer_session import CustomerSession
from objects.order_tracker import OrderTracker
from objects.knowledge_base import KnowledgeBase

async def register_handlers(worker) -> None:
    """Register all application handlers with the worker."""
    
    # Register durable workflow functions
    await worker.register_function(process_order_workflow, "process_order")
    await worker.register_function(resolve_issue_workflow, "resolve_issue") 
    await worker.register_function(generate_reports_workflow, "generate_reports")
    
    # Register agent request handlers
    await worker.register_function(handle_customer_request, "customer_service")
    await worker.register_function(handle_technical_request, "technical_support")
    await worker.register_function(handle_order_request, "order_management")
    await worker.register_function(process_analytics, "analytics")
    
    # Register durable object factories
    await worker.register_object_factory(CustomerSession, "customer_session")
    await worker.register_object_factory(OrderTracker, "order_tracker")
    await worker.register_object_factory(KnowledgeBase, "knowledge_base")
    
    print("✅ All handlers registered successfully")

async def main():
    """Main worker entry point."""
    
    # Setup logging
    log_level = os.getenv("AGNT5_LOG_LEVEL", "info")
    setup_logging(log_level)
    
    # Configuration
    service_name = os.getenv("AGNT5_SERVICE_NAME", "agnt5-python-bench")
    service_version = os.getenv("AGNT5_SERVICE_VERSION", "1.0.0") 
    coordinator_endpoint = os.getenv("AGNT5_RUNTIME_ENDPOINT", "http://localhost:8081")
    
    print(f"🚀 Starting {service_name} v{service_version}")
    print(f"📡 Connecting to runtime: {coordinator_endpoint}")
    
    try:
        # Create and configure worker
        worker = get_worker(
            service_name=service_name,
            service_version=service_version,
            coordinator_endpoint=coordinator_endpoint
        )
        
        # Register all handlers
        await register_handlers(worker)
        
        # Start the worker
        print("🔄 Starting worker...")
        await worker.start()
        print(f"✅ {service_name} worker started successfully")
        print("📊 Ready to process requests and benchmarks")
        
        # Keep running
        await worker.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    except Exception as e:
        print(f"❌ Worker failed to start: {e}")
        raise
    finally:
        print("🔄 Shutting down worker...")
        if 'worker' in locals():
            await worker.stop()
        print("✅ Worker shutdown complete")

def print_startup_info():
    """Print startup information and configuration."""
    print("=" * 60)
    print("🤖 AGNT5 Python Benchmark Application")
    print("=" * 60)
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"🔧 Service Name: {os.getenv('AGNT5_SERVICE_NAME', 'agnt5-python-bench')}")
    print(f"🌐 Runtime Endpoint: {os.getenv('AGNT5_RUNTIME_ENDPOINT', 'http://localhost:8080')}")
    print(f"📈 Log Level: {os.getenv('AGNT5_LOG_LEVEL', 'info')}")
    print("=" * 60)

if __name__ == "__main__":
    print_startup_info()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
