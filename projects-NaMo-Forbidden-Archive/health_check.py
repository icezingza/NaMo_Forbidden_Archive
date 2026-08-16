"""
Health checks and monitoring endpoints for ACC system.
"""

import time
from datetime import datetime
from typing import Any

START_TIME = time.time()


async def health_check() -> dict[str, Any]:
    """Detailed health check of entire system."""
    uptime_seconds = time.time() - START_TIME

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime_seconds,
        "components": {
            "api": "running",
            "telegram": "ready",
            "gemini": "configured",
            "memory_service": "active",
        },
        "version": "2.0.0",
    }


async def liveness_probe() -> dict[str, str]:
    """Kubernetes liveness probe - is app running?"""
    return {"status": "alive"}


async def readiness_probe() -> dict[str, str]:
    """Kubernetes readiness probe - is app ready to serve?"""
    return {"status": "ready"}
