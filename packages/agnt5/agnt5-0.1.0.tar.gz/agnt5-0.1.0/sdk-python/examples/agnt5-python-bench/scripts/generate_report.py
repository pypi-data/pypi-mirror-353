#!/usr/bin/env python3
"""
Benchmark Report Generator

Generates comprehensive reports from benchmark results with charts and analysis.
"""

import json
import os
import sys
import glob
from typing import Dict, Any, List
from datetime import datetime


def load_benchmark_results(results_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load all benchmark result files."""
    
    results = {
        "performance": [],
        "scalability": [],
        "load_test": []
    }
    
    # Find all result files
    for pattern in ["performance_*.json", "scalability_*.json", "load_test_*.json"]:
        files = glob.glob(os.path.join(results_dir, pattern))
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if "performance" in file_path:
                    results["performance"].append(data)
                elif "scalability" in file_path:
                    results["scalability"].append(data)
                elif "load_test" in file_path:
                    results["load_test"].append(data)
                    
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}", file=sys.stderr)
    
    return results


def generate_performance_summary(performance_results: List[Dict[str, Any]]) -> str:
    """Generate performance benchmark summary."""
    
    if not performance_results:
        return "No performance benchmark results found.\n"
    
    # Use the most recent results
    latest_result = max(performance_results, key=lambda x: x["benchmark_info"]["timestamp"])
    
    summary = []
    summary.append("PERFORMANCE BENCHMARK RESULTS")
    summary.append("=" * 40)
    summary.append("")
    
    # Basic info
    total_time = latest_result["benchmark_info"]["total_time"]
    total_tests = latest_result["benchmark_info"]["total_tests"]
    
    summary.append(f"Benchmark Duration: {total_time:.2f}s")
    summary.append(f"Total Tests: {total_tests}")
    summary.append(f"Timestamp: {datetime.fromtimestamp(latest_result['benchmark_info']['timestamp'])}")
    summary.append("")
    
    # Test results
    summary.append("Test Results:")
    summary.append("-" * 20)
    
    for result in latest_result["results"]:
        test_name = result["test_name"]
        iterations = result["iterations"]
        avg_latency = result["average_latency"]
        p95_latency = result["p95_latency"]
        throughput = result["throughput"]
        success_rate = result["success_rate"]
        
        summary.append(f"{test_name}:")
        summary.append(f"  Iterations: {iterations}")
        summary.append(f"  Avg Latency: {avg_latency:.3f}s")
        summary.append(f"  P95 Latency: {p95_latency:.3f}s")
        summary.append(f"  Throughput: {throughput:.1f} ops/s")
        summary.append(f"  Success Rate: {success_rate:.1%}")
        summary.append("")
    
    # Summary metrics
    if "summary" in latest_result:
        summary.append("Summary:")
        summary.append("-" * 10)
        
        total_ops = latest_result["summary"]["total_operations"]
        total_errors = latest_result["summary"]["total_errors"]
        avg_success_rate = latest_result["summary"]["average_success_rate"]
        fastest_test = latest_result["summary"]["fastest_test"]
        slowest_test = latest_result["summary"]["slowest_test"]
        
        summary.append(f"Total Operations: {total_ops}")
        summary.append(f"Total Errors: {total_errors}")
        summary.append(f"Avg Success Rate: {avg_success_rate:.1%}")
        summary.append(f"Fastest Test: {fastest_test}")
        summary.append(f"Slowest Test: {slowest_test}")
        summary.append("")
    
    return "\n".join(summary)


def generate_scalability_summary(scalability_results: List[Dict[str, Any]]) -> str:
    """Generate scalability test summary."""
    
    if not scalability_results:
        return "No scalability test results found.\n"
    
    # Use the most recent results
    latest_result = max(scalability_results, key=lambda x: x["test_info"]["timestamp"])
    
    summary = []
    summary.append("SCALABILITY TEST RESULTS")
    summary.append("=" * 30)
    summary.append("")
    
    # Basic info
    total_time = latest_result["test_info"]["total_time"]
    total_tests = latest_result["test_info"]["total_tests"]
    base_memory = latest_result["test_info"]["base_memory_mb"]
    
    summary.append(f"Test Duration: {total_time:.2f}s")
    summary.append(f"Total Tests: {total_tests}")
    summary.append(f"Base Memory: {base_memory:.1f} MB")
    summary.append(f"Timestamp: {datetime.fromtimestamp(latest_result['test_info']['timestamp'])}")
    summary.append("")
    
    # Scalability analysis
    if "scalability_analysis" in latest_result:
        summary.append("Scalability Analysis:")
        summary.append("-" * 25)
        
        for test_name, analysis in latest_result["scalability_analysis"].items():
            linear_score = analysis["linear_scalability_score"]
            throughput_scaling = analysis["throughput_scaling"]
            latency_degradation = analysis["latency_degradation"]
            memory_scaling = analysis["memory_scaling"]
            
            summary.append(f"{test_name}:")
            summary.append(f"  Linear Scalability Score: {linear_score:.2f}")
            summary.append(f"  Throughput Scaling: {throughput_scaling:.2f}")
            summary.append(f"  Latency Degradation: {latency_degradation:.2f}x")
            summary.append(f"  Memory Scaling: {memory_scaling:.2f}")
            summary.append("")
    
    # Summary metrics
    if "summary" in latest_result:
        summary.append("Summary:")
        summary.append("-" * 10)
        
        peak_memory = latest_result["summary"]["peak_memory_usage"]
        peak_throughput = latest_result["summary"]["peak_throughput"]
        error_rate = latest_result["summary"]["overall_error_rate"]
        best_scaling = latest_result["summary"].get("best_scaling_test")
        worst_scaling = latest_result["summary"].get("worst_scaling_test")
        
        summary.append(f"Peak Memory Usage: {peak_memory:.1f} MB")
        summary.append(f"Peak Throughput: {peak_throughput:.1f} ops/s")
        summary.append(f"Overall Error Rate: {error_rate:.1%}")
        
        if best_scaling:
            summary.append(f"Best Scaling Test: {best_scaling}")
        if worst_scaling:
            summary.append(f"Worst Scaling Test: {worst_scaling}")
        
        summary.append("")
    
    # Detailed results
    summary.append("Detailed Results:")
    summary.append("-" * 20)
    
    # Group results by test type
    test_groups = {}
    for result in latest_result["results"]:
        test_name = result["test_name"]
        if test_name not in test_groups:
            test_groups[test_name] = []
        test_groups[test_name].append(result)
    
    for test_name, results in test_groups.items():
        summary.append(f"{test_name}:")
        
        for result in sorted(results, key=lambda x: x["load_level"]):
            load_level = result["load_level"]
            throughput = result["throughput"]
            avg_latency = result["average_latency"]
            memory_usage = result["memory_usage_mb"]
            error_rate = result["error_rate"]
            
            summary.append(f"  Load {load_level}: {throughput:.1f} ops/s, "
                         f"{avg_latency:.3f}s latency, "
                         f"{memory_usage:.1f} MB memory, "
                         f"{error_rate:.1%} errors")
        
        summary.append("")
    
    return "\n".join(summary)


def generate_load_test_summary(load_test_results: List[Dict[str, Any]]) -> str:
    """Generate load test summary."""
    
    if not load_test_results:
        return "No load test results found.\n"
    
    summary = []
    summary.append("LOAD TEST RESULTS")
    summary.append("=" * 20)
    summary.append("")
    
    for i, result in enumerate(load_test_results, 1):
        summary.append(f"Load Test {i}:")
        summary.append(f"  Duration: {result['duration']:.1f}s")
        summary.append(f"  Total Requests: {result['total_requests']}")
        summary.append(f"  Successful: {result['successful_requests']}")
        summary.append(f"  Failed: {result['failed_requests']}")
        summary.append(f"  Error Rate: {result['error_rate']:.1%}")
        summary.append(f"  Throughput: {result['throughput']:.1f} req/s")
        summary.append(f"  Avg Latency: {result['average_latency']:.3f}s")
        summary.append(f"  P95 Latency: {result['p95_latency']:.3f}s")
        summary.append(f"  P99 Latency: {result['p99_latency']:.3f}s")
        summary.append("")
    
    return "\n".join(summary)


def generate_comparison_analysis(results: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate cross-benchmark comparison analysis."""
    
    summary = []
    summary.append("BENCHMARK COMPARISON ANALYSIS")
    summary.append("=" * 35)
    summary.append("")
    
    # Performance vs Load Test comparison
    if results["performance"] and results["load_test"]:
        perf_result = results["performance"][-1]
        load_result = results["load_test"][-1]
        
        summary.append("Performance vs Load Test:")
        summary.append("-" * 30)
        
        # Find comparable metrics
        if "results" in perf_result:
            # Get agent execution performance
            agent_perf = next(
                (r for r in perf_result["results"] if r["test_name"] == "agent_execution"),
                None
            )
            
            if agent_perf:
                summary.append(f"Agent Execution (Isolated): {agent_perf['throughput']:.1f} ops/s")
                summary.append(f"Agent Execution (Load Test): {load_result['throughput']:.1f} req/s")
                
                if agent_perf['throughput'] > 0:
                    performance_ratio = load_result['throughput'] / agent_perf['throughput']
                    summary.append(f"Load Test Performance Ratio: {performance_ratio:.2f}")
                
                summary.append("")
    
    # Scalability insights
    if results["scalability"]:
        scalability_result = results["scalability"][-1]
        
        summary.append("Scalability Insights:")
        summary.append("-" * 22)
        
        if "scalability_analysis" in scalability_result:
            best_score = 0
            worst_score = 1
            
            for test_name, analysis in scalability_result["scalability_analysis"].items():
                score = analysis["linear_scalability_score"]
                if score > best_score:
                    best_score = score
                if score < worst_score:
                    worst_score = score
            
            summary.append(f"Best Scalability Score: {best_score:.2f}")
            summary.append(f"Worst Scalability Score: {worst_score:.2f}")
            summary.append(f"Scalability Range: {best_score - worst_score:.2f}")
            summary.append("")
    
    # Resource utilization
    peak_memory = 0
    peak_throughput = 0
    
    for result_type, result_list in results.items():
        for result in result_list:
            if result_type == "performance" and "results" in result:
                for test_result in result["results"]:
                    if test_result["throughput"] > peak_throughput:
                        peak_throughput = test_result["throughput"]
            
            elif result_type == "scalability" and "summary" in result:
                memory = result["summary"].get("peak_memory_usage", 0)
                throughput = result["summary"].get("peak_throughput", 0)
                
                if memory > peak_memory:
                    peak_memory = memory
                if throughput > peak_throughput:
                    peak_throughput = throughput
            
            elif result_type == "load_test":
                if result["throughput"] > peak_throughput:
                    peak_throughput = result["throughput"]
    
    summary.append("Resource Utilization:")
    summary.append("-" * 22)
    summary.append(f"Peak Memory Usage: {peak_memory:.1f} MB")
    summary.append(f"Peak Throughput: {peak_throughput:.1f} ops/s")
    summary.append("")
    
    return "\n".join(summary)


def generate_recommendations(results: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate performance recommendations based on results."""
    
    summary = []
    summary.append("PERFORMANCE RECOMMENDATIONS")
    summary.append("=" * 30)
    summary.append("")
    
    recommendations = []
    
    # Analyze error rates
    total_errors = 0
    total_operations = 0
    
    for result_type, result_list in results.items():
        for result in result_list:
            if result_type == "performance" and "summary" in result:
                total_errors += result["summary"]["total_errors"]
                total_operations += result["summary"]["total_operations"]
            elif result_type == "scalability" and "summary" in result:
                error_rate = result["summary"]["overall_error_rate"]
                if error_rate > 0.01:  # > 1% error rate
                    recommendations.append(
                        f"• Scalability tests show {error_rate:.1%} error rate - investigate error handling"
                    )
    
    if total_operations > 0:
        overall_error_rate = total_errors / total_operations
        if overall_error_rate > 0.05:  # > 5% error rate
            recommendations.append(
                f"• High error rate ({overall_error_rate:.1%}) detected - review error handling and retry logic"
            )
    
    # Analyze latency
    high_latency_tests = []
    for result_type, result_list in results.items():
        for result in result_list:
            if result_type == "performance" and "results" in result:
                for test_result in result["results"]:
                    if test_result["p95_latency"] > 1.0:  # > 1 second P95
                        high_latency_tests.append(test_result["test_name"])
    
    if high_latency_tests:
        recommendations.append(
            f"• High latency detected in: {', '.join(set(high_latency_tests))} - consider optimization"
        )
    
    # Analyze scalability
    if results["scalability"]:
        scalability_result = results["scalability"][-1]
        if "scalability_analysis" in scalability_result:
            poor_scaling_tests = []
            
            for test_name, analysis in scalability_result["scalability_analysis"].items():
                score = analysis["linear_scalability_score"]
                if score < 0.5:  # Poor scalability
                    poor_scaling_tests.append(test_name)
            
            if poor_scaling_tests:
                recommendations.append(
                    f"• Poor scalability in: {', '.join(poor_scaling_tests)} - review concurrency patterns"
                )
    
    # Memory recommendations
    if results["scalability"]:
        scalability_result = results["scalability"][-1]
        if "summary" in scalability_result:
            peak_memory = scalability_result["summary"]["peak_memory_usage"]
            if peak_memory > 1000:  # > 1GB
                recommendations.append(
                    f"• High memory usage ({peak_memory:.0f} MB) - consider memory optimization"
                )
    
    # Generic recommendations
    if not recommendations:
        recommendations.extend([
            "• Performance appears to be within acceptable ranges",
            "• Consider running extended load tests for production validation",
            "• Monitor memory usage patterns in production environments",
            "• Implement alerting for error rates and latency thresholds"
        ])
    
    for recommendation in recommendations:
        summary.append(recommendation)
    
    summary.append("")
    
    return "\n".join(summary)


def main():
    """Main report generation."""
    
    if len(sys.argv) != 2:
        print("Usage: python generate_report.py <results_directory>")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    
    if not os.path.exists(results_dir):
        print(f"Results directory does not exist: {results_dir}")
        sys.exit(1)
    
    # Load all results
    results = load_benchmark_results(results_dir)
    
    # Generate report sections
    print("AGNT5 PYTHON BENCHMARK REPORT")
    print("=" * 50)
    print(f"Generated: {datetime.now()}")
    print(f"Results Directory: {results_dir}")
    print("")
    
    # Performance summary
    print(generate_performance_summary(results["performance"]))
    
    # Scalability summary
    print(generate_scalability_summary(results["scalability"]))
    
    # Load test summary
    print(generate_load_test_summary(results["load_test"]))
    
    # Comparison analysis
    print(generate_comparison_analysis(results))
    
    # Recommendations
    print(generate_recommendations(results))
    
    print("=" * 50)
    print("End of Report")


if __name__ == "__main__":
    main()