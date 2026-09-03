#!/bin/bash
# Multi-platform build and push to Docker Hub with Build Cloud

set -e

IMAGE_NAME="icezingza/namo"
TAG="latest"
REGISTRY="${IMAGE_NAME}:${TAG}"

echo "🚀 Building multi-platform image: ${REGISTRY}"
echo "Platforms: linux/amd64, linux/arm64"
echo ""

# Option 1: With Docker Build Cloud (recommended)
if docker buildx ls | grep -q "cloud"; then
    echo "✓ Docker Build Cloud detected. Using native builder."
    docker buildx build \
      --push \
      --platform linux/amd64,linux/arm64 \
      --tag "${REGISTRY}" \
      --cache-from=type=registry,ref="${REGISTRY}:buildcache" \
      --cache-to=type=registry,ref="${REGISTRY}:buildcache",mode=max \
      --progress=plain \
      .
else
    echo "⚠ Docker Build Cloud not available. Using local buildx."
    docker buildx build \
      --load \
      --tag "${REGISTRY}" \
      .
    echo ""
    echo "Pushing to Docker Hub..."
    docker push "${REGISTRY}"
fi

echo ""
echo "✅ Build complete! Image pushed: ${REGISTRY}"
echo ""
echo "Run in production:"
echo "  docker compose -f docker-compose.production.yml up -d"
