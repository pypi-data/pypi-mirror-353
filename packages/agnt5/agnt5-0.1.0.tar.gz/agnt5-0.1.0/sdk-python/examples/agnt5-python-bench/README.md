# AGNT5 Python Benchmark Application

A comprehensive benchmarking and testing application for the AGNT5 Python SDK, implementing a customer support system that demonstrates all platform capabilities.

## Overview

This application simulates a production customer support platform with multiple AI agents, durable workflows, and persistent state management. It serves as both a comprehensive test suite and performance benchmark for the AGNT5 platform.

## Architecture

### Components

- **Agents**: AI-powered customer service, technical support, and order management
- **Workflows**: Order processing, issue resolution, and reporting pipelines  
- **Objects**: Persistent customer sessions, order tracking, and knowledge base
- **Tools**: External API integrations for payments, shipping, and notifications
- **Benchmarks**: Performance and scalability testing suites

### Key Features

- Multi-agent coordination with handoffs
- Durable state persistence across failures
- Complex workflow orchestration
- External service integration
- Comprehensive error handling
- Performance monitoring and benchmarking

## Usage

### Start the Worker

```bash
cd examples/agnt5-python-bench
python main.py
```

### Run Benchmarks

```bash
python benchmarks/performance_tests.py
python benchmarks/scalability_tests.py
python benchmarks/durability_tests.py
```

### Test Individual Components

```bash
python -m pytest agents/test_customer_service.py
python -m pytest workflows/test_order_processing.py
python -m pytest objects/test_customer_session.py
```

## Testing Scenarios

1. **Concurrent Load**: 100+ simultaneous customer sessions
2. **High Throughput**: 1000+ orders per hour processing
3. **Failure Recovery**: Service interruptions and state recovery
4. **Cross-Component**: Multi-agent workflows with shared state
5. **Performance**: Latency and throughput measurements

## Configuration

Set environment variables for external services:

```bash
export AGNT5_SERVICE_NAME="agnt5-python-bench"
export AGNT5_RUNTIME_ENDPOINT="http://localhost:8080"
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

## Metrics

The application tracks:
- Function invocation latency
- State persistence performance
- Memory usage efficiency
- Cross-partition communication
- Error rates and recovery times