#!/usr/bin/env python3
"""
Comprehensive example demonstrating durable.flow capabilities.

This example shows:
- Multi-step workflow with shared state
- Automatic checkpointing and recovery
- Error handling and retries
- Parallel execution of independent steps
- Integration with external services
"""

import asyncio
import logging
from typing import List, Dict, Any
from agnt5 import durable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example: Data Processing Pipeline
@durable.flow(
    name="data_processing_pipeline",
    checkpoint_interval=2,  # Checkpoint every 2 steps
    max_concurrent_steps=3,  # Allow up to 3 parallel steps
    max_retries=3,
    timeout=30.0
)
async def data_processing_pipeline(ctx, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    A comprehensive data processing pipeline that demonstrates durable flow features.
    
    Steps:
    1. Extract data from multiple sources
    2. Validate and clean the data
    3. Transform data in parallel
    4. Aggregate results
    5. Store final results
    """
    logger.info(f"Starting data processing pipeline with input: {input_data}")
    
    # Step 1: Extract data from multiple sources
    logger.info("Step 1: Extracting data from sources")
    source_urls = input_data.get("sources", [])
    extracted_data = []
    
    for i, source_url in enumerate(source_urls):
        # Simulate external API call with durable.call
        data = await ctx.call("data_extractor", "extract", {"url": source_url})
        extracted_data.append({
            "source_id": i,
            "url": source_url,
            "data": data,
            "extracted_at": "2024-01-01T00:00:00Z"
        })
    
    # Store intermediate state
    await ctx.state.set("extracted_data", extracted_data)
    logger.info(f"Extracted data from {len(extracted_data)} sources")
    
    # Step 2: Validate and clean data (checkpoint triggered here due to interval=2)
    logger.info("Step 2: Validating and cleaning data")
    cleaned_data = []
    
    for item in extracted_data:
        # Simulate data validation/cleaning
        validation_result = await ctx.call("data_validator", "validate", item["data"])
        if validation_result.get("valid", False):
            cleaned_item = await ctx.call("data_cleaner", "clean", item["data"])
            cleaned_data.append({
                **item,
                "cleaned_data": cleaned_item,
                "validation_score": validation_result.get("score", 0.0)
            })
        else:
            logger.warning(f"Skipping invalid data from source {item['source_id']}")
    
    await ctx.state.set("cleaned_data", cleaned_data)
    logger.info(f"Cleaned {len(cleaned_data)} valid data items")
    
    # Step 3: Transform data in parallel (multiple transforms can run concurrently)
    logger.info("Step 3: Transforming data")
    
    # Simulate multiple transformation types that can run in parallel
    transform_types = ["normalize", "enrich", "categorize"]
    transformed_results = {}
    
    # These transforms will run in parallel up to max_concurrent_steps limit
    for transform_type in transform_types:
        logger.info(f"Starting {transform_type} transformation")
        transform_result = await ctx.call(
            "data_transformer", 
            transform_type, 
            {"data": cleaned_data, "type": transform_type}
        )
        transformed_results[transform_type] = transform_result
        await ctx.state.set(f"transform_{transform_type}", transform_result)
    
    logger.info("All transformations completed")
    
    # Step 4: Aggregate results (checkpoint triggered here)
    logger.info("Step 4: Aggregating transformed data")
    aggregation_input = {
        "cleaned_data": cleaned_data,
        "transforms": transformed_results,
        "metadata": {
            "pipeline_version": "1.0.0",
            "processing_time": "2024-01-01T00:00:00Z",
            "source_count": len(source_urls)
        }
    }
    
    aggregated_result = await ctx.call("data_aggregator", "aggregate", aggregation_input)
    await ctx.state.set("aggregated_result", aggregated_result)
    
    # Step 5: Store final results
    logger.info("Step 5: Storing final results")
    storage_config = input_data.get("storage", {"type": "database", "table": "processed_data"})
    
    storage_result = await ctx.call(
        "data_storage", 
        "store", 
        {
            "data": aggregated_result,
            "config": storage_config,
            "metadata": {
                "pipeline_id": ctx.execution_id,
                "input_sources": len(source_urls),
                "processed_items": len(cleaned_data)
            }
        }
    )
    
    # Final result
    final_result = {
        "success": True,
        "pipeline_id": ctx.execution_id,
        "processed_items": len(cleaned_data),
        "storage_location": storage_result.get("location"),
        "processing_summary": {
            "sources_processed": len(source_urls),
            "items_extracted": len(extracted_data),
            "items_cleaned": len(cleaned_data),
            "transforms_applied": len(transform_types),
            "final_size": aggregated_result.get("size", 0)
        }
    }
    
    logger.info(f"Pipeline completed successfully: {final_result}")
    return final_result


# Example: Research Workflow
@durable.flow(
    name="research_workflow",
    checkpoint_interval=1,  # Checkpoint after each major step
    max_retries=5,
    deterministic=True
)
async def research_workflow(ctx, topic: str, depth: str = "standard") -> Dict[str, Any]:
    """
    Research workflow that searches, analyzes, and synthesizes information.
    
    This demonstrates:
    - Sequential steps with dependencies
    - Conditional logic based on intermediate results
    - Error recovery and retries
    - State preservation across steps
    """
    logger.info(f"Starting research workflow for topic: {topic}")
    
    # Step 1: Search for sources
    search_params = {
        "query": topic,
        "depth": depth,
        "max_results": 10 if depth == "standard" else 20,
        "include_academic": True if depth == "deep" else False
    }
    
    sources = await ctx.call("search_service", "search", search_params)
    await ctx.state.set("sources", sources)
    logger.info(f"Found {len(sources)} sources for topic: {topic}")
    
    # Step 2: Analyze each source
    analyses = []
    for i, source in enumerate(sources):
        logger.info(f"Analyzing source {i+1}/{len(sources)}: {source.get('title', 'Unknown')}")
        
        try:
            analysis = await ctx.call("analysis_service", "analyze", {
                "content": source.get("content", ""),
                "metadata": source.get("metadata", {}),
                "analysis_type": "comprehensive" if depth == "deep" else "summary"
            })
            
            analyses.append({
                "source_id": i,
                "source": source,
                "analysis": analysis,
                "relevance_score": analysis.get("relevance_score", 0.0)
            })
            
        except Exception as e:
            logger.warning(f"Failed to analyze source {i}: {e}")
            # Continue with other sources
            continue
    
    await ctx.state.set("analyses", analyses)
    
    # Filter by relevance if we have too many results
    if len(analyses) > 5:
        analyses = sorted(analyses, key=lambda x: x["relevance_score"], reverse=True)[:5]
        logger.info(f"Filtered to top 5 most relevant analyses")
    
    # Step 3: Synthesize findings
    synthesis_input = {
        "topic": topic,
        "analyses": analyses,
        "synthesis_type": "comprehensive" if depth == "deep" else "summary",
        "target_audience": "general"
    }
    
    synthesis = await ctx.call("synthesis_service", "synthesize", synthesis_input)
    await ctx.state.set("synthesis", synthesis)
    
    # Step 4: Generate final report
    report_data = {
        "topic": topic,
        "research_depth": depth,
        "sources_found": len(sources),
        "sources_analyzed": len(analyses),
        "key_findings": synthesis.get("key_findings", []),
        "conclusions": synthesis.get("conclusions", []),
        "confidence_score": synthesis.get("confidence_score", 0.0),
        "research_metadata": {
            "execution_id": ctx.execution_id,
            "completed_at": "2024-01-01T00:00:00Z",
            "processing_steps": 4
        }
    }
    
    final_report = await ctx.call("report_generator", "generate", report_data)
    
    logger.info(f"Research workflow completed for topic: {topic}")
    return {
        "success": True,
        "topic": topic,
        "report": final_report,
        "metadata": report_data["research_metadata"]
    }


# Example: E-commerce Order Processing Flow
@durable.flow(
    name="order_processing_flow",
    checkpoint_interval=1,
    max_concurrent_steps=2,  # Can process payment and inventory in parallel
    max_retries=3
)
async def order_processing_flow(ctx, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    E-commerce order processing flow with payment, inventory, and fulfillment.
    
    Demonstrates:
    - Business logic workflows
    - Error handling with compensation
    - Parallel processing where possible
    - State management for complex transactions
    """
    order_id = order_data.get("order_id")
    logger.info(f"Processing order {order_id}")
    
    # Step 1: Validate order
    validation_result = await ctx.call("order_service", "validate", order_data)
    if not validation_result.get("valid", False):
        raise ValueError(f"Invalid order: {validation_result.get('reason')}")
    
    await ctx.state.set("validation", validation_result)
    
    # Step 2: Reserve inventory (with rollback capability)
    items = order_data.get("items", [])
    reservation_results = []
    
    for item in items:
        reservation = await ctx.call("inventory_service", "reserve", {
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "order_id": order_id
        })
        reservation_results.append(reservation)
    
    await ctx.state.set("reservations", reservation_results)
    
    # Check if all reservations succeeded
    failed_reservations = [r for r in reservation_results if not r.get("success", False)]
    if failed_reservations:
        # Rollback successful reservations
        successful_reservations = [r for r in reservation_results if r.get("success", False)]
        for reservation in successful_reservations:
            await ctx.call("inventory_service", "release", {
                "reservation_id": reservation["reservation_id"]
            })
        
        raise ValueError(f"Insufficient inventory for {len(failed_reservations)} items")
    
    # Step 3: Process payment
    payment_data = {
        "order_id": order_id,
        "amount": order_data.get("total_amount"),
        "payment_method": order_data.get("payment_method"),
        "customer_id": order_data.get("customer_id")
    }
    
    payment_result = await ctx.call("payment_service", "charge", payment_data)
    await ctx.state.set("payment", payment_result)
    
    if not payment_result.get("success", False):
        # Rollback inventory reservations
        for reservation in reservation_results:
            await ctx.call("inventory_service", "release", {
                "reservation_id": reservation["reservation_id"]
            })
        
        raise ValueError(f"Payment failed: {payment_result.get('reason')}")
    
    # Step 4: Confirm inventory allocation
    for reservation in reservation_results:
        confirmation = await ctx.call("inventory_service", "confirm", {
            "reservation_id": reservation["reservation_id"]
        })
        if not confirmation.get("success", False):
            logger.warning(f"Failed to confirm reservation {reservation['reservation_id']}")
    
    # Step 5: Create shipment
    shipment_data = {
        "order_id": order_id,
        "items": items,
        "shipping_address": order_data.get("shipping_address"),
        "shipping_method": order_data.get("shipping_method", "standard")
    }
    
    shipment_result = await ctx.call("fulfillment_service", "create_shipment", shipment_data)
    await ctx.state.set("shipment", shipment_result)
    
    # Step 6: Send confirmation
    notification_data = {
        "order_id": order_id,
        "customer_id": order_data.get("customer_id"),
        "email": order_data.get("customer_email"),
        "order_total": order_data.get("total_amount"),
        "tracking_number": shipment_result.get("tracking_number")
    }
    
    await ctx.call("notification_service", "send_confirmation", notification_data)
    
    return {
        "success": True,
        "order_id": order_id,
        "payment_id": payment_result.get("payment_id"),
        "tracking_number": shipment_result.get("tracking_number"),
        "status": "processed",
        "processing_summary": {
            "items_count": len(items),
            "total_amount": order_data.get("total_amount"),
            "payment_method": order_data.get("payment_method"),
            "estimated_delivery": shipment_result.get("estimated_delivery")
        }
    }


async def main():
    """Demonstrate the durable flow examples."""
    
    # Example 1: Data Processing Pipeline
    print("=" * 60)
    print("Example 1: Data Processing Pipeline")
    print("=" * 60)
    
    pipeline_input = {
        "sources": [
            "https://api.example.com/data/1",
            "https://api.example.com/data/2",
            "https://api.example.com/data/3"
        ],
        "storage": {
            "type": "database",
            "table": "processed_data"
        }
    }
    
    try:
        pipeline_result = await data_processing_pipeline(pipeline_input)
        print(f"Pipeline Result: {pipeline_result}")
    except Exception as e:
        print(f"Pipeline Error: {e}")
    
    # Example 2: Research Workflow
    print("\n" + "=" * 60)
    print("Example 2: Research Workflow")
    print("=" * 60)
    
    try:
        research_result = await research_workflow("artificial intelligence", "deep")
        print(f"Research Result: {research_result}")
    except Exception as e:
        print(f"Research Error: {e}")
    
    # Example 3: Order Processing Flow
    print("\n" + "=" * 60)
    print("Example 3: Order Processing Flow")
    print("=" * 60)
    
    order_input = {
        "order_id": "ORD-12345",
        "customer_id": "CUST-67890",
        "customer_email": "customer@example.com",
        "items": [
            {"product_id": "PROD-1", "quantity": 2, "price": 29.99},
            {"product_id": "PROD-2", "quantity": 1, "price": 59.99}
        ],
        "total_amount": 119.97,
        "payment_method": "credit_card",
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        },
        "shipping_method": "express"
    }
    
    try:
        order_result = await order_processing_flow(order_input)
        print(f"Order Result: {order_result}")
    except Exception as e:
        print(f"Order Error: {e}")
    
    # Show registered flows
    print("\n" + "=" * 60)
    print("Registered Durable Flows")
    print("=" * 60)
    
    flows = durable.get_all_flows()
    for flow in flows:
        print(f"- {flow.config.name} (v{flow.config.version})")
        print(f"  Checkpoint interval: {flow.config.checkpoint_interval}")
        print(f"  Max retries: {flow.config.max_retries}")
        print(f"  Deterministic: {flow.config.deterministic}")
        if flow.config.timeout:
            print(f"  Timeout: {flow.config.timeout}s")
        print()


if __name__ == "__main__":
    asyncio.run(main())