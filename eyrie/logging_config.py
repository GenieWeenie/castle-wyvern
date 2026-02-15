"""
Castle Wyvern Structured Logging Configuration
Provides JSON structured logging with rotation.
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extras'):
            log_data.update(record.extras)
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        formatted = f"{color}[{record.levelname}]{reset} {record.getMessage()}"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class CastleWyvernLogger:
    """Centralized logging configuration for Castle Wyvern."""
    
    def __init__(self, log_dir: Optional[str] = None, debug_mode: bool = False):
        """
        Initialize logging configuration.
        
        Args:
            log_dir: Directory for log files (default: ~/.castle_wyvern/logs)
            debug_mode: Enable debug level logging
        """
        self.log_dir = Path(log_dir or "~/.castle_wyvern/logs").expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.debug_mode = debug_mode
        
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Main application log
        self._setup_logger(
            'castle_wyvern',
            self.log_dir / 'castle_wyvern.log',
            level=logging.DEBUG if self.debug_mode else logging.INFO
        )
        
        # Error log (only ERROR and above)
        self._setup_logger(
            'castle_wyvern.errors',
            self.log_dir / 'errors.log',
            level=logging.ERROR,
            json_format=True
        )
        
        # Audit log (security events)
        self._setup_logger(
            'castle_wyvern.audit',
            self.log_dir / 'audit.log',
            level=logging.INFO,
            json_format=True
        )
        
        # API log
        self._setup_logger(
            'castle_wyvern.api',
            self.log_dir / 'api.log',
            level=logging.DEBUG if self.debug_mode else logging.INFO,
            json_format=True
        )
        
        # Console output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        
        # Add console handler to root logger
        root_logger = logging.getLogger('castle_wyvern')
        root_logger.addHandler(console_handler)
    
    def _setup_logger(self, name: str, log_file: Path, level: int = logging.INFO, 
                      json_format: bool = False):
        """Setup individual logger with rotation."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers
        logger.handlers = []
        
        # File handler with rotation (7 days = 7 backups, daily rotation)
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        handler.setLevel(level)
        
        # Formatter
        if json_format:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        
        logger.addHandler(handler)
        self.loggers[name] = logger
        
        return logger
    
    def get_logger(self, name: str = 'castle_wyvern') -> logging.Logger:
        """Get a logger by name."""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]
    
    def set_debug_mode(self, enabled: bool = True):
        """Enable or disable debug mode."""
        self.debug_mode = enabled
        level = logging.DEBUG if enabled else logging.INFO
        
        for logger in self.loggers.values():
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)
    
    def log_audit(self, event: str, user: str = None, details: Dict = None):
        """Log audit event."""
        audit_logger = self.get_logger('castle_wyvern.audit')
        audit_logger.info(event, extra={'extras': {
            'user': user,
            'event_type': 'audit',
            'details': details or {}
        }})
    
    def log_api_call(self, endpoint: str, method: str, status: int, duration: float):
        """Log API call."""
        api_logger = self.get_logger('castle_wyvern.api')
        api_logger.debug(f"API Call: {method} {endpoint}", extra={'extras': {
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'duration_ms': int(duration * 1000)
        }})


# Global logger instance
_logging_config: Optional[CastleWyvernLogger] = None


def setup_logging(log_dir: Optional[str] = None, debug_mode: bool = False) -> CastleWyvernLogger:
    """Setup global logging configuration."""
    global _logging_config
    _logging_config = CastleWyvernLogger(log_dir, debug_mode)
    return _logging_config


def get_logger(name: str = 'castle_wyvern') -> logging.Logger:
    """Get logger instance."""
    global _logging_config
    if _logging_config is None:
        _logging_config = CastleWyvernLogger()
    return _logging_config.get_logger(name)


def set_debug_mode(enabled: bool = True):
    """Toggle debug mode."""
    global _logging_config
    if _logging_config is None:
        _logging_config = CastleWyvernLogger(debug_mode=enabled)
    else:
        _logging_config.set_debug_mode(enabled)


def log_audit(event: str, user: str = None, details: Dict = None):
    """Log audit event."""
    global _logging_config
    if _logging_config is None:
        _logging_config = CastleWyvernLogger()
    _logging_config.log_audit(event, user, details)


def log_api_call(endpoint: str, method: str, status: int, duration: float):
    """Log API call."""
    global _logging_config
    if _logging_config is None:
        _logging_config = CastleWyvernLogger()
    _logging_config.log_api_call(endpoint, method, status, duration)
