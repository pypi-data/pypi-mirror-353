"""
OrderTracker - Durable Object for order lifecycle management

Tracks order state, status changes, and business events throughout the order lifecycle.
Demonstrates state machine patterns and event-driven durable object architecture.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal

from agnt5.durable import durable, DurableObject


class OrderStatus(Enum):
    """Order status state machine."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_FAILED = "payment_failed"
    PROCESSING = "processing"
    FULFILLMENT = "fulfillment"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUND_REQUESTED = "refund_requested"
    REFUNDED = "refunded"
    RETURNED = "returned"


class EventType(Enum):
    """Types of order events."""
    CREATED = "created"
    CONFIRMED = "confirmed"
    PAYMENT_ATTEMPTED = "payment_attempted"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    INVENTORY_RESERVED = "inventory_reserved"
    FULFILLMENT_STARTED = "fulfillment_started"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUND_REQUESTED = "refund_requested"
    REFUND_PROCESSED = "refund_processed"
    CUSTOMER_CONTACTED = "customer_contacted"
    ISSUE_REPORTED = "issue_reported"


@dataclass
class OrderEvent:
    """Order lifecycle event."""
    event_id: str
    event_type: EventType
    timestamp: float
    actor: str  # system, customer, agent, external_service
    details: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OrderItem:
    """Individual order item."""
    item_id: str
    name: str
    sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: str = "pending"  # pending, reserved, fulfilled, shipped


@dataclass
class ShippingInfo:
    """Shipping and delivery information."""
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_method: str = "standard"
    estimated_delivery: Optional[float] = None
    actual_delivery: Optional[float] = None
    shipping_address: Dict[str, str] = None
    
    def __post_init__(self):
        if self.shipping_address is None:
            self.shipping_address = {}


@dataclass
class PaymentInfo:
    """Payment processing information."""
    payment_method: str
    payment_id: Optional[str] = None
    payment_status: str = "pending"
    amount: Decimal = Decimal("0.00")
    currency: str = "USD"
    processor: str = "stripe"
    transaction_fees: Decimal = Decimal("0.00")


@durable.object
class OrderTracker(DurableObject):
    """
    Durable order tracking object with state machine and event history.
    
    Maintains complete order lifecycle with automatic state transitions,
    event logging, and business rule enforcement.
    """
    
    def __init__(self, order_id: str, customer_id: str):
        super().__init__()
        self.order_id = order_id
        self.customer_id = customer_id
        self.created_at = time.time()
        self.last_updated = time.time()
        
        # Core order data
        self.status = OrderStatus.PENDING
        self.items: List[OrderItem] = []
        self.total_amount = Decimal("0.00")
        self.tax_amount = Decimal("0.00")
        self.shipping_amount = Decimal("0.00")
        
        # Order components
        self.payment_info: Optional[PaymentInfo] = None
        self.shipping_info = ShippingInfo()
        
        # Event tracking
        self.events: List[OrderEvent] = []
        self.state_history: List[Dict[str, Any]] = []
        
        # Business metrics
        self.retry_count = 0
        self.max_retries = 3
        self.escalation_level = 0
        self.priority = "normal"  # low, normal, high, urgent
        
        # Flags and indicators
        self.requires_manual_review = False
        self.fraud_check_passed = True
        self.customer_notified = False
        
        print(f"📦 Created order tracker {self.order_id}")
        
        # Log creation event
        asyncio.create_task(self._add_event(
            EventType.CREATED,
            "system",
            {"customer_id": customer_id, "initial_status": self.status.value}
        ))
    
    async def add_item(self, item_id: str, name: str, sku: str, quantity: int, unit_price: Decimal) -> None:
        """Add an item to the order."""
        total_price = unit_price * quantity
        
        item = OrderItem(
            item_id=item_id,
            name=name,
            sku=sku,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        
        self.items.append(item)
        self.total_amount += total_price
        self.last_updated = time.time()
        
        await self._add_event(
            EventType.CREATED,
            "customer",
            {
                "item_added": {
                    "item_id": item_id,
                    "name": name,
                    "quantity": quantity,
                    "unit_price": float(unit_price),
                    "total_price": float(total_price)
                }
            }
        )
        
        await self.save()
        print(f"➕ Added item {name} (x{quantity}) to order {self.order_id}")
    
    async def confirm_order(self, payment_info: Dict[str, Any]) -> bool:
        """Confirm the order and initiate payment processing."""
        if self.status != OrderStatus.PENDING:
            print(f"❌ Cannot confirm order {self.order_id} - current status: {self.status.value}")
            return False
        
        # Set payment information
        self.payment_info = PaymentInfo(
            payment_method=payment_info["method"],
            amount=self.total_amount,
            currency=payment_info.get("currency", "USD"),
            processor=payment_info.get("processor", "stripe")
        )
        
        # Transition to confirmed
        await self._transition_status(OrderStatus.CONFIRMED, "customer", "Order confirmed by customer")
        
        await self._add_event(
            EventType.CONFIRMED,
            "customer",
            {"payment_method": payment_info["method"], "total_amount": float(self.total_amount)}
        )
        
        await self.save()
        print(f"✅ Confirmed order {self.order_id}")
        return True
    
    async def process_payment(self, payment_result: Dict[str, Any]) -> bool:
        """Process payment and update order status accordingly."""
        if self.status not in [OrderStatus.CONFIRMED, OrderStatus.PAYMENT_FAILED]:
            print(f"❌ Cannot process payment for order {self.order_id} - current status: {self.status.value}")
            return False
        
        # Transition to payment processing
        await self._transition_status(OrderStatus.PAYMENT_PROCESSING, "system", "Payment processing started")
        
        await self._add_event(
            EventType.PAYMENT_ATTEMPTED,
            "system",
            {"processor": self.payment_info.processor if self.payment_info else "unknown"}
        )
        
        # Simulate payment processing
        success = payment_result.get("success", True)
        
        if success:
            # Payment successful
            if self.payment_info:
                self.payment_info.payment_status = "completed"
                self.payment_info.payment_id = payment_result.get("payment_id", f"pay_{int(time.time())}")
                self.payment_info.transaction_fees = Decimal(str(payment_result.get("fees", 0.00)))
            
            await self._transition_status(OrderStatus.PROCESSING, "system", "Payment completed successfully")
            
            await self._add_event(
                EventType.PAYMENT_COMPLETED,
                "system",
                {
                    "payment_id": self.payment_info.payment_id if self.payment_info else None,
                    "amount": float(self.total_amount)
                }
            )
            
            print(f"💳 Payment processed successfully for order {self.order_id}")
        else:
            # Payment failed
            self.retry_count += 1
            
            if self.payment_info:
                self.payment_info.payment_status = "failed"
            
            await self._transition_status(OrderStatus.PAYMENT_FAILED, "system", "Payment processing failed")
            
            await self._add_event(
                EventType.PAYMENT_FAILED,
                "system",
                {
                    "reason": payment_result.get("error", "Payment declined"),
                    "retry_count": self.retry_count
                }
            )
            
            # Check if we should escalate
            if self.retry_count >= self.max_retries:
                self.requires_manual_review = True
                self.escalation_level = 1
            
            print(f"❌ Payment failed for order {self.order_id} (attempt {self.retry_count})")
        
        await self.save()
        return success
    
    async def start_fulfillment(self) -> bool:
        """Start order fulfillment process."""
        if self.status != OrderStatus.PROCESSING:
            print(f"❌ Cannot start fulfillment for order {self.order_id} - current status: {self.status.value}")
            return False
        
        await self._transition_status(OrderStatus.FULFILLMENT, "system", "Fulfillment process started")
        
        # Reserve inventory for all items
        for item in self.items:
            item.status = "reserved"
        
        await self._add_event(
            EventType.INVENTORY_RESERVED,
            "system",
            {"items_reserved": len(self.items)}
        )
        
        await self._add_event(
            EventType.FULFILLMENT_STARTED,
            "system",
            {"fulfillment_location": "warehouse_001"}
        )
        
        await self.save()
        print(f"📋 Started fulfillment for order {self.order_id}")
        return True
    
    async def ship_order(self, shipping_details: Dict[str, Any]) -> bool:
        """Ship the order with tracking information."""
        if self.status != OrderStatus.FULFILLMENT:
            print(f"❌ Cannot ship order {self.order_id} - current status: {self.status.value}")
            return False
        
        # Update shipping information
        self.shipping_info.carrier = shipping_details.get("carrier")
        self.shipping_info.tracking_number = shipping_details.get("tracking_number")
        self.shipping_info.shipping_method = shipping_details.get("method", "standard")
        self.shipping_info.estimated_delivery = shipping_details.get("estimated_delivery")
        
        # Mark all items as shipped
        for item in self.items:
            item.status = "shipped"
        
        await self._transition_status(OrderStatus.SHIPPED, "system", "Order shipped to customer")
        
        await self._add_event(
            EventType.SHIPPED,
            "system",
            {
                "carrier": self.shipping_info.carrier,
                "tracking_number": self.shipping_info.tracking_number,
                "estimated_delivery": self.shipping_info.estimated_delivery
            }
        )
        
        await self.save()
        print(f"🚚 Shipped order {self.order_id} via {self.shipping_info.carrier}")
        return True
    
    async def mark_delivered(self, delivery_confirmation: Dict[str, Any]) -> bool:
        """Mark order as delivered."""
        if self.status not in [OrderStatus.SHIPPED, OrderStatus.IN_TRANSIT]:
            print(f"❌ Cannot mark order {self.order_id} as delivered - current status: {self.status.value}")
            return False
        
        self.shipping_info.actual_delivery = time.time()
        
        await self._transition_status(OrderStatus.DELIVERED, "system", "Order delivered to customer")
        
        await self._add_event(
            EventType.DELIVERED,
            "system",
            {
                "delivery_time": self.shipping_info.actual_delivery,
                "signature": delivery_confirmation.get("signature"),
                "location": delivery_confirmation.get("location")
            }
        )
        
        await self.save()
        print(f"📋 Order {self.order_id} delivered successfully")
        return True
    
    async def request_refund(self, reason: str, amount: Optional[Decimal] = None) -> str:
        """Request a refund for the order."""
        if self.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
            print(f"❌ Cannot refund order {self.order_id} - current status: {self.status.value}")
            return None
        
        refund_amount = amount or self.total_amount
        refund_id = f"REF_{self.order_id}_{int(time.time())}"
        
        await self._transition_status(OrderStatus.REFUND_REQUESTED, "customer", f"Refund requested: {reason}")
        
        await self._add_event(
            EventType.REFUND_REQUESTED,
            "customer",
            {
                "refund_id": refund_id,
                "reason": reason,
                "amount": float(refund_amount)
            }
        )
        
        # Check if refund requires manual review
        if refund_amount > 500 or "fraud" in reason.lower():
            self.requires_manual_review = True
            self.escalation_level = 2
        
        await self.save()
        print(f"💰 Refund requested for order {self.order_id}: {reason}")
        return refund_id
    
    async def cancel_order(self, reason: str, actor: str = "customer") -> bool:
        """Cancel the order."""
        # Can only cancel orders that haven't shipped
        if self.status in [OrderStatus.SHIPPED, OrderStatus.IN_TRANSIT, OrderStatus.DELIVERED]:
            print(f"❌ Cannot cancel order {self.order_id} - order has shipped")
            return False
        
        await self._transition_status(OrderStatus.CANCELLED, actor, f"Order cancelled: {reason}")
        
        await self._add_event(
            EventType.CANCELLED,
            actor,
            {"reason": reason, "cancelled_at": time.time()}
        )
        
        await self.save()
        print(f"❌ Cancelled order {self.order_id}: {reason}")
        return True
    
    async def _transition_status(self, new_status: OrderStatus, actor: str, reason: str) -> None:
        """Internal method to handle status transitions."""
        old_status = self.status
        
        # Record state history
        self.state_history.append({
            "from_status": old_status.value,
            "to_status": new_status.value,
            "timestamp": time.time(),
            "actor": actor,
            "reason": reason
        })
        
        self.status = new_status
        self.last_updated = time.time()
        
        print(f"🔄 Order {self.order_id}: {old_status.value} → {new_status.value}")
    
    async def _add_event(self, event_type: EventType, actor: str, details: Dict[str, Any]) -> None:
        """Internal method to add an event to the order history."""
        event = OrderEvent(
            event_id=f"evt_{int(time.time() * 1000)}",
            event_type=event_type,
            timestamp=time.time(),
            actor=actor,
            details=details
        )
        
        self.events.append(event)
        
        # Keep only the last 50 events to prevent unlimited growth
        if len(self.events) > 50:
            self.events = self.events[-50:]
    
    async def get_order_summary(self) -> Dict[str, Any]:
        """Get a comprehensive order summary."""
        duration = time.time() - self.created_at
        
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "duration": duration,
            "total_amount": float(self.total_amount),
            "item_count": len(self.items),
            "event_count": len(self.events),
            "retry_count": self.retry_count,
            "escalation_level": self.escalation_level,
            "requires_manual_review": self.requires_manual_review,
            "shipping_info": asdict(self.shipping_info) if self.shipping_info else None,
            "payment_status": self.payment_info.payment_status if self.payment_info else None
        }
    
    async def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent order events."""
        recent_events = self.events[-count:] if count > 0 else self.events
        return [asdict(event) for event in recent_events]


# Example usage and testing
async def main():
    """Test the OrderTracker durable object."""
    
    print("🧪 Testing OrderTracker Durable Object")
    print("=" * 50)
    
    # Create a new order tracker
    order = OrderTracker("ORD_12345", "cust_001")
    
    # Add items to the order
    await order.add_item("item_001", "Wireless Headphones", "WH-001", 1, Decimal("199.99"))
    await order.add_item("item_002", "Phone Case", "PC-001", 2, Decimal("29.99"))
    
    # Confirm the order
    payment_info = {
        "method": "credit_card",
        "currency": "USD",
        "processor": "stripe"
    }
    success = await order.confirm_order(payment_info)
    print(f"Order confirmation: {success}")
    
    # Process payment
    payment_result = {"success": True, "payment_id": "pay_12345", "fees": 8.50}
    success = await order.process_payment(payment_result)
    print(f"Payment processing: {success}")
    
    # Start fulfillment
    success = await order.start_fulfillment()
    print(f"Fulfillment started: {success}")
    
    # Ship the order
    shipping_details = {
        "carrier": "UPS",
        "tracking_number": "1Z999AA1234567890",
        "method": "ground",
        "estimated_delivery": time.time() + 86400 * 3  # 3 days
    }
    success = await order.ship_order(shipping_details)
    print(f"Order shipped: {success}")
    
    # Mark as delivered
    delivery_confirmation = {
        "signature": "J.Doe",
        "location": "Front door"
    }
    success = await order.mark_delivered(delivery_confirmation)
    print(f"Order delivered: {success}")
    
    # Get order summary
    summary = await order.get_order_summary()
    print(f"\n📊 Order Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Get recent events
    events = await order.get_recent_events(5)
    print(f"\n📋 Recent Events ({len(events)}):")
    for event in events:
        print(f"   [{event['event_type']}] {event['details']}")
    
    # Test refund scenario
    print(f"\n🔄 Testing refund scenario...")
    
    # Create another order for refund testing
    refund_order = OrderTracker("ORD_67890", "cust_002")
    await refund_order.add_item("item_003", "Laptop", "LAP-001", 1, Decimal("999.99"))
    await refund_order.confirm_order(payment_info)
    await refund_order.process_payment({"success": True, "payment_id": "pay_67890"})
    
    # Request refund
    refund_id = await refund_order.request_refund("Product arrived damaged")
    print(f"Refund ID: {refund_id}")
    
    refund_summary = await refund_order.get_order_summary()
    print(f"Refund order status: {refund_summary['status']}")


if __name__ == "__main__":
    asyncio.run(main())