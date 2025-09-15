"""
Configuration settings for Paisalo Google AdK Chatbot
"""

import os
from typing import Dict, Any


class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'paisalo-adk-chatbot-secret-key-2024')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Google AdK settings
    GOOGLE_PROJECT_ID = os.environ.get('GOOGLE_PROJECT_ID', 'paisalo-chatbot')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', '30'))
    MAX_ACTIVE_SESSIONS = int(os.environ.get('MAX_ACTIVE_SESSIONS', '1000'))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    
    @classmethod
    def get_loan_rules(cls) -> Dict[str, Any]:
        """Get Paisalo loan business rules"""
        return {
            'age': {
                'min': 21,
                'max': 57
            },
            'credit_score': {
                'min_threshold': 18,  # Scores < 18 are eligible
                'max_threshold': 650  # Scores > 650 are eligible
                # Scores between 18-650 (inclusive) are NOT eligible
            },
            'documents': {
                'required_combinations': [
                    ['pan', 'voter_id'],
                    ['pan', 'driving_license']
                ]
            },
            'loan_amount': {
                'min': 50000,
                'max': 100000
            },
            'tenure_options': [12, 24, 36, 48],  # months
            'roi_rates': {
                12: 7.0,   # 7% for 12 months
                24: 9.0,   # 9% for 24 months
                36: 12.0,  # 12% for 36 months
                48: 18.0   # 18% for 48 months
            },
            'expense_ratio': {
                'max_percentage': 50  # Expenses should not exceed 50% of income
            },
            'company_name': 'Paisalo'
        }
    
    @classmethod
    def get_pan_regex(cls) -> str:
        """Get PAN validation regex pattern"""
        return r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    @classmethod
    def get_conversation_messages(cls) -> Dict[str, str]:
        """Get conversation flow messages"""
        return {
            'welcome': (
                "🏦 Welcome to Paisalo Digital Limited! 🏦\n\n"
                "I'm here to help you check your loan eligibility quickly and easily.\n\n"
                "To get started, please tell me your age."
            ),
            'age_prompt': "Please tell me your age to check loan eligibility.",
            'credit_score_prompt': "Great! Now, please tell me your credit score.",
            'documents_prompt': (
                "Perfect! Now I need to verify your documents.\n\n"
                "Please tell me which documents you have:\n"
                "• PAN Card and Voter ID\n"
                "• PAN Card and Driving License\n\n"
                "Which combination do you have?"
            ),
            'pan_prompt': "Please provide your PAN card number for verification.",
            'loan_amount_prompt': (
                "Excellent! Now, how much loan amount do you need?\n"
                "(Minimum: ₹50,000, Maximum: ₹1,00,000)"
            ),
            'tenure_prompt': (
                "Great! Please select your preferred loan tenure:\n"
                "• 12 months (7% ROI)\n"
                "• 24 months (9% ROI)\n"
                "• 36 months (12% ROI)\n"
                "• 48 months (18% ROI)"
            ),
            'income_prompt': "Please tell me your monthly income.",
            'expenses_prompt': "Finally, please tell me your monthly expenses.",
            'processing': "Let me calculate your loan eligibility...",
            'approved': (
                "🎉 Congratulations! You are eligible for the loan! 🎉\n\n"
                "Your loan details:\n"
                "💰 Amount: ₹{amount:,}\n"
                "📅 Tenure: {tenure} months\n"
                "📊 ROI: {roi}%\n"
                "💳 Monthly EMI: ₹{emi:,.2f}\n\n"
                "Thank you for choosing Paisalo! 🏦"
            ),
            'rejected': (
                "❌ Sorry, you are not eligible for the loan.\n\n"
                "Reason: {reason}\n\n"
                "Thank you for your interest in Paisalo. "
                "Please feel free to apply again when you meet our eligibility criteria."
            ),
            'error': (
                "I'm sorry, I didn't understand that. "
                "Could you please provide the information again?"
            ),
            'invalid_input': "Please provide a valid {field}.",
            'session_expired': (
                "Your session has expired. Please start over by saying 'hello' or 'start'."
            )
        }

