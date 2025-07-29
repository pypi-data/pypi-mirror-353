"""
Customer Service Agent - Primary support interface

Handles initial customer inquiries, basic troubleshooting, and routing to specialized agents.
Demonstrates agent creation, tool usage, and handoff patterns.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from agnt5 import Agent, tool
from agnt5.durable import durable, DurableContext
from agnt5.types import Message


@dataclass
class CustomerRequest:
    """Customer service request structure."""
    customer_id: str
    message: str
    priority: str = "normal"  # low, normal, high, urgent
    category: str = "general"  # general, technical, billing, order
    metadata: Dict[str, Any] = None


@dataclass
class ServiceResponse:
    """Customer service response structure."""
    agent: str
    response: str
    actions_taken: List[str]
    handoff_required: bool = False
    handoff_agent: Optional[str] = None
    resolution_status: str = "in_progress"  # in_progress, resolved, escalated


@tool
def search_knowledge_base(query: str) -> str:
    """Search internal knowledge base for answers."""
    # Simulate knowledge base search
    time.sleep(0.1)  # Simulate API call latency
    
    knowledge_responses = {
        "password": "To reset your password: 1) Go to login page 2) Click 'Forgot Password' 3) Check your email",
        "refund": "Refund requests are processed within 3-5 business days. We'll need your order number.",
        "shipping": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days.",
        "account": "Account issues can usually be resolved by clearing your browser cache and cookies.",
        "billing": "For billing questions, please provide your invoice number and we'll look into it.",
    }
    
    # Simple keyword matching
    for keyword, response in knowledge_responses.items():
        if keyword.lower() in query.lower():
            return f"Knowledge Base Result: {response}"
    
    return "No specific knowledge base entry found. Please provide more details."


@tool
def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """Retrieve customer information and history."""
    # Simulate customer database lookup
    time.sleep(0.05)
    
    # Mock customer data
    customers = {
        "cust_001": {
            "name": "John Doe",
            "tier": "premium",
            "orders": 15,
            "last_contact": "2024-01-10",
            "issues": ["billing_2024_01", "shipping_2024_02"]
        },
        "cust_002": {
            "name": "Jane Smith", 
            "tier": "standard",
            "orders": 3,
            "last_contact": "2024-01-15",
            "issues": []
        }
    }
    
    return customers.get(customer_id, {
        "name": "Unknown Customer",
        "tier": "standard", 
        "orders": 0,
        "last_contact": "never",
        "issues": []
    })


@tool
def create_support_ticket(customer_id: str, issue_type: str, description: str, priority: str = "normal") -> str:
    """Create a support ticket for tracking."""
    # Simulate ticket creation
    ticket_id = f"TICK_{int(time.time())}"
    
    print(f"📋 Created support ticket {ticket_id}")
    print(f"   Customer: {customer_id}")
    print(f"   Type: {issue_type}")
    print(f"   Priority: {priority}")
    
    return ticket_id


class CustomerServiceAgent:
    """Primary customer service agent with knowledge base and handoff capabilities."""
    
    def __init__(self, model: str = "anthropic/claude-3-5-sonnet"):
        self.agent = Agent(
            name="customer-service",
            model=model,
            system_prompt="""You are a helpful customer service representative. Your role is to:

1. Greet customers warmly and professionally
2. Listen to their concerns and gather necessary information
3. Use available tools to search for solutions and customer information
4. Provide clear, accurate answers
5. Create support tickets when needed
6. Determine when to handoff to specialized agents

Handoff Guidelines:
- Technical issues → technical_support agent
- Complex orders/refunds → order_management agent  
- Billing disputes → escalate with priority
- General questions → handle directly

Always be empathetic, solution-focused, and professional.""",
            tools=[search_knowledge_base, get_customer_info, create_support_ticket],
            temperature=0.7
        )
    
    async def handle_request(self, request: CustomerRequest) -> ServiceResponse:
        """Handle a customer service request."""
        
        # Get customer information first
        customer_info = get_customer_info(request.customer_id)
        
        # Build context message
        context = f"""
        Customer Information:
        - Name: {customer_info.get('name', 'Unknown')}
        - Tier: {customer_info.get('tier', 'standard')}
        - Order History: {customer_info.get('orders', 0)} orders
        - Previous Issues: {len(customer_info.get('issues', []))} issues
        
        Current Request:
        - Priority: {request.priority}
        - Category: {request.category}
        - Message: {request.message}
        
        Please help this customer with their request. Use your tools as needed.
        """
        
        # Process the request
        response = await self.agent.run(context)
        
        # Determine if handoff is needed based on category and complexity
        handoff_required, handoff_agent = self._determine_handoff(request, response.content)
        
        # Create ticket for tracking if this is a complex issue
        actions_taken = []
        if request.priority in ["high", "urgent"] or handoff_required:
            ticket_id = create_support_ticket(
                request.customer_id,
                request.category,
                request.message,
                request.priority
            )
            actions_taken.append(f"Created ticket {ticket_id}")
        
        return ServiceResponse(
            agent="customer_service",
            response=response.content,
            actions_taken=actions_taken,
            handoff_required=handoff_required,
            handoff_agent=handoff_agent,
            resolution_status="resolved" if not handoff_required else "escalated"
        )
    
    def _determine_handoff(self, request: CustomerRequest, response: str) -> tuple[bool, Optional[str]]:
        """Determine if request should be handed off to specialized agent."""
        
        # Technical keywords
        technical_keywords = ["error", "bug", "crash", "not working", "broken", "technical"]
        
        # Order-related keywords  
        order_keywords = ["order", "refund", "return", "shipment", "delivery", "tracking"]
        
        # Check for technical issues
        if request.category == "technical" or any(keyword in request.message.lower() for keyword in technical_keywords):
            return True, "technical_support"
        
        # Check for order issues
        if request.category == "order" or any(keyword in request.message.lower() for keyword in order_keywords):
            return True, "order_management"
        
        # Check for urgent/high priority that might need escalation
        if request.priority in ["urgent"] and request.category == "billing":
            return True, "order_management"  # Billing handled by order management
        
        # Check if response indicates need for specialist
        if any(phrase in response.lower() for phrase in ["need to transfer", "specialist", "escalate"]):
            return True, "technical_support"
        
        return False, None


# Durable function wrapper for worker registration
@durable.function
async def handle_customer_request(ctx: DurableContext, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Durable wrapper for customer service requests."""
    
    # Convert dict to CustomerRequest
    request = CustomerRequest(
        customer_id=request_data["customer_id"],
        message=request_data["message"],
        priority=request_data.get("priority", "normal"),
        category=request_data.get("category", "general"),
        metadata=request_data.get("metadata", {})
    )
    
    # Create agent and process request
    agent = CustomerServiceAgent()
    response = await agent.handle_request(request)
    
    # Store interaction in context state for tracking
    await ctx.state.set("last_response", {
        "timestamp": time.time(),
        "customer_id": request.customer_id,
        "resolution_status": response.resolution_status,
        "handoff_required": response.handoff_required
    })
    
    # Convert response to dict for serialization
    return {
        "agent": response.agent,
        "response": response.response,
        "actions_taken": response.actions_taken,
        "handoff_required": response.handoff_required,
        "handoff_agent": response.handoff_agent,
        "resolution_status": response.resolution_status
    }


# Example usage and testing
async def main():
    """Test the customer service agent."""
    
    # Test requests
    test_requests = [
        {
            "customer_id": "cust_001",
            "message": "I can't log into my account, it says my password is wrong",
            "category": "technical",
            "priority": "normal"
        },
        {
            "customer_id": "cust_002", 
            "message": "I want to return my order, it arrived damaged",
            "category": "order",
            "priority": "high"
        },
        {
            "customer_id": "cust_001",
            "message": "When will my order be delivered?",
            "category": "general",
            "priority": "normal"
        }
    ]
    
    agent = CustomerServiceAgent()
    
    for i, test_data in enumerate(test_requests, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {test_data['category']} - {test_data['priority']}")
        print(f"Message: {test_data['message']}")
        print(f"{'='*50}")
        
        request = CustomerRequest(**test_data)
        response = await agent.handle_request(request)
        
        print(f"Response: {response.response}")
        print(f"Actions: {response.actions_taken}")
        print(f"Handoff Required: {response.handoff_required}")
        if response.handoff_required:
            print(f"Handoff Agent: {response.handoff_agent}")
        print(f"Status: {response.resolution_status}")


if __name__ == "__main__":
    asyncio.run(main())