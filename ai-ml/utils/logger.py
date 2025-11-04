"""
Logging Configuration for AI/ML Module
Provides structured logging with file rotation and console output
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import Optional


class AIMLLogger:
    """Custom logger for AI/ML module with structured output"""
    
    def __init__(
        self,
        log_file: Optional[str] = None,
        log_level: str = "INFO",
        rotation: str = "10 MB",
        retention: str = "30 days"
    ):
        """
        Initialize logger with file and console handlers
        
        Args:
            log_file: Path to log file (default: logs/ai_ml_{date}.log)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            rotation: Log rotation size/time
            retention: How long to keep logs
        """
        # Remove default logger
        logger.remove()
        
        # Set log level
        self.log_level = log_level.upper()
        
        # Console handler with color
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.log_level,
            colorize=True,
        )
        
        # File handler with rotation
        if log_file is None:
            log_dir = Path(__file__).parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"ai_ml_{datetime.now():%Y%m%d}.log"
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=self.log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )
        
        self.logger = logger
        logger.info(f"Logger initialized - Level: {self.log_level}, File: {log_file}")
    
    def get_logger(self):
        """Return the configured logger instance"""
        return self.logger


# Global logger instance
def get_logger(name: Optional[str] = None):
    """
    Get a logger instance
    
    Args:
        name: Optional logger name for context
    
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize default logger
_default_logger = AIMLLogger()
default_logger = _default_logger.get_logger()


if __name__ == "__main__":
    # Test logging
    test_logger = get_logger("test")
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.success("This is a success message")
