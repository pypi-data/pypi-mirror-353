"""
Reporting Pipeline Workflow - Automated analytics and report generation

Orchestrates data collection, processing, analysis, and report delivery.
Demonstrates complex workflow patterns with data transformation, visualization, and distribution.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from agnt5.durable import durable, DurableContext
from agnt5 import tool


class ReportType(Enum):
    """Types of reports that can be generated."""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_ANALYTICS = "weekly_analytics"
    MONTHLY_PERFORMANCE = "monthly_performance"
    CUSTOM_QUERY = "custom_query"


class DataSource(Enum):
    """Available data sources."""
    ORDERS = "orders"
    CUSTOMERS = "customers"
    INVENTORY = "inventory"
    SUPPORT_TICKETS = "support_tickets"
    ANALYTICS = "analytics"


class ProcessingStage(Enum):
    """Report processing stages."""
    DATA_COLLECTION = "data_collection"
    DATA_VALIDATION = "data_validation"
    DATA_TRANSFORMATION = "data_transformation"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    REPORT_GENERATION = "report_generation"
    DISTRIBUTION = "distribution"
    COMPLETION = "completion"


@dataclass
class ReportRequest:
    """Report request data structure."""
    report_id: str
    report_type: ReportType
    data_sources: List[DataSource]
    date_range: Dict[str, str]
    filters: Dict[str, Any]
    recipients: List[str]
    format: str = "pdf"
    schedule: Optional[str] = None


@dataclass
class ProcessingResult:
    """Result of a processing stage."""
    stage: ProcessingStage
    success: bool
    data: Dict[str, Any]
    errors: List[str] = None
    processing_time: float = 0.0
    records_processed: int = 0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


# Data collection tools
@tool
def collect_orders_data(date_range: Dict[str, str], filters: Dict[str, Any]) -> Dict[str, Any]:
    """Collect orders data from the database."""
    time.sleep(0.2)  # Simulate database query time
    
    # Mock orders data
    orders_data = [
        {
            "order_id": f"ORD_{i:06d}",
            "customer_id": f"cust_{i%1000:03d}",
            "total_amount": round(50 + (i % 500), 2),
            "status": ["pending", "completed", "shipped", "delivered"][i % 4],
            "order_date": "2024-01-01",
            "items_count": (i % 5) + 1,
            "category": ["electronics", "clothing", "books", "home"][i % 4]
        }
        for i in range(1000)  # Generate 1000 mock orders
    ]
    
    # Apply filters
    filtered_data = orders_data
    if "status" in filters:
        filtered_data = [order for order in filtered_data if order["status"] == filters["status"]]
    if "min_amount" in filters:
        filtered_data = [order for order in filtered_data if order["total_amount"] >= filters["min_amount"]]
    
    return {
        "source": "orders",
        "records_count": len(filtered_data),
        "data": filtered_data[:100],  # Return first 100 for processing
        "total_revenue": sum(order["total_amount"] for order in filtered_data),
        "collection_time": time.time()
    }


@tool
def collect_customers_data(date_range: Dict[str, str], filters: Dict[str, Any]) -> Dict[str, Any]:
    """Collect customer data from the database."""
    time.sleep(0.15)
    
    customers_data = [
        {
            "customer_id": f"cust_{i:03d}",
            "registration_date": "2024-01-01",
            "total_orders": (i % 20) + 1,
            "total_spent": round(100 + (i % 2000), 2),
            "customer_tier": ["bronze", "silver", "gold", "platinum"][i % 4],
            "last_order_date": "2024-01-15"
        }
        for i in range(500)  # Generate 500 mock customers
    ]
    
    return {
        "source": "customers",
        "records_count": len(customers_data),
        "data": customers_data,
        "average_customer_value": sum(c["total_spent"] for c in customers_data) / len(customers_data),
        "collection_time": time.time()
    }


@tool
def collect_support_tickets_data(date_range: Dict[str, str], filters: Dict[str, Any]) -> Dict[str, Any]:
    """Collect support tickets data."""
    time.sleep(0.1)
    
    tickets_data = [
        {
            "ticket_id": f"TKT_{i:06d}",
            "customer_id": f"cust_{i%500:03d}",
            "category": ["billing", "technical", "shipping", "product"][i % 4],
            "priority": ["low", "medium", "high", "critical"][i % 4],
            "status": ["open", "in_progress", "resolved", "closed"][i % 4],
            "created_date": "2024-01-01",
            "resolution_time_hours": (i % 48) + 1 if i % 4 == 3 else None  # Only resolved tickets
        }
        for i in range(200)  # Generate 200 mock tickets
    ]
    
    return {
        "source": "support_tickets",
        "records_count": len(tickets_data),
        "data": tickets_data,
        "average_resolution_time": 24.5,
        "collection_time": time.time()
    }


@tool
def validate_data_quality(data_collection_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate the quality and consistency of collected data."""
    time.sleep(0.1)
    
    validation_results = []
    total_records = 0
    quality_score = 100.0
    
    for result in data_collection_results:
        source = result["source"]
        records = result["records_count"]
        total_records += records
        
        # Mock validation checks
        missing_data_rate = 0.02  # 2% missing data
        duplicate_rate = 0.01     # 1% duplicates
        
        source_quality = 100 - (missing_data_rate * 20) - (duplicate_rate * 30)
        quality_score = min(quality_score, source_quality)
        
        validation_results.append({
            "source": source,
            "records": records,
            "quality_score": source_quality,
            "missing_data_rate": missing_data_rate,
            "duplicate_rate": duplicate_rate,
            "issues": ["Some missing customer emails"] if missing_data_rate > 0 else []
        })
    
    return {
        "overall_quality_score": quality_score,
        "total_records": total_records,
        "validation_results": validation_results,
        "data_quality_acceptable": quality_score >= 80,
        "validated_at": time.time()
    }


@tool
def transform_and_aggregate_data(data_collection_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Transform and aggregate data for analysis."""
    time.sleep(0.3)
    
    # Mock data transformation and aggregation
    transformations = []
    
    for result in data_collection_results:
        source = result["source"]
        
        if source == "orders":
            # Calculate order metrics
            total_revenue = result.get("total_revenue", 0)
            order_count = result["records_count"]
            avg_order_value = total_revenue / order_count if order_count > 0 else 0
            
            transformations.append({
                "source": source,
                "metrics": {
                    "total_revenue": total_revenue,
                    "order_count": order_count,
                    "average_order_value": round(avg_order_value, 2),
                    "revenue_growth": 15.2,  # Mock growth rate
                    "top_categories": ["electronics", "clothing", "books"]
                }
            })
            
        elif source == "customers":
            # Calculate customer metrics
            customer_count = result["records_count"]
            avg_customer_value = result.get("average_customer_value", 0)
            
            transformations.append({
                "source": source,
                "metrics": {
                    "total_customers": customer_count,
                    "average_customer_value": round(avg_customer_value, 2),
                    "new_customers": int(customer_count * 0.1),  # Mock 10% new
                    "customer_retention_rate": 85.5,
                    "customer_tier_distribution": {"bronze": 40, "silver": 35, "gold": 20, "platinum": 5}
                }
            })
            
        elif source == "support_tickets":
            # Calculate support metrics
            ticket_count = result["records_count"]
            avg_resolution = result.get("average_resolution_time", 0)
            
            transformations.append({
                "source": source,
                "metrics": {
                    "total_tickets": ticket_count,
                    "average_resolution_time": avg_resolution,
                    "ticket_resolution_rate": 92.5,
                    "customer_satisfaction": 4.2,
                    "category_distribution": {"billing": 30, "technical": 25, "shipping": 25, "product": 20}
                }
            })
    
    return {
        "transformations": transformations,
        "aggregation_summary": {
            "sources_processed": len(transformations),
            "transformation_complete": True
        },
        "transformed_at": time.time()
    }


@tool
def perform_advanced_analysis(transformed_data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
    """Perform advanced analytics based on report type."""
    time.sleep(0.4)
    
    analysis_results = {}
    
    if report_type == "daily_summary":
        analysis_results = {
            "key_insights": [
                "Daily revenue increased by 12% compared to yesterday",
                "Customer satisfaction remains high at 4.2/5.0",
                "Electronics category shows strongest performance"
            ],
            "trends": {
                "revenue_trend": "increasing",
                "order_volume_trend": "stable",
                "customer_growth_trend": "increasing"
            },
            "alerts": []
        }
    elif report_type == "weekly_analytics":
        analysis_results = {
            "key_insights": [
                "Weekly revenue reached $125,000, up 15% from last week",
                "New customer acquisition increased by 8%",
                "Support ticket volume decreased by 5%"
            ],
            "trends": {
                "revenue_trend": "strong_growth",
                "customer_acquisition_trend": "positive",
                "support_efficiency_trend": "improving"
            },
            "recommendations": [
                "Consider increasing inventory for electronics category",
                "Implement customer retention program for bronze tier",
                "Optimize support processes for billing inquiries"
            ]
        }
    elif report_type == "monthly_performance":
        analysis_results = {
            "key_insights": [
                "Monthly revenue of $500,000 exceeded target by 10%",
                "Customer lifetime value increased to $890",
                "Support resolution time improved by 20%"
            ],
            "performance_metrics": {
                "revenue_vs_target": 110,
                "customer_satisfaction_vs_target": 105,
                "efficiency_vs_target": 120
            },
            "strategic_recommendations": [
                "Expand into new product categories",
                "Invest in customer experience improvements",
                "Scale support team for growth"
            ]
        }
    
    return {
        "analysis_type": report_type,
        "analysis_results": analysis_results,
        "confidence_score": 0.92,
        "analyzed_at": time.time()
    }


@tool
def generate_visualizations(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate charts and visualizations for the report."""
    time.sleep(0.2)
    
    # Mock visualization generation
    visualizations = [
        {
            "type": "line_chart",
            "title": "Revenue Trend",
            "description": "Daily revenue over the past 30 days",
            "data_points": 30,
            "chart_url": "https://charts.example.com/revenue_trend.png"
        },
        {
            "type": "pie_chart", 
            "title": "Category Distribution",
            "description": "Sales by product category",
            "data_points": 4,
            "chart_url": "https://charts.example.com/category_dist.png"
        },
        {
            "type": "bar_chart",
            "title": "Customer Satisfaction",
            "description": "Satisfaction scores by category",
            "data_points": 5,
            "chart_url": "https://charts.example.com/satisfaction.png"
        }
    ]
    
    return {
        "visualizations": visualizations,
        "chart_count": len(visualizations),
        "generated_at": time.time()
    }


@tool
def compile_report(analysis_data: Dict[str, Any], visualizations: Dict[str, Any], report_format: str) -> Dict[str, Any]:
    """Compile the final report in the requested format."""
    time.sleep(0.3)
    
    report_id = f"RPT_{int(time.time())}"
    
    # Mock report compilation
    report_sections = [
        "Executive Summary",
        "Key Metrics",
        "Trend Analysis", 
        "Performance Insights",
        "Recommendations",
        "Appendix"
    ]
    
    return {
        "report_id": report_id,
        "format": report_format,
        "sections": report_sections,
        "page_count": 15,
        "file_size_mb": 2.4,
        "report_url": f"https://reports.example.com/{report_id}.{report_format}",
        "compiled_at": time.time()
    }


@tool
def distribute_report(report_data: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
    """Distribute the report to recipients."""
    time.sleep(0.1)
    
    distribution_results = []
    
    for recipient in recipients:
        distribution_results.append({
            "recipient": recipient,
            "delivery_method": "email",
            "delivered": True,
            "delivery_time": time.time()
        })
    
    return {
        "distribution_results": distribution_results,
        "total_recipients": len(recipients),
        "successful_deliveries": len(distribution_results),
        "distributed_at": time.time()
    }


@durable.flow
async def generate_reports_workflow(ctx: DurableContext, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete reporting pipeline workflow with data collection, analysis, and distribution.
    
    Orchestrates the entire report generation process from data collection through delivery.
    """
    
    # Initialize workflow state
    workflow_id = f"reports_{request_data['report_id']}_{int(time.time())}"
    start_time = time.time()
    
    await ctx.state.set("workflow_id", workflow_id)
    await ctx.state.set("start_time", start_time)
    await ctx.state.set("current_stage", ProcessingStage.DATA_COLLECTION.value)
    
    # Convert to ReportRequest for type safety
    request = ReportRequest(
        report_id=request_data["report_id"],
        report_type=ReportType(request_data["report_type"]),
        data_sources=[DataSource(ds) for ds in request_data["data_sources"]],
        date_range=request_data["date_range"],
        filters=request_data.get("filters", {}),
        recipients=request_data["recipients"],
        format=request_data.get("format", "pdf"),
        schedule=request_data.get("schedule")
    )
    
    results = []
    
    try:
        # Stage 1: Data Collection
        print(f"📊 Starting data collection for {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.DATA_COLLECTION.value)
        
        collection_start = time.time()
        data_collection_results = []
        
        # Collect data from each requested source
        for source in request.data_sources:
            if source == DataSource.ORDERS:
                orders_data = await ctx.call(collect_orders_data, request.date_range, request.filters)
                data_collection_results.append(orders_data)
            elif source == DataSource.CUSTOMERS:
                customers_data = await ctx.call(collect_customers_data, request.date_range, request.filters)
                data_collection_results.append(customers_data)
            elif source == DataSource.SUPPORT_TICKETS:
                tickets_data = await ctx.call(collect_support_tickets_data, request.date_range, request.filters)
                data_collection_results.append(tickets_data)
        
        collection_time = time.time() - collection_start
        total_records = sum(result["records_count"] for result in data_collection_results)
        
        collection_processing = ProcessingResult(
            stage=ProcessingStage.DATA_COLLECTION,
            success=len(data_collection_results) > 0,
            data={"sources_collected": len(data_collection_results)},
            processing_time=collection_time,
            records_processed=total_records
        )
        results.append(collection_processing)
        
        # Stage 2: Data Validation
        print(f"✅ Validating data quality for {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.DATA_VALIDATION.value)
        
        validation_start = time.time()
        validation_result = await ctx.call(validate_data_quality, data_collection_results)
        validation_time = time.time() - validation_start
        
        validation_processing = ProcessingResult(
            stage=ProcessingStage.DATA_VALIDATION,
            success=validation_result["data_quality_acceptable"],
            data=validation_result,
            processing_time=validation_time
        )
        results.append(validation_processing)
        
        if not validation_result["data_quality_acceptable"]:
            return {
                "workflow_id": workflow_id,
                "report_id": request.report_id,
                "status": "failed",
                "stage": ProcessingStage.DATA_VALIDATION.value,
                "error": "Data quality below acceptable threshold",
                "results": [result.__dict__ for result in results],
                "total_time": time.time() - start_time
            }
        
        # Stage 3: Data Transformation
        print(f"🔄 Transforming and aggregating data for {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.DATA_TRANSFORMATION.value)
        
        transform_start = time.time()
        transform_result = await ctx.call(transform_and_aggregate_data, data_collection_results)
        transform_time = time.time() - transform_start
        
        transform_processing = ProcessingResult(
            stage=ProcessingStage.DATA_TRANSFORMATION,
            success=transform_result["aggregation_summary"]["transformation_complete"],
            data=transform_result,
            processing_time=transform_time
        )
        results.append(transform_processing)
        
        # Stage 4: Advanced Analysis
        print(f"🧠 Performing analysis for {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.ANALYSIS.value)
        
        analysis_start = time.time()
        analysis_result = await ctx.call(perform_advanced_analysis, transform_result, request.report_type.value)
        analysis_time = time.time() - analysis_start
        
        analysis_processing = ProcessingResult(
            stage=ProcessingStage.ANALYSIS,
            success=analysis_result["confidence_score"] > 0.8,
            data=analysis_result,
            processing_time=analysis_time
        )
        results.append(analysis_processing)
        
        # Stage 5: Visualization Generation
        print(f"📈 Generating visualizations for {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.VISUALIZATION.value)
        
        viz_start = time.time()
        viz_result = await ctx.call(generate_visualizations, analysis_result)
        viz_time = time.time() - viz_start
        
        viz_processing = ProcessingResult(
            stage=ProcessingStage.VISUALIZATION,
            success=viz_result["chart_count"] > 0,
            data=viz_result,
            processing_time=viz_time
        )
        results.append(viz_processing)
        
        # Stage 6: Report Compilation
        print(f"📄 Compiling report for {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.REPORT_GENERATION.value)
        
        compile_start = time.time()
        compile_result = await ctx.call(compile_report, analysis_result, viz_result, request.format)
        compile_time = time.time() - compile_start
        
        compile_processing = ProcessingResult(
            stage=ProcessingStage.REPORT_GENERATION,
            success=True,
            data=compile_result,
            processing_time=compile_time
        )
        results.append(compile_processing)
        
        # Stage 7: Distribution
        print(f"📨 Distributing report {request.report_id}")
        await ctx.state.set("current_stage", ProcessingStage.DISTRIBUTION.value)
        
        dist_start = time.time()
        dist_result = await ctx.call(distribute_report, compile_result, request.recipients)
        dist_time = time.time() - dist_start
        
        dist_processing = ProcessingResult(
            stage=ProcessingStage.DISTRIBUTION,
            success=dist_result["successful_deliveries"] == dist_result["total_recipients"],
            data=dist_result,
            processing_time=dist_time
        )
        results.append(dist_processing)
        
        # Stage 8: Completion
        await ctx.state.set("current_stage", ProcessingStage.COMPLETION.value)
        
        # Store final state
        await ctx.state.set("report_url", compile_result["report_url"])
        await ctx.state.set("total_recipients", dist_result["total_recipients"])
        await ctx.state.set("records_processed", total_records)
        
        total_time = time.time() - start_time
        
        print(f"✅ Report {request.report_id} completed in {total_time:.2f}s")
        
        return {
            "workflow_id": workflow_id,
            "report_id": request.report_id,
            "status": "completed",
            "stage": ProcessingStage.COMPLETION.value,
            "report_url": compile_result["report_url"],
            "total_recipients": dist_result["total_recipients"],
            "records_processed": total_records,
            "results": [result.__dict__ for result in results],
            "total_time": total_time
        }
        
    except Exception as e:
        # Handle any unexpected errors
        error_time = time.time() - start_time
        
        return {
            "workflow_id": workflow_id,
            "report_id": request.report_id,
            "status": "error",
            "stage": await ctx.state.get("current_stage", "unknown"),
            "error": str(e),
            "results": [result.__dict__ for result in results],
            "total_time": error_time
        }


# Example usage and testing
async def main():
    """Test the reporting pipeline workflow."""
    
    print("🧪 Testing Reporting Pipeline Workflow")
    print("=" * 50)
    
    # Test weekly analytics report
    test_request = {
        "report_id": "RPT_WEEKLY_001",
        "report_type": "weekly_analytics",
        "data_sources": ["orders", "customers", "support_tickets"],
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-01-07"
        },
        "filters": {
            "min_amount": 50
        },
        "recipients": ["manager@example.com", "analyst@example.com"],
        "format": "pdf"
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
    
    print(f"📊 Generating report {test_request['report_id']}")
    result = await generate_reports_workflow(ctx, test_request)
    
    print(f"\n📊 Workflow Result:")
    print(f"   Status: {result['status']}")
    print(f"   Report ID: {result['report_id']}")
    print(f"   Final Stage: {result['stage']}")
    print(f"   Total Time: {result['total_time']:.2f}s")
    
    if "report_url" in result:
        print(f"   Report URL: {result['report_url']}")
    if "records_processed" in result:
        print(f"   Records Processed: {result['records_processed']}")
    
    print(f"\n📋 Processing Stages:")
    for stage_result in result['results']:
        print(f"   {stage_result['stage']}: {'✅' if stage_result['success'] else '❌'} "
              f"({stage_result['processing_time']:.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())