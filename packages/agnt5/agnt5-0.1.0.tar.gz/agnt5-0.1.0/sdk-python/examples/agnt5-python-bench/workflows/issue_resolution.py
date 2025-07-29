"""
Issue Resolution Workflow - Customer support ticket processing

Orchestrates the complete issue resolution pipeline from ticket creation through resolution.
Demonstrates complex workflow patterns with escalation, knowledge base integration, and customer communication.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from agnt5.durable import durable, DurableContext
from agnt5 import tool


class IssuePriority(Enum):
    """Issue priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Issue categories."""
    BILLING = "billing"
    TECHNICAL = "technical"
    PRODUCT = "product"
    SHIPPING = "shipping"
    ACCOUNT = "account"
    OTHER = "other"


class ResolutionStage(Enum):
    """Issue resolution stages."""
    TRIAGE = "triage"
    INVESTIGATION = "investigation"
    SOLUTION_SEARCH = "solution_search"
    CUSTOMER_CONTACT = "customer_contact"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    FOLLOW_UP = "follow_up"
    CLOSURE = "closure"


@dataclass
class IssueData:
    """Issue data structure."""
    ticket_id: str
    customer_id: str
    subject: str
    description: str
    category: IssueCategory
    priority: IssuePriority
    contact_method: str = "email"
    customer_email: str = ""
    customer_phone: str = ""


@dataclass
class ResolutionResult:
    """Result of a resolution stage."""
    stage: ResolutionStage
    success: bool
    data: Dict[str, Any]
    errors: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


# Support tools
@tool
def categorize_and_prioritize_issue(description: str, subject: str) -> Dict[str, Any]:
    """Automatically categorize and prioritize the issue based on content."""
    time.sleep(0.1)
    
    # Simple keyword-based categorization
    description_lower = description.lower()
    subject_lower = subject.lower()
    combined_text = f"{subject_lower} {description_lower}"
    
    # Determine category
    if any(word in combined_text for word in ["bill", "payment", "charge", "refund", "invoice"]):
        category = IssueCategory.BILLING
    elif any(word in combined_text for word in ["bug", "error", "crash", "login", "password"]):
        category = IssueCategory.TECHNICAL
    elif any(word in combined_text for word in ["product", "quality", "defect", "broken"]):
        category = IssueCategory.PRODUCT
    elif any(word in combined_text for word in ["shipping", "delivery", "package", "tracking"]):
        category = IssueCategory.SHIPPING
    elif any(word in combined_text for word in ["account", "profile", "settings"]):
        category = IssueCategory.ACCOUNT
    else:
        category = IssueCategory.OTHER
    
    # Determine priority
    if any(word in combined_text for word in ["urgent", "critical", "down", "broken", "emergency"]):
        priority = IssuePriority.CRITICAL
    elif any(word in combined_text for word in ["important", "asap", "quickly", "soon"]):
        priority = IssuePriority.HIGH
    elif any(word in combined_text for word in ["when possible", "convenience", "minor"]):
        priority = IssuePriority.LOW
    else:
        priority = IssuePriority.MEDIUM
    
    return {
        "category": category.value,
        "priority": priority.value,
        "confidence": 0.85,
        "keywords_found": [word for word in ["bill", "payment", "bug", "shipping"] if word in combined_text],
        "categorized_at": time.time()
    }


@tool
def search_knowledge_base(query: str, category: str) -> Dict[str, Any]:
    """Search the knowledge base for relevant solutions."""
    time.sleep(0.2)
    
    # Mock knowledge base with solutions
    knowledge_base = {
        "billing": [
            {
                "id": "kb_001",
                "title": "How to request a refund",
                "content": "To request a refund, please contact support with your order number...",
                "relevance": 0.9
            },
            {
                "id": "kb_002", 
                "title": "Understanding your invoice",
                "content": "Your invoice includes the following sections...",
                "relevance": 0.7
            }
        ],
        "technical": [
            {
                "id": "kb_101",
                "title": "Password reset instructions",
                "content": "To reset your password: 1. Go to login page 2. Click 'Forgot Password'...",
                "relevance": 0.95
            },
            {
                "id": "kb_102",
                "title": "Browser compatibility issues",
                "content": "Our platform supports Chrome, Firefox, Safari...",
                "relevance": 0.8
            }
        ],
        "shipping": [
            {
                "id": "kb_201",
                "title": "Tracking your order",
                "content": "You can track your order using the tracking number...",
                "relevance": 0.9
            }
        ]
    }
    
    solutions = knowledge_base.get(category, [])
    
    return {
        "solutions_found": len(solutions),
        "solutions": solutions,
        "search_time": 0.2,
        "searched_at": time.time()
    }


@tool
def generate_response_template(category: str, priority: str, solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a response template based on category and available solutions."""
    time.sleep(0.1)
    
    if solutions:
        template = f"""
Dear Customer,

Thank you for contacting us regarding your {category} issue. 

Based on your inquiry, I found the following helpful information:

{chr(10).join([f"• {sol['title']}: {sol['content'][:100]}..." for sol in solutions[:2]])}

Please try these solutions and let us know if you need additional assistance.

Best regards,
Customer Support Team
        """.strip()
    else:
        template = f"""
Dear Customer,

Thank you for contacting us regarding your {category} issue.

We are currently investigating your request and will get back to you shortly with a resolution.

If this is urgent, please contact us at support@example.com.

Best regards,
Customer Support Team
        """.strip()
    
    return {
        "template": template,
        "has_solutions": len(solutions) > 0,
        "estimated_resolution_time": "24 hours" if priority == "high" else "48 hours",
        "generated_at": time.time()
    }


@tool
def send_customer_response(customer_id: str, message: str, contact_method: str) -> Dict[str, Any]:
    """Send response to customer."""
    time.sleep(0.1)
    
    return {
        "message_id": f"msg_{int(time.time())}",
        "delivery_method": contact_method,
        "delivered": True,
        "sent_at": time.time()
    }


@tool
def escalate_to_specialist(ticket_id: str, category: str, reason: str) -> Dict[str, Any]:
    """Escalate ticket to specialist team."""
    time.sleep(0.1)
    
    specialists = {
        "billing": "billing_team",
        "technical": "engineering_team", 
        "product": "product_team",
        "shipping": "logistics_team"
    }
    
    assigned_team = specialists.get(category, "general_support")
    
    return {
        "escalation_id": f"esc_{ticket_id}_{int(time.time())}",
        "assigned_team": assigned_team,
        "escalated_at": time.time(),
        "priority": "high",
        "reason": reason
    }


@tool
def mark_issue_resolved(ticket_id: str, resolution_summary: str, customer_satisfied: bool = True) -> Dict[str, Any]:
    """Mark the issue as resolved."""
    time.sleep(0.05)
    
    return {
        "resolved_at": time.time(),
        "resolution_summary": resolution_summary,
        "customer_satisfied": customer_satisfied,
        "resolution_rating": 4.5 if customer_satisfied else 2.0,
        "ticket_status": "closed"
    }


@durable.flow
async def resolve_issue_workflow(ctx: DurableContext, issue_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete issue resolution workflow with triage, investigation, and customer communication.
    
    Orchestrates the entire support ticket lifecycle from creation through resolution.
    """
    
    # Initialize workflow state
    workflow_id = f"resolution_{issue_data['ticket_id']}_{int(time.time())}"
    start_time = time.time()
    
    await ctx.state.set("workflow_id", workflow_id)
    await ctx.state.set("start_time", start_time)
    await ctx.state.set("current_stage", ResolutionStage.TRIAGE.value)
    
    # Convert to IssueData for type safety
    issue = IssueData(
        ticket_id=issue_data["ticket_id"],
        customer_id=issue_data["customer_id"],
        subject=issue_data["subject"],
        description=issue_data["description"],
        category=IssueCategory(issue_data.get("category", "other")),
        priority=IssuePriority(issue_data.get("priority", "medium")),
        contact_method=issue_data.get("contact_method", "email"),
        customer_email=issue_data.get("customer_email", ""),
        customer_phone=issue_data.get("customer_phone", "")
    )
    
    results = []
    
    try:
        # Stage 1: Triage - Categorize and prioritize
        print(f"🎯 Triaging issue {issue.ticket_id}")
        await ctx.state.set("current_stage", ResolutionStage.TRIAGE.value)
        
        triage_start = time.time()
        triage_result = await ctx.call(categorize_and_prioritize_issue, issue.description, issue.subject)
        triage_time = time.time() - triage_start
        
        # Update issue with auto-detected category/priority if not provided
        if issue.category == IssueCategory.OTHER:
            issue.category = IssueCategory(triage_result["category"])
        if issue.priority == IssuePriority.MEDIUM:
            issue.priority = IssuePriority(triage_result["priority"])
        
        triage_processing = ResolutionResult(
            stage=ResolutionStage.TRIAGE,
            success=True,
            data=triage_result,
            processing_time=triage_time
        )
        results.append(triage_processing)
        
        # Stage 2: Knowledge Base Search
        print(f"🔍 Searching knowledge base for {issue.ticket_id}")
        await ctx.state.set("current_stage", ResolutionStage.SOLUTION_SEARCH.value)
        
        search_start = time.time()
        search_result = await ctx.call(search_knowledge_base, issue.description, issue.category.value)
        search_time = time.time() - search_start
        
        search_processing = ResolutionResult(
            stage=ResolutionStage.SOLUTION_SEARCH,
            success=search_result["solutions_found"] > 0,
            data=search_result,
            processing_time=search_time
        )
        results.append(search_processing)
        
        # Stage 3: Generate Response
        print(f"📝 Generating response for {issue.ticket_id}")
        await ctx.state.set("current_stage", ResolutionStage.CUSTOMER_CONTACT.value)
        
        response_start = time.time()
        response_result = await ctx.call(
            generate_response_template, 
            issue.category.value, 
            issue.priority.value,
            search_result["solutions"]
        )
        response_time = time.time() - response_start
        
        response_processing = ResolutionResult(
            stage=ResolutionStage.CUSTOMER_CONTACT,
            success=True,
            data=response_result,
            processing_time=response_time
        )
        results.append(response_processing)
        
        # Stage 4: Send Response to Customer
        contact_start = time.time()
        contact_result = await ctx.call(
            send_customer_response,
            issue.customer_id,
            response_result["template"],
            issue.contact_method
        )
        contact_time = time.time() - contact_start
        
        # Stage 5: Determine if escalation is needed
        needs_escalation = (
            issue.priority in [IssuePriority.CRITICAL, IssuePriority.HIGH] and
            not response_result["has_solutions"]
        )
        
        if needs_escalation:
            print(f"⬆️ Escalating {issue.ticket_id} to specialist")
            await ctx.state.set("current_stage", ResolutionStage.ESCALATION.value)
            
            escalation_start = time.time()
            escalation_result = await ctx.call(
                escalate_to_specialist,
                issue.ticket_id,
                issue.category.value,
                "High priority issue without available solutions"
            )
            escalation_time = time.time() - escalation_start
            
            escalation_processing = ResolutionResult(
                stage=ResolutionStage.ESCALATION,
                success=True,
                data=escalation_result,
                processing_time=escalation_time
            )
            results.append(escalation_processing)
            
            # For escalated issues, return pending status
            return {
                "workflow_id": workflow_id,
                "ticket_id": issue.ticket_id,
                "status": "escalated",
                "stage": ResolutionStage.ESCALATION.value,
                "escalation_id": escalation_result["escalation_id"],
                "assigned_team": escalation_result["assigned_team"],
                "results": [result.__dict__ for result in results],
                "total_time": time.time() - start_time
            }
        
        # Stage 6: Auto-resolution for cases with solutions
        if response_result["has_solutions"]:
            print(f"✅ Auto-resolving {issue.ticket_id}")
            await ctx.state.set("current_stage", ResolutionStage.RESOLUTION.value)
            
            resolution_start = time.time()
            resolution_result = await ctx.call(
                mark_issue_resolved,
                issue.ticket_id,
                f"Resolved with knowledge base solutions for {issue.category.value} issue",
                True
            )
            resolution_time = time.time() - resolution_start
            
            resolution_processing = ResolutionResult(
                stage=ResolutionStage.RESOLUTION,
                success=True,
                data=resolution_result,
                processing_time=resolution_time
            )
            results.append(resolution_processing)
            
            # Store final state
            await ctx.state.set("resolution_summary", resolution_result["resolution_summary"])
            await ctx.state.set("customer_satisfied", resolution_result["customer_satisfied"])
            await ctx.state.set("message_id", contact_result["message_id"])
            
            total_time = time.time() - start_time
            
            print(f"✅ Issue {issue.ticket_id} resolved in {total_time:.2f}s")
            
            return {
                "workflow_id": workflow_id,
                "ticket_id": issue.ticket_id,
                "status": "resolved",
                "stage": ResolutionStage.RESOLUTION.value,
                "resolution_summary": resolution_result["resolution_summary"],
                "customer_satisfied": resolution_result["customer_satisfied"],
                "message_id": contact_result["message_id"],
                "results": [result.__dict__ for result in results],
                "total_time": total_time
            }
        else:
            # No solutions found, mark as pending follow-up
            return {
                "workflow_id": workflow_id,
                "ticket_id": issue.ticket_id,
                "status": "pending_followup",
                "stage": ResolutionStage.FOLLOW_UP.value,
                "message_id": contact_result["message_id"],
                "results": [result.__dict__ for result in results],
                "total_time": time.time() - start_time
            }
        
    except Exception as e:
        # Handle any unexpected errors
        error_time = time.time() - start_time
        
        return {
            "workflow_id": workflow_id,
            "ticket_id": issue.ticket_id,
            "status": "error",
            "stage": await ctx.state.get("current_stage", "unknown"),
            "error": str(e),
            "results": [result.__dict__ for result in results],
            "total_time": error_time
        }


# Example usage and testing
async def main():
    """Test the issue resolution workflow."""
    
    print("🧪 Testing Issue Resolution Workflow")
    print("=" * 50)
    
    # Test issue with available solution
    test_issue = {
        "ticket_id": "TKT_001",
        "customer_id": "cust_001",
        "subject": "Cannot reset password",
        "description": "I forgot my password and the reset link is not working. Please help me access my account.",
        "category": "technical",
        "priority": "medium",
        "contact_method": "email",
        "customer_email": "user@example.com"
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
    
    ctx = MockContext()
    
    print(f"🎫 Processing ticket {test_issue['ticket_id']}")
    result = await resolve_issue_workflow(ctx, test_issue)
    
    print(f"\n📊 Workflow Result:")
    print(f"   Status: {result['status']}")
    print(f"   Ticket ID: {result['ticket_id']}")
    print(f"   Final Stage: {result['stage']}")
    print(f"   Total Time: {result['total_time']:.2f}s")
    
    if "resolution_summary" in result:
        print(f"   Resolution: {result['resolution_summary']}")
    if "escalation_id" in result:
        print(f"   Escalation ID: {result['escalation_id']}")
    
    print(f"\n📋 Resolution Stages:")
    for stage_result in result['results']:
        print(f"   {stage_result['stage']}: {'✅' if stage_result['success'] else '❌'} "
              f"({stage_result['processing_time']:.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())