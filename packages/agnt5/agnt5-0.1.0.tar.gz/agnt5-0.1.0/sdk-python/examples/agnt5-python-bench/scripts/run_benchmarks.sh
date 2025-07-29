#!/bin/bash
set -e

# AGNT5 Python Benchmark Runner Script
# Orchestrates running the complete benchmark suite with various configurations

echo "🚀 AGNT5 Python Benchmark Suite"
echo "================================"

# Configuration
RUNTIME_ENDPOINT=${AGNT5_RUNTIME_ENDPOINT:-"http://agnt5-runtime:8080"}
RESULTS_DIR=${AGNT5_RESULTS_DIR:-"/app/results"}
LOG_LEVEL=${AGNT5_LOG_LEVEL:-"INFO"}

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to wait for runtime to be ready
wait_for_runtime() {
    echo "⏳ Waiting for AGNT5 runtime to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$RUNTIME_ENDPOINT/health" > /dev/null 2>&1; then
            echo "✅ Runtime is ready"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - Runtime not ready, waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ Runtime failed to become ready after $max_attempts attempts"
    return 1
}

# Function to run individual benchmark
run_benchmark() {
    local benchmark_name="$1"
    local script_path="$2"
    
    echo ""
    echo "🔥 Running $benchmark_name"
    echo "========================"
    
    if python "$script_path"; then
        echo "✅ $benchmark_name completed successfully"
        return 0
    else
        echo "❌ $benchmark_name failed"
        return 1
    fi
}

# Function to start the benchmark worker
start_worker() {
    echo "🤖 Starting AGNT5 Python benchmark worker..."
    
    # Start worker in background
    python main.py &
    WORKER_PID=$!
    
    # Wait for worker to initialize
    sleep 15
    
    # Check if worker is still running
    if ! kill -0 $WORKER_PID 2>/dev/null; then
        echo "❌ Worker failed to start"
        return 1
    fi
    
    echo "✅ Worker started with PID $WORKER_PID"
    return 0
}

# Function to stop the worker
stop_worker() {
    if [ ! -z "$WORKER_PID" ] && kill -0 $WORKER_PID 2>/dev/null; then
        echo "🛑 Stopping benchmark worker..."
        kill $WORKER_PID
        wait $WORKER_PID 2>/dev/null || true
        echo "✅ Worker stopped"
    fi
}

# Main execution
main() {
    local failed_tests=0
    local total_tests=0
    
    # Trap to ensure cleanup
    trap stop_worker EXIT INT TERM
    
    # Wait for runtime
    if ! wait_for_runtime; then
        echo "❌ Cannot proceed without runtime"
        exit 1
    fi
    
    # Start the benchmark worker
    if ! start_worker; then
        echo "❌ Cannot proceed without worker"
        exit 1
    fi
    
    echo ""
    echo "📊 Running benchmark suite..."
    echo "   Runtime: $RUNTIME_ENDPOINT"
    echo "   Results: $RESULTS_DIR"
    echo "   Log Level: $LOG_LEVEL"
    
    # Run performance benchmarks
    total_tests=$((total_tests + 1))
    if ! run_benchmark "Performance Tests" "benchmarks/performance_tests.py"; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Run scalability tests
    total_tests=$((total_tests + 1))
    if ! run_benchmark "Scalability Tests" "benchmarks/scalability_tests.py"; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Run integration tests (if they exist)
    if [ -f "benchmarks/integration_tests.py" ]; then
        total_tests=$((total_tests + 1))
        if ! run_benchmark "Integration Tests" "benchmarks/integration_tests.py"; then
            failed_tests=$((failed_tests + 1))
        fi
    fi
    
    # Generate summary report
    echo ""
    echo "📈 Generating benchmark summary..."
    python scripts/generate_report.py "$RESULTS_DIR" > "$RESULTS_DIR/benchmark_summary.txt" 2>/dev/null || echo "⚠️ Could not generate summary report"
    
    # Final results
    echo ""
    echo "🏁 Benchmark Suite Complete"
    echo "=========================="
    echo "   Total Tests: $total_tests"
    echo "   Passed: $((total_tests - failed_tests))"
    echo "   Failed: $failed_tests"
    echo "   Results Directory: $RESULTS_DIR"
    
    if [ $failed_tests -eq 0 ]; then
        echo "🎉 All benchmarks completed successfully!"
        return 0
    else
        echo "⚠️ Some benchmarks failed"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "performance")
        echo "🔥 Running performance tests only..."
        wait_for_runtime && start_worker && run_benchmark "Performance Tests" "benchmarks/performance_tests.py"
        ;;
    "scalability")
        echo "📈 Running scalability tests only..."
        wait_for_runtime && start_worker && run_benchmark "Scalability Tests" "benchmarks/scalability_tests.py"
        ;;
    "worker-only")
        echo "🤖 Starting worker only (for external testing)..."
        wait_for_runtime && start_worker
        echo "Worker is running. Press Ctrl+C to stop."
        sleep infinity
        ;;
    "all"|*)
        main
        ;;
esac