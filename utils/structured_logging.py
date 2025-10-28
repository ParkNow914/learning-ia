"""Structured logging configuration using structlog."""
import logging
import sys
from typing import Any, Dict
import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log entries."""
    event_dict["app"] = "knowledge-tracing-api"
    event_dict["version"] = "2.2.0"
    return event_dict


def configure_structured_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output logs in JSON format (recommended for production)
    
    Example:
        >>> configure_structured_logging(log_level="INFO", json_logs=True)
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    
    shared_processors: list[Processor] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_app_context,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if json_logs:
        # Production: JSON logs
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Pretty console logs with colors
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured structlog logger
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)


# Convenience function for logging with context
def log_with_context(logger: structlog.BoundLogger, level: str, message: str, **kwargs: Any) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: Structlog logger instance
        level: Log level (info, warning, error, etc.)
        message: Log message
        **kwargs: Additional context to include in log
    
    Example:
        >>> logger = get_logger(__name__)
        >>> log_with_context(logger, "info", "prediction_made",
        ...                  student_id=123, prediction=0.85, model_version="2.0")
    """
    log_method = getattr(logger, level.lower())
    log_method(message, **kwargs)
