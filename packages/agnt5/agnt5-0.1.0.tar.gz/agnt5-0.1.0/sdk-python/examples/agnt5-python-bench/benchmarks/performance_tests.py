#!/usr/bin/env python3
"""
Performance Benchmarks for AGNT5 Python SDK

Comprehensive performance testing suite that measures latency, throughput,
and resource utilization across all SDK components.
"""

import asyncio
import json
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

# Add SDK to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from agnt5 import get_worker, setup_logging


@dataclass
class BenchmarkResult:
    """Benchmark test result."""

    test_name: str
    iterations: int
    total_time: float
    average_latency: float
    min_latency: float
    max_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    throughput: float
    success_rate: float
    error_count: int


class PerformanceBenchmarks:
    """Performance benchmark suite for AGNT5 Python SDK."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.setup_complete = False

    async def setup(self):
        """Setup benchmark environment."""
        print("🔧 Setting up performance benchmarks...")

        # Initialize logging
        setup_logging("info")

        # Import benchmark components
        sys.path.insert(0, os.path.dirname(__file__) + "/..")

        self.setup_complete = True
        print("✅ Benchmark setup complete")

    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks."""

        if not self.setup_complete:
            await self.setup()

        print("🚀 Starting performance benchmarks...")
        start_time = time.time()

        # Core SDK benchmarks
        await self._benchmark_agent_creation()
        await self._benchmark_agent_execution()
        await self._benchmark_durable_objects()
        await self._benchmark_workflows()
        await self._benchmark_state_operations()
        await self._benchmark_concurrent_operations()

        total_time = time.time() - start_time

        # Generate summary
        summary = self._generate_summary(total_time)

        # Save results
        await self._save_results(summary)

        return summary

    async def _benchmark_agent_creation(self):
        """Benchmark agent creation performance."""
        print("📊 Benchmarking agent creation...")

        iterations = 100
        latencies = []
        errors = 0

        for i in range(iterations):
            start = time.time()

            try:
                # Import here to avoid import-time overhead
                from agents.customer_service import CustomerServiceAgent

                agent = CustomerServiceAgent()

                latency = time.time() - start
                latencies.append(latency)

            except Exception as e:
                errors += 1
                print(f"Error in agent creation {i}: {e}")

        result = self._calculate_benchmark_result("agent_creation", iterations, latencies, errors)

        self.results.append(result)
        print(f"   Avg latency: {result.average_latency:.3f}s")
        print(f"   P95 latency: {result.p95_latency:.3f}s")

    async def _benchmark_agent_execution(self):
        """Benchmark agent execution performance."""
        print("📊 Benchmarking agent execution...")

        from agents.customer_service import CustomerRequest, CustomerServiceAgent

        agent = CustomerServiceAgent()
        iterations = 50  # Fewer iterations for LLM calls
        latencies = []
        errors = 0

        # Test requests
        test_requests = [CustomerRequest(customer_id=f"cust_{i:03d}", message="I need help with my password", category="technical", priority="normal") for i in range(iterations)]

        for i, request in enumerate(test_requests):
            start = time.time()

            try:
                # Note: This will use mock responses in testing
                response = await agent.handle_request(request)

                latency = time.time() - start
                latencies.append(latency)

            except Exception as e:
                errors += 1
                print(f"Error in agent execution {i}: {e}")

        result = self._calculate_benchmark_result("agent_execution", iterations, latencies, errors)

        self.results.append(result)
        print(f"   Avg latency: {result.average_latency:.3f}s")
        print(f"   P95 latency: {result.p95_latency:.3f}s")

    async def _benchmark_durable_objects(self):
        """Benchmark durable object operations."""
        print("📊 Benchmarking durable objects...")

        from objects.customer_session import CustomerSession

        iterations = 200
        latencies = []
        errors = 0

        # Create session once
        session = CustomerSession("bench_customer")

        for i in range(iterations):
            start = time.time()

            try:
                # Test various operations
                await session.add_message("user", f"Test message {i}")
                await session.set_context_variable(f"var_{i}", f"value_{i}")
                value = await session.get_context_variable(f"var_{i}")

                latency = time.time() - start
                latencies.append(latency)

            except Exception as e:
                errors += 1
                print(f"Error in durable object operation {i}: {e}")

        result = self._calculate_benchmark_result("durable_objects", iterations, latencies, errors)

        self.results.append(result)
        print(f"   Avg latency: {result.average_latency:.3f}s")
        print(f"   P95 latency: {result.p95_latency:.3f}s")

    async def _benchmark_workflows(self):
        """Benchmark workflow execution performance."""
        print("📊 Benchmarking workflows...")

        from workflows.order_processing import process_order_workflow

        iterations = 20  # Fewer iterations for complex workflows
        latencies = []
        errors = 0

        # Mock context for testing
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

        # Test order data
        test_order = {
            "order_id": f"ORD_BENCH_001",
            "customer_id": "bench_customer",
            "items": [{"item_id": "item_001", "name": "Test Product", "sku": "TEST-001", "quantity": 1, "price": 99.99}],
            "total_amount": 99.99,
            "shipping_address": {"street": "123 Test St", "city": "Test City", "state": "TS", "zip": "12345"},
            "billing_address": {"street": "123 Test St", "city": "Test City", "state": "TS", "zip": "12345"},
            "payment_method": {"type": "credit_card", "processor": "stripe"},
        }

        for i in range(iterations):
            start = time.time()

            try:
                ctx = MockContext()
                test_order["order_id"] = f"ORD_BENCH_{i:03d}"

                result = await process_order_workflow(ctx, test_order)

                latency = time.time() - start
                latencies.append(latency)

            except Exception as e:
                errors += 1
                print(f"Error in workflow execution {i}: {e}")

        result = self._calculate_benchmark_result("workflows", iterations, latencies, errors)

        self.results.append(result)
        print(f"   Avg latency: {result.average_latency:.3f}s")
        print(f"   P95 latency: {result.p95_latency:.3f}s")

    async def _benchmark_state_operations(self):
        """Benchmark state storage and retrieval."""
        print("📊 Benchmarking state operations...")

        from objects.order_tracker import OrderTracker

        iterations = 300
        latencies = []
        errors = 0

        # Create order tracker
        tracker = OrderTracker("BENCH_ORDER", "bench_customer")

        for i in range(iterations):
            start = time.time()

            try:
                # Test state operations
                summary = await tracker.get_order_summary()
                events = await tracker.get_recent_events(5)

                latency = time.time() - start
                latencies.append(latency)

            except Exception as e:
                errors += 1
                print(f"Error in state operation {i}: {e}")

        result = self._calculate_benchmark_result("state_operations", iterations, latencies, errors)

        self.results.append(result)
        print(f"   Avg latency: {result.average_latency:.3f}s")
        print(f"   P95 latency: {result.p95_latency:.3f}s")

    async def _benchmark_concurrent_operations(self):
        """Benchmark concurrent operation performance."""
        print("📊 Benchmarking concurrent operations...")

        from objects.customer_session import CustomerSession

        concurrent_sessions = 20
        operations_per_session = 10
        total_operations = concurrent_sessions * operations_per_session

        async def session_worker(session_id: str) -> List[float]:
            """Worker that performs operations on a session."""
            session = CustomerSession(f"concurrent_{session_id}")
            latencies = []

            for i in range(operations_per_session):
                start = time.time()

                try:
                    await session.add_message("user", f"Concurrent message {i}")
                    await session.set_context_variable(f"concurrent_var_{i}", i)

                    latency = time.time() - start
                    latencies.append(latency)

                except Exception as e:
                    print(f"Error in concurrent operation {session_id}:{i}: {e}")

            return latencies

        # Run concurrent workers
        start_time = time.time()

        tasks = []
        for i in range(concurrent_sessions):
            task = asyncio.create_task(session_worker(f"session_{i:02d}"))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # Collect all latencies
        all_latencies = []
        errors = 0

        for result in results:
            if isinstance(result, Exception):
                errors += 1
            else:
                all_latencies.extend(result)

        result = self._calculate_benchmark_result("concurrent_operations", total_operations, all_latencies, errors)

        self.results.append(result)
        print(f"   Concurrent sessions: {concurrent_sessions}")
        print(f"   Avg latency: {result.average_latency:.3f}s")
        print(f"   P95 latency: {result.p95_latency:.3f}s")

    def _calculate_benchmark_result(self, test_name: str, iterations: int, latencies: List[float], errors: int) -> BenchmarkResult:
        """Calculate benchmark result from latency data."""

        if not latencies:
            return BenchmarkResult(
                test_name=test_name,
                iterations=iterations,
                total_time=0,
                average_latency=0,
                min_latency=0,
                max_latency=0,
                p50_latency=0,
                p95_latency=0,
                p99_latency=0,
                throughput=0,
                success_rate=0,
                error_count=errors,
            )

        latencies_sorted = sorted(latencies)
        total_time = sum(latencies)

        return BenchmarkResult(
            test_name=test_name,
            iterations=iterations,
            total_time=total_time,
            average_latency=statistics.mean(latencies),
            min_latency=min(latencies),
            max_latency=max(latencies),
            p50_latency=statistics.median(latencies),
            p95_latency=latencies_sorted[int(len(latencies_sorted) * 0.95)],
            p99_latency=latencies_sorted[int(len(latencies_sorted) * 0.99)],
            throughput=len(latencies) / total_time if total_time > 0 else 0,
            success_rate=(iterations - errors) / iterations if iterations > 0 else 0,
            error_count=errors,
        )

    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate benchmark summary."""

        return {
            "benchmark_info": {"total_time": total_time, "total_tests": len(self.results), "timestamp": time.time(), "python_version": sys.version, "platform": sys.platform},
            "results": [asdict(result) for result in self.results],
            "summary": {
                "total_operations": sum(r.iterations for r in self.results),
                "total_errors": sum(r.error_count for r in self.results),
                "average_success_rate": statistics.mean([r.success_rate for r in self.results]),
                "fastest_test": min(self.results, key=lambda x: x.average_latency).test_name,
                "slowest_test": max(self.results, key=lambda x: x.average_latency).test_name,
                "highest_throughput": max(self.results, key=lambda x: x.throughput).test_name,
            },
        }

    async def _save_results(self, summary: Dict[str, Any]):
        """Save benchmark results to file."""

        results_dir = "/app/results"
        os.makedirs(results_dir, exist_ok=True)

        results_file = f"{results_dir}/performance_benchmark_{int(time.time())}.json"

        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"💾 Results saved to {results_file}")


async def main():
    """Main benchmark execution."""

    print("🧪 AGNT5 Python SDK Performance Benchmarks")
    print("=" * 50)

    benchmarks = PerformanceBenchmarks()
    summary = await benchmarks.run_all_benchmarks()

    # Print summary
    print(f"\n📊 Benchmark Summary:")
    print(f"   Total Time: {summary['benchmark_info']['total_time']:.2f}s")
    print(f"   Total Tests: {summary['benchmark_info']['total_tests']}")
    print(f"   Total Operations: {summary['summary']['total_operations']}")
    print(f"   Total Errors: {summary['summary']['total_errors']}")
    print(f"   Avg Success Rate: {summary['summary']['average_success_rate']:.1%}")
    print(f"   Fastest Test: {summary['summary']['fastest_test']}")
    print(f"   Slowest Test: {summary['summary']['slowest_test']}")
    print(f"   Highest Throughput: {summary['summary']['highest_throughput']}")

    print(f"\n📋 Individual Test Results:")
    for result in summary["results"]:
        print(f"   {result['test_name']}:")
        print(f"      Iterations: {result['iterations']}")
        print(f"      Avg Latency: {result['average_latency']:.3f}s")
        print(f"      P95 Latency: {result['p95_latency']:.3f}s")
        print(f"      Throughput: {result['throughput']:.1f} ops/s")
        print(f"      Success Rate: {result['success_rate']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
