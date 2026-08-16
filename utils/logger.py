"""
Logging System
Centralized logging for the entire application
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Main log file
    log_file = os.path.join(LOG_DIR, 'shop_management.log')
    error_log_file = os.path.join(LOG_DIR, 'errors.log')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Format for logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler - rotates at 5MB
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)


def log_error(error_msg, exc_info=True):
    """Log an error with full exception info"""
    logger = logging.getLogger('error')
    logger.error(error_msg, exc_info=exc_info)


def log_info(message):
    """Log an info message"""
    logger = logging.getLogger('info')
    logger.info(message)


def log_warning(message):
    """Log a warning message"""
    logger = logging.getLogger('warning')
    logger.warning(message)


def log_user_action(user, action, details=""):
    """Log user actions for audit trail"""
    logger = logging.getLogger('audit')
    logger.info(f"USER: {user} | ACTION: {action} | DETAILS: {details}")


# ===== DECORATORS =====

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"CALL: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"RETURN: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"ERROR in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper


