#!/usr/bin/env python3.13
"""
Paisalo Loan Chatbot - Production Runner
Simple script to run the chatbot with proper configuration

Author: Codegen for Paisalo Digital Limited
"""

import os
import sys
from paisalo_chatbot import PaisaloChatbot

def main():
    """Main entry point for running the chatbot"""
    
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🏦 Starting Paisalo Loan Chatbot...")
    print(f"🐍 Python Version: {sys.version}")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug Mode: {debug}")
    print(f"📋 Business Rules: Age 21-57, Credit Score 18-650, Loan ₹50k-₹100k")
    print(f"💰 ROI Rates: 12m:7%, 24m:9%, 36m:12%, 48m:18%")
    print("-" * 60)
    
    try:
        # Create and run the chatbot
        chatbot = PaisaloChatbot()
        chatbot.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Paisalo Loan Chatbot...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting chatbot: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

