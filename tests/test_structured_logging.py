"""Tests for structured logging functionality."""
import logging
import pytest
from utils.structured_logging import (
    configure_structured_logging,
    get_logger,
    log_with_context
)


def test_configure_structured_logging_development():
    """Test structured logging configuration for development."""
    configure_structured_logging(log_level="DEBUG", json_logs=False)
    logger = get_logger("test")
    
    # Should not raise errors
    logger.info("test_message", user_id=123, action="login")
    logger.debug("debug_message", details="test")
    logger.warning("warning_message", code=404)


def test_configure_structured_logging_production():
    """Test structured logging configuration for production (JSON)."""
    configure_structured_logging(log_level="INFO", json_logs=True)
    logger = get_logger("test")
    
    # Should output JSON logs
    logger.info("production_log", environment="prod", version="2.2.0")


def test_get_logger():
    """Test logger instance creation."""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    assert logger1 is not None
    assert logger2 is not None


def test_log_with_context():
    """Test logging with additional context."""
    logger = get_logger(__name__)
    
    # Should not raise errors
    log_with_context(
        logger,
        "info",
        "user_action",
        user_id=456,
        action="prediction",
        model="dkt",
        score=0.85
    )
    
    log_with_context(
        logger,
        "error",
        "prediction_failed",
        user_id=789,
        error="Model not found"
    )


def test_logging_levels():
    """Test different logging levels."""
    configure_structured_logging(log_level="INFO", json_logs=False)
    logger = get_logger("test_levels")
    
    # All should work without errors
    logger.debug("debug", level="DEBUG")
    logger.info("info", level="INFO")
    logger.warning("warning", level="WARNING")
    logger.error("error", level="ERROR")
    logger.critical("critical", level="CRITICAL")


def test_context_preservation():
    """Test that context is preserved across log calls."""
    logger = get_logger("test_context")
    
    # Bind context to logger
    bound_logger = logger.bind(request_id="12345", user_id=999)
    
    # Context should be included in all subsequent logs
    bound_logger.info("first_action")
    bound_logger.info("second_action")
    bound_logger.info("third_action")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
