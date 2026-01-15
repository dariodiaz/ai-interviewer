"""LLM response caching utility."""
import hashlib
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheEntry:
    """Cache entry with TTL."""

    def __init__(self, value: str, ttl: int):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
        self.created_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now() > self.expires_at


class LLMCache:
    """In-memory cache for LLM responses with TTL support."""

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            max_size: Maximum number of entries (default: 1000)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def generate_key(
        self,
        prompt: str,
        model: str,
        temperature: float,
        agent_name: str = "",
    ) -> str:
        """
        Generate cache key from prompt and parameters.

        Args:
            prompt: The prompt text
            model: Model name
            temperature: Temperature setting
            agent_name: Optional agent name

        Returns:
            Hash-based cache key
        """
        # Create deterministic key from all parameters
        key_parts = [
            prompt,
            model,
            f"{temperature:.2f}",
            agent_name,
        ]
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry.value

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        # Evict oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()

        ttl = ttl or self.default_ttl
        self._cache[key] = CacheEntry(value, ttl)

    def _evict_oldest(self) -> None:
        """Evict oldest cache entry."""
        if not self._cache:
            return

        # Find oldest entry
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at,
        )
        del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "default_ttl": self.default_ttl,
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items() if entry.is_expired()
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


# Global cache instance
_cache_instance: Optional[LLMCache] = None


def get_cache() -> LLMCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        from app.config import settings

        _cache_instance = LLMCache(
            default_ttl=getattr(settings, "cache_ttl_seconds", 3600),
            max_size=getattr(settings, "cache_max_size", 1000),
        )
    return _cache_instance
