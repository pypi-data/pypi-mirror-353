#!/usr/bin/env python3
"""
Example demonstrating the Rust-Python bridge for AGNT5 SDK.

This example shows how to:
1. Create a durable worker using the Rust core
2. Register Python functions as durable handlers
3. Handle async/await compatibility
4. Use proper error handling and type conversions
"""

import asyncio
import json
from typing import Dict, Any, List
import agnt5


async def process_order(ctx: agnt5.DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example durable function that processes an order.
    
    This function demonstrates:
    - Durable state management
    - External service calls
    - Error handling
    - Type conversions between Python and Rust
    """
    order_id = order_data.get("order_id")
    items = order_data.get("items", [])
    
    print(f"Processing order {order_id} with {len(items)} items")
    
    # Store initial state
    await ctx.state_set("order_status", "processing")
    await ctx.state_set("processed_items", 0)
    
    try:
        # Process each item (simulate external service calls)
        results = []
        for i, item in enumerate(items):
            print(f"Processing item {i+1}/{len(items)}: {item['name']}")
            
            # Simulate external inventory check
            inventory_result = await ctx.call(
                service_name="inventory_service",
                method_name="check_availability", 
                args={"sku": item["sku"], "quantity": item["quantity"]},
                timeout_secs=30
            )
            
            if not inventory_result.get("available", False):
                raise Exception(f"Item {item['name']} not available")
            
            # Update progress state
            await ctx.state_set("processed_items", i + 1)
            
            results.append({
                "item": item,
                "inventory": inventory_result,
                "status": "processed"
            })
            
            # Simulate processing delay
            await ctx.sleep(0.1)
        
        # Calculate total and process payment
        total = sum(item["price"] * item["quantity"] for item in items)
        
        payment_result = await ctx.call(
            service_name="payment_service",
            method_name="process_payment",
            args={
                "order_id": order_id,
                "amount": total,
                "payment_method": order_data.get("payment_method", "credit_card")
            },
            timeout_secs=60
        )
        
        # Update final state
        await ctx.state_set("order_status", "completed")
        await ctx.state_set("payment_id", payment_result.get("payment_id"))
        
        return {
            "order_id": order_id,
            "status": "completed",
            "total": total,
            "payment_id": payment_result.get("payment_id"),
            "processed_items": results,
            "timestamp": ctx.generate_id()  # Use context to generate unique ID
        }
        
    except Exception as e:
        # Update error state
        await ctx.state_set("order_status", "failed")
        await ctx.state_set("error", str(e))
        
        # Re-raise for proper error handling
        raise


async def calculate_shipping(ctx: agnt5.DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example function for calculating shipping costs.
    
    Demonstrates parallel execution with spawn.
    """
    items = order_data.get("items", [])
    shipping_address = order_data.get("shipping_address", {})
    
    # Use spawn for parallel shipping calculations
    shipping_options = await ctx.spawn([
        ("shipping_service", "calculate_standard", {"items": items, "address": shipping_address}),
        ("shipping_service", "calculate_express", {"items": items, "address": shipping_address}),
        ("shipping_service", "calculate_overnight", {"items": items, "address": shipping_address}),
    ])
    
    return {
        "shipping_options": shipping_options,
        "recommended": shipping_options[0] if shipping_options else None
    }


async def wait_for_approval(ctx: agnt5.DurableContext, approval_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example function that waits for external approval.
    
    Demonstrates event waiting with timeout.
    """
    approval_id = approval_data.get("approval_id")
    timeout_hours = approval_data.get("timeout_hours", 24)
    
    print(f"Waiting for approval {approval_id} (timeout: {timeout_hours}h)")
    
    try:
        # Wait for approval event with timeout
        approval_result = await ctx.wait_for_event(
            event_id=f"approval_{approval_id}",
            timeout_secs=timeout_hours * 3600
        )
        
        return {
            "approval_id": approval_id,
            "status": "approved" if approval_result.get("approved", False) else "rejected",
            "approver": approval_result.get("approver"),
            "notes": approval_result.get("notes", ""),
            "timestamp": approval_result.get("timestamp")
        }
        
    except Exception:
        # Timeout or other error
        return {
            "approval_id": approval_id,
            "status": "timeout",
            "notes": f"No response within {timeout_hours} hours"
        }


async def main():
    """Main function demonstrating the Rust-Python bridge."""
    
    print("AGNT5 Python SDK - Rust Bridge Example")
    print("=" * 50)
    
    # Check if Rust core is available
    print(f"Rust core available: {agnt5._rust_core_available}")
    
    if not agnt5._rust_core_available:
        print("Warning: Rust core not available, using Python fallback")
    
    try:
        # Create a worker (will use Rust core if available)
        worker = agnt5.get_worker(
            service_name="order_processor",
            service_version="1.0.0",
            coordinator_endpoint="http://localhost:34185",
            use_rust_core=True
        )
        
        print(f"Created worker: {type(worker).__name__}")
        
        # Register durable functions
        await worker.register_function(process_order, name="process_order", timeout=300, retry=3)
        await worker.register_function(calculate_shipping, name="calculate_shipping", timeout=60, retry=2)
        await worker.register_function(wait_for_approval, name="wait_for_approval", timeout=86400, retry=1)
        
        print("Registered functions:")
        handlers = await worker.list_handlers()
        for handler in handlers:
            print(f"  - {handler}")
        
        # Get worker configuration
        config = worker.config
        print(f"\nWorker configuration:")
        print(f"  Service: {config.service_name}@{config.service_version}")
        print(f"  Endpoint: {config.coordinator_endpoint}")
        print(f"  Max concurrent: {config.max_concurrent_invocations}")
        print(f"  Connection timeout: {config.connection_timeout_secs}s")
        
        # Start the worker (in a real scenario, this would run continuously)
        print("\nStarting worker...")
        print("Worker would now listen for invocations from the coordinator...")
        print("In a real deployment, the worker would run until stopped.")
        
        # Simulate some basic operations without actually starting
        print("\nWorker ready to handle invocations!")
        
        # Demonstrate error handling
        try:
            # This would normally be called by the coordinator
            # but we can test error handling here
            agnt5.AgntError("Test error for demonstration")
        except Exception as e:
            print(f"Error handling works: {e}")
        
        # Get recent errors (for debugging)
        recent_errors = agnt5.get_recent_errors() if hasattr(agnt5, 'get_recent_errors') else []
        print(f"Recent errors tracked: {len(recent_errors)}")
        
    except Exception as e:
        print(f"Error during worker setup: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())