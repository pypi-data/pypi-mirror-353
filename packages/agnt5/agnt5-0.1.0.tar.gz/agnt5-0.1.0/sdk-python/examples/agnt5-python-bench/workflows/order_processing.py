"""
Order Processing Workflow - End-to-end order lifecycle management

Orchestrates the complete order processing pipeline from validation through delivery.
Demonstrates complex workflow patterns with error handling, retries, and state management.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from agnt5.durable import durable, DurableContext
from agnt5 import tool


class ProcessingStage(Enum):
    """Order processing stages."""
    VALIDATION = "validation"
    PAYMENT = "payment"
    INVENTORY = "inventory"
    FULFILLMENT = "fulfillment"
    SHIPPING = "shipping"
    NOTIFICATION = "notification"
    COMPLETION = "completion"


@dataclass
class OrderData:
    """Order processing data structure."""
    order_id: str
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: Decimal
    shipping_address: Dict[str, str]
    billing_address: Dict[str, str]
    payment_method: Dict[str, str]
    priority: str = "normal"
    special_instructions: str = ""


@dataclass
class ProcessingResult:
    """Result of a processing stage."""
    stage: ProcessingStage
    success: bool
    data: Dict[str, Any]
    errors: List[str] = None
    warnings: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


# External service simulation tools
@tool
def validate_order_data(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate order data for completeness and business rules."""
    time.sleep(0.1)  # Simulate validation time
    
    errors = []
    warnings = []
    
    # Check required fields
    required_fields = ["order_id", "customer_id", "items", "total_amount"]
    for field in required_fields:
        if field not in order_data or not order_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate items
    if "items" in order_data:
        items = order_data["items"]
        if not isinstance(items, list) or len(items) == 0:
            errors.append("Order must contain at least one item")
        
        for i, item in enumerate(items):
            if "quantity" not in item or item["quantity"] <= 0:
                errors.append(f"Item {i+1}: Invalid quantity")
            if "price" not in item or item["price"] <= 0:
                errors.append(f"Item {i+1}: Invalid price")
    
    # Validate amount
    if "total_amount" in order_data:
        try:
            amount = float(order_data["total_amount"])
            if amount <= 0:
                errors.append("Total amount must be positive")
            elif amount > 10000:
                warnings.append("High value order requires manager approval")
        except (ValueError, TypeError):
            errors.append("Invalid total amount format")
    
    # Validate addresses
    address_fields = ["street", "city", "state", "zip"]
    for addr_type in ["shipping_address", "billing_address"]:
        if addr_type in order_data:
            address = order_data[addr_type]
            for field in address_fields:
                if field not in address or not address[field]:
                    errors.append(f"{addr_type}: Missing {field}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validated_at": time.time()
    }


@tool
def check_inventory_availability(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check inventory availability for order items."""
    time.sleep(0.15)  # Simulate inventory check
    
    availability_results = []
    all_available = True
    
    # Mock inventory data
    inventory = {
        "item_001": {"available": 150, "reserved": 25},
        "item_002": {"available": 300, "reserved": 50},
        "item_003": {"available": 75, "reserved": 10},
        "item_004": {"available": 0, "reserved": 0}  # Out of stock
    }
    
    for item in items:
        item_id = item.get("item_id", item.get("sku", "unknown"))
        quantity = item.get("quantity", 0)
        
        inv_data = inventory.get(item_id, {"available": 0, "reserved": 0})
        available = inv_data["available"] - inv_data["reserved"]
        
        item_result = {
            "item_id": item_id,
            "name": item.get("name", "Unknown"),
            "requested_quantity": quantity,
            "available_quantity": available,
            "sufficient": available >= quantity,
            "estimated_restock": None
        }
        
        if not item_result["sufficient"]:
            all_available = False
            # Simulate restock date for out of stock items
            item_result["estimated_restock"] = time.time() + 86400 * 7  # 7 days
        
        availability_results.append(item_result)
    
    return {
        "all_available": all_available,
        "items": availability_results,
        "checked_at": time.time()
    }


@tool
def process_payment(payment_info: Dict[str, Any], amount: float) -> Dict[str, Any]:
    """Process payment for the order."""
    time.sleep(0.3)  # Simulate payment processing
    
    # Simulate payment processing with occasional failures
    import random
    
    # 10% chance of payment failure for testing
    payment_success = random.random() > 0.1
    
    if payment_success:
        return {
            "success": True,
            "payment_id": f"pay_{int(time.time())}",
            "transaction_id": f"txn_{int(time.time())}",
            "amount": amount,
            "currency": "USD",
            "processor": payment_info.get("processor", "stripe"),
            "fees": round(amount * 0.029 + 0.30, 2),  # Typical credit card fees
            "processed_at": time.time()
        }
    else:
        return {
            "success": False,
            "error_code": "payment_declined",
            "error_message": "Your payment method was declined. Please try a different payment method.",
            "retry_allowed": True,
            "processor": payment_info.get("processor", "stripe"),
            "attempted_at": time.time()
        }


@tool
def reserve_inventory(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reserve inventory for order items."""
    time.sleep(0.1)
    
    reservations = []
    all_reserved = True
    
    for item in items:
        item_id = item.get("item_id", item.get("sku"))
        quantity = item.get("quantity", 0)
        
        # Simulate reservation
        reservation_id = f"res_{item_id}_{int(time.time())}"
        
        reservations.append({
            "item_id": item_id,
            "quantity": quantity,
            "reservation_id": reservation_id,
            "expires_at": time.time() + 3600,  # 1 hour expiration
            "warehouse": "WH_001"
        })
    
    return {
        "all_reserved": all_reserved,
        "reservations": reservations,
        "reserved_at": time.time()
    }


@tool
def create_fulfillment_order(order_id: str, items: List[Dict[str, Any]], address: Dict[str, str]) -> Dict[str, Any]:
    """Create fulfillment order in warehouse system."""
    time.sleep(0.2)
    
    fulfillment_id = f"ff_{order_id}_{int(time.time())}"
    
    return {
        "fulfillment_id": fulfillment_id,
        "warehouse": "WH_001",
        "estimated_pickup_time": time.time() + 86400,  # 1 day
        "items": items,
        "shipping_address": address,
        "priority": "standard",
        "created_at": time.time()
    }


@tool
def create_shipping_label(fulfillment_id: str, address: Dict[str, str], items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create shipping label and schedule pickup."""
    time.sleep(0.2)
    
    # Calculate shipping method based on total weight/value
    total_value = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
    
    if total_value > 500:
        method = "express"
        carrier = "FedEx"
        estimated_days = 2
    else:
        method = "ground"
        carrier = "UPS"
        estimated_days = 5
    
    tracking_number = f"1Z999AA{int(time.time())}"
    
    return {
        "tracking_number": tracking_number,
        "carrier": carrier,
        "service": method,
        "estimated_delivery": time.time() + (86400 * estimated_days),
        "shipping_cost": 9.99 if method == "ground" else 24.99,
        "label_url": f"https://shipping.example.com/labels/{tracking_number}",
        "created_at": time.time()
    }


@tool
def send_customer_notification(customer_id: str, notification_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Send notification to customer."""
    time.sleep(0.05)
    
    notification_id = f"notif_{int(time.time())}"
    
    # Simulate different notification types
    notifications = {
        "order_confirmed": "Your order has been confirmed and is being processed.",
        "payment_processed": "Payment has been successfully processed.",
        "order_shipped": f"Your order has shipped! Tracking: {data.get('tracking_number', 'N/A')}",
        "order_delivered": "Your order has been delivered. Thank you for your business!",
        "payment_failed": "Payment failed. Please update your payment method.",
        "inventory_unavailable": "Some items in your order are temporarily unavailable."
    }
    
    message = notifications.get(notification_type, "Order status update")
    
    return {
        "notification_id": notification_id,
        "type": notification_type,
        "message": message,
        "delivery_method": "email",
        "sent_at": time.time(),
        "status": "delivered"
    }


@durable.flow
async def process_order_workflow(ctx: DurableContext, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete order processing workflow with error handling and retries.
    
    Orchestrates the entire order lifecycle from validation through delivery notification.
    """
    
    # Initialize workflow state
    workflow_id = f"wf_{order_data['order_id']}_{int(time.time())}"
    start_time = time.time()
    
    await ctx.state.set("workflow_id", workflow_id)
    await ctx.state.set("start_time", start_time)
    await ctx.state.set("current_stage", ProcessingStage.VALIDATION.value)
    
    # Convert to OrderData for type safety
    order = OrderData(
        order_id=order_data["order_id"],
        customer_id=order_data["customer_id"],
        items=order_data["items"],
        total_amount=Decimal(str(order_data["total_amount"])),
        shipping_address=order_data["shipping_address"],
        billing_address=order_data["billing_address"],
        payment_method=order_data["payment_method"],
        priority=order_data.get("priority", "normal"),
        special_instructions=order_data.get("special_instructions", "")
    )
    
    results = []
    
    try:
        # Stage 1: Order Validation
        print(f"🔍 Starting order validation for {order.order_id}")
        await ctx.state.set("current_stage", ProcessingStage.VALIDATION.value)
        
        validation_start = time.time()
        validation_result = await ctx.call(validate_order_data, order_data)
        validation_time = time.time() - validation_start
        
        validation_processing = ProcessingResult(
            stage=ProcessingStage.VALIDATION,
            success=validation_result["valid"],
            data=validation_result,
            errors=validation_result["errors"],
            warnings=validation_result["warnings"],
            processing_time=validation_time
        )
        results.append(validation_processing)
        
        if not validation_result["valid"]:
            # Send failure notification
            await ctx.call(send_customer_notification, order.customer_id, "validation_failed", {
                "errors": validation_result["errors"]
            })
            
            return {
                "workflow_id": workflow_id,
                "order_id": order.order_id,
                "status": "failed",
                "stage": ProcessingStage.VALIDATION.value,
                "results": [result.__dict__ for result in results],
                "total_time": time.time() - start_time
            }
        
        # Stage 2: Inventory Check
        print(f"📦 Checking inventory for {order.order_id}")
        await ctx.state.set("current_stage", ProcessingStage.INVENTORY.value)
        
        inventory_start = time.time()
        inventory_result = await ctx.call(check_inventory_availability, order.items)
        inventory_time = time.time() - inventory_start
        
        inventory_processing = ProcessingResult(
            stage=ProcessingStage.INVENTORY,
            success=inventory_result["all_available"],
            data=inventory_result,
            processing_time=inventory_time
        )
        results.append(inventory_processing)
        
        if not inventory_result["all_available"]:
            # Send inventory unavailable notification
            await ctx.call(send_customer_notification, order.customer_id, "inventory_unavailable", {
                "unavailable_items": [item for item in inventory_result["items"] if not item["sufficient"]]
            })
            
            return {
                "workflow_id": workflow_id,
                "order_id": order.order_id,
                "status": "failed",
                "stage": ProcessingStage.INVENTORY.value,
                "results": [result.__dict__ for result in results],
                "total_time": time.time() - start_time
            }
        
        # Stage 3: Payment Processing
        print(f"💳 Processing payment for {order.order_id}")
        await ctx.state.set("current_stage", ProcessingStage.PAYMENT.value)
        
        payment_start = time.time()
        payment_result = await ctx.call(process_payment, order.payment_method, float(order.total_amount))
        payment_time = time.time() - payment_start
        
        payment_processing = ProcessingResult(
            stage=ProcessingStage.PAYMENT,
            success=payment_result["success"],
            data=payment_result,
            processing_time=payment_time
        )
        results.append(payment_processing)
        
        if not payment_result["success"]:
            # Send payment failure notification
            await ctx.call(send_customer_notification, order.customer_id, "payment_failed", payment_result)
            
            return {
                "workflow_id": workflow_id,
                "order_id": order.order_id,
                "status": "failed",
                "stage": ProcessingStage.PAYMENT.value,
                "results": [result.__dict__ for result in results],
                "total_time": time.time() - start_time
            }
        
        # Payment successful - send confirmation
        await ctx.call(send_customer_notification, order.customer_id, "payment_processed", payment_result)
        
        # Stage 4: Reserve Inventory
        print(f"🔒 Reserving inventory for {order.order_id}")
        
        reserve_start = time.time()
        reserve_result = await ctx.call(reserve_inventory, order.items)
        reserve_time = time.time() - reserve_start
        
        reserve_processing = ProcessingResult(
            stage=ProcessingStage.INVENTORY,
            success=reserve_result["all_reserved"],
            data=reserve_result,
            processing_time=reserve_time
        )
        results.append(reserve_processing)
        
        # Stage 5: Create Fulfillment Order
        print(f"📋 Creating fulfillment order for {order.order_id}")
        await ctx.state.set("current_stage", ProcessingStage.FULFILLMENT.value)
        
        fulfillment_start = time.time()
        fulfillment_result = await ctx.call(create_fulfillment_order, order.order_id, order.items, order.shipping_address)
        fulfillment_time = time.time() - fulfillment_start
        
        fulfillment_processing = ProcessingResult(
            stage=ProcessingStage.FULFILLMENT,
            success=True,
            data=fulfillment_result,
            processing_time=fulfillment_time
        )
        results.append(fulfillment_processing)
        
        # Send order confirmed notification
        await ctx.call(send_customer_notification, order.customer_id, "order_confirmed", {
            "fulfillment_id": fulfillment_result["fulfillment_id"],
            "estimated_pickup": fulfillment_result["estimated_pickup_time"]
        })
        
        # Stage 6: Create Shipping Label
        print(f"🚚 Creating shipping label for {order.order_id}")
        await ctx.state.set("current_stage", ProcessingStage.SHIPPING.value)
        
        shipping_start = time.time()
        shipping_result = await ctx.call(
            create_shipping_label,
            fulfillment_result["fulfillment_id"],
            order.shipping_address,
            order.items
        )
        shipping_time = time.time() - shipping_start
        
        shipping_processing = ProcessingResult(
            stage=ProcessingStage.SHIPPING,
            success=True,
            data=shipping_result,
            processing_time=shipping_time
        )
        results.append(shipping_processing)
        
        # Send shipping notification
        await ctx.call(send_customer_notification, order.customer_id, "order_shipped", shipping_result)
        
        # Stage 7: Completion
        await ctx.state.set("current_stage", ProcessingStage.COMPLETION.value)
        
        # Store final state
        await ctx.state.set("payment_id", payment_result["payment_id"])
        await ctx.state.set("fulfillment_id", fulfillment_result["fulfillment_id"])
        await ctx.state.set("tracking_number", shipping_result["tracking_number"])
        
        total_time = time.time() - start_time
        
        print(f"✅ Order {order.order_id} processing completed in {total_time:.2f}s")
        
        return {
            "workflow_id": workflow_id,
            "order_id": order.order_id,
            "status": "completed",
            "stage": ProcessingStage.COMPLETION.value,
            "results": [result.__dict__ for result in results],
            "payment_id": payment_result["payment_id"],
            "fulfillment_id": fulfillment_result["fulfillment_id"],
            "tracking_number": shipping_result["tracking_number"],
            "estimated_delivery": shipping_result["estimated_delivery"],
            "total_time": total_time
        }
        
    except Exception as e:
        # Handle any unexpected errors
        error_time = time.time() - start_time
        
        # Send error notification
        await ctx.call(send_customer_notification, order.customer_id, "processing_error", {
            "error": str(e),
            "order_id": order.order_id
        })
        
        return {
            "workflow_id": workflow_id,
            "order_id": order.order_id,
            "status": "error",
            "stage": await ctx.state.get("current_stage", "unknown"),
            "error": str(e),
            "results": [result.__dict__ for result in results],
            "total_time": error_time
        }


# Example usage and testing
async def main():
    """Test the order processing workflow."""
    
    print("🧪 Testing Order Processing Workflow")
    print("=" * 50)
    
    # Test successful order
    test_order = {
        "order_id": "ORD_TEST_001",
        "customer_id": "cust_001",
        "items": [
            {
                "item_id": "item_001",
                "name": "Wireless Headphones",
                "sku": "WH-001",
                "quantity": 1,
                "price": 199.99
            },
            {
                "item_id": "item_002",
                "name": "Phone Case",
                "sku": "PC-001",
                "quantity": 2,
                "price": 29.99
            }
        ],
        "total_amount": 259.97,
        "shipping_address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105"
        },
        "billing_address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105"
        },
        "payment_method": {
            "type": "credit_card",
            "processor": "stripe",
            "token": "tok_123456"
        },
        "priority": "normal"
    }
    
    # Create a mock context for testing
    class MockContext:
        def __init__(self):
            self.state_data = {}
        
        async def call(self, func, *args, **kwargs):
            return func(*args, **kwargs)
        
        @property
        def state(self):
            return self
        
        async def set(self, key, value):
            self.state_data[key] = value
        
        async def get(self, key, default=None):
            return self.state_data.get(key, default)
    
    # Mock the workflow function call
    ctx = MockContext()
    
    print(f"🚀 Processing order {test_order['order_id']}")
    result = await process_order_workflow(ctx, test_order)
    
    print(f"\n📊 Workflow Result:")
    print(f"   Status: {result['status']}")
    print(f"   Order ID: {result['order_id']}")
    print(f"   Final Stage: {result['stage']}")
    print(f"   Total Time: {result['total_time']:.2f}s")
    
    if "payment_id" in result:
        print(f"   Payment ID: {result['payment_id']}")
    if "tracking_number" in result:
        print(f"   Tracking: {result['tracking_number']}")
    
    print(f"\n📋 Processing Stages:")
    for stage_result in result['results']:
        print(f"   {stage_result['stage']}: {'✅' if stage_result['success'] else '❌'} "
              f"({stage_result['processing_time']:.2f}s)")
        if stage_result['errors']:
            print(f"      Errors: {', '.join(stage_result['errors'])}")
        if stage_result['warnings']:
            print(f"      Warnings: {', '.join(stage_result['warnings'])}")


if __name__ == "__main__":
    asyncio.run(main())