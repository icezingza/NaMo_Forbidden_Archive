# Production Deployment Guide

## Quick Start

1. **Authenticate with Docker Hub:**
   ```bash
   docker login
   ```

2. **Build and push multi-platform image:**
   ```bash
   chmod +x build-and-push.sh
   ./build-and-push.sh
   ```

3. **Deploy in production:**
   ```bash
   docker compose -f docker-compose.production.yml up -d
   ```

## What's Configured

### Multi-Platform Builds
- **Platforms**: `linux/amd64` (Intel/AMD) and `linux/arm64` (Apple Silicon, ARM servers)
- **Build Cloud**: Leverages Docker Build Cloud for native ARM builds on amd64 hosts
- **Caching**: Registry-based cache reduces rebuild time by ~70%

### Production Compose (`docker-compose.production.yml`)
- **Resource Limits**: CPU (2 cores max, 0.5 reserved), Memory (2GB max, 512MB reserved)
- **Restart Policy**: Always restart on failure
- **Health Checks**: Automated monitoring every 30s
- **Logging**: JSON driver with 10MB rotation (max 3 files)
- **Security**: Read-only root filesystem, `no-new-privileges`, minimal temp mount

### GitHub Actions CI/CD
- Triggers on pushes to `main` or `production` branches
- Multi-platform build (QEMU + Buildx)
- Automatic push to Docker Hub
- Dual tags: `latest` + commit SHA
- Registry caching for fast rebuilds

## GitHub Secrets Setup

Add to your GitHub repo (Settings → Secrets and variables):
```
DOCKER_USERNAME = icezingza
DOCKER_PASSWORD = <your_docker_password_or_token>
```

## Manual Commands

**Build locally (single platform):**
```bash
docker buildx build -t icezingza/namo:latest .
```

**Build multi-platform (requires Build Cloud or QEMU):**
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t icezingza/namo:latest --push .
```

**Pull and run:**
```bash
docker run -p 8000:8000 icezingza/namo:latest
```

## Health Check

Container reports healthy after 10s startup window, then verifies every 30s:
```bash
docker compose logs namo  # Check logs
docker compose ps         # View health status
```

## Rollback

```bash
docker compose -f docker-compose.production.yml down
docker rmi icezingza/namo:previous-tag
docker pull icezingza/namo:previous-tag
docker compose -f docker-compose.production.yml up -d
```
