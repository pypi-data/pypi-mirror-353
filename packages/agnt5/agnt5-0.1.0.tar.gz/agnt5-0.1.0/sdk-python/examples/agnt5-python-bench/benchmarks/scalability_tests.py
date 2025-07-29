#!/usr/bin/env python3
"""
Scalability Tests for AGNT5 Python SDK

Tests the scalability characteristics of the SDK under increasing load,
measuring performance degradation and resource utilization patterns.
"""

import asyncio
import time
import psutil
import sys
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Add SDK to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


@dataclass
class ScalabilityResult:
    """Scalability test result."""
    test_name: str
    load_level: int
    duration: float
    throughput: float
    average_latency: float
    p95_latency: float
    error_rate: float
    cpu_usage: float
    memory_usage_mb: float
    success_count: int
    error_count: int


class ScalabilityTests:
    """Scalability testing suite for AGNT5 Python SDK."""
    
    def __init__(self):
        self.results: List[ScalabilityResult] = []
        self.base_memory = 0
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all scalability tests."""
        
        print("🚀 Starting scalability tests...")
        start_time = time.time()
        
        # Measure baseline memory
        self.base_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Test scenarios with increasing load
        await self._test_concurrent_sessions()
        await self._test_high_throughput_orders()
        await self._test_memory_usage_scaling()
        await self._test_long_running_workflows()
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(total_time)
        
        # Save results
        await self._save_results(summary)
        
        return summary
    
    async def _test_concurrent_sessions(self):
        """Test scalability with increasing concurrent sessions."""
        print("📊 Testing concurrent session scalability...")
        
        from objects.customer_session import CustomerSession
        
        # Test with increasing concurrency levels
        concurrency_levels = [10, 25, 50, 100, 200]
        operations_per_session = 20
        
        for concurrency in concurrency_levels:
            print(f"   Testing {concurrency} concurrent sessions...")
            
            async def session_worker(session_id: str) -> Dict[str, Any]:
                """Worker that performs operations on a session."""
                session = CustomerSession(f"scale_{session_id}")
                start_time = time.time()
                errors = 0
                successes = 0
                latencies = []
                
                for i in range(operations_per_session):
                    op_start = time.time()
                    try:
                        await session.add_message("user", f"Scale test message {i}")
                        await session.set_context_variable(f"scale_var_{i}", i)
                        await session.get_context_variable(f"scale_var_{i}")
                        
                        latencies.append(time.time() - op_start)
                        successes += 1
                    except Exception as e:
                        errors += 1
                
                return {
                    "duration": time.time() - start_time,
                    "successes": successes,
                    "errors": errors,
                    "latencies": latencies
                }
            
            # Measure resources before test
            process = psutil.Process()
            cpu_before = process.cpu_percent()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            # Run concurrent workers
            test_start = time.time()
            
            tasks = []
            for i in range(concurrency):
                task = asyncio.create_task(session_worker(f"session_{i:03d}"))
                tasks.append(task)
            
            # Wait for completion
            worker_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            test_duration = time.time() - test_start
            
            # Measure resources after test
            cpu_after = process.cpu_percent()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            # Aggregate results
            total_successes = 0
            total_errors = 0
            all_latencies = []
            
            for result in worker_results:
                if isinstance(result, Exception):
                    total_errors += operations_per_session
                else:
                    total_successes += result["successes"]
                    total_errors += result["errors"]
                    all_latencies.extend(result["latencies"])
            
            # Calculate metrics
            throughput = total_successes / test_duration if test_duration > 0 else 0
            error_rate = total_errors / (total_successes + total_errors) if (total_successes + total_errors) > 0 else 0
            avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
            p95_latency = sorted(all_latencies)[int(len(all_latencies) * 0.95)] if all_latencies else 0
            
            result = ScalabilityResult(
                test_name="concurrent_sessions",
                load_level=concurrency,
                duration=test_duration,
                throughput=throughput,
                average_latency=avg_latency,
                p95_latency=p95_latency,
                error_rate=error_rate,
                cpu_usage=(cpu_after + cpu_before) / 2,
                memory_usage_mb=memory_after - self.base_memory,
                success_count=total_successes,
                error_count=total_errors
            )
            
            self.results.append(result)
            
            print(f"      Throughput: {throughput:.1f} ops/s")
            print(f"      Avg Latency: {avg_latency:.3f}s")
            print(f"      Error Rate: {error_rate:.1%}")
    
    async def _test_high_throughput_orders(self):
        """Test order processing throughput scaling."""
        print("📊 Testing order processing throughput...")
        
        from workflows.order_processing import process_order_workflow
        
        # Mock context
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
        
        # Test with increasing order volumes
        order_counts = [5, 10, 20, 40]
        
        for order_count in order_counts:
            print(f"   Processing {order_count} orders...")
            
            # Measure resources before
            process = psutil.Process()
            cpu_before = process.cpu_percent()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            start_time = time.time()
            successes = 0
            errors = 0
            latencies = []
            
            # Create test orders
            async def process_order(order_id: int) -> Dict[str, Any]:
                order_data = {
                    "order_id": f"SCALE_ORD_{order_id:03d}",
                    "customer_id": f"scale_customer_{order_id}",
                    "items": [
                        {
                            "item_id": "scale_item_001",
                            "name": "Scale Test Product",
                            "sku": "SCALE-001",
                            "quantity": 1,
                            "price": 99.99
                        }
                    ],
                    "total_amount": 99.99,
                    "shipping_address": {
                        "street": "123 Scale St",
                        "city": "Scale City",
                        "state": "SC",
                        "zip": "12345"
                    },
                    "billing_address": {
                        "street": "123 Scale St",
                        "city": "Scale City",
                        "state": "SC",
                        "zip": "12345"
                    },
                    "payment_method": {
                        "type": "credit_card",
                        "processor": "stripe"
                    }
                }
                
                order_start = time.time()
                try:
                    ctx = MockContext()
                    result = await process_order_workflow(ctx, order_data)
                    latencies.append(time.time() - order_start)
                    return {"success": True, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            
            # Process orders concurrently
            tasks = [process_order(i) for i in range(order_count)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = time.time() - start_time
            
            # Count results
            for result in results:
                if isinstance(result, Exception) or not result.get("success", False):
                    errors += 1
                else:
                    successes += 1
            
            # Measure resources after
            cpu_after = process.cpu_percent()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            # Calculate metrics
            throughput = successes / duration if duration > 0 else 0
            error_rate = errors / (successes + errors) if (successes + errors) > 0 else 0
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
            
            result = ScalabilityResult(
                test_name="order_throughput",
                load_level=order_count,
                duration=duration,
                throughput=throughput,
                average_latency=avg_latency,
                p95_latency=p95_latency,
                error_rate=error_rate,
                cpu_usage=(cpu_after + cpu_before) / 2,
                memory_usage_mb=memory_after - self.base_memory,
                success_count=successes,
                error_count=errors
            )
            
            self.results.append(result)
            
            print(f"      Throughput: {throughput:.1f} orders/s")
            print(f"      Avg Latency: {avg_latency:.3f}s")
            print(f"      Error Rate: {error_rate:.1%}")
    
    async def _test_memory_usage_scaling(self):
        """Test memory usage scaling with object count."""
        print("📊 Testing memory usage scaling...")
        
        from objects.customer_session import CustomerSession
        from objects.order_tracker import OrderTracker
        
        # Test with increasing object counts
        object_counts = [50, 100, 200, 500]
        
        for count in object_counts:
            print(f"   Creating {count} objects...")
            
            # Measure memory before
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            start_time = time.time()
            
            # Create objects
            sessions = []
            trackers = []
            
            for i in range(count // 2):
                session = CustomerSession(f"memory_test_{i}")
                await session.add_message("user", f"Memory test message {i}")
                sessions.append(session)
                
                tracker = OrderTracker(f"MEM_ORDER_{i}", f"memory_customer_{i}")
                trackers.append(tracker)
            
            creation_time = time.time() - start_time
            
            # Measure memory after creation
            memory_after_creation = process.memory_info().rss / 1024 / 1024
            
            # Perform operations on objects
            op_start = time.time()
            for i, (session, tracker) in enumerate(zip(sessions[:min(50, len(sessions))], trackers[:min(50, len(trackers))])):
                await session.set_context_variable(f"test_var_{i}", i)
                summary = await tracker.get_order_summary()
            
            operation_time = time.time() - op_start
            
            # Measure final memory
            memory_final = process.memory_info().rss / 1024 / 1024
            
            result = ScalabilityResult(
                test_name="memory_scaling",
                load_level=count,
                duration=creation_time + operation_time,
                throughput=count / creation_time if creation_time > 0 else 0,
                average_latency=creation_time / count if count > 0 else 0,
                p95_latency=0,  # Not applicable for this test
                error_rate=0,  # Assume no errors for memory test
                cpu_usage=process.cpu_percent(),
                memory_usage_mb=memory_final - self.base_memory,
                success_count=count,
                error_count=0
            )
            
            self.results.append(result)
            
            print(f"      Memory per object: {(memory_final - memory_before) / count:.2f} MB")
            print(f"      Creation rate: {result.throughput:.1f} objects/s")
    
    async def _test_long_running_workflows(self):
        """Test performance of long-running workflow scenarios."""
        print("📊 Testing long-running workflow performance...")
        
        from objects.customer_session import CustomerSession
        
        # Simulate long-running sessions with many interactions
        session_durations = [100, 200, 500, 1000]  # Number of interactions
        
        for interaction_count in session_durations:
            print(f"   Testing {interaction_count} interactions...")
            
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            start_time = time.time()
            session = CustomerSession(f"long_running_{interaction_count}")
            
            errors = 0
            successes = 0
            latencies = []
            
            # Simulate long conversation
            for i in range(interaction_count):
                op_start = time.time()
                try:
                    await session.add_message("user", f"Long conversation message {i}")
                    await session.add_message("assistant", f"Response to message {i}", "customer_service")
                    
                    if i % 10 == 0:  # Periodic context updates
                        await session.set_context_variable(f"checkpoint_{i//10}", i)
                    
                    latencies.append(time.time() - op_start)
                    successes += 1
                    
                except Exception as e:
                    errors += 1
            
            duration = time.time() - start_time
            memory_after = process.memory_info().rss / 1024 / 1024
            
            # Get session summary
            summary = await session.get_conversation_summary()
            
            # Calculate metrics
            throughput = successes / duration if duration > 0 else 0
            error_rate = errors / (successes + errors) if (successes + errors) > 0 else 0
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
            
            result = ScalabilityResult(
                test_name="long_running_workflow",
                load_level=interaction_count,
                duration=duration,
                throughput=throughput,
                average_latency=avg_latency,
                p95_latency=p95_latency,
                error_rate=error_rate,
                cpu_usage=process.cpu_percent(),
                memory_usage_mb=memory_after - self.base_memory,
                success_count=successes,
                error_count=errors
            )
            
            self.results.append(result)
            
            print(f"      Throughput: {throughput:.1f} interactions/s")
            print(f"      Session memory: {(memory_after - memory_before):.2f} MB")
            print(f"      Message count: {summary['message_count']}")
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate scalability test summary."""
        
        # Group results by test type
        test_groups = {}
        for result in self.results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)
        
        # Calculate scalability metrics
        scalability_analysis = {}
        
        for test_name, results in test_groups.items():
            if len(results) > 1:
                results.sort(key=lambda x: x.load_level)
                
                # Calculate scalability characteristics
                load_factor = results[-1].load_level / results[0].load_level
                throughput_factor = results[-1].throughput / results[0].throughput if results[0].throughput > 0 else 0
                latency_factor = results[-1].average_latency / results[0].average_latency if results[0].average_latency > 0 else 0
                memory_factor = results[-1].memory_usage_mb / results[0].memory_usage_mb if results[0].memory_usage_mb > 0 else 0
                
                scalability_analysis[test_name] = {
                    "load_factor": load_factor,
                    "throughput_scaling": throughput_factor / load_factor if load_factor > 0 else 0,
                    "latency_degradation": latency_factor,
                    "memory_scaling": memory_factor / load_factor if load_factor > 0 else 0,
                    "linear_scalability_score": min(1.0, throughput_factor / load_factor) if load_factor > 0 else 0
                }
        
        return {
            "test_info": {
                "total_time": total_time,
                "total_tests": len(self.results),
                "timestamp": time.time(),
                "base_memory_mb": self.base_memory
            },
            "results": [asdict(result) for result in self.results],
            "scalability_analysis": scalability_analysis,
            "summary": {
                "best_scaling_test": max(scalability_analysis.items(), key=lambda x: x[1]["linear_scalability_score"])[0] if scalability_analysis else None,
                "worst_scaling_test": min(scalability_analysis.items(), key=lambda x: x[1]["linear_scalability_score"])[0] if scalability_analysis else None,
                "peak_memory_usage": max(r.memory_usage_mb for r in self.results),
                "peak_throughput": max(r.throughput for r in self.results),
                "overall_error_rate": sum(r.error_count for r in self.results) / sum(r.success_count + r.error_count for r in self.results) if sum(r.success_count + r.error_count for r in self.results) > 0 else 0
            }
        }
    
    async def _save_results(self, summary: Dict[str, Any]):
        """Save scalability test results."""
        
        results_dir = "/app/results"
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = f"{results_dir}/scalability_test_{int(time.time())}.json"
        
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Results saved to {results_file}")


async def main():
    """Main scalability test execution."""
    
    print("🧪 AGNT5 Python SDK Scalability Tests")
    print("=" * 50)
    
    tests = ScalabilityTests()
    summary = await tests.run_all_tests()
    
    # Print summary
    print(f"\n📊 Scalability Test Summary:")
    print(f"   Total Time: {summary['test_info']['total_time']:.2f}s")
    print(f"   Total Tests: {summary['test_info']['total_tests']}")
    print(f"   Peak Memory: {summary['summary']['peak_memory_usage']:.1f} MB")
    print(f"   Peak Throughput: {summary['summary']['peak_throughput']:.1f} ops/s")
    print(f"   Overall Error Rate: {summary['summary']['overall_error_rate']:.1%}")
    
    if summary['summary']['best_scaling_test']:
        print(f"   Best Scaling: {summary['summary']['best_scaling_test']}")
    if summary['summary']['worst_scaling_test']:
        print(f"   Worst Scaling: {summary['summary']['worst_scaling_test']}")
    
    print(f"\n📋 Scalability Analysis:")
    for test_name, analysis in summary['scalability_analysis'].items():
        print(f"   {test_name}:")
        print(f"      Linear Scalability Score: {analysis['linear_scalability_score']:.2f}")
        print(f"      Throughput Scaling: {analysis['throughput_scaling']:.2f}")
        print(f"      Latency Degradation: {analysis['latency_degradation']:.2f}x")
        print(f"      Memory Scaling: {analysis['memory_scaling']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())