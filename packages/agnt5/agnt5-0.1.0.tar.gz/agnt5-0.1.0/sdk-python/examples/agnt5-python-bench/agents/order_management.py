"""
Order Management Agent - Order lifecycle and billing operations

Handles order inquiries, modifications, refunds, and billing issues.
Demonstrates complex business logic and external service integration.
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

from agnt5 import Agent, tool
from agnt5.durable import durable, DurableContext


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class RefundReason(Enum):
    """Refund reason enumeration."""
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"
    SHIPPING_DELAY = "shipping_delay"
    DUPLICATE_ORDER = "duplicate_order"


@dataclass
class OrderInfo:
    """Order information structure."""
    order_id: str
    customer_id: str
    status: OrderStatus
    items: List[Dict[str, Any]]
    total_amount: Decimal
    shipping_address: Dict[str, str]
    payment_method: str
    order_date: str
    expected_delivery: Optional[str] = None
    tracking_number: Optional[str] = None


@dataclass
class OrderRequest:
    """Order management request structure."""
    customer_id: str
    order_id: Optional[str] = None
    request_type: str = "inquiry"  # inquiry, modify, cancel, refund, track
    details: str = ""
    refund_reason: Optional[RefundReason] = None
    priority: str = "normal"


@tool
def lookup_order(order_id: str) -> Optional[Dict[str, Any]]:
    """Look up order information by order ID."""
    time.sleep(0.1)  # Simulate database lookup
    
    # Mock order data
    orders = {
        "ORD_001": {
            "order_id": "ORD_001",
            "customer_id": "cust_001",
            "status": "shipped",
            "items": [
                {"name": "Wireless Headphones", "quantity": 1, "price": 199.99},
                {"name": "Phone Case", "quantity": 2, "price": 29.99}
            ],
            "total_amount": 259.97,
            "shipping_address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94105"
            },
            "payment_method": "Credit Card ****1234",
            "order_date": "2024-01-10",
            "expected_delivery": "2024-01-15",
            "tracking_number": "1Z999AA1234567890"
        },
        "ORD_002": {
            "order_id": "ORD_002",
            "customer_id": "cust_002", 
            "status": "processing",
            "items": [
                {"name": "Laptop Stand", "quantity": 1, "price": 89.99}
            ],
            "total_amount": 89.99,
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Austin",
                "state": "TX", 
                "zip": "73301"
            },
            "payment_method": "PayPal",
            "order_date": "2024-01-12",
            "expected_delivery": "2024-01-18"
        }
    }
    
    return orders.get(order_id)


@tool
def track_shipment(tracking_number: str) -> Dict[str, Any]:
    """Track shipment status using tracking number."""
    time.sleep(0.15)  # Simulate shipping API call
    
    # Mock tracking data
    tracking_info = {
        "tracking_number": tracking_number,
        "status": "in_transit",
        "current_location": "Distribution Center - Oakland, CA",
        "estimated_delivery": "2024-01-15 by 8:00 PM",
        "updates": [
            {"date": "2024-01-13", "location": "San Francisco, CA", "status": "Package shipped"},
            {"date": "2024-01-14", "location": "Oakland, CA", "status": "In transit"},
            {"date": "2024-01-14", "location": "Oakland, CA", "status": "Out for delivery"}
        ]
    }
    
    return tracking_info


@tool
def check_refund_eligibility(order_id: str, reason: str) -> Dict[str, Any]:
    """Check if an order is eligible for refund."""
    time.sleep(0.1)
    
    order = lookup_order(order_id)
    if not order:
        return {"eligible": False, "reason": "Order not found"}
    
    # Business rules for refund eligibility
    if order["status"] in ["cancelled", "refunded"]:
        return {"eligible": False, "reason": "Order already cancelled or refunded"}
    
    # Calculate days since order
    order_date = order["order_date"]  # Would parse in real implementation
    days_since_order = 5  # Mock calculation
    
    # Different rules by reason
    if reason == "defective":
        return {"eligible": True, "refund_amount": order["total_amount"], "processing_time": "3-5 business days"}
    elif reason == "wrong_item":
        return {"eligible": True, "refund_amount": order["total_amount"], "processing_time": "5-7 business days"} 
    elif reason == "changed_mind":
        if days_since_order <= 30 and order["status"] != "delivered":
            return {"eligible": True, "refund_amount": order["total_amount"] * 0.85, "processing_time": "7-10 business days"}
        else:
            return {"eligible": False, "reason": "Return window expired or item delivered"}
    else:
        return {"eligible": True, "refund_amount": order["total_amount"], "processing_time": "5-7 business days"}


@tool
def process_refund(order_id: str, amount: float, reason: str) -> str:
    """Process a refund for an order."""
    time.sleep(0.2)  # Simulate payment processing
    
    refund_id = f"REF_{int(time.time())}"
    
    print(f"💰 Processing refund {refund_id}")
    print(f"   Order: {order_id}")
    print(f"   Amount: ${amount:.2f}")
    print(f"   Reason: {reason}")
    
    return refund_id


@tool
def check_inventory(item_name: str) -> Dict[str, Any]:
    """Check inventory levels for an item."""
    time.sleep(0.05)
    
    # Mock inventory data
    inventory = {
        "Wireless Headphones": {"available": 150, "reserved": 25, "location": "Warehouse A"},
        "Phone Case": {"available": 500, "reserved": 50, "location": "Warehouse B"},
        "Laptop Stand": {"available": 75, "reserved": 10, "location": "Warehouse A"}
    }
    
    return inventory.get(item_name, {"available": 0, "reserved": 0, "location": "Unknown"})


@tool
def modify_order(order_id: str, modifications: Dict[str, Any]) -> bool:
    """Attempt to modify an order if possible."""
    time.sleep(0.1)
    
    order = lookup_order(order_id)
    if not order:
        return False
    
    # Can only modify orders that haven't shipped
    if order["status"] in ["shipped", "delivered", "cancelled"]:
        return False
    
    print(f"📝 Modified order {order_id}")
    print(f"   Changes: {modifications}")
    
    return True


class OrderManagementAgent:
    """Specialized order management agent with business logic capabilities."""
    
    def __init__(self, model: str = "anthropic/claude-3-5-sonnet"):
        self.agent = Agent(
            name="order-management",
            model=model,
            system_prompt="""You are an expert order management specialist. Your responsibilities include:

1. Order status inquiries and tracking
2. Order modifications and cancellations
3. Refund processing and eligibility assessment
4. Billing issue resolution
5. Inventory checks and availability
6. Shipping and delivery coordination

Your approach:
1. Always look up order details first
2. Explain order status clearly with tracking info
3. Check eligibility before processing refunds
4. Provide clear timelines and expectations  
5. Offer alternatives when requests can't be fulfilled
6. Ensure compliance with return/refund policies

Be helpful, accurate, and always explain the business rules when declining requests.""",
            tools=[
                lookup_order,
                track_shipment,
                check_refund_eligibility,
                process_refund,
                check_inventory,
                modify_order
            ],
            temperature=0.4  # Moderate creativity for customer service
        )
    
    async def handle_request(self, request: OrderRequest) -> Dict[str, Any]:
        """Handle an order management request."""
        
        # Build context with order information if provided
        context_parts = [
            f"Order Management Request:",
            f"Customer ID: {request.customer_id}",
            f"Request Type: {request.request_type}",
            f"Priority: {request.priority}",
            f"Details: {request.details}"
        ]
        
        if request.order_id:
            context_parts.append(f"Order ID: {request.order_id}")
        
        if request.refund_reason:
            context_parts.append(f"Refund Reason: {request.refund_reason.value}")
        
        context_parts.append("""
        Please help this customer with their order-related request:
        1. Look up order details if order ID provided
        2. Provide accurate status and tracking information
        3. Check eligibility for any requested changes
        4. Process requests according to business rules
        5. Explain any limitations or requirements clearly
        """)
        
        context = "\n".join(context_parts)
        
        # Process the request
        response = await self.agent.run(context)
        
        # Determine resolution status based on request type
        resolution_status = self._determine_resolution_status(request, response.content)
        
        # Extract any actions taken from the response
        actions_taken = self._extract_actions(response.content)
        
        return {
            "agent": "order_management",
            "response": response.content,
            "request_type": request.request_type,
            "actions_taken": actions_taken,
            "resolution_status": resolution_status,
            "requires_followup": self._requires_followup(request, response.content)
        }
    
    def _determine_resolution_status(self, request: OrderRequest, response: str) -> str:
        """Determine the resolution status based on the request and response."""
        
        # Check for successful actions in response
        success_indicators = ["processed", "approved", "completed", "confirmed"]
        failure_indicators = ["cannot", "unable", "not eligible", "denied", "failed"]
        
        response_lower = response.lower()
        
        if any(indicator in response_lower for indicator in success_indicators):
            return "resolved"
        elif any(indicator in response_lower for indicator in failure_indicators):
            return "declined"
        else:
            return "in_progress"
    
    def _extract_actions(self, response: str) -> List[str]:
        """Extract actions taken from the response."""
        actions = []
        
        # Look for action indicators in the response
        if "refund" in response.lower() and "processed" in response.lower():
            actions.append("Refund processed")
        if "tracking" in response.lower():
            actions.append("Tracking information provided")
        if "modified" in response.lower():
            actions.append("Order modified")
        if "cancelled" in response.lower():
            actions.append("Order cancelled")
        if "eligibility" in response.lower():
            actions.append("Eligibility checked")
        
        return actions
    
    def _requires_followup(self, request: OrderRequest, response: str) -> bool:
        """Determine if the request requires follow-up."""
        
        # Refunds and cancellations typically need follow-up
        if request.request_type in ["refund", "cancel"]:
            return True
        
        # Check if response indicates pending actions
        followup_indicators = ["will process", "pending", "follow up", "contact you"]
        
        return any(indicator in response.lower() for indicator in followup_indicators)


# Durable function wrapper for worker registration
@durable.function
async def handle_order_request(ctx: DurableContext, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Durable wrapper for order management requests."""
    
    # Convert dict to OrderRequest
    refund_reason = None
    if request_data.get("refund_reason"):
        refund_reason = RefundReason(request_data["refund_reason"])
    
    request = OrderRequest(
        customer_id=request_data["customer_id"],
        order_id=request_data.get("order_id"),
        request_type=request_data.get("request_type", "inquiry"),
        details=request_data.get("details", ""),
        refund_reason=refund_reason,
        priority=request_data.get("priority", "normal")
    )
    
    # Create agent and process request
    agent = OrderManagementAgent()
    response = await agent.handle_request(request)
    
    # Store order interaction in context state
    await ctx.state.set("order_interaction", {
        "timestamp": time.time(),
        "customer_id": request.customer_id,
        "order_id": request.order_id,
        "request_type": request.request_type,
        "resolution_status": response["resolution_status"],
        "actions_taken": response["actions_taken"]
    })
    
    return response


# Example usage and testing
async def main():
    """Test the order management agent."""
    
    test_requests = [
        {
            "customer_id": "cust_001",
            "order_id": "ORD_001",
            "request_type": "track",
            "details": "I want to know where my order is",
            "priority": "normal"
        },
        {
            "customer_id": "cust_001", 
            "order_id": "ORD_001",
            "request_type": "refund",
            "details": "The headphones arrived damaged",
            "refund_reason": "defective",
            "priority": "high"
        },
        {
            "customer_id": "cust_002",
            "order_id": "ORD_002",
            "request_type": "modify",
            "details": "I want to change the shipping address",
            "priority": "normal"
        },
        {
            "customer_id": "cust_001",
            "request_type": "inquiry",
            "details": "Do you have wireless headphones in stock?",
            "priority": "normal"
        }
    ]
    
    agent = OrderManagementAgent()
    
    for i, test_data in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"Order Test {i}: {test_data['request_type']} - {test_data['priority']}")
        print(f"Details: {test_data['details']}")
        if test_data.get("order_id"):
            print(f"Order ID: {test_data['order_id']}")
        print(f"{'='*60}")
        
        request = OrderRequest(**test_data)
        response = await agent.handle_request(request)
        
        print(f"Response: {response['response'][:200]}...")
        print(f"Actions Taken: {response['actions_taken']}")
        print(f"Resolution Status: {response['resolution_status']}")
        print(f"Requires Follow-up: {response['requires_followup']}")


if __name__ == "__main__":
    asyncio.run(main())