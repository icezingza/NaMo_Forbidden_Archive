"""
Cache with TTL and automatic expiration.
"""

import time
import threading
import logging
from typing import Any, Optional, Callable
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with TTL."""

    value: Any
    timestamp: float
    ttl: int  # seconds


class TTLCache:
    """
    Thread-safe cache with TTL support.
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize TTL cache.

        Args:
            default_ttl: Default time-to-live in seconds (1 hour)
            max_size: Maximum cache entries
        """
        self.cache: dict = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.lock = threading.RLock()
        self.logger = logging.getLogger(f"{__name__}.TTLCache")

        # Start cleanup thread
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""

        def cleanup_loop():
            while True:
                try:
                    time.sleep(300)  # Every 5 minutes
                    expired_count = self.cleanup_expired()
                    if expired_count > 0:
                        self.logger.debug(f"Cleaned up {expired_count} expired cache entries")
                except Exception as e:
                    self.logger.error(f"Cache cleanup error: {str(e)}")

        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set cache value with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self.lock:
            # Check size
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
                del self.cache[oldest_key]
                self.logger.debug(f"Evicted oldest cache entry: {oldest_key}")

            ttl_value = ttl or self.default_ttl

            self.cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl_value)

            self.logger.debug(f"Cached key: {key} (TTL: {ttl_value}s)")

    def get(self, key: str) -> Optional[Any]:
        """
        Get cache value if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]

            # Check if expired
            age = time.time() - entry.timestamp
            if age > entry.ttl:
                del self.cache[key]
                self.logger.debug(f"Expired cache entry: {key}")
                return None

            self.logger.debug(f"Cache hit: {key}")
            return entry.value

    def delete(self, key: str) -> bool:
        """
        Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.logger.debug(f"Deleted cache entry: {key}")
                return True
            return False

    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.logger.info(f"Cleared {count} cache entries")

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, entry in self.cache.items()
                if (current_time - entry.timestamp) > entry.ttl
            ]

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self.lock:
            expired_count = 0
            current_time = time.time()

            for entry in self.cache.values():
                if (current_time - entry.timestamp) > entry.ttl:
                    expired_count += 1

            return {
                "total_entries": len(self.cache),
                "expired_entries": expired_count,
                "active_entries": len(self.cache) - expired_count,
                "max_size": self.max_size,
                "utilization_percent": (len(self.cache) / self.max_size) * 100,
            }


class cache_with_ttl:
    """
    Decorator for function result caching with TTL.
    """

    def __init__(self, ttl: int = 3600):
        """
        Initialize cache decorator.

        Args:
            ttl: Time-to-live in seconds
        """
        self.ttl = ttl
        self.cache = TTLCache(default_ttl=ttl)
        self.logger = logging.getLogger(f"{__name__}.cache_with_ttl")

    def __call__(self, func: Callable) -> Callable:
        """
        Decorate function with caching.

        Args:
            func: Function to decorate

        Returns:
            Wrapped function
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = self.cache.get(key)
            if cached_result is not None:
                self.logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Call function and cache result
            result = func(*args, **kwargs)
            self.cache.set(key, result, self.ttl)

            return result

        wrapper.cache = self.cache
        return wrapper
