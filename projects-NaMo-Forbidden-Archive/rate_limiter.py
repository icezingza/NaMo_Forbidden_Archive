"""
Rate limiting per user for Telegram bot.
"""

import time
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter. Use Redis for distributed systems."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: dict[str, list] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limit."""
        now = time.time()
        user_id = str(user_id)

        # Remove old timestamps outside window
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if now - ts < self.window_seconds
        ]

        # Check if under limit
        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(now)
            return True

        return False

    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        user_id = str(user_id)

        # Remove old timestamps
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if now - ts < self.window_seconds
        ]

        return max(0, self.max_requests - len(self.user_requests[user_id]))


# Global rate limiter
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
