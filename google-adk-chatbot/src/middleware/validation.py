"""
Request validation middleware for Google AdK integration
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_adk_request(request_data: Dict[str, Any]) -> Optional[str]:
    """
    Validate Google AdK webhook request
    
    Args:
        request_data: Request payload from Google AdK
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not request_data:
        return "Request body is empty"
    
    # Check for required fields in AdK request
    required_fields = ['queryResult']
    
    for field in required_fields:
        if field not in request_data:
            return f"Missing required field: {field}"
    
    query_result = request_data.get('queryResult', {})
    
    # Validate queryResult structure
    if not isinstance(query_result, dict):
        return "queryResult must be an object"
    
    # Check for queryText (user's message)
    if 'queryText' not in query_result:
        return "Missing queryText in queryResult"
    
    query_text = query_result.get('queryText', '')
    if not isinstance(query_text, str):
        return "queryText must be a string"
    
    # Optional: Validate session ID format
    session_id = request_data.get('session', '')
    if session_id and not isinstance(session_id, str):
        return "session must be a string"
    
    # Optional: Validate intent structure
    intent = query_result.get('intent', {})
    if intent and not isinstance(intent, dict):
        return "intent must be an object"
    
    # Optional: Validate parameters
    parameters = query_result.get('parameters', {})
    if parameters and not isinstance(parameters, dict):
        return "parameters must be an object"
    
    logger.debug(f"AdK request validation passed for session: {session_id}")
    return None


def validate_test_request(request_data: Dict[str, Any]) -> Optional[str]:
    """
    Validate test endpoint request
    
    Args:
        request_data: Request payload for test endpoint
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not request_data:
        return "Request body is empty"
    
    # Check for message field
    if 'message' not in request_data:
        return "Missing required field: message"
    
    message = request_data.get('message', '')
    if not isinstance(message, str) or not message.strip():
        return "message must be a non-empty string"
    
    # Optional: Validate sessionId
    session_id = request_data.get('sessionId', '')
    if session_id and not isinstance(session_id, str):
        return "sessionId must be a string"
    
    return None


def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        user_input: Raw user input
        
    Returns:
        Sanitized input
    """
    if not isinstance(user_input, str):
        return ""
    
    # Remove potentially dangerous characters
    sanitized = user_input.strip()
    
    # Remove HTML tags (basic sanitization)
    import re
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Remove script tags and javascript
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    # Limit length to prevent DoS
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"User input truncated to {max_length} characters")
    
    return sanitized


def extract_session_id(request_data: Dict[str, Any]) -> str:
    """
    Extract session ID from AdK request
    
    Args:
        request_data: AdK request payload
        
    Returns:
        Session ID string
    """
    # Try different possible locations for session ID
    session_id = request_data.get('session', '')
    
    if not session_id:
        # Try alternative locations
        session_id = request_data.get('sessionId', '')
    
    if not session_id:
        # Extract from session path if present
        session_path = request_data.get('session', '')
        if session_path and '/' in session_path:
            # Format: projects/PROJECT_ID/agent/sessions/SESSION_ID
            parts = session_path.split('/')
            if len(parts) >= 4 and parts[-2] == 'sessions':
                session_id = parts[-1]
    
    return session_id or 'unknown'


def extract_intent_name(request_data: Dict[str, Any]) -> str:
    """
    Extract intent name from AdK request
    
    Args:
        request_data: AdK request payload
        
    Returns:
        Intent name string
    """
    query_result = request_data.get('queryResult', {})
    intent = query_result.get('intent', {})
    
    intent_name = intent.get('displayName', '')
    if not intent_name:
        intent_name = intent.get('name', '')
    
    return intent_name or 'unknown'


def extract_user_message(request_data: Dict[str, Any]) -> str:
    """
    Extract user message from AdK request
    
    Args:
        request_data: AdK request payload
        
    Returns:
        User message string
    """
    query_result = request_data.get('queryResult', {})
    query_text = query_result.get('queryText', '')
    
    return sanitize_user_input(query_text)

