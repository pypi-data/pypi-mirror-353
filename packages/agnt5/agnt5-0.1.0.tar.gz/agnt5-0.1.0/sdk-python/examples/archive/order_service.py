#!/usr/bin/env python3
"""
AGNT5 Local Development - Example Order Service

This file demonstrates how to create durable functions using the AGNT5 Python SDK
for the local development environment. It implements a complete order processing
workflow as described in E2E_Execution.md.

Usage:
    python3 order_service.py

This service registers durable functions that can be invoked via:
    POST http://localhost:8080/invoke/order-service/process_order
"""

import setproctitle

setproctitle.setproctitle("MyApp-Debug-OrderService")

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add the AGNT5 SDK to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

try:
    from agnt5.durable import DurableContext, durable
    from agnt5.runtime import run_service
except ImportError as e:
    print(f"Error importing AGNT5 SDK: {e}")
    print("Make sure the Python SDK is properly installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@durable.function
async def process_order(ctx: DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main order processing workflow that demonstrates durable execution.

    This function implements the order processing flow described in E2E_Execution.md:
    1. Validate the order
    2. Process payment
    3. Create shipment
    4. Update inventory
    5. Send notifications

    All steps are durable and will survive failures and restarts.
    """
    logger.info(f"🛒 Processing order {order_data.get('order_id', 'unknown')}")

    order_id = order_data.get("order_id", "unknown")
    customer_id = order_data.get("customer_id", "unknown")
    items = order_data.get("items", [])

    # Store initial order state
    await ctx.state.set("order_status", "processing")
    await ctx.state.set("order_data", order_data)
    await ctx.state.set("started_at", datetime.now().isoformat())

    try:
        # Step 1: Validate order
        logger.info(f"📋 Validating order {order_id}")
        validation_result = await validate_order(ctx, order_data)

        if not validation_result["valid"]:
            await ctx.state.set("order_status", "validation_failed")
            return {"status": "failed", "reason": "Order validation failed", "validation_errors": validation_result["errors"], "order_id": order_id}

        await ctx.state.set("validation_completed", True)

        # Step 2: Process payment (external service call)
        logger.info(f"💳 Processing payment for order {order_id}")
        payment_request = {"customer_id": customer_id, "amount": calculate_total(items), "currency": "USD", "order_id": order_id}

        # Simulate calling external payment service through context
        payment_result = await ctx.call("payment_service", "charge", payment_request)

        if not payment_result.get("success", False):
            await ctx.state.set("order_status", "payment_failed")
            return {"status": "failed", "reason": "Payment processing failed", "payment_error": payment_result.get("error", "Unknown error"), "order_id": order_id}

        await ctx.state.set("payment_id", payment_result.get("payment_id"))
        await ctx.state.set("payment_completed", True)

        # Step 3: Create shipment
        logger.info(f"📦 Creating shipment for order {order_id}")
        shipment_request = {"order_id": order_id, "customer_id": customer_id, "items": items, "shipping_address": order_data.get("shipping_address", {})}

        shipment_result = await ctx.call("shipping_service", "create", shipment_request)

        await ctx.state.set("shipment_id", shipment_result.get("shipment_id"))
        await ctx.state.set("shipment_created", True)

        # Step 4: Update inventory
        logger.info(f"📊 Updating inventory for order {order_id}")
        for item in items:
            inventory_update = {"product_id": item.get("product_id"), "quantity_sold": item.get("quantity", 1), "order_id": order_id}
            await ctx.call("inventory_service", "update", inventory_update)

        await ctx.state.set("inventory_updated", True)

        # Step 5: Send notifications
        logger.info(f"📧 Sending notifications for order {order_id}")
        notification_data = {
            "customer_id": customer_id,
            "order_id": order_id,
            "type": "order_confirmation",
            "payment_id": payment_result.get("payment_id"),
            "shipment_id": shipment_result.get("shipment_id"),
        }

        await ctx.call("notification_service", "send", notification_data)

        # Final state update
        await ctx.state.set("order_status", "completed")
        await ctx.state.set("completed_at", datetime.now().isoformat())

        logger.info(f"✅ Order {order_id} processed successfully")

        return {
            "status": "completed",
            "order_id": order_id,
            "customer_id": customer_id,
            "payment_id": payment_result.get("payment_id"),
            "shipment_id": shipment_result.get("shipment_id"),
            "items_count": len(items),
            "total_amount": calculate_total(items),
            "processed_at": datetime.now().isoformat(),
            "message": f"Order {order_id} has been processed successfully",
        }

    except Exception as e:
        logger.error(f"❌ Error processing order {order_id}: {e}")
        await ctx.state.set("order_status", "error")
        await ctx.state.set("error_message", str(e))

        # In a real system, you might want to trigger compensation workflows here
        raise


@durable.function
async def validate_order(ctx: DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate order data and business rules."""

    errors = []

    # Check required fields
    required_fields = ["order_id", "customer_id", "items"]
    for field in required_fields:
        if not order_data.get(field):
            errors.append(f"Missing required field: {field}")

    # Validate items
    items = order_data.get("items", [])
    if not items:
        errors.append("Order must contain at least one item")

    for i, item in enumerate(items):
        if not item.get("product_id"):
            errors.append(f"Item {i}: Missing product_id")

        quantity = item.get("quantity", 0)
        if not isinstance(quantity, int) or quantity <= 0:
            errors.append(f"Item {i}: Invalid quantity")

        price = item.get("price", 0)
        if not isinstance(price, (int, float)) or price <= 0:
            errors.append(f"Item {i}: Invalid price")

    # Business rule: Check order total
    total = calculate_total(items)
    if total > 10000:  # $10,000 limit
        errors.append("Order total exceeds maximum allowed amount")

    is_valid = len(errors) == 0

    return {"valid": is_valid, "errors": errors, "total_amount": total if is_valid else 0}


@durable.function
async def get_order_status(ctx: DurableContext, order_id: str) -> Dict[str, Any]:
    """Get the current status of an order."""

    # Retrieve order state
    order_status = await ctx.state.get("order_status")
    order_data = await ctx.state.get("order_data")
    started_at = await ctx.state.get("started_at")
    completed_at = await ctx.state.get("completed_at")

    # Get progress indicators
    validation_completed = await ctx.state.get("validation_completed", False)
    payment_completed = await ctx.state.get("payment_completed", False)
    shipment_created = await ctx.state.get("shipment_created", False)
    inventory_updated = await ctx.state.get("inventory_updated", False)

    return {
        "order_id": order_id,
        "status": order_status or "not_found",
        "order_data": order_data,
        "started_at": started_at,
        "completed_at": completed_at,
        "progress": {
            "validation_completed": validation_completed,
            "payment_completed": payment_completed,
            "shipment_created": shipment_created,
            "inventory_updated": inventory_updated,
        },
        "payment_id": await ctx.state.get("payment_id"),
        "shipment_id": await ctx.state.get("shipment_id"),
    }


@durable.function
async def cancel_order(ctx: DurableContext, order_id: str, reason: str = "Customer request") -> Dict[str, Any]:
    """Cancel an order and trigger compensation workflows."""

    current_status = await ctx.state.get("order_status")

    if current_status == "completed":
        return {"status": "error", "message": "Cannot cancel completed order", "order_id": order_id}

    # Update status
    await ctx.state.set("order_status", "cancelling")
    await ctx.state.set("cancellation_reason", reason)
    await ctx.state.set("cancelled_at", datetime.now().isoformat())

    # Trigger compensation workflows
    compensations = []

    # Refund payment if it was processed
    payment_completed = await ctx.state.get("payment_completed", False)
    if payment_completed:
        payment_id = await ctx.state.get("payment_id")
        refund_result = await ctx.call("payment_service", "refund", {"payment_id": payment_id, "reason": reason})
        compensations.append({"action": "payment_refund", "result": refund_result})

    # Cancel shipment if it was created
    shipment_created = await ctx.state.get("shipment_created", False)
    if shipment_created:
        shipment_id = await ctx.state.get("shipment_id")
        cancel_result = await ctx.call("shipping_service", "cancel", {"shipment_id": shipment_id, "reason": reason})
        compensations.append({"action": "shipment_cancel", "result": cancel_result})

    await ctx.state.set("order_status", "cancelled")
    await ctx.state.set("compensations", compensations)

    return {"status": "cancelled", "order_id": order_id, "reason": reason, "cancelled_at": datetime.now().isoformat(), "compensations": compensations}


# Utility functions


def calculate_total(items: list) -> float:
    """Calculate total order amount."""
    total = 0.0
    for item in items:
        price = item.get("price", 0)
        quantity = item.get("quantity", 1)
        total += price * quantity
    return total


# Simple order assistant (without Agent API for now)


@durable.function
async def order_assistant(ctx: DurableContext, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple order assistant for order-related queries.

    This is a simplified version that doesn't use the Agent API.
    """
    user_message = query.get("message", "")
    order_id = query.get("order_id")

    # Get order context if order_id is provided
    context = ""
    if order_id:
        try:
            order_status = await get_order_status(ctx, order_id)
            context = f"Order {order_id} status: {order_status.get('status', 'unknown')}"
        except Exception:
            context = f"Order {order_id} not found"

    # Simple response logic (in real implementation, would use AI)
    response = f"Thank you for your inquiry about {user_message}. "
    if context:
        response += f"{context}. "
    response += "How else can I help you today?"

    return {"response": response, "order_id": order_id, "timestamp": datetime.now().isoformat()}


async def main():
    """
    Main function to run the order service.

    This registers all the durable functions and starts the service.
    """
    logger.info("🚀 Starting AGNT5 Order Service...")

    # Start the service
    await run_service(service_name="order-service", runtime_endpoint="http://localhost:8080", service_version="1.0.0")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Order service stopped by user")
    except Exception as e:
        print(f"❌ Order service failed: {e}")
        sys.exit(1)
