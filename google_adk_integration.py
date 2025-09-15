#!/usr/bin/env python3.13
"""
Google ADK Integration Module for Paisalo Loan Agent
Handles Android app integration and API endpoints

Company: Paisalo
Author: Codegen Agent
Python Version: 3.13
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from typing import Dict, Any
from paisalo_loan_agent import PaisaloLoanAgent, UserProfile, LoanApplication, LoanStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleADKIntegration:
    """
    Google ADK Integration for Paisalo Loan Processing
    Provides REST API endpoints for Android app integration
    """
    
    def __init__(self):
        """Initialize the Flask app and loan agent"""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for Android app
        self.loan_agent = PaisaloLoanAgent()
        self.setup_routes()
        
        logger.info("Google ADK Integration initialized")
    
    def setup_routes(self):
        """Setup API routes for Android app"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "service": "Paisalo Loan Agent",
                "version": "1.0.0"
            })
        
        @self.app.route('/api/loan/eligibility', methods=['POST'])
        def check_loan_eligibility():
            """
            Check loan eligibility
            Expected JSON payload:
            {
                "user_profile": {
                    "age": 35,
                    "credit_score": 600,
                    "income": 50000,
                    "expense": 20000,
                    "family_income": 30000,
                    "family_expense": 10000,
                    "documents": ["PAN", "VOTER_ID"],
                    "pan_number": "ABCDE1234F"
                },
                "loan_amount": 75000,
                "tenure_months": 24
            }
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "error": "No JSON data provided",
                        "status": "error"
                    }), 400
                
                # Validate required fields
                required_fields = ['user_profile', 'loan_amount', 'tenure_months']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "error": f"Missing required field: {field}",
                            "status": "error"
                        }), 400
                
                # Create user profile
                user_data = data['user_profile']
                user_profile = UserProfile(
                    age=user_data.get('age'),
                    credit_score=user_data.get('credit_score'),
                    income=user_data.get('income', 0),
                    expense=user_data.get('expense', 0),
                    family_income=user_data.get('family_income', 0),
                    family_expense=user_data.get('family_expense', 0),
                    documents=user_data.get('documents', []),
                    pan_number=user_data.get('pan_number')
                )
                
                # Create loan application
                loan_application = LoanApplication(
                    amount=data['loan_amount'],
                    tenure_months=data['tenure_months'],
                    user_profile=user_profile
                )
                
                # Process the application
                result = self.loan_agent.process_loan_application(loan_application)
                summary = self.loan_agent.generate_loan_summary(loan_application, result)
                
                return jsonify({
                    "status": "success",
                    "data": summary
                })
                
            except Exception as e:
                logger.error(f"Error processing loan application: {str(e)}")
                return jsonify({
                    "error": f"Internal server error: {str(e)}",
                    "status": "error"
                }), 500
        
        @self.app.route('/api/loan/calculate-emi', methods=['POST'])
        def calculate_emi():
            """
            Calculate EMI for given parameters
            Expected JSON payload:
            {
                "principal": 75000,
                "tenure_months": 24
            }
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "error": "No JSON data provided",
                        "status": "error"
                    }), 400
                
                principal = data.get('principal')
                tenure_months = data.get('tenure_months')
                
                if not principal or not tenure_months:
                    return jsonify({
                        "error": "Missing principal or tenure_months",
                        "status": "error"
                    }), 400
                
                # Get ROI for tenure
                roi = self.loan_agent.get_roi_for_tenure(tenure_months)
                if roi is None:
                    return jsonify({
                        "error": f"Invalid tenure {tenure_months} months",
                        "available_tenures": list(self.loan_agent.ROI_MAPPING.keys()),
                        "status": "error"
                    }), 400
                
                # Calculate EMI
                emi = self.loan_agent.calculate_emi_slm(principal, roi, tenure_months)
                total_amount = emi * tenure_months
                total_interest = total_amount - principal
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "principal": principal,
                        "tenure_months": tenure_months,
                        "roi_percent": roi,
                        "monthly_emi": emi,
                        "total_amount": total_amount,
                        "total_interest": total_interest
                    }
                })
                
            except Exception as e:
                logger.error(f"Error calculating EMI: {str(e)}")
                return jsonify({
                    "error": f"Internal server error: {str(e)}",
                    "status": "error"
                }), 500
        
        @self.app.route('/api/validate/pan', methods=['POST'])
        def validate_pan():
            """
            Validate PAN number
            Expected JSON payload:
            {
                "pan_number": "ABCDE1234F"
            }
            """
            try:
                data = request.get_json()
                
                if not data or 'pan_number' not in data:
                    return jsonify({
                        "error": "PAN number is required",
                        "status": "error"
                    }), 400
                
                pan_number = data['pan_number']
                is_valid, message = self.loan_agent.validate_pan_number(pan_number)
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "pan_number": pan_number,
                        "is_valid": is_valid,
                        "message": message
                    }
                })
                
            except Exception as e:
                logger.error(f"Error validating PAN: {str(e)}")
                return jsonify({
                    "error": f"Internal server error: {str(e)}",
                    "status": "error"
                }), 500
        
        @self.app.route('/api/loan/rules', methods=['GET'])
        def get_loan_rules():
            """
            Get all loan rules and configurations
            """
            try:
                rules = {
                    "age_limits": {
                        "min_age": self.loan_agent.MIN_AGE,
                        "max_age": self.loan_agent.MAX_AGE
                    },
                    "credit_score_limits": {
                        "min_credit_score": self.loan_agent.MIN_CREDIT_SCORE,
                        "max_credit_score": self.loan_agent.MAX_CREDIT_SCORE
                    },
                    "loan_amount_limits": {
                        "min_amount": self.loan_agent.MIN_LOAN_AMOUNT,
                        "max_amount": self.loan_agent.MAX_LOAN_AMOUNT
                    },
                    "roi_mapping": self.loan_agent.ROI_MAPPING,
                    "valid_document_combinations": [
                        ["VOTER_ID", "PAN"],
                        ["PAN", "DL"]
                    ],
                    "expense_ratio_limit": 50,
                    "pan_format": "AAAAA9999A"
                }
                
                return jsonify({
                    "status": "success",
                    "data": rules
                })
                
            except Exception as e:
                logger.error(f"Error getting loan rules: {str(e)}")
                return jsonify({
                    "error": f"Internal server error: {str(e)}",
                    "status": "error"
                }), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors"""
            return jsonify({
                "error": "Endpoint not found",
                "status": "error"
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors"""
            return jsonify({
                "error": "Internal server error",
                "status": "error"
            }), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"Starting Paisalo Loan Agent API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def main():
    """
    Main function to run the Google ADK Integration server
    """
    print("🚀 Starting Paisalo Loan Agent - Google ADK Integration")
    print("=" * 60)
    
    # Create and run the integration server
    integration = GoogleADKIntegration()
    integration.run(debug=True)

if __name__ == "__main__":
    main()
