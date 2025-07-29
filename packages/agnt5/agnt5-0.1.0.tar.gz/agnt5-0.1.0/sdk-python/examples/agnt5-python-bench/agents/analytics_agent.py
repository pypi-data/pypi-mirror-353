"""
Analytics Agent - Background data processing and reporting

Handles data analysis, report generation, and business intelligence.
Demonstrates background processing patterns and data-intensive workflows.
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from agnt5 import Agent, tool, durable, DurableContext


class ReportType(Enum):
    """Types of reports that can be generated."""
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    ORDER_ANALYTICS = "order_analytics"
    SUPPORT_METRICS = "support_metrics"
    PERFORMANCE_DASHBOARD = "performance_dashboard"
    REVENUE_ANALYSIS = "revenue_analysis"


class MetricPeriod(Enum):
    """Time periods for metrics."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class AnalyticsRequest:
    """Analytics processing request structure."""
    report_type: ReportType
    period: MetricPeriod
    start_date: str
    end_date: str
    filters: Dict[str, Any] = None
    format: str = "json"  # json, csv, pdf
    priority: str = "normal"


@tool
def query_customer_data(period: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Query customer interaction data from the database."""
    time.sleep(0.3)  # Simulate database query time
    
    # Mock customer data
    data = {
        "total_customers": 15420,
        "new_customers": 543,
        "active_customers": 8921,
        "churn_rate": 2.3,
        "satisfaction_scores": {
            "average": 4.2,
            "distribution": {
                "5_star": 45,
                "4_star": 32,
                "3_star": 15,
                "2_star": 5,
                "1_star": 3
            }
        },
        "top_issues": [
            {"category": "login", "count": 234, "avg_resolution_time": 15},
            {"category": "order", "count": 189, "avg_resolution_time": 45},
            {"category": "billing", "count": 156, "avg_resolution_time": 32}
        ]
    }
    
    return data


@tool
def query_order_data(period: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Query order and sales data."""
    time.sleep(0.25)
    
    # Mock order data
    data = {
        "total_orders": 8934,
        "total_revenue": 892340.50,
        "average_order_value": 99.87,
        "order_status_breakdown": {
            "completed": 7234,
            "processing": 892,
            "shipped": 634,
            "cancelled": 174
        },
        "top_products": [
            {"name": "Wireless Headphones", "orders": 1234, "revenue": 245670.00},
            {"name": "Phone Case", "orders": 987, "revenue": 29610.00},
            {"name": "Laptop Stand", "orders": 876, "revenue": 78840.00}
        ],
        "refund_rate": 3.2,
        "return_reasons": {
            "defective": 45,
            "wrong_item": 23, 
            "not_as_described": 18,
            "changed_mind": 14
        }
    }
    
    return data


@tool
def query_support_metrics(period: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Query customer support performance metrics."""
    time.sleep(0.2)
    
    # Mock support metrics
    data = {
        "total_tickets": 2341,
        "resolved_tickets": 2103,
        "average_response_time": 12.5,  # minutes
        "average_resolution_time": 187.3,  # minutes
        "first_contact_resolution_rate": 73.2,
        "escalation_rate": 8.9,
        "agent_performance": {
            "customer_service": {
                "tickets_handled": 1456,
                "avg_rating": 4.3,
                "resolution_rate": 89.2
            },
            "technical_support": {
                "tickets_handled": 567,
                "avg_rating": 4.1,
                "resolution_rate": 82.1
            },
            "order_management": {
                "tickets_handled": 318,
                "avg_rating": 4.4,
                "resolution_rate": 94.3
            }
        },
        "common_escalation_reasons": [
            {"reason": "complex_technical_issue", "count": 89},
            {"reason": "billing_dispute", "count": 67},
            {"reason": "policy_exception", "count": 34}
        ]
    }
    
    return data


@tool
def query_performance_data(period: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Query system performance and infrastructure metrics."""
    time.sleep(0.15)
    
    # Mock performance data
    data = {
        "system_availability": 99.97,
        "average_response_time": 245,  # milliseconds
        "throughput": {
            "requests_per_second": 1234,
            "peak_rps": 2987,
            "total_requests": 8924567
        },
        "error_rates": {
            "4xx_errors": 0.23,
            "5xx_errors": 0.08,
            "total_error_rate": 0.31
        },
        "resource_utilization": {
            "cpu_average": 65.4,
            "memory_average": 78.9,
            "storage_usage": 45.2
        },
        "api_performance": {
            "customer_service": {"avg_latency": 89, "error_rate": 0.12},
            "order_management": {"avg_latency": 156, "error_rate": 0.34},
            "payment_processing": {"avg_latency": 234, "error_rate": 0.45}
        }
    }
    
    return data


@tool
def generate_insights(data: Dict[str, Any], report_type: str) -> List[str]:
    """Generate analytical insights from the data."""
    time.sleep(0.4)  # Simulate AI analysis time
    
    insights = []
    
    if report_type == "customer_satisfaction":
        if data.get("satisfaction_scores", {}).get("average", 0) > 4.0:
            insights.append("Customer satisfaction is above target (4.0+)")
        
        top_issue = data.get("top_issues", [{}])[0]
        if top_issue:
            insights.append(f"Primary support issue is {top_issue.get('category', 'unknown')} with {top_issue.get('count', 0)} cases")
    
    elif report_type == "order_analytics":
        aov = data.get("average_order_value", 0)
        if aov > 90:
            insights.append(f"Average order value of ${aov:.2f} is strong")
        
        refund_rate = data.get("refund_rate", 0)
        if refund_rate > 5:
            insights.append(f"Refund rate of {refund_rate}% may need attention")
    
    elif report_type == "support_metrics":
        fcr_rate = data.get("first_contact_resolution_rate", 0)
        if fcr_rate < 70:
            insights.append(f"First contact resolution rate of {fcr_rate}% is below target")
        
        escalation_rate = data.get("escalation_rate", 0)
        if escalation_rate > 10:
            insights.append(f"Escalation rate of {escalation_rate}% suggests need for agent training")
    
    elif report_type == "performance_dashboard":
        availability = data.get("system_availability", 0)
        if availability < 99.9:
            insights.append(f"System availability of {availability}% is below SLA")
        
        error_rate = data.get("error_rates", {}).get("total_error_rate", 0)
        if error_rate > 1.0:
            insights.append(f"Error rate of {error_rate}% indicates stability issues")
    
    # Add generic insights if no specific ones
    if not insights:
        insights.append("All metrics appear to be within normal ranges")
        insights.append("Recommend continuing current operational practices")
    
    return insights


@tool
def export_report(data: Dict[str, Any], format: str = "json") -> str:
    """Export report data in the specified format."""
    time.sleep(0.1)
    
    export_id = f"RPT_{int(time.time())}"
    
    print(f"📊 Exported report {export_id}")
    print(f"   Format: {format}")
    print(f"   Size: {len(str(data))} characters")
    
    return export_id


class AnalyticsAgent:
    """Background analytics and reporting agent."""
    
    def __init__(self, model: str = "anthropic/claude-3-5-sonnet"):
        self.agent = Agent(
            name="analytics-agent",
            model=model,
            system_prompt="""You are a senior data analyst and business intelligence specialist. Your expertise includes:

1. Data collection and aggregation from multiple sources
2. Statistical analysis and trend identification
3. Business metric calculation and interpretation
4. Report generation with actionable insights
5. Performance monitoring and alerting
6. Data visualization recommendations

Your approach:
1. Understand the specific analytics requirements
2. Query relevant data sources efficiently
3. Perform thorough analysis of the data
4. Generate meaningful insights and recommendations
5. Present findings in clear, actionable formats
6. Highlight trends, anomalies, and opportunities

Always focus on business value and provide specific, actionable recommendations based on the data.""",
            tools=[
                query_customer_data,
                query_order_data,
                query_support_metrics,
                query_performance_data,
                generate_insights,
                export_report
            ],
            temperature=0.3  # Lower temperature for analytical accuracy
        )
    
    async def process_analytics(self, request: AnalyticsRequest) -> Dict[str, Any]:
        """Process an analytics request and generate a report."""
        
        # Build context for the analytics request
        context = f"""
        Analytics Report Request:
        
        Report Type: {request.report_type.value}
        Time Period: {request.period.value}
        Date Range: {request.start_date} to {request.end_date}
        Output Format: {request.format}
        Priority: {request.priority}
        
        Filters: {request.filters or 'None'}
        
        Please generate a comprehensive analytics report:
        1. Query the appropriate data sources
        2. Analyze the data for trends and patterns
        3. Generate actionable insights
        4. Export the report in the requested format
        5. Provide executive summary and recommendations
        """
        
        # Process the analytics request
        response = await self.agent.run(context)
        
        # Simulate data processing time based on complexity
        processing_time = self._calculate_processing_time(request)
        
        return {
            "agent": "analytics",
            "report_type": request.report_type.value,
            "period": request.period.value,
            "response": response.content,
            "processing_time": processing_time,
            "status": "completed",
            "export_format": request.format
        }
    
    def _calculate_processing_time(self, request: AnalyticsRequest) -> float:
        """Calculate simulated processing time based on request complexity."""
        
        base_time = 1.0  # Base processing time in seconds
        
        # Adjust based on report type complexity
        complexity_factors = {
            ReportType.CUSTOMER_SATISFACTION: 1.2,
            ReportType.ORDER_ANALYTICS: 1.5,
            ReportType.SUPPORT_METRICS: 1.3,
            ReportType.PERFORMANCE_DASHBOARD: 2.0,
            ReportType.REVENUE_ANALYSIS: 1.8
        }
        
        # Adjust based on time period
        period_factors = {
            MetricPeriod.HOURLY: 0.8,
            MetricPeriod.DAILY: 1.0,
            MetricPeriod.WEEKLY: 1.3,
            MetricPeriod.MONTHLY: 1.6
        }
        
        complexity = complexity_factors.get(request.report_type, 1.0)
        period = period_factors.get(request.period, 1.0)
        
        return base_time * complexity * period


# Durable function wrapper for worker registration
@durable.function
async def process_analytics(ctx: DurableContext, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Durable wrapper for analytics processing."""
    
    # Convert dict to AnalyticsRequest
    request = AnalyticsRequest(
        report_type=ReportType(request_data["report_type"]),
        period=MetricPeriod(request_data["period"]),
        start_date=request_data["start_date"],
        end_date=request_data["end_date"],
        filters=request_data.get("filters"),
        format=request_data.get("format", "json"),
        priority=request_data.get("priority", "normal")
    )
    
    # Store analytics request in context state
    await ctx.state.set("analytics_request", {
        "timestamp": time.time(),
        "report_type": request.report_type.value,
        "period": request.period.value,
        "start_date": request.start_date,
        "end_date": request.end_date
    })
    
    # Create agent and process request
    agent = AnalyticsAgent()
    response = await agent.process_analytics(request)
    
    # Store completion in context state
    await ctx.state.set("analytics_result", {
        "completion_time": time.time(),
        "processing_time": response["processing_time"],
        "status": response["status"]
    })
    
    return response


# Example usage and testing
async def main():
    """Test the analytics agent."""
    
    test_requests = [
        {
            "report_type": "customer_satisfaction",
            "period": "weekly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "format": "json",
            "priority": "normal"
        },
        {
            "report_type": "order_analytics",
            "period": "monthly", 
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "filters": {"category": "electronics"},
            "format": "csv",
            "priority": "high"
        },
        {
            "report_type": "support_metrics",
            "period": "daily",
            "start_date": "2024-01-15",
            "end_date": "2024-01-15",
            "format": "json",
            "priority": "normal"
        },
        {
            "report_type": "performance_dashboard",
            "period": "hourly",
            "start_date": "2024-01-15T00:00:00",
            "end_date": "2024-01-15T23:59:59",
            "format": "json",
            "priority": "urgent"
        }
    ]
    
    agent = AnalyticsAgent()
    
    for i, test_data in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"Analytics Test {i}: {test_data['report_type']} - {test_data['period']}")
        print(f"Date Range: {test_data['start_date']} to {test_data['end_date']}")
        print(f"{'='*60}")
        
        request = AnalyticsRequest(**test_data)
        response = await agent.process_analytics(request)
        
        print(f"Response: {response['response'][:200]}...")
        print(f"Processing Time: {response['processing_time']:.2f}s")
        print(f"Status: {response['status']}")
        print(f"Export Format: {response['export_format']}")


if __name__ == "__main__":
    asyncio.run(main())