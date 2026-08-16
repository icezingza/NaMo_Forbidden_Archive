"""
Centralized logging configuration.
"""
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Setup comprehensive logging to console + file."""
    
    # Create logs directory
    log_dir = os.getenv("LOG_DIR", "./logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler (Rotating)
    log_file = os.path.join(log_dir, f"acc_bot_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Initialize on import
logger = setup_logging(
    level=logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO
)
