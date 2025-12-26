"""
Enhanced authentication and rate limiting.
"""

import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
import jwt
import logging

logger = logging.getLogger(__name__)

# ============ Configuration ============

API_KEY = os.getenv("API_KEY", "default-key-change-in-production")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============ Rate Limiting ============

limiter = Limiter(key_func=get_remote_address)

# Define rate limit strategies
RATE_LIMITS = {
    "chat": "100/minute",  # 100 requests per minute
    "recall": "50/minute",  # 50 requests per minute
    "store": "100/minute",  # 100 requests per minute
    "session_stats": "200/minute",  # 200 requests per minute
    "debug": "10/minute",  # 10 requests per minute
}


# ============ JWT Token Management ============


class TokenManager:
    """Manage JWT tokens for API authentication."""

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

        logger.info(f"Token created for user: {data.get('sub')}")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token data

        Raises:
            HTTPException if token is invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")


# ============ API Key Authentication ============


class APIKeyAuth:
    """API Key based authentication."""

    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.valid_keys = set([api_key])  # Can extend with multiple keys
        self.logger = logging.getLogger(f"{__name__}.APIKeyAuth")

    async def verify_api_key(self, x_api_key: str = Header(...)) -> str:
        """
        Verify API key from header.

        Args:
            x_api_key: API key from X-API-Key header

        Returns:
            API key if valid

        Raises:
            HTTPException if invalid
        """
        if x_api_key not in self.valid_keys:
            self.logger.warning(f"Invalid API key attempt: {x_api_key[:5]}***")
            raise HTTPException(status_code=403, detail="Invalid API key")

        self.logger.info("API key verified successfully")
        return x_api_key

    def add_key(self, new_key: str):
        """Add new API key."""
        self.valid_keys.add(new_key)
        self.logger.info(f"Added new API key: {new_key[:5]}***")

    def revoke_key(self, key: str):
        """Revoke API key."""
        if key in self.valid_keys:
            self.valid_keys.remove(key)
            self.logger.info(f"Revoked API key: {key[:5]}***")


# ============ Bearer Token Authentication ============


class BearerTokenAuth:
    """Bearer token authentication using JWT."""

    security = HTTPBearer()

    async def verify_bearer_token(
        self, credentials: HTTPAuthCredentials = Depends(security)
    ) -> dict:
        """
        Verify bearer token.

        Args:
            credentials: Bearer token credentials

        Returns:
            Decoded token payload

        Raises:
            HTTPException if token invalid
        """
        token = credentials.credentials

        try:
            payload = TokenManager.verify_token(token)
            return payload

        except HTTPException:
            raise


# ============ Rate Limit Error Handler ============


class RateLimitExceptionHandler:
    """Handle rate limit exceeded errors."""

    @staticmethod
    def handle_rate_limit_error(request, exc: RateLimitExceeded):
        """Handle rate limit exceeded."""
        logger.warning(f"Rate limit exceeded for {request.client.host}: {exc.detail}")

        return HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": "60 seconds",
            },
        )


# ============ Setup Functions ============


def setup_security(app: FastAPI):
    """
    Setup security features on FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Add rate limiter
    app.state.limiter = limiter

    # Add exception handler for rate limits
    app.add_exception_handler(RateLimitExceeded, RateLimitExceptionHandler.handle_rate_limit_error)

    logger.info("Security features initialized")


def get_api_key_auth() -> APIKeyAuth:
    """Get API key auth instance."""
    return APIKeyAuth()


def get_bearer_auth() -> BearerTokenAuth:
    """Get bearer token auth instance."""
    return BearerTokenAuth()
