import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class LoggerSetup:
    """Configure application-wide logging"""
    
    _configured = False
    
    @classmethod
    def setup(cls, log_dir: str = "logs") -> logging.Logger:
        """
        Setup centralized logging for the application.
        
        Args:
            log_dir: Directory to store log files
        
        Returns:
            Configured logger instance
        """
        if cls._configured:
            return logging.getLogger("codeerax_heart")
        
        # Create logs directory
        Path(log_dir).mkdir(exist_ok=True)
        
        # Create logger
        logger = logging.getLogger("codeerax_heart")
        logger.setLevel(logging.DEBUG)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler - all logs
        log_file = os.path.join(log_dir, f"heart_api_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # File handler - errors only
        error_log_file = os.path.join(log_dir, f"heart_api_errors_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5242880,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        cls._configured = True
        return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(f"codeerax_heart.{name}")
