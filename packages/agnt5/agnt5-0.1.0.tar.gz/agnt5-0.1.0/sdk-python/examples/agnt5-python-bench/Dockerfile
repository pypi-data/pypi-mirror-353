# Multi-stage Dockerfile for AGNT5 Python Benchmark Application
# Use our pre-built base image with all heavy dependencies
FROM arunreddy/agnt5-python-base:latest

# All the heavy lifting (system deps, Rust, UV) is already done in the base image
# Set environment variables (inherited from base but explicit for clarity)
ENV PATH="/home/agnt5/.cargo/bin:${PATH}"
ENV CARGO_HOME="/home/agnt5/.cargo"
ENV RUSTUP_HOME="/home/agnt5/.rustup"
ENV UV_CACHE_DIR="/home/agnt5/.cache/uv"
ENV CARGO_TARGET_DIR="/app/sdk-python/target"

# Stay as root for file operations
USER root

# Copy SDK components and protos (required for Rust dependency and build)
COPY sdk/sdk-python/pyproject.toml sdk/sdk-python/uv.lock /app/sdk-python/
COPY sdk/sdk-python /app/sdk-python
COPY sdk/sdk-core /app/sdk-core
COPY protos /app/protos

# Set proper ownership
RUN chown -R agnt5:agnt5 /app

# Switch to agnt5 user for building
USER agnt5

# Install Python dependencies and build the extension
WORKDIR /app/sdk-python

# Ensure clean build environment for Rust extension
RUN rm -rf target/ src/agnt5/_core*.so .venv/lib/python*/site-packages/agnt5/_core*.so || true

# Install dependencies first (will use UV cache)
RUN uv sync --frozen

# Force clean build of Rust extension for correct target architecture
ENV CARGO_TARGET_DIR="/app/sdk-python/target"
RUN uv run maturin develop --release --strip \
    --target $(uname -m)-unknown-linux-gnu

# Verify the extension was built correctly for Linux
RUN ls -la src/agnt5/
RUN file src/agnt5/_core*.so
RUN ldd src/agnt5/_core*.so || echo "Static binary or missing libs"

# Test that we can import the extension
RUN uv run python -c "import sys; sys.path.insert(0, 'src'); import agnt5._core; print('Rust extension loaded successfully')"

# Copy benchmark application (as root first, then fix ownership)
USER root
COPY sdk/sdk-python/examples/agnt5-python-bench /app/benchmark
RUN chown -R agnt5:agnt5 /app/benchmark

# Switch back to agnt5 user
USER agnt5

# Set working directory to the benchmark app
WORKDIR /app/benchmark

# Environment configuration
ENV PYTHONPATH="/app/sdk-python/src:$PYTHONPATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AGNT5_SERVICE_NAME="agnt5-python-bench"

ENV AGNT5_SERVICE_VERSION="1.0.0"
ENV AGNT5_RUNTIME_ENDPOINT="http://agnt5-runtime:8080"
ENV AGNT5_LOG_LEVEL="INFO"
ENV PATH="/app/sdk-python/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "main.py"]