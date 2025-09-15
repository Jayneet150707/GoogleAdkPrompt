"""
Logging utilities for Paisalo Google AdK Chatbot
"""

import logging
import sys
from typing import Optional
from datetime import datetime


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup logger with consistent formatting
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


class ChatbotLogger:
    """Specialized logger for chatbot operations"""
    
    def __init__(self, name: str = "paisalo_chatbot"):
        self.logger = setup_logger(name)
    
    def log_conversation_start(self, session_id: str, user_message: str):
        """Log conversation start"""
        self.logger.info(
            f"Conversation started - Session: {session_id}, Message: {user_message}"
        )
    
    def log_step_transition(self, session_id: str, from_step: str, to_step: str):
        """Log conversation step transition"""
        self.logger.info(
            f"Step transition: {from_step} -> {to_step} - Session: {session_id}"
        )
    
    def log_validation_error(self, session_id: str, field: str, value: str, error: str):
        """Log validation error"""
        self.logger.warning(
            f"Validation error for {field}: {error} - Session: {session_id}, Value: {value}"
        )
    
    def log_loan_decision(self, session_id: str, decision: str, reason: Optional[str] = None):
        """Log loan eligibility decision"""
        message = f"Loan decision: {decision} - Session: {session_id}"
        if reason:
            message += f", Reason: {reason}"
        self.logger.info(message)
    
    def log_session_cleanup(self, session_id: str, reason: str):
        """Log session cleanup"""
        self.logger.info(f"Session cleanup: {reason} - Session: {session_id}")
    
    def log_error(self, session_id: str, error: Exception, context: Optional[dict] = None):
        """Log error with context"""
        message = f"Error occurred: {str(error)} - Session: {session_id}"
        if context:
            message += f", Context: {context}"
        self.logger.error(message, exc_info=True)
    
    def log_adk_request(self, request_id: str, session_id: str, intent: str):
        """Log Google AdK request"""
        self.logger.info(
            f"AdK request received: {intent} - Request: {request_id}, Session: {session_id}"
        )
    
    def log_adk_response(self, request_id: str, session_id: str, response_text: str):
        """Log Google AdK response"""
        self.logger.info(
            f"AdK response sent - Request: {request_id}, Session: {session_id}, Length: {len(response_text)}"
        )

