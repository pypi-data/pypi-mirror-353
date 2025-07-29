#!/usr/bin/env python3
"""
Simple standalone benchmark for AGNT5 Python components

This benchmark tests the core components without relying on the full SDK,
providing a basic performance baseline for the application architecture.
"""

import asyncio
import time
import statistics
import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class BenchmarkResult:
    """Simple benchmark result."""
    test_name: str
    iterations: int
    total_time: float
    average_latency: float
    p95_latency: float
    throughput: float
    success_rate: float


class SimpleBenchmark:
    """Standalone benchmark for core components."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all simple benchmarks."""
        
        print("🚀 Starting Simple AGNT5 Benchmarks")
        print("=" * 40)
        
        start_time = time.time()
        
        # Test core components independently
        await self._test_customer_session()
        await self._test_order_tracker()
        await self._test_knowledge_base()
        await self._test_workflow_simulation()
        await self._test_concurrent_operations()
        
        total_time = time.time() - start_time
        
        # Generate report
        summary = self._generate_summary(total_time)
        
        # Save results
        await self._save_results(summary)
        
        return summary
    
    async def _test_customer_session(self):
        """Test CustomerSession durable object performance."""
        print("📊 Testing CustomerSession performance...")
        
        # Import locally to avoid global import issues
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        
        from objects.customer_session import CustomerSession
        
        iterations = 100
        latencies = []
        errors = 0
        
        session = CustomerSession("benchmark_customer")
        
        for i in range(iterations):
            start = time.time()
            
            try:
                await session.add_message("user", f"Benchmark message {i}")
                await session.set_context_variable(f"bench_var_{i}", i)
                await session.get_context_variable(f"bench_var_{i}")
                
                latency = time.time() - start
                latencies.append(latency)
                
            except Exception as e:
                errors += 1
                print(f"   Error in iteration {i}: {e}")
        
        result = self._calculate_result("customer_session", iterations, latencies, errors)
        self.results.append(result)
        
        print(f"   Avg Latency: {result.average_latency:.3f}s")
        print(f"   Throughput: {result.throughput:.1f} ops/s")
        print(f"   Success Rate: {result.success_rate:.1%}")
    
    async def _test_order_tracker(self):
        """Test OrderTracker durable object performance."""
        print("📊 Testing OrderTracker performance...")
        
        from objects.order_tracker import OrderTracker
        from decimal import Decimal
        
        iterations = 50
        latencies = []
        errors = 0
        
        for i in range(iterations):
            start = time.time()
            
            try:
                tracker = OrderTracker(f"BENCH_ORDER_{i}", "benchmark_customer")
                
                # Add an item
                await tracker.add_item(
                    f"item_{i}",
                    f"Benchmark Product {i}",
                    f"BENCH-{i:03d}",
                    1,
                    Decimal("99.99")
                )
                
                # Get summary
                summary = await tracker.get_order_summary()
                
                latency = time.time() - start
                latencies.append(latency)
                
            except Exception as e:
                errors += 1
                print(f"   Error in iteration {i}: {e}")
        
        result = self._calculate_result("order_tracker", iterations, latencies, errors)
        self.results.append(result)
        
        print(f"   Avg Latency: {result.average_latency:.3f}s")
        print(f"   Throughput: {result.throughput:.1f} ops/s")
        print(f"   Success Rate: {result.success_rate:.1%}")
    
    async def _test_knowledge_base(self):
        """Test KnowledgeBase search performance."""
        print("📊 Testing KnowledgeBase performance...")
        
        from objects.knowledge_base import KnowledgeBase, SearchQuery
        
        iterations = 30
        latencies = []
        errors = 0
        
        # Create knowledge base (will auto-initialize with content)
        kb = KnowledgeBase("benchmark_kb")
        
        # Wait for initialization
        await asyncio.sleep(0.2)
        
        search_queries = [
            "password reset",
            "order tracking",
            "refund policy",
            "login issues",
            "shipping information"
        ]
        
        for i in range(iterations):
            start = time.time()
            
            try:
                query_text = search_queries[i % len(search_queries)]
                query = SearchQuery(query=query_text)
                
                results = await kb.search(query)
                
                latency = time.time() - start
                latencies.append(latency)
                
            except Exception as e:
                errors += 1
                print(f"   Error in iteration {i}: {e}")
        
        result = self._calculate_result("knowledge_base", iterations, latencies, errors)
        self.results.append(result)
        
        print(f"   Avg Latency: {result.average_latency:.3f}s")
        print(f"   Throughput: {result.throughput:.1f} ops/s")
        print(f"   Success Rate: {result.success_rate:.1%}")
    
    async def _test_workflow_simulation(self):
        """Test workflow tools performance."""
        print("📊 Testing Workflow Tools performance...")
        
        from workflows.order_processing import (
            validate_order_data,
            check_inventory_availability,
            process_payment,
            create_fulfillment_order
        )
        
        iterations = 40
        latencies = []
        errors = 0
        
        # Test order data
        test_order = {
            "order_id": "BENCH_ORDER_001",
            "customer_id": "benchmark_customer",
            "items": [
                {
                    "item_id": "bench_item_001",
                    "name": "Benchmark Product",
                    "quantity": 1,
                    "price": 99.99
                }
            ],
            "total_amount": 99.99,
            "shipping_address": {
                "street": "123 Benchmark St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            },
            "billing_address": {
                "street": "123 Benchmark St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            }
        }
        
        for i in range(iterations):
            start = time.time()
            
            try:
                # Test workflow steps
                validation = validate_order_data(test_order)
                inventory = check_inventory_availability(test_order["items"])
                payment = process_payment({"processor": "stripe"}, 99.99)
                fulfillment = create_fulfillment_order(
                    f"BENCH_ORDER_{i}",
                    test_order["items"],
                    test_order["shipping_address"]
                )
                
                latency = time.time() - start
                latencies.append(latency)
                
            except Exception as e:
                errors += 1
                print(f"   Error in iteration {i}: {e}")
        
        result = self._calculate_result("workflow_tools", iterations, latencies, errors)
        self.results.append(result)
        
        print(f"   Avg Latency: {result.average_latency:.3f}s")
        print(f"   Throughput: {result.throughput:.1f} ops/s")
        print(f"   Success Rate: {result.success_rate:.1%}")
    
    async def _test_concurrent_operations(self):
        """Test concurrent performance."""
        print("📊 Testing Concurrent Operations...")
        
        from objects.customer_session import CustomerSession
        
        concurrent_sessions = 10
        operations_per_session = 20
        
        async def session_worker(session_id: str) -> List[float]:
            """Worker function for concurrent testing."""
            session = CustomerSession(f"concurrent_bench_{session_id}")
            latencies = []
            
            for i in range(operations_per_session):
                start = time.time()
                
                try:
                    await session.add_message("user", f"Concurrent message {i}")
                    await session.set_context_variable(f"concurrent_var_{i}", i)
                    
                    latency = time.time() - start
                    latencies.append(latency)
                    
                except Exception as e:
                    print(f"   Concurrent error in {session_id}:{i}: {e}")
            
            return latencies
        
        # Run concurrent workers
        start_time = time.time()
        
        tasks = []
        for i in range(concurrent_sessions):
            task = asyncio.create_task(session_worker(f"session_{i:02d}"))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all latencies
        all_latencies = []
        errors = 0
        
        for result in results:
            if isinstance(result, Exception):
                errors += 1
            else:
                all_latencies.extend(result)
        
        total_operations = concurrent_sessions * operations_per_session
        result = self._calculate_result("concurrent_operations", total_operations, all_latencies, errors)
        self.results.append(result)
        
        print(f"   Concurrent Sessions: {concurrent_sessions}")
        print(f"   Avg Latency: {result.average_latency:.3f}s")
        print(f"   Throughput: {result.throughput:.1f} ops/s")
        print(f"   Success Rate: {result.success_rate:.1%}")
    
    def _calculate_result(
        self,
        test_name: str,
        iterations: int,
        latencies: List[float],
        errors: int
    ) -> BenchmarkResult:
        """Calculate benchmark result."""
        
        if not latencies:
            return BenchmarkResult(
                test_name=test_name,
                iterations=iterations,
                total_time=0,
                average_latency=0,
                p95_latency=0,
                throughput=0,
                success_rate=0
            )
        
        latencies_sorted = sorted(latencies)
        total_time = sum(latencies)
        
        return BenchmarkResult(
            test_name=test_name,
            iterations=iterations,
            total_time=total_time,
            average_latency=statistics.mean(latencies),
            p95_latency=latencies_sorted[int(len(latencies_sorted) * 0.95)],
            throughput=len(latencies) / total_time if total_time > 0 else 0,
            success_rate=(iterations - errors) / iterations if iterations > 0 else 0
        )
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate benchmark summary."""
        
        return {
            "benchmark_info": {
                "total_time": total_time,
                "total_tests": len(self.results),
                "timestamp": time.time()
            },
            "results": [asdict(result) for result in self.results],
            "summary": {
                "fastest_test": min(self.results, key=lambda x: x.average_latency).test_name if self.results else None,
                "slowest_test": max(self.results, key=lambda x: x.average_latency).test_name if self.results else None,
                "highest_throughput": max(self.results, key=lambda x: x.throughput).test_name if self.results else None,
                "average_success_rate": statistics.mean([r.success_rate for r in self.results]) if self.results else 0
            }
        }
    
    async def _save_results(self, summary: Dict[str, Any]):
        """Save benchmark results."""
        
        results_file = f"simple_benchmark_results_{int(time.time())}.json"
        
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to {results_file}")


async def main():
    """Run the simple benchmark."""
    
    benchmark = SimpleBenchmark()
    summary = await benchmark.run_all_benchmarks()
    
    # Print detailed report
    print(f"\n" + "=" * 50)
    print("📊 SIMPLE BENCHMARK REPORT")
    print("=" * 50)
    
    print(f"\n🔧 Test Information:")
    print(f"   Total Duration: {summary['benchmark_info']['total_time']:.2f}s")
    print(f"   Total Tests: {summary['benchmark_info']['total_tests']}")
    
    print(f"\n📈 Summary:")
    print(f"   Fastest Test: {summary['summary']['fastest_test']}")
    print(f"   Slowest Test: {summary['summary']['slowest_test']}")
    print(f"   Highest Throughput: {summary['summary']['highest_throughput']}")
    print(f"   Average Success Rate: {summary['summary']['average_success_rate']:.1%}")
    
    print(f"\n📋 Detailed Results:")
    for result in summary['results']:
        print(f"\n   {result['test_name']}:")
        print(f"      Iterations: {result['iterations']}")
        print(f"      Total Time: {result['total_time']:.2f}s")
        print(f"      Avg Latency: {result['average_latency']:.3f}s")
        print(f"      P95 Latency: {result['p95_latency']:.3f}s")
        print(f"      Throughput: {result['throughput']:.1f} ops/s")
        print(f"      Success Rate: {result['success_rate']:.1%}")
    
    print(f"\n" + "=" * 50)
    print("✅ Benchmark Complete")


if __name__ == "__main__":
    asyncio.run(main())