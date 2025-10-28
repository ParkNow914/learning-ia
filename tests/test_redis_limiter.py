"""Tests for Redis-backed rate limiter."""
import pytest
import time
from utils.redis_limiter import RateLimiter, get_rate_limiter


def test_rate_limiter_memory_basic():
    """Test basic rate limiting with in-memory storage."""
    limiter = RateLimiter(redis_url=None, default_limit=5, window_seconds=2)
    
    # First 5 requests should be allowed
    for i in range(5):
        allowed, info = limiter.is_allowed("user_1")
        assert allowed is True
        assert info["used"] == i + 1
        assert info["remaining"] == 5 - (i + 1)
    
    # 6th request should be denied
    allowed, info = limiter.is_allowed("user_1")
    assert allowed is False
    assert info["used"] == 6
    assert info["remaining"] == 0


def test_rate_limiter_memory_window():
    """Test that rate limit resets after window expires."""
    limiter = RateLimiter(redis_url=None, default_limit=3, window_seconds=1)
    
    # Use up limit
    for i in range(3):
        allowed, info = limiter.is_allowed("user_2")
        assert allowed is True
    
    # Should be denied
    allowed, info = limiter.is_allowed("user_2")
    assert allowed is False
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should be allowed again
    allowed, info = limiter.is_allowed("user_2")
    assert allowed is True


def test_rate_limiter_multiple_keys():
    """Test that rate limiting is per-key."""
    limiter = RateLimiter(redis_url=None, default_limit=2, window_seconds=10)
    
    # User 1 uses limit
    allowed, _ = limiter.is_allowed("user_1")
    assert allowed is True
    allowed, _ = limiter.is_allowed("user_1")
    assert allowed is True
    allowed, _ = limiter.is_allowed("user_1")
    assert allowed is False
    
    # User 2 should still have full limit
    allowed, _ = limiter.is_allowed("user_2")
    assert allowed is True
    allowed, _ = limiter.is_allowed("user_2")
    assert allowed is True


def test_rate_limiter_custom_limit():
    """Test using custom limit per request."""
    limiter = RateLimiter(redis_url=None, default_limit=10, window_seconds=10)
    
    # Use custom limit of 2
    allowed, info = limiter.is_allowed("user_3", limit=2)
    assert allowed is True
    allowed, info = limiter.is_allowed("user_3", limit=2)
    assert allowed is True
    allowed, info = limiter.is_allowed("user_3", limit=2)
    assert allowed is False


def test_rate_limiter_reset():
    """Test resetting rate limit for a key."""
    limiter = RateLimiter(redis_url=None, default_limit=2, window_seconds=10)
    
    # Use up limit
    limiter.is_allowed("user_4")
    limiter.is_allowed("user_4")
    allowed, _ = limiter.is_allowed("user_4")
    assert allowed is False
    
    # Reset
    limiter.reset("user_4")
    
    # Should be allowed again
    allowed, _ = limiter.is_allowed("user_4")
    assert allowed is True


def test_rate_limiter_get_stats():
    """Test getting stats for a key."""
    limiter = RateLimiter(redis_url=None, default_limit=5, window_seconds=10)
    
    # Make some requests
    limiter.is_allowed("user_5")
    limiter.is_allowed("user_5")
    limiter.is_allowed("user_5")
    
    # Get stats
    stats = limiter.get_stats("user_5")
    assert stats["used"] == 4  # 3 previous + 1 from get_stats
    assert stats["remaining"] == 1
    assert stats["limit"] == 5


def test_rate_limiter_storage_type():
    """Test that storage type is correctly identified."""
    # Memory storage
    limiter_mem = RateLimiter(redis_url=None)
    assert limiter_mem.storage_type == "memory"
    
    allowed, info = limiter_mem.is_allowed("test")
    assert info["storage"] == "memory"


def test_get_global_rate_limiter():
    """Test getting global rate limiter instance."""
    limiter = get_rate_limiter()
    assert limiter is not None
    assert isinstance(limiter, RateLimiter)
    
    # Should return same instance
    limiter2 = get_rate_limiter()
    assert limiter is limiter2


def test_rate_limiter_sliding_window():
    """Test sliding window algorithm."""
    limiter = RateLimiter(
        redis_url=None,
        default_limit=3,
        window_seconds=2,
        use_sliding_window=True
    )
    
    # Make 3 requests
    for _ in range(3):
        allowed, _ = limiter.is_allowed("user_6")
        assert allowed is True
    
    # 4th should fail
    allowed, _ = limiter.is_allowed("user_6")
    assert allowed is False
    
    # Wait half window
    time.sleep(1)
    
    # Should still fail (sliding window)
    allowed, _ = limiter.is_allowed("user_6")
    assert allowed is False
    
    # Wait full window
    time.sleep(1.5)
    
    # Should succeed now
    allowed, _ = limiter.is_allowed("user_6")
    assert allowed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
