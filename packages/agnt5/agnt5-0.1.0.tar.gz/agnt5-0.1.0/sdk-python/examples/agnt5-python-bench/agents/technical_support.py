"""
Technical Support Agent - Specialized technical troubleshooting

Handles complex technical issues, system diagnostics, and advanced troubleshooting.
Demonstrates specialized agent capabilities and technical problem-solving workflows.
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from agnt5 import Agent, tool
from agnt5.durable import durable, DurableContext


class TechIssueType(Enum):
    """Types of technical issues."""
    LOGIN = "login"
    PERFORMANCE = "performance" 
    BUG = "bug"
    INTEGRATION = "integration"
    SECURITY = "security"
    DATA = "data"


@dataclass
class TechnicalRequest:
    """Technical support request structure."""
    customer_id: str
    issue_type: TechIssueType
    description: str
    error_message: Optional[str] = None
    steps_to_reproduce: Optional[List[str]] = None
    environment: Dict[str, str] = None
    priority: str = "normal"


@dataclass
class DiagnosticResult:
    """Diagnostic test result."""
    test_name: str
    status: str  # passed, failed, warning
    details: str
    recommendation: Optional[str] = None


@tool
def run_system_diagnostics(customer_id: str, test_type: str = "basic") -> List[Dict[str, Any]]:
    """Run system diagnostics for a customer's environment."""
    time.sleep(0.2)  # Simulate diagnostic time
    
    # Mock diagnostic results
    basic_tests = [
        {
            "test_name": "connectivity_check",
            "status": "passed",
            "details": "Network connectivity is stable",
            "recommendation": None
        },
        {
            "test_name": "auth_service_check", 
            "status": "failed" if random.random() < 0.3 else "passed",
            "details": "Authentication service response time: 1.2s",
            "recommendation": "Consider clearing browser cache if login issues persist"
        },
        {
            "test_name": "api_rate_limits",
            "status": "warning" if random.random() < 0.2 else "passed",
            "details": "API usage at 75% of rate limit",
            "recommendation": "Monitor API usage to avoid throttling"
        }
    ]
    
    advanced_tests = basic_tests + [
        {
            "test_name": "database_connection",
            "status": "passed",
            "details": "Database connection pool healthy",
            "recommendation": None
        },
        {
            "test_name": "memory_usage",
            "status": "warning",
            "details": "Memory usage at 85%",
            "recommendation": "Consider optimizing queries or scaling resources"
        }
    ]
    
    return advanced_tests if test_type == "advanced" else basic_tests


@tool
def check_system_logs(customer_id: str, timeframe: str = "1hour") -> List[Dict[str, Any]]:
    """Check system logs for errors and issues."""
    time.sleep(0.15)  # Simulate log analysis
    
    # Mock log entries
    log_entries = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "level": "ERROR",
            "service": "auth-service",
            "message": "Failed login attempt for user", 
            "count": 3
        },
        {
            "timestamp": "2024-01-15T10:25:00Z",
            "level": "WARN",
            "service": "api-gateway",
            "message": "Rate limit approaching for customer",
            "count": 1
        },
        {
            "timestamp": "2024-01-15T10:20:00Z",
            "level": "INFO", 
            "service": "order-service",
            "message": "Order processed successfully",
            "count": 150
        }
    ]
    
    # Filter by timeframe
    if timeframe == "1hour":
        return log_entries[:2]
    elif timeframe == "24hours":
        return log_entries
    else:
        return log_entries


@tool
def check_service_status() -> Dict[str, str]:
    """Check the status of all system services."""
    time.sleep(0.1)
    
    services = {
        "auth-service": "operational",
        "api-gateway": "operational", 
        "order-service": "operational",
        "payment-service": "degraded" if random.random() < 0.1 else "operational",
        "notification-service": "operational",
        "analytics-service": "maintenance" if random.random() < 0.05 else "operational"
    }
    
    return services


@tool
def create_technical_ticket(customer_id: str, issue_type: str, severity: str, description: str) -> str:
    """Create a technical support ticket with detailed information."""
    ticket_id = f"TECH_{int(time.time())}"
    
    print(f"🔧 Created technical ticket {ticket_id}")
    print(f"   Customer: {customer_id}")
    print(f"   Type: {issue_type}")
    print(f"   Severity: {severity}")
    print(f"   Description: {description[:100]}...")
    
    return ticket_id


@tool
def escalate_to_engineering(ticket_id: str, reason: str) -> str:
    """Escalate technical issue to engineering team."""
    escalation_id = f"ENG_{int(time.time())}"
    
    print(f"⚡ Escalated ticket {ticket_id} to engineering")
    print(f"   Escalation ID: {escalation_id}")
    print(f"   Reason: {reason}")
    
    return escalation_id


class TechnicalSupportAgent:
    """Specialized technical support agent with diagnostic capabilities."""
    
    def __init__(self, model: str = "anthropic/claude-3-5-sonnet"):
        self.agent = Agent(
            name="technical-support",
            model=model,
            system_prompt="""You are a senior technical support specialist. Your expertise includes:

1. System diagnostics and troubleshooting
2. Log analysis and pattern recognition  
3. Performance optimization
4. Security issue investigation
5. Integration debugging
6. Escalation to engineering when needed

Your approach:
1. Gather detailed technical information
2. Run appropriate diagnostic tests
3. Analyze logs and system status
4. Provide step-by-step troubleshooting
5. Create detailed technical tickets
6. Escalate complex issues to engineering

Always be thorough, methodical, and provide clear technical explanations that customers can follow.""",
            tools=[
                run_system_diagnostics,
                check_system_logs, 
                check_service_status,
                create_technical_ticket,
                escalate_to_engineering
            ],
            temperature=0.3  # Lower temperature for more focused technical responses
        )
    
    async def handle_request(self, request: TechnicalRequest) -> Dict[str, Any]:
        """Handle a technical support request with comprehensive diagnostics."""
        
        # Build detailed context
        context = f"""
        Technical Support Request:
        
        Customer ID: {request.customer_id}
        Issue Type: {request.issue_type.value}
        Priority: {request.priority}
        
        Description: {request.description}
        
        Error Message: {request.error_message or 'Not provided'}
        
        Steps to Reproduce:
        {self._format_steps(request.steps_to_reproduce)}
        
        Environment:
        {self._format_environment(request.environment)}
        
        Please investigate this technical issue thoroughly:
        1. Run appropriate diagnostics
        2. Check system logs for related errors
        3. Verify service status
        4. Provide detailed troubleshooting steps
        5. Create a technical ticket if needed
        6. Escalate to engineering if this requires code changes
        """
        
        # Process the technical request
        response = await self.agent.run(context)
        
        # Determine severity and next steps
        severity = self._assess_severity(request)
        needs_escalation = self._needs_engineering_escalation(request, response.content)
        
        # Create technical ticket for tracking
        ticket_id = create_technical_ticket(
            request.customer_id,
            request.issue_type.value,
            severity,
            request.description
        )
        
        escalation_id = None
        if needs_escalation:
            escalation_id = escalate_to_engineering(
                ticket_id,
                f"Complex {request.issue_type.value} issue requiring engineering review"
            )
        
        return {
            "agent": "technical_support",
            "response": response.content,
            "ticket_id": ticket_id,
            "severity": severity,
            "escalated": needs_escalation,
            "escalation_id": escalation_id,
            "resolution_status": "escalated" if needs_escalation else "in_progress"
        }
    
    def _format_steps(self, steps: Optional[List[str]]) -> str:
        """Format steps to reproduce."""
        if not steps:
            return "Not provided"
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    
    def _format_environment(self, env: Optional[Dict[str, str]]) -> str:
        """Format environment information."""
        if not env:
            return "Not provided"
        return "\n".join(f"- {key}: {value}" for key, value in env.items())
    
    def _assess_severity(self, request: TechnicalRequest) -> str:
        """Assess the severity of a technical issue."""
        
        # High severity conditions
        if request.issue_type in [TechIssueType.SECURITY, TechIssueType.DATA]:
            return "high"
        
        if request.priority == "urgent":
            return "high"
        
        if request.error_message and any(keyword in request.error_message.lower() 
                                       for keyword in ["critical", "fatal", "crash", "data loss"]):
            return "high"
        
        # Medium severity
        if request.issue_type in [TechIssueType.INTEGRATION, TechIssueType.PERFORMANCE]:
            return "medium"
        
        if request.priority == "high":
            return "medium"
        
        # Default to low
        return "low"
    
    def _needs_engineering_escalation(self, request: TechnicalRequest, response: str) -> bool:
        """Determine if issue needs engineering escalation."""
        
        # Always escalate security and data issues
        if request.issue_type in [TechIssueType.SECURITY, TechIssueType.DATA]:
            return True
        
        # Escalate if response indicates code changes needed
        escalation_keywords = [
            "bug in the code",
            "needs engineering",
            "requires development", 
            "code fix needed",
            "software defect"
        ]
        
        return any(keyword in response.lower() for keyword in escalation_keywords)


# Durable function wrapper for worker registration
@durable.function
async def handle_technical_request(ctx: DurableContext, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Durable wrapper for technical support requests."""
    
    # Convert dict to TechnicalRequest
    request = TechnicalRequest(
        customer_id=request_data["customer_id"],
        issue_type=TechIssueType(request_data["issue_type"]),
        description=request_data["description"],
        error_message=request_data.get("error_message"),
        steps_to_reproduce=request_data.get("steps_to_reproduce"),
        environment=request_data.get("environment", {}),
        priority=request_data.get("priority", "normal")
    )
    
    # Create agent and process request
    agent = TechnicalSupportAgent()
    response = await agent.handle_request(request)
    
    # Store technical details in context state
    await ctx.state.set("technical_analysis", {
        "timestamp": time.time(),
        "customer_id": request.customer_id,
        "issue_type": request.issue_type.value,
        "severity": response["severity"],
        "ticket_id": response["ticket_id"],
        "escalated": response["escalated"]
    })
    
    return response


# Example usage and testing
async def main():
    """Test the technical support agent."""
    
    test_requests = [
        {
            "customer_id": "cust_001",
            "issue_type": "login",
            "description": "Unable to login, getting authentication errors",
            "error_message": "Invalid credentials - Error 401",
            "steps_to_reproduce": [
                "Go to login page",
                "Enter valid username and password", 
                "Click login button",
                "Receive error message"
            ],
            "environment": {
                "browser": "Chrome 120",
                "os": "Windows 11",
                "device": "Desktop"
            },
            "priority": "high"
        },
        {
            "customer_id": "cust_002",
            "issue_type": "performance",
            "description": "API responses are extremely slow",
            "error_message": "Request timeout after 30 seconds",
            "environment": {
                "api_version": "v2.1",
                "region": "us-east-1"
            },
            "priority": "normal"
        },
        {
            "customer_id": "cust_003",
            "issue_type": "security",
            "description": "Suspicious activity detected in account",
            "priority": "urgent"
        }
    ]
    
    agent = TechnicalSupportAgent()
    
    for i, test_data in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"Technical Test {i}: {test_data['issue_type']} - {test_data['priority']}")
        print(f"Description: {test_data['description']}")
        print(f"{'='*60}")
        
        request = TechnicalRequest(**test_data)
        response = await agent.handle_request(request)
        
        print(f"Response: {response['response'][:200]}...")
        print(f"Ticket ID: {response['ticket_id']}")
        print(f"Severity: {response['severity']}")
        print(f"Escalated: {response['escalated']}")
        if response['escalated']:
            print(f"Escalation ID: {response['escalation_id']}")
        print(f"Status: {response['resolution_status']}")


if __name__ == "__main__":
    asyncio.run(main())