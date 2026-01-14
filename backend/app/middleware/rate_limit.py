"""Rate limiting configuration for API endpoints."""
from slowapi import Limiter
from slowapi.util import get_remote_address


# Initialize rate limiter with in-memory storage
limiter = Limiter(key_func=get_remote_address)


# Rate limit configurations
RATE_LIMIT_AUTH = "5/minute"  # Strict limit for authentication (prevent brute force)
RATE_LIMIT_ADMIN = "30/minute"  # Moderate limit for admin operations
RATE_LIMIT_CHAT = "60/minute"  # Lenient limit for chat (allow conversation flow)
RATE_LIMIT_DEFAULT = "100/minute"  # Default limit for other endpoints
