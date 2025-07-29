"""
Logger handler untuk ArisDev Framework
"""

import logging
import os
from datetime import datetime

class Logger:
    """Logger handler untuk ArisDev Framework"""
    
    def __init__(self, name="arisdev", level=logging.INFO, log_file=None):
        """Inisialisasi logger
        
        Args:
            name (str): Logger name
            level (int): Logging level
            log_file (str): Log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler if log_file is specified
        if log_file:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Log debug message
        
        Args:
            message (str): Log message
        """
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message
        
        Args:
            message (str): Log message
        """
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message
        
        Args:
            message (str): Log message
        """
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message
        
        Args:
            message (str): Log message
        """
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message
        
        Args:
            message (str): Log message
        """
        self.logger.critical(message)
    
    def exception(self, message):
        """Log exception message
        
        Args:
            message (str): Log message
        """
        self.logger.exception(message)
    
    def log(self, level, message):
        """Log message with specified level
        
        Args:
            level (int): Logging level
            message (str): Log message
        """
        self.logger.log(level, message)
    
    def set_level(self, level):
        """Set logging level
        
        Args:
            level (int): Logging level
        """
        self.logger.setLevel(level)
    
    def get_level(self):
        """Get logging level"""
        return self.logger.level
    
    def add_handler(self, handler):
        """Add handler
        
        Args:
            handler: Logging handler
        """
        self.logger.addHandler(handler)
    
    def remove_handler(self, handler):
        """Remove handler
        
        Args:
            handler: Logging handler
        """
        self.logger.removeHandler(handler)
    
    def clear_handlers(self):
        """Clear all handlers"""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
    
    def get_handlers(self):
        """Get all handlers"""
        return self.logger.handlers

    def log_request(self, request):
        self.info(f"Request: {request.method} {request.path} - {request.remote_addr}")

    def log_error(self, request, error):
        self.error(f"Error in {request.method} {request.path}: {str(error)}")

    def log_response(self, request, response):
        self.info(f"Response: {request.method} {request.path} - {response.status_code}") 