"""
Enhanced error handling and recovery system for the Telegram News Bot
"""
import logging
import traceback
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable
from functools import wraps
import telegram
from telegram.error import TelegramError, NetworkError, RetryAfter

logger = logging.getLogger(__name__)

class ErrorStats:
    """Track error statistics for monitoring"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}
        self.total_errors = 0
        self.start_time = datetime.now(timezone.utc)
    
    def record_error(self, error_type: str, error_message: str = ""):
        """Record an error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_errors[error_type] = datetime.now(timezone.utc)
        self.total_errors += 1
        
        logger.warning(f"Error recorded: {error_type} - {error_message}")
    
    def get_error_rate(self, error_type: str, time_window_minutes: int = 60) -> float:
        """Get error rate for a specific error type within time window"""
        if error_type not in self.last_errors:
            return 0.0
        
        last_error = self.last_errors[error_type]
        time_threshold = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        
        if last_error > time_threshold:
            return self.error_counts[error_type] / time_window_minutes
        return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        uptime = datetime.now(timezone.utc) - self.start_time
        
        return {
            'total_errors': self.total_errors,
            'error_types': len(self.error_counts),
            'uptime_hours': uptime.total_seconds() / 3600,
            'errors_per_hour': self.total_errors / max(uptime.total_seconds() / 3600, 1),
            'error_breakdown': dict(self.error_counts),
            'last_errors': {k: v.isoformat() for k, v in self.last_errors.items()}
        }

# Global error statistics
error_stats = ErrorStats()

class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor

def with_retry(config: RetryConfig = None, error_types: tuple = None):
    """Decorator for adding retry logic to functions"""
    if config is None:
        config = RetryConfig()
    
    if error_types is None:
        error_types = (NetworkError, RetryAfter, ConnectionError, TimeoutError)
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except error_types as e:
                    last_exception = e
                    error_type = type(e).__name__
                    error_stats.record_error(f"retry_{error_type}", str(e))
                    
                    if attempt < config.max_retries:
                        delay = config.base_delay * (config.backoff_factor ** attempt)
                        
                        # Special handling for Telegram RetryAfter error
                        if isinstance(e, RetryAfter):
                            delay = max(delay, e.retry_after)
                        
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {config.max_retries + 1} attempts failed for {func.__name__}")
                        raise last_exception
                        
                except Exception as e:
                    # Don't retry for non-recoverable errors
                    error_stats.record_error(f"non_recoverable_{type(e).__name__}", str(e))
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except error_types as e:
                    last_exception = e
                    error_type = type(e).__name__
                    error_stats.record_error(f"retry_{error_type}", str(e))
                    
                    if attempt < config.max_retries:
                        delay = config.base_delay * (config.backoff_factor ** attempt)
                        
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {config.max_retries + 1} attempts failed for {func.__name__}")
                        raise last_exception
                        
                except Exception as e:
                    error_stats.record_error(f"non_recoverable_{type(e).__name__}", str(e))
                    raise e
            
            raise last_exception
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class HealthMonitor:
    """Monitor bot health and detect issues"""
    
    def __init__(self):
        self.last_successful_scrape = None
        self.last_successful_post = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.health_check_interval = 300  # 5 minutes
    
    def record_successful_scrape(self):
        """Record successful scraping operation"""
        self.last_successful_scrape = datetime.now(timezone.utc)
        self.consecutive_failures = 0
    
    def record_successful_post(self):
        """Record successful Telegram post"""
        self.last_successful_post = datetime.now(timezone.utc)
    
    def record_failure(self):
        """Record a failure"""
        self.consecutive_failures += 1
    
    def is_healthy(self) -> tuple[bool, str]:
        """Check if bot is healthy"""
        now = datetime.now(timezone.utc)
        
        # Check if too many consecutive failures
        if self.consecutive_failures >= self.max_consecutive_failures:
            return False, f"Too many consecutive failures: {self.consecutive_failures}"
        
        # Check if scraping has been working recently
        if self.last_successful_scrape:
            time_since_scrape = now - self.last_successful_scrape
            if time_since_scrape.total_seconds() > 3600:  # 1 hour
                return False, f"No successful scrape in {time_since_scrape}"
        
        # Check error rates
        network_error_rate = error_stats.get_error_rate("NetworkError", 60)
        if network_error_rate > 10:  # More than 10 errors per minute
            return False, f"High network error rate: {network_error_rate}/min"
        
        return True, "Healthy"
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        is_healthy, reason = self.is_healthy()
        
        return {
            'is_healthy': is_healthy,
            'reason': reason,
            'last_successful_scrape': self.last_successful_scrape.isoformat() if self.last_successful_scrape else None,
            'last_successful_post': self.last_successful_post.isoformat() if self.last_successful_post else None,
            'consecutive_failures': self.consecutive_failures,
            'error_stats': error_stats.get_summary()
        }

# Global health monitor
health_monitor = HealthMonitor()

async def safe_telegram_operation(operation: Callable, operation_name: str, *args, **kwargs):
    """Safely execute Telegram operations with error handling"""
    try:
        result = await operation(*args, **kwargs)
        health_monitor.record_successful_post()
        return result
        
    except RetryAfter as e:
        error_stats.record_error("telegram_rate_limit", f"Retry after {e.retry_after}s")
        logger.warning(f"Rate limited by Telegram: {e.retry_after}s")
        await asyncio.sleep(e.retry_after)
        raise e
        
    except NetworkError as e:
        error_stats.record_error("telegram_network_error", str(e))
        logger.error(f"Telegram network error in {operation_name}: {e}")
        health_monitor.record_failure()
        raise e
        
    except TelegramError as e:
        error_stats.record_error("telegram_api_error", str(e))
        logger.error(f"Telegram API error in {operation_name}: {e}")
        
        # Some Telegram errors are not recoverable
        if "chat not found" in str(e).lower():
            logger.critical("Channel not found - bot may not be added to channel")
        elif "bot was blocked" in str(e).lower():
            logger.critical("Bot was blocked - check bot permissions")
        
        raise e
        
    except Exception as e:
        error_stats.record_error("unexpected_telegram_error", str(e))
        logger.error(f"Unexpected error in {operation_name}: {e}")
        logger.error(traceback.format_exc())
        health_monitor.record_failure()
        raise e

def setup_logging(log_level: str = "INFO", log_file: str = "logs/bot.log"):
    """Set up comprehensive logging configuration"""
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from external libraries
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logger.info("Logging configured successfully")

class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
                
            except Exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now(timezone.utc) - self.last_failure_time).total_seconds() > self.timeout
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("Circuit breaker opened due to failures")

# Export key components
__all__ = [
    'with_retry',
    'RetryConfig',
    'safe_telegram_operation',
    'setup_logging',
    'health_monitor',
    'error_stats',
    'CircuitBreaker'
] 