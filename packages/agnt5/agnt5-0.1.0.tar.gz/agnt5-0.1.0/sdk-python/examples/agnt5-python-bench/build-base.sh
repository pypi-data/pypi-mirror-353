#!/bin/bash
# Build the base image with all heavy dependencies
# This should be run once or when base dependencies change

set -e

echo "🔨 Building AGNT5 Python Base Image..."
echo "This may take a while but only needs to be done once."

docker build \
  -f Dockerfile.base \
  -t agnt5-python-base:latest \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  .

echo "✅ Base image built successfully!"
echo "📦 Image: agnt5-python-base:latest"

# Show image size
echo "📊 Image size:"
docker images agnt5-python-base:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "🚀 You can now use 'docker compose build' for much faster builds!"
echo "💡 Only rebuild this base image when system dependencies change."