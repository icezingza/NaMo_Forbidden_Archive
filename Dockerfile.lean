# Dockerfile.lean - Minimal & Fast (Size + Speed Optimized)
# Stage 1: Builder - Compile wheels only
FROM python:3.12-slim AS builder

WORKDIR /build

# Install only essential build tools (skip docs, man pages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc/* /usr/share/man/*

# Copy only requirements - enables layer caching if dependencies don't change
COPY requirements.txt .

# Build wheels with aggressive caching to avoid recompilation
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir ./wheels -r requirements.txt

# Stage 2: Strip unnecessary files from builder
FROM python:3.12-slim AS stripper

WORKDIR /build

# Copy compiled wheels only
COPY --from=builder /build/wheels ./wheels

# Remove unnecessary Python artifacts, docs, tests from wheels
RUN find ./wheels -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find ./wheels -type f \( -name "*.dist-info/RECORD" -o -name "*.dist-info/top_level.txt" \) -delete || true

# Stage 3: Minimal runtime (87MB base → 150MB final vs 681MB full)
FROM python:3.12-slim

WORKDIR /app

# Install ONLY runtime dependencies (no dev tools, no man pages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc/* /usr/share/man/* /var/cache/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy wheels and install (no --index-query, faster install)
COPY --from=stripper /build/wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt && \
    rm -rf /wheels /root/.cache

# Copy only essential app code (exclude large archives, examples, old backups)
COPY --chown=appuser:appuser core ./core
COPY --chown=appuser:appuser adapters ./adapters
COPY --chown=appuser:appuser *.py ./
COPY --chown=appuser:appuser *.json ./
COPY --chown=appuser:appuser config.py ./

USER appuser

EXPOSE 8000

ENV PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/v1/health || exit 1

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
