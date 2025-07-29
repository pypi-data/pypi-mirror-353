#!/usr/bin/env python3
"""
Load Generator for AGNT5 Python Benchmark

Generates realistic load patterns to test the benchmark application under stress.
Simulates concurrent customer interactions, order processing, and analytics requests.
"""

import asyncio
import aiohttp
import json
import time
import random
import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class LoadTestConfig:
    """Load test configuration."""
    runtime_endpoint: str
    duration: int = 300  # 5 minutes
    concurrency: int = 50
    rps: int = 10  # requests per second
    scenarios: Dict[str, float] = None  # scenario -> weight
    
    def __post_init__(self):
        if self.scenarios is None:
            self.scenarios = {
                "customer_service": 0.4,
                "order_processing": 0.3,
                "technical_support": 0.2,
                "analytics": 0.1
            }


@dataclass
class LoadTestResult:
    """Result of a load test."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    p95_latency: float
    p99_latency: float
    throughput: float
    error_rate: float
    duration: float


class LoadGenerator:
    """Generate load against the AGNT5 benchmark application."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.session: aiohttp.ClientSession = None
        
        # Test data generators
        self.customer_ids = [f"cust_{i:03d}" for i in range(1, 101)]
        self.order_ids = [f"ORD_{i:05d}" for i in range(10000, 20000)]
        
        # Results tracking
        self.results: List[Dict[str, Any]] = []
        self.start_time = 0
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def run_load_test(self) -> LoadTestResult:
        """Run the complete load test."""
        print(f"🚀 Starting load test")
        print(f"   Duration: {self.config.duration}s")
        print(f"   Concurrency: {self.config.concurrency}")
        print(f"   Target RPS: {self.config.rps}")
        print(f"   Endpoint: {self.config.runtime_endpoint}")
        
        self.start_time = time.time()
        
        # Create worker tasks
        workers = []
        for i in range(self.config.concurrency):
            worker = asyncio.create_task(
                self._worker(f"worker_{i:02d}")
            )
            workers.append(worker)
        
        # Run for specified duration
        await asyncio.sleep(self.config.duration)
        
        # Cancel all workers
        for worker in workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*workers, return_exceptions=True)
        
        # Calculate results
        return self._calculate_results()
    
    async def _worker(self, worker_id: str) -> None:
        """Individual worker that generates requests."""
        
        target_interval = self.config.concurrency / self.config.rps
        
        try:
            while True:
                start = time.time()
                
                # Select scenario based on weights
                scenario = self._select_scenario()
                
                # Execute the scenario
                await self._execute_scenario(scenario, worker_id)
                
                # Rate limiting
                elapsed = time.time() - start
                sleep_time = max(0, target_interval - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
        except asyncio.CancelledError:
            print(f"🛑 Worker {worker_id} stopped")
    
    def _select_scenario(self) -> str:
        """Select a scenario based on configured weights."""
        rand = random.random()
        cumulative = 0
        
        for scenario, weight in self.config.scenarios.items():
            cumulative += weight
            if rand <= cumulative:
                return scenario
        
        return list(self.config.scenarios.keys())[0]
    
    async def _execute_scenario(self, scenario: str, worker_id: str) -> None:
        """Execute a specific test scenario."""
        
        start_time = time.time()
        
        try:
            if scenario == "customer_service":
                await self._customer_service_scenario()
            elif scenario == "order_processing":
                await self._order_processing_scenario()
            elif scenario == "technical_support":
                await self._technical_support_scenario()
            elif scenario == "analytics":
                await self._analytics_scenario()
            else:
                raise ValueError(f"Unknown scenario: {scenario}")
            
            # Record success
            latency = time.time() - start_time
            self.results.append({
                "scenario": scenario,
                "worker_id": worker_id,
                "success": True,
                "latency": latency,
                "timestamp": start_time,
                "error": None
            })
            
        except Exception as e:
            # Record failure
            latency = time.time() - start_time
            self.results.append({
                "scenario": scenario,
                "worker_id": worker_id,
                "success": False,
                "latency": latency,
                "timestamp": start_time,
                "error": str(e)
            })
    
    async def _customer_service_scenario(self) -> None:
        """Simulate customer service interaction."""
        
        customer_id = random.choice(self.customer_ids)
        
        # Random customer service requests
        messages = [
            "I need help with my password reset",
            "When will my order arrive?",
            "I want to return an item",
            "My account is locked",
            "I have a billing question",
            "How do I track my shipment?",
            "I need to update my address",
            "Can you help me with my order?"
        ]
        
        request_data = {
            "customer_id": customer_id,
            "message": random.choice(messages),
            "priority": random.choice(["normal", "normal", "normal", "high"]),
            "category": random.choice(["general", "account", "order", "billing"])
        }
        
        await self._call_function("customer_service", request_data)
    
    async def _order_processing_scenario(self) -> None:
        """Simulate order processing workflow."""
        
        order_id = random.choice(self.order_ids)
        customer_id = random.choice(self.customer_ids)
        
        # Generate realistic order data
        items = []
        item_count = random.randint(1, 3)
        
        for i in range(item_count):
            items.append({
                "item_id": f"item_{random.randint(1, 100):03d}",
                "name": f"Product {random.randint(1, 50)}",
                "sku": f"SKU-{random.randint(1000, 9999)}",
                "quantity": random.randint(1, 5),
                "price": round(random.uniform(10.0, 500.0), 2)
            })
        
        total_amount = sum(item["price"] * item["quantity"] for item in items)
        
        order_data = {
            "order_id": order_id,
            "customer_id": customer_id,
            "items": items,
            "total_amount": total_amount,
            "shipping_address": {
                "street": f"{random.randint(100, 9999)} Main St",
                "city": random.choice(["San Francisco", "New York", "Austin", "Seattle"]),
                "state": random.choice(["CA", "NY", "TX", "WA"]),
                "zip": f"{random.randint(10000, 99999)}"
            },
            "billing_address": {
                "street": f"{random.randint(100, 9999)} Main St",
                "city": random.choice(["San Francisco", "New York", "Austin", "Seattle"]),
                "state": random.choice(["CA", "NY", "TX", "WA"]),
                "zip": f"{random.randint(10000, 99999)}"
            },
            "payment_method": {
                "type": "credit_card",
                "processor": "stripe"
            },
            "priority": random.choice(["normal", "normal", "high"])
        }
        
        await self._call_function("process_order", order_data)
    
    async def _technical_support_scenario(self) -> None:
        """Simulate technical support request."""
        
        customer_id = random.choice(self.customer_ids)
        
        technical_issues = [
            {
                "issue_type": "login",
                "description": "Cannot login to account",
                "error_message": "Authentication failed"
            },
            {
                "issue_type": "performance",
                "description": "Application is running slowly",
                "error_message": "Request timeout"
            },
            {
                "issue_type": "bug",
                "description": "Feature not working correctly",
                "error_message": "Unexpected behavior in checkout"
            }
        ]
        
        issue = random.choice(technical_issues)
        
        request_data = {
            "customer_id": customer_id,
            "issue_type": issue["issue_type"],
            "description": issue["description"],
            "error_message": issue.get("error_message"),
            "priority": random.choice(["normal", "high"])
        }
        
        await self._call_function("technical_support", request_data)
    
    async def _analytics_scenario(self) -> None:
        """Simulate analytics processing request."""
        
        import datetime
        
        # Generate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=random.randint(1, 30))
        
        request_data = {
            "report_type": random.choice([
                "customer_satisfaction",
                "order_analytics", 
                "support_metrics",
                "performance_dashboard"
            ]),
            "period": random.choice(["daily", "weekly"]),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "format": "json"
        }
        
        await self._call_function("analytics", request_data)
    
    async def _call_function(self, function_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call a function via the AGNT5 runtime."""
        
        url = f"{self.config.runtime_endpoint}/v1/functions/{function_name}/invoke"
        
        async with self.session.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"}
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    def _calculate_results(self) -> LoadTestResult:
        """Calculate load test results from collected data."""
        
        if not self.results:
            return LoadTestResult(0, 0, 0, 0, 0, 0, 0, 1.0, 0)
        
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r["success"])
        failed_requests = total_requests - successful_requests
        
        # Calculate latencies
        latencies = [r["latency"] for r in self.results]
        latencies.sort()
        
        average_latency = sum(latencies) / len(latencies)
        p95_latency = latencies[int(len(latencies) * 0.95)]
        p99_latency = latencies[int(len(latencies) * 0.99)]
        
        # Calculate throughput and error rate
        duration = time.time() - self.start_time
        throughput = total_requests / duration
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        return LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_latency=average_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            throughput=throughput,
            error_rate=error_rate,
            duration=duration
        )


async def main():
    """Main load test execution."""
    
    # Load configuration from environment
    config = LoadTestConfig(
        runtime_endpoint=os.getenv("AGNT5_RUNTIME_ENDPOINT", "http://localhost:8080"),
        duration=int(os.getenv("LOAD_TEST_DURATION", "300")),
        concurrency=int(os.getenv("LOAD_TEST_CONCURRENCY", "50")),
        rps=int(os.getenv("LOAD_TEST_RPS", "10"))
    )
    
    # Run load test
    async with LoadGenerator(config) as generator:
        result = await generator.run_load_test()
    
    # Print results
    print(f"\n📊 Load Test Results:")
    print(f"   Duration: {result.duration:.1f}s")
    print(f"   Total Requests: {result.total_requests}")
    print(f"   Successful: {result.successful_requests}")
    print(f"   Failed: {result.failed_requests}")
    print(f"   Error Rate: {result.error_rate:.1%}")
    print(f"   Throughput: {result.throughput:.1f} req/s")
    print(f"   Avg Latency: {result.average_latency:.3f}s")
    print(f"   P95 Latency: {result.p95_latency:.3f}s")
    print(f"   P99 Latency: {result.p99_latency:.3f}s")
    
    # Save results to file
    results_file = "/app/results/load_test_results.json"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump(asdict(result), f, indent=2)
    
    print(f"💾 Results saved to {results_file}")


if __name__ == "__main__":
    asyncio.run(main())