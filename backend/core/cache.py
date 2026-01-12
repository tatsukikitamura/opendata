"""
Generic in-memory cache utilities with TTL support.

Consolidates caching patterns used across services (e.g., risk.py).
"""
import time
from typing import TypeVar, Generic, Callable, Optional
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """A single cache entry with expiration time."""
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    """
    Simple in-memory cache with time-to-live (TTL) support.
    
    Usage:
        cache = TTLCache[dict](ttl_seconds=300)
        
        # Get or compute value
        result = cache.get_or_set("key", lambda: expensive_computation())
        
        # Manual operations
        cache.set("key", value)
        value = cache.get("key")
        cache.clear()
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self._ttl = ttl_seconds
        self._cache: dict[str, CacheEntry[T]] = {}
    
    def get(self, key: str) -> Optional[T]:
        """Get value from cache if exists and not expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None
        return entry.value
    
    def set(self, key: str, value: T) -> None:
        """Set value in cache with TTL."""
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=time.time() + self._ttl
        )
    
    def get_or_set(self, key: str, factory: Callable[[], T]) -> T:
        """Get from cache or compute using factory function."""
        cached = self.get(key)
        if cached is not None:
            return cached
        value = factory()
        self.set(key, value)
        return value
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
    
    def invalidate(self, key: str) -> bool:
        """Remove a specific key from cache. Returns True if key existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False


# ==============================================================================
# Pre-configured cache instances for common use cases
# ==============================================================================

# Cache for current delays (5 minutes TTL)
delays_cache: TTLCache[dict] = TTLCache(ttl_seconds=300)

# Cache for railway statistics (5 minutes TTL) 
railway_stats_cache: TTLCache[dict] = TTLCache(ttl_seconds=300)
