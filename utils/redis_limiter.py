"""Redis-backed rate limiting for production use."""
import os
import time
from typing import Optional
from datetime import datetime, timedelta

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RateLimiter:
    """
    Redis-backed rate limiter with fallback to in-memory storage.
    
    Supports:
    - Fixed window rate limiting
    - Sliding window rate limiting
    - Per-user and per-IP limits
    - Persistent storage with Redis
    - In-memory fallback when Redis unavailable
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_limit: int = 60,
        window_seconds: int = 60,
        use_sliding_window: bool = True
    ):
        """
        Initialize rate limiter.
        
        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
            default_limit: Default number of requests allowed per window
            window_seconds: Time window in seconds
            use_sliding_window: Use sliding window algorithm (more accurate)
        """
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.use_sliding_window = use_sliding_window
        
        # Try to connect to Redis
        self.redis_client: Optional[Redis] = None
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                self.storage_type = "redis"
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory fallback.")
                self.storage_type = "memory"
        else:
            self.storage_type = "memory"
        
        # In-memory fallback storage
        self.memory_store: dict[str, list[float]] = {}
    
    def is_allowed(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (e.g., user_id, IP address)
            limit: Custom limit for this check (overrides default)
            window: Custom window for this check (overrides default)
        
        Returns:
            Tuple of (allowed: bool, info: dict)
            info contains: remaining, reset_at, limit, used
        
        Example:
            >>> limiter = RateLimiter(default_limit=100)
            >>> allowed, info = limiter.is_allowed("user_123")
            >>> if not allowed:
            ...     print(f"Rate limit exceeded. Retry after {info['reset_at']}")
        """
        limit = limit or self.default_limit
        window = window or self.window_seconds
        
        if self.storage_type == "redis" and self.redis_client:
            return self._check_redis(key, limit, window)
        else:
            return self._check_memory(key, limit, window)
    
    def _check_redis(self, key: str, limit: int, window: int) -> tuple[bool, dict]:
        """Check rate limit using Redis."""
        now = time.time()
        redis_key = f"ratelimit:{key}"
        
        if self.use_sliding_window:
            # Sliding window: remove old entries and count current
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(redis_key, 0, now - window)
            pipe.zadd(redis_key, {str(now): now})
            pipe.zcard(redis_key)
            pipe.expire(redis_key, window)
            results = pipe.execute()
            
            count = results[2]
        else:
            # Fixed window: simple counter with expiry
            count = self.redis_client.incr(redis_key)
            if count == 1:
                self.redis_client.expire(redis_key, window)
            ttl = self.redis_client.ttl(redis_key)
            if ttl < 0:
                ttl = window
        
        allowed = count <= limit
        remaining = max(0, limit - count)
        reset_at = datetime.now() + timedelta(seconds=window)
        
        return allowed, {
            "allowed": allowed,
            "limit": limit,
            "used": count,
            "remaining": remaining,
            "reset_at": reset_at.isoformat(),
            "storage": "redis"
        }
    
    def _check_memory(self, key: str, limit: int, window: int) -> tuple[bool, dict]:
        """Check rate limit using in-memory storage (fallback)."""
        now = time.time()
        
        # Initialize key if not exists
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Remove expired timestamps
        cutoff = now - window
        self.memory_store[key] = [ts for ts in self.memory_store[key] if ts > cutoff]
        
        # Add current request
        self.memory_store[key].append(now)
        
        count = len(self.memory_store[key])
        allowed = count <= limit
        remaining = max(0, limit - count)
        reset_at = datetime.now() + timedelta(seconds=window)
        
        return allowed, {
            "allowed": allowed,
            "limit": limit,
            "used": count,
            "remaining": remaining,
            "reset_at": reset_at.isoformat(),
            "storage": "memory"
        }
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        if self.storage_type == "redis" and self.redis_client:
            self.redis_client.delete(f"ratelimit:{key}")
        else:
            self.memory_store.pop(key, None)
    
    def get_stats(self, key: str) -> dict:
        """Get current stats for a key."""
        _, info = self.is_allowed(key, limit=self.default_limit)
        return info


# Global instance (configured from environment)
_global_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _global_limiter
    
    if _global_limiter is None:
        redis_url = os.getenv("REDIS_URL")
        limit = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
        
        _global_limiter = RateLimiter(
            redis_url=redis_url,
            default_limit=limit,
            window_seconds=60,
            use_sliding_window=True
        )
    
    return _global_limiter
