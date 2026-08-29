# Dockerfile for NaMo Forbidden Archive (Production-Optimized Multi-Stage Build)
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install minimal build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt ./

# Build wheels in isolation with strict error handling
RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime image (minimal)
FROM python:3.12-slim

WORKDIR /app

# Install only runtime deps (curl for healthchecks, libpq for database)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy wheels from builder and install
COPY --from=builder /build/wheels /wheels
COPY requirements.txt ./

RUN pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application code (use .dockerignore to exclude unnecessary files)
COPY --chown=appuser:appuser core ./core
COPY --chown=appuser:appuser adapters ./adapters
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port (single port as PRIMARY)
EXPOSE 8000

# Environment defaults
ENV PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/v1/health || exit 1

# Default: start FastAPI server with explicit args (no shell for faster startup)
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
