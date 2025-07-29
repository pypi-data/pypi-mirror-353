#!/usr/bin/env python3
"""
Example: Order Processing with AGNT5 Durable Functions

This example shows how to build a durable order processing workflow using
AGNT5 Python SDK. The workflow survives failures and maintains state across
restarts, with automatic retries and exactly-once guarantees.

To run this example:
    python examples/order_processing.py
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Import AGNT5 SDK components
from agnt5.durable import durable, DurableContext, DurableObject


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Order:
    """Order data structure."""
    id: str
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: str = "pending"


@dataclass
class PaymentResult:
    """Payment processing result."""
    payment_id: str
    amount: float
    status: str
    transaction_id: str


@dataclass
class ShipmentResult:
    """Shipment creation result."""
    shipment_id: str
    tracking_number: str
    estimated_delivery: str


# Durable Functions
@durable.function
async def validate_order(ctx: DurableContext, order: Order) -> Dict[str, Any]:
    """
    Validate an order before processing.
    
    This function validates inventory, pricing, and customer data.
    """
    logger.info(f"Validating order {order.id}")
    
    # Simulate inventory check via external service
    inventory_result = await ctx.call(
        "inventory_service", 
        "check_availability", 
        order.items
    )
    
    # Simulate customer validation
    customer_result = await ctx.call(
        "customer_service",
        "validate_customer", 
        order.customer_id
    )
    
    # Simulate pricing validation
    pricing_result = await ctx.call(
        "pricing_service",
        "validate_pricing",
        order.items,
        order.total_amount
    )
    
    return {
        "inventory_valid": True,  # Would use inventory_result
        "customer_valid": True,   # Would use customer_result  
        "pricing_valid": True,    # Would use pricing_result
        "validated_at": datetime.utcnow().isoformat()
    }


@durable.function
async def process_payment(ctx: DurableContext, order: Order) -> PaymentResult:
    """
    Process payment for an order.
    
    This function handles payment processing with automatic retries.
    """
    logger.info(f"Processing payment for order {order.id}")
    
    # Store payment attempt in state
    attempt_count = await ctx.state.get("payment_attempts", 0)
    attempt_count += 1
    await ctx.state.set("payment_attempts", attempt_count)
    
    # Call payment service
    payment_response = await ctx.call(
        "payment_service",
        "charge_customer",
        {
            "customer_id": order.customer_id,
            "amount": order.total_amount,
            "order_id": order.id,
            "attempt": attempt_count
        }
    )
    
    # Return structured result
    return PaymentResult(
        payment_id=f"pay_{order.id}_{attempt_count}",
        amount=order.total_amount,
        status="completed",
        transaction_id=f"txn_{order.id}"
    )


@durable.function 
async def create_shipment(ctx: DurableContext, order: Order, payment: PaymentResult) -> ShipmentResult:
    """
    Create shipment for a paid order.
    
    This function creates shipping labels and schedules pickup.
    """
    logger.info(f"Creating shipment for order {order.id}")
    
    # Create shipping label
    label_response = await ctx.call(
        "shipping_service",
        "create_label",
        {
            "order_id": order.id,
            "payment_id": payment.payment_id,
            "items": order.items
        }
    )
    
    # Schedule pickup
    pickup_response = await ctx.call(
        "shipping_service", 
        "schedule_pickup",
        {
            "order_id": order.id,
            "pickup_date": "tomorrow"
        }
    )
    
    return ShipmentResult(
        shipment_id=f"ship_{order.id}",
        tracking_number=f"track_{order.id}",
        estimated_delivery="3-5 business days"
    )


@durable.function
async def send_confirmation(ctx: DurableContext, order: Order, shipment: ShipmentResult) -> None:
    """
    Send order confirmation to customer.
    
    This function sends email and SMS notifications.
    """
    logger.info(f"Sending confirmation for order {order.id}")
    
    # Send email confirmation
    await ctx.call(
        "notification_service",
        "send_email",
        {
            "customer_id": order.customer_id,
            "template": "order_confirmation",
            "data": {
                "order_id": order.id,
                "tracking_number": shipment.tracking_number,
                "estimated_delivery": shipment.estimated_delivery
            }
        }
    )
    
    # Send SMS notification
    await ctx.call(
        "notification_service", 
        "send_sms",
        {
            "customer_id": order.customer_id,
            "message": f"Order {order.id} confirmed! Track: {shipment.tracking_number}"
        }
    )


# Durable Flow
@durable.flow
async def process_order_workflow(ctx: DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete order processing workflow.
    
    This flow orchestrates the entire order processing pipeline:
    1. Validate order
    2. Process payment  
    3. Create shipment
    4. Send confirmation
    
    Each step is automatically checkpointed for durability.
    """
    logger.info(f"Starting order processing workflow for order {order_data['id']}")
    
    # Create order object
    order = Order(**order_data)
    
    # Step 1: Validate order
    validation_result = await validate_order(ctx, order)
    if not all(validation_result.values()):
        raise ValueError(f"Order validation failed: {validation_result}")
    
    # Update state after validation
    await ctx.state.set("validation_completed", True)
    await ctx.state.set("validation_result", validation_result)
    
    # Step 2: Process payment
    payment_result = await process_payment(ctx, order)
    await ctx.state.set("payment_completed", True)
    await ctx.state.set("payment_result", payment_result.__dict__)
    
    # Step 3: Create shipment
    shipment_result = await create_shipment(ctx, order, payment_result)
    await ctx.state.set("shipment_completed", True)
    await ctx.state.set("shipment_result", shipment_result.__dict__)
    
    # Step 4: Send confirmation
    await send_confirmation(ctx, order, shipment_result)
    await ctx.state.set("confirmation_sent", True)
    
    # Return final result
    return {
        "order_id": order.id,
        "status": "completed",
        "payment": payment_result.__dict__,
        "shipment": shipment_result.__dict__,
        "completed_at": datetime.utcnow().isoformat()
    }


# Durable Object
@durable.object
class OrderTracker(DurableObject):
    """
    Durable object for tracking order state.
    
    Maintains order status and provides methods for updates.
    """
    
    def __init__(self, order_id: str):
        super().__init__(f"order_tracker_{order_id}")
        self.order_id = order_id
        self.status = "created"
        self.events: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow().isoformat()
    
    async def update_status(self, status: str, metadata: Dict[str, Any] = None) -> None:
        """Update order status with event logging."""
        self.status = status
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "metadata": metadata or {}
        }
        self.events.append(event)
        
        logger.info(f"Order {self.order_id} status updated to: {status}")
        await self.save()
    
    async def get_status(self) -> str:
        """Get current order status."""
        return self.status
    
    async def get_events(self) -> List[Dict[str, Any]]:
        """Get order event history."""
        return self.events.copy()


# Example order processing with error handling
@durable.flow
async def robust_order_processing(ctx: DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Robust order processing with error handling and tracking.
    """
    order_id = order_data["id"]
    
    # Get or create order tracker
    tracker = await ctx.get_object(OrderTracker, order_id)
    
    try:
        # Update status to processing
        await tracker.update_status("processing", {"started_at": datetime.utcnow().isoformat()})
        
        # Process the order
        result = await process_order_workflow(ctx, order_data)
        
        # Update status to completed
        await tracker.update_status("completed", result)
        
        return result
        
    except Exception as e:
        # Update status to failed
        await tracker.update_status("failed", {
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
        raise


# Delayed processing example
@durable.function
async def delayed_order_reminder(ctx: DurableContext, order_id: str, delay_hours: int = 24) -> None:
    """
    Send a reminder about incomplete order after delay.
    """
    logger.info(f"Setting up {delay_hours}h reminder for order {order_id}")
    
    # Sleep for the specified duration (survives restarts)
    await ctx.sleep(delay_hours * 3600)  # Convert hours to seconds
    
    # Check if order is still incomplete
    tracker = await ctx.get_object(OrderTracker, order_id)
    status = await tracker.get_status()
    
    if status in ["created", "processing"]:
        # Send reminder
        await ctx.call(
            "notification_service",
            "send_reminder",
            {
                "order_id": order_id,
                "message": f"Your order {order_id} is still being processed."
            }
        )
        
        await tracker.update_status("reminder_sent", {
            "reminder_hours": delay_hours
        })


async def example_usage():
    """Example of how to use the durable functions."""
    
    # Example order data
    order_data = {
        "id": "order_123",
        "customer_id": "customer_456", 
        "items": [
            {"sku": "ITEM001", "quantity": 2, "price": 29.99},
            {"sku": "ITEM002", "quantity": 1, "price": 49.99}
        ],
        "total_amount": 109.97
    }
    
    logger.info("=== AGNT5 Order Processing Example ===")
    
    # Test individual function (for local testing)
    print("\n1. Testing individual durable function:")
    try:
        validation_result = await validate_order(None, Order(**order_data))
        print(f"Validation result: {validation_result}")
    except Exception as e:
        print(f"Function test failed: {e}")
    
    # Test durable object
    print("\n2. Testing durable object:")
    try:
        tracker = await OrderTracker.get_or_create(order_data["id"])
        await tracker.update_status("testing")
        status = await tracker.get_status()
        events = await tracker.get_events()
        print(f"Tracker status: {status}")
        print(f"Tracker events: {len(events)} events")
    except Exception as e:
        print(f"Object test failed: {e}")
    
    print("\n3. Ready to process orders with AGNT5 Runtime!")
    print("   Run with: python -m agnt5.runtime --service-name=order-service")


if __name__ == "__main__":
    # If running standalone, show example usage
    asyncio.run(example_usage())