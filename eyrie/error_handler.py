"""
Castle Wyvern Error Handling Module
Provides robust error handling, logging, and retry logic.
"""

import logging
import time
from functools import wraps
from typing import Optional, Callable, Any
from enum import Enum

# Use root logging config; CLI/app entrypoints call setup_logging() so we avoid
# import-time side effects (creating logs/, basicConfig) when used as a library.
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for Castle Wyvern."""
    LOW = "low"           # Minor issue, can continue
    MEDIUM = "medium"     # Warning, should investigate
    HIGH = "high"         # Significant problem, needs attention
    CRITICAL = "critical" # System failure, immediate action required


class CastleWyvernError(Exception):
    """Base exception for Castle Wyvern."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 details: Optional[dict] = None):
        super().__init__(message)
        self.severity = severity
        self.details = details or {}
        self.timestamp = time.time()
        
        # Log the error
        log_func = {
            ErrorSeverity.LOW: logger.info,
            ErrorSeverity.MEDIUM: logger.warning,
            ErrorSeverity.HIGH: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(severity, logger.error)
        
        log_func(f"[{severity.value.upper()}] {message}", extra=self.details)


class PhoenixGateError(CastleWyvernError):
    """Errors related to the Phoenix Gate (AI API calls)."""
    pass


class GrimoorumError(CastleWyvernError):
    """Errors related to the Grimoorum (memory system)."""
    pass


class ClanMemberError(CastleWyvernError):
    """Errors related to clan member operations."""
    pass


def retry_on_error(max_retries: int = 3, delay: float = 1.0, 
                   exceptions: tuple = (Exception,),
                   backoff_multiplier: float = 2.0):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        exceptions: Tuple of exceptions to catch and retry
        backoff_multiplier: Multiplier for exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


def validate_input(validator: Callable[[Any], bool], error_message: str):
    """
    Decorator to validate function inputs.
    
    Args:
        validator: Function that returns True if input is valid
        error_message: Error message to raise if validation fails
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Validate first positional arg (after self if present)
            target = args[1] if len(args) > 1 and hasattr(args[0], '__class__') else args[0] if args else None
            
            if target is not None and not validator(target):
                raise CastleWyvernError(
                    error_message,
                    severity=ErrorSeverity.MEDIUM,
                    details={'function': func.__name__, 'input': target}
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.
    
    States:
        CLOSED: Normal operation, requests pass through
        OPEN: Failure threshold reached, requests blocked
        HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise CastleWyvernError(
                    "Circuit breaker is OPEN - service temporarily unavailable",
                    severity=ErrorSeverity.HIGH,
                    details={'state': self.state, 'retry_after': self.recovery_timeout}
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Reset circuit breaker on successful call."""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker CLOSED - service recovered")
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
    
    def _on_failure(self):
        """Track failure and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.critical(
                f"Circuit breaker OPENED after {self.failure_count} failures"
            )


# Global circuit breakers for external services
zai_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
openai_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)