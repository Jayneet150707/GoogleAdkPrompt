#!/usr/bin/env python3
"""
Paisalo Google AdK Chatbot - Python Flask Application
Handles loan eligibility conversations with Google AdK integration
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from src.chatbot import PaisaloAdkChatbot
from src.utils.logger import setup_logger
from src.middleware.validation import validate_adk_request
from src.config import Config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Setup logging
logger = setup_logger(__name__)

# Initialize chatbot
chatbot = PaisaloAdkChatbot()

@app.before_request
def before_request():
    """Add request ID and logging for each request"""
    request.request_id = str(uuid.uuid4())
    logger.info(
        f"{request.method} {request.path}",
        extra={
            "request_id": request.request_id,
            "user_agent": request.headers.get("User-Agent"),
            "remote_addr": request.remote_addr
        }
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Paisalo Google AdK Chatbot',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
    })

@app.route('/webhook', methods=['POST'])
def adk_webhook():
    """Google AdK webhook endpoint"""
    try:
        # Validate request
        validation_error = validate_adk_request(request.json)
        if validation_error:
            logger.warning(f"Invalid AdK request: {validation_error}", 
                         extra={"request_id": request.request_id})
            return jsonify({
                'fulfillmentText': 'Sorry, I received an invalid request. Please try again.',
                'source': 'paisalo-adk-chatbot'
            }), 400
        
        # Process AdK request
        response = chatbot.handle_adk_request(request.json, request.request_id)
        
        logger.info("AdK request processed successfully", 
                   extra={
                       "request_id": request.request_id,
                       "session_id": request.json.get('sessionId', 'unknown')
                   })
        
        return jsonify(response)
        
    except Exception as error:
        logger.error(f"Error processing AdK request: {str(error)}", 
                    extra={
                        "request_id": request.request_id,
                        "error": str(error)
                    }, exc_info=True)
        
        return jsonify({
            'fulfillmentText': 'Sorry, I encountered an error. Please try again.',
            'source': 'paisalo-adk-chatbot'
        }), 500

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint for development and debugging"""
    try:
        data = request.json or {}
        message = data.get('message', '')
        session_id = data.get('sessionId', str(uuid.uuid4()))
        
        if not message:
            return jsonify({
                'error': 'Message is required',
                'example': {
                    'message': 'hello',
                    'sessionId': 'optional-session-id'
                }
            }), 400
        
        # Process test message
        response = chatbot.handle_test_message(message, session_id)
        
        return jsonify({
            'sessionId': session_id,
            'response': response['fulfillmentText'],
            'step': response.get('step'),
            'data': response.get('data'),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        logger.error(f"Error in test endpoint: {str(error)}", 
                    extra={"request_id": request.request_id}, 
                    exc_info=True)
        
        return jsonify({
            'error': 'Internal server error',
            'message': str(error)
        }), 500

@app.route('/session/<session_id>', methods=['GET'])
def get_session_info(session_id: str):
    """Get session information for debugging"""
    try:
        session_info = chatbot.get_session_info(session_id)
        
        if not session_info:
            return jsonify({
                'error': 'Session not found',
                'sessionId': session_id
            }), 404
        
        return jsonify({
            'sessionId': session_id,
            'sessionInfo': session_info,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        logger.error(f"Error getting session info: {str(error)}", 
                    extra={"request_id": request.request_id}, 
                    exc_info=True)
        
        return jsonify({
            'error': 'Internal server error',
            'message': str(error)
        }), 500

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions (for debugging)"""
    try:
        sessions = chatbot.list_active_sessions()
        
        return jsonify({
            'activeSessions': len(sessions),
            'sessions': sessions,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        logger.error(f"Error listing sessions: {str(error)}", 
                    extra={"request_id": request.request_id}, 
                    exc_info=True)
        
        return jsonify({
            'error': 'Internal server error',
            'message': str(error)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'error': 'Endpoint not found',
        'path': request.path,
        'method': request.method
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Unhandled error: {str(error)}", 
                extra={"request_id": getattr(request, 'request_id', 'unknown')}, 
                exc_info=True)
    
    return jsonify({
        'error': 'Internal server error',
        'request_id': getattr(request, 'request_id', 'unknown')
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Paisalo Google AdK Chatbot on port {port}")
    print(f"🚀 Paisalo Google AdK Chatbot server running on port {port}")
    print(f"📋 Health check: http://localhost:{port}/health")
    print(f"🧪 Test endpoint: http://localhost:{port}/test")
    print(f"🔗 AdK webhook: http://localhost:{port}/webhook")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

