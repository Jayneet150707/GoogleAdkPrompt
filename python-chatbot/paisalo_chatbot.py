#!/usr/bin/env python3.13
"""
Paisalo Loan Chatbot - Python 3.13 Implementation
Google AdK Integration for loan eligibility and EMI calculation

Author: Codegen for Paisalo Digital Limited
Python Version: 3.13+
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationStep(Enum):
    """Enumeration for conversation steps"""
    WELCOME = "welcome"
    AGE = "age"
    CREDIT_SCORE = "credit_score"
    DOCUMENTS = "documents"
    PAN_NUMBER = "pan_number"
    LOAN_AMOUNT = "loan_amount"
    TENURE = "tenure"
    INCOME = "income"
    EXPENSE = "expense"
    FAMILY_INCOME = "family_income"
    FAMILY_EXPENSE = "family_expense"
    COMPLETE = "complete"

@dataclass
class LoanRules:
    """Paisalo loan business rules"""
    MIN_AGE: int = 21
    MAX_AGE: int = 57
    MIN_CREDIT_SCORE: int = 18
    MAX_CREDIT_SCORE: int = 650
    MIN_LOAN_AMOUNT: int = 50000
    MAX_LOAN_AMOUNT: int = 100000
    MAX_EXPENSE_PERCENTAGE: float = 50.0
    
    # ROI rates based on tenure
    ROI_RATES: Dict[int, float] = field(default_factory=lambda: {
        12: 7.0,   # 12 months - 7% ROI
        24: 9.0,   # 24 months - 9% ROI
        36: 12.0,  # 36 months - 12% ROI
        48: 18.0   # 48 months - 18% ROI
    })
    
    VALID_TENURES: List[int] = field(default_factory=lambda: [12, 24, 36, 48])
    
    VALID_DOCUMENT_COMBINATIONS: List[List[str]] = field(default_factory=lambda: [
        ['VOTER', 'PAN'],
        ['PAN', 'DL'],
        ['VOTER_ID', 'PAN'],
        ['DL', 'PAN']
    ])

@dataclass
class UserProfile:
    """User profile data structure"""
    age: Optional[int] = None
    credit_score: Optional[int] = None
    documents: List[str] = field(default_factory=list)
    pan_number: Optional[str] = None
    loan_amount: Optional[int] = None
    tenure: Optional[int] = None
    income: Optional[float] = None
    expense: Optional[float] = None
    family_income: Optional[float] = None
    family_expense: Optional[float] = None
    is_eligible: bool = False
    emi_amount: Optional[float] = None

@dataclass
class UserSession:
    """User session management"""
    session_id: str
    step: ConversationStep = ConversationStep.WELCOME
    profile: UserProfile = field(default_factory=UserProfile)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class PANValidator:
    """PAN number validation utility"""
    
    @staticmethod
    def validate_pan_format(pan: str) -> Tuple[bool, str]:
        """
        Validate PAN number format using regex
        Format: AAAAA9999A (5 letters + 4 digits + 1 letter)
        """
        if not pan:
            return False, "PAN number is required"
        
        pan = pan.upper().strip()
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        if re.match(pan_pattern, pan):
            return True, "Valid PAN format"
        else:
            return False, "Invalid PAN format. Expected format: AAAAA9999A (e.g., ABCDE1234F)"

class LoanValidator:
    """Loan eligibility validation utilities"""
    
    def __init__(self, rules: LoanRules):
        self.rules = rules
    
    def validate_age(self, age: int) -> Tuple[bool, str]:
        """Validate user age"""
        if not isinstance(age, int) or age <= 0:
            return False, "Please provide a valid age"
        
        if age < self.rules.MIN_AGE or age > self.rules.MAX_AGE:
            return False, f"Age must be between {self.rules.MIN_AGE} and {self.rules.MAX_AGE} years"
        
        return True, "Age is valid"
    
    def validate_credit_score(self, score: int) -> Tuple[bool, str]:
        """Validate credit score"""
        if not isinstance(score, int) or score < 0:
            return False, "Please provide a valid credit score"
        
        if score < self.rules.MIN_CREDIT_SCORE or score > self.rules.MAX_CREDIT_SCORE:
            return False, f"Credit score must be between {self.rules.MIN_CREDIT_SCORE} and {self.rules.MAX_CREDIT_SCORE}"
        
        return True, "Credit score is valid"
    
    def validate_documents(self, documents: List[str]) -> Tuple[bool, str]:
        """Validate document combinations"""
        if not documents or len(documents) < 2:
            return False, "At least 2 documents are required"
        
        # Normalize document names
        normalized_docs = [doc.upper().replace(' ', '_') for doc in documents]
        
        # Check if any valid combination exists
        for valid_combo in self.rules.VALID_DOCUMENT_COMBINATIONS:
            if all(doc in normalized_docs for doc in valid_combo):
                return True, "Valid document combination"
        
        return False, "Invalid document combination. Required: (Voter ID + PAN) or (PAN + DL)"
    
    def validate_loan_amount(self, amount: int) -> Tuple[bool, str]:
        """Validate loan amount"""
        if not isinstance(amount, int) or amount <= 0:
            return False, "Please provide a valid loan amount"
        
        if amount < self.rules.MIN_LOAN_AMOUNT or amount > self.rules.MAX_LOAN_AMOUNT:
            return False, f"Loan amount must be between ₹{self.rules.MIN_LOAN_AMOUNT:,} and ₹{self.rules.MAX_LOAN_AMOUNT:,}"
        
        return True, "Loan amount is valid"
    
    def validate_tenure(self, tenure: int) -> Tuple[bool, str]:
        """Validate loan tenure"""
        if tenure not in self.rules.VALID_TENURES:
            return False, f"Invalid tenure. Choose from: {', '.join(map(str, self.rules.VALID_TENURES))} months"
        
        return True, "Tenure is valid"
    
    def validate_income_expense_ratio(self, income: float, expense: float) -> Tuple[bool, str]:
        """Validate income to expense ratio"""
        if income <= 0:
            return False, "Income must be greater than 0"
        
        if expense < 0:
            return False, "Expense cannot be negative"
        
        expense_percentage = (expense / income) * 100
        
        if expense_percentage > self.rules.MAX_EXPENSE_PERCENTAGE:
            return False, f"Expenses ({expense_percentage:.1f}%) exceed {self.rules.MAX_EXPENSE_PERCENTAGE}% of income"
        
        return True, f"Expense ratio is acceptable ({expense_percentage:.1f}%)"

class EMICalculator:
    """EMI calculation using Straight Line Method (SLM)"""
    
    def __init__(self, rules: LoanRules):
        self.rules = rules
    
    def calculate_emi_slm(self, principal: int, tenure_months: int) -> Dict[str, float]:
        """
        Calculate EMI using Straight Line Method (SLM)
        Formula: 
        - Total Interest = Principal × ROI × (Tenure in years)
        - Total Amount = Principal + Total Interest
        - EMI = Total Amount ÷ Tenure in months
        """
        if tenure_months not in self.rules.ROI_RATES:
            raise ValueError(f"Invalid tenure: {tenure_months}")
        
        roi_percentage = self.rules.ROI_RATES[tenure_months]
        tenure_years = tenure_months / 12
        
        # SLM calculation
        total_interest = principal * (roi_percentage / 100) * tenure_years
        total_amount = principal + total_interest
        emi = total_amount / tenure_months
        
        return {
            'principal': float(principal),
            'roi_percentage': roi_percentage,
            'tenure_months': tenure_months,
            'tenure_years': tenure_years,
            'total_interest': round(total_interest, 2),
            'total_amount': round(total_amount, 2),
            'emi': round(emi, 2)
        }

class ResponseGenerator:
    """Generate responses for Google AdK"""
    
    @staticmethod
    def create_simple_response(text: str, end_conversation: bool = False) -> Dict[str, Any]:
        """Create a simple text response"""
        response = {
            "fulfillmentText": text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [text]
                    }
                }
            ]
        }
        
        if end_conversation:
            response["endInteraction"] = True
        
        return response
    
    @staticmethod
    def create_welcome_response() -> Dict[str, Any]:
        """Create welcome response"""
        welcome_text = (
            "🏦 Welcome to Paisalo Digital Limited! "
            "I'm here to help you check your loan eligibility and calculate EMI. "
            "Let's start with some basic information. What is your age?"
        )
        return ResponseGenerator.create_simple_response(welcome_text)
    
    @staticmethod
    def create_eligibility_result(profile: UserProfile, emi_details: Dict[str, float]) -> Dict[str, Any]:
        """Create final eligibility result response"""
        if profile.is_eligible:
            result_text = (
                f"🎉 Congratulations! You are eligible for a loan.\n\n"
                f"📋 Loan Details:\n"
                f"• Loan Amount: ₹{emi_details['principal']:,.0f}\n"
                f"• Tenure: {emi_details['tenure_months']} months\n"
                f"• Interest Rate: {emi_details['roi_percentage']}% per annum\n"
                f"• Total Interest: ₹{emi_details['total_interest']:,.2f}\n"
                f"• Total Amount: ₹{emi_details['total_amount']:,.2f}\n"
                f"• Monthly EMI: ₹{emi_details['emi']:,.2f}\n\n"
                f"Thank you for choosing Paisalo Digital Limited! 🙏"
            )
        else:
            result_text = (
                "❌ Sorry, you are not eligible for a loan at this time. "
                "Please contact our customer service for more information."
            )
        
        return ResponseGenerator.create_simple_response(result_text, end_conversation=True)

class PaisaloChatbot:
    """Main Paisalo Chatbot class"""
    
    def __init__(self):
        self.rules = LoanRules()
        self.validator = LoanValidator(self.rules)
        self.emi_calculator = EMICalculator(self.rules)
        self.response_generator = ResponseGenerator()
        self.sessions: Dict[str, UserSession] = {}
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "service": "Paisalo Loan Chatbot",
                "version": "1.0.0",
                "python_version": "3.13"
            })
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Google AdK webhook endpoint"""
            try:
                req_data = request.get_json()
                response = self.handle_webhook_request(req_data)
                return jsonify(response)
            except Exception as e:
                logger.error(f"Webhook error: {str(e)}")
                return jsonify(self.response_generator.create_simple_response(
                    "Sorry, something went wrong. Please try again."
                ))
        
        @self.app.route('/test', methods=['POST'])
        def test_endpoint():
            """Test endpoint for manual testing"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                session_id = data.get('sessionId', str(uuid.uuid4()))
                
                # Create mock request for testing
                mock_request = {
                    'session': session_id,
                    'queryResult': {
                        'queryText': message,
                        'intent': {
                            'displayName': 'Default Welcome Intent' if not self.sessions.get(session_id) else 'Default Fallback Intent'
                        }
                    }
                }
                
                response = self.handle_webhook_request(mock_request)
                return jsonify({
                    'sessionId': session_id,
                    'response': response['fulfillmentText'],
                    'step': self.sessions.get(session_id, {}).step.value if self.sessions.get(session_id) else 'welcome'
                })
            except Exception as e:
                logger.error(f"Test endpoint error: {str(e)}")
                return jsonify({'error': str(e)})
    
    def handle_webhook_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook request"""
        try:
            session_id = request_data.get('session', str(uuid.uuid4()))
            query_text = request_data.get('queryResult', {}).get('queryText', '').lower()
            intent_name = request_data.get('queryResult', {}).get('intent', {}).get('displayName', '')
            
            # Initialize session if not exists
            if session_id not in self.sessions:
                self.sessions[session_id] = UserSession(session_id=session_id)
            
            session = self.sessions[session_id]
            session.last_updated = datetime.now()
            
            # Handle different intents
            if intent_name == 'Default Welcome Intent' or query_text in ['hello', 'hi', 'start', 'help']:
                return self.handle_welcome(session)
            else:
                return self.handle_conversation_flow(query_text, session)
                
        except Exception as e:
            logger.error(f"Webhook request error: {str(e)}")
            return self.response_generator.create_simple_response(
                "Sorry, I encountered an error. Please try again."
            )
    
    def handle_welcome(self, session: UserSession) -> Dict[str, Any]:
        """Handle welcome intent"""
        session.step = ConversationStep.AGE
        return self.response_generator.create_welcome_response()
    
    def handle_conversation_flow(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle conversation flow based on current step"""
        try:
            if session.step == ConversationStep.AGE:
                return self.handle_age_input(user_input, session)
            elif session.step == ConversationStep.CREDIT_SCORE:
                return self.handle_credit_score_input(user_input, session)
            elif session.step == ConversationStep.DOCUMENTS:
                return self.handle_documents_input(user_input, session)
            elif session.step == ConversationStep.PAN_NUMBER:
                return self.handle_pan_input(user_input, session)
            elif session.step == ConversationStep.LOAN_AMOUNT:
                return self.handle_loan_amount_input(user_input, session)
            elif session.step == ConversationStep.TENURE:
                return self.handle_tenure_input(user_input, session)
            elif session.step == ConversationStep.INCOME:
                return self.handle_income_input(user_input, session)
            elif session.step == ConversationStep.EXPENSE:
                return self.handle_expense_input(user_input, session)
            else:
                return self.response_generator.create_simple_response(
                    "I didn't understand that. Could you please try again?"
                )
        except Exception as e:
            logger.error(f"Conversation flow error: {str(e)}")
            return self.response_generator.create_simple_response(
                "Sorry, something went wrong. Please try again."
            )
    
    def handle_age_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle age input"""
        age_match = re.search(r'\d+', user_input)
        if not age_match:
            return self.response_generator.create_simple_response(
                "Please provide your age as a number. For example: 'I am 25 years old' or just '25'."
            )
        
        age = int(age_match.group())
        is_valid, message = self.validator.validate_age(age)
        
        if not is_valid:
            return self.response_generator.create_simple_response(
                f"❌ {message}. Unfortunately, you are not eligible for a loan.",
                end_conversation=True
            )
        
        session.profile.age = age
        session.step = ConversationStep.CREDIT_SCORE
        
        return self.response_generator.create_simple_response(
            "Great! Now, what is your credit score?"
        )
    
    def handle_credit_score_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle credit score input"""
        score_match = re.search(r'\d+', user_input)
        if not score_match:
            return self.response_generator.create_simple_response(
                "Please provide your credit score as a number. For example: 'My credit score is 650' or just '650'."
            )
        
        credit_score = int(score_match.group())
        is_valid, message = self.validator.validate_credit_score(credit_score)
        
        if not is_valid:
            return self.response_generator.create_simple_response(
                f"❌ {message}. Unfortunately, you are not eligible for a loan.",
                end_conversation=True
            )
        
        session.profile.credit_score = credit_score
        session.step = ConversationStep.DOCUMENTS
        
        return self.response_generator.create_simple_response(
            "Excellent! Which documents do you have? Please mention if you have: Voter ID, PAN Card, or Driving License (DL)."
        )
    
    def handle_documents_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle documents input"""
        # Parse documents from user input
        documents = []
        user_input_lower = user_input.lower()
        
        if 'voter' in user_input_lower:
            documents.append('VOTER')
        if 'pan' in user_input_lower:
            documents.append('PAN')
        if 'dl' in user_input_lower or 'driving' in user_input_lower or 'license' in user_input_lower:
            documents.append('DL')
        
        is_valid, message = self.validator.validate_documents(documents)
        
        if not is_valid:
            return self.response_generator.create_simple_response(
                f"❌ {message}. Unfortunately, you are not eligible for a loan.",
                end_conversation=True
            )
        
        session.profile.documents = documents
        session.step = ConversationStep.PAN_NUMBER
        
        return self.response_generator.create_simple_response(
            "Perfect! Please provide your PAN number for verification."
        )
    
    def handle_pan_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle PAN number input"""
        # Extract PAN from input
        pan_match = re.search(r'[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}', user_input)
        if not pan_match:
            return self.response_generator.create_simple_response(
                "Please provide a valid PAN number in the format: AAAAA9999A (e.g., ABCDE1234F)."
            )
        
        pan_number = pan_match.group().upper()
        is_valid, message = PANValidator.validate_pan_format(pan_number)
        
        if not is_valid:
            return self.response_generator.create_simple_response(f"❌ {message}")
        
        session.profile.pan_number = pan_number
        session.step = ConversationStep.LOAN_AMOUNT
        
        return self.response_generator.create_simple_response(
            f"Thank you! Your PAN {pan_number} is verified. "
            f"How much loan amount do you need? (Between ₹{self.rules.MIN_LOAN_AMOUNT:,} to ₹{self.rules.MAX_LOAN_AMOUNT:,})"
        )
    
    def handle_loan_amount_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle loan amount input"""
        amount_match = re.search(r'\d+', user_input.replace(',', ''))
        if not amount_match:
            return self.response_generator.create_simple_response(
                "Please provide the loan amount as a number. For example: '75000' or '75,000'."
            )
        
        loan_amount = int(amount_match.group())
        is_valid, message = self.validator.validate_loan_amount(loan_amount)
        
        if not is_valid:
            return self.response_generator.create_simple_response(f"❌ {message}")
        
        session.profile.loan_amount = loan_amount
        session.step = ConversationStep.TENURE
        
        tenure_options = ', '.join(f"{t} months" for t in self.rules.VALID_TENURES)
        return self.response_generator.create_simple_response(
            f"Great! You want a loan of ₹{loan_amount:,}. "
            f"For how many months do you want the loan? Choose from: {tenure_options}."
        )
    
    def handle_tenure_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle tenure input"""
        tenure_match = re.search(r'\d+', user_input)
        if not tenure_match:
            return self.response_generator.create_simple_response(
                "Please provide the tenure in months. For example: '24 months' or just '24'."
            )
        
        tenure = int(tenure_match.group())
        is_valid, message = self.validator.validate_tenure(tenure)
        
        if not is_valid:
            return self.response_generator.create_simple_response(f"❌ {message}")
        
        session.profile.tenure = tenure
        session.step = ConversationStep.INCOME
        
        roi = self.rules.ROI_RATES[tenure]
        return self.response_generator.create_simple_response(
            f"Perfect! {tenure} months tenure with {roi}% interest rate. "
            f"What is your monthly income?"
        )
    
    def handle_income_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle income input"""
        income_match = re.search(r'\d+', user_input.replace(',', ''))
        if not income_match:
            return self.response_generator.create_simple_response(
                "Please provide your monthly income as a number. For example: '50000' or '50,000'."
            )
        
        income = float(income_match.group())
        session.profile.income = income
        session.step = ConversationStep.EXPENSE
        
        return self.response_generator.create_simple_response(
            f"Thank you! Your monthly income is ₹{income:,.0f}. "
            f"What are your monthly expenses?"
        )
    
    def handle_expense_input(self, user_input: str, session: UserSession) -> Dict[str, Any]:
        """Handle expense input and complete eligibility check"""
        expense_match = re.search(r'\d+', user_input.replace(',', ''))
        if not expense_match:
            return self.response_generator.create_simple_response(
                "Please provide your monthly expenses as a number. For example: '20000' or '20,000'."
            )
        
        expense = float(expense_match.group())
        session.profile.expense = expense
        
        # Validate income-expense ratio
        is_valid, message = self.validator.validate_income_expense_ratio(
            session.profile.income, expense
        )
        
        if not is_valid:
            return self.response_generator.create_simple_response(
                f"❌ {message}. Unfortunately, you are not eligible for a loan at this time.",
                end_conversation=True
            )
        
        # All validations passed - calculate EMI and generate final response
        session.profile.is_eligible = True
        session.step = ConversationStep.COMPLETE
        
        try:
            emi_details = self.emi_calculator.calculate_emi_slm(
                session.profile.loan_amount,
                session.profile.tenure
            )
            session.profile.emi_amount = emi_details['emi']
            
            return self.response_generator.create_eligibility_result(session.profile, emi_details)
            
        except Exception as e:
            logger.error(f"EMI calculation error: {str(e)}")
            return self.response_generator.create_simple_response(
                "Sorry, there was an error calculating your EMI. Please try again.",
                end_conversation=True
            )
    
    def run(self, host: str = '0.0.0.0', port: int = 3000, debug: bool = False):
        """Run the Flask application"""
        logger.info(f"Starting Paisalo Chatbot on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # Create and run the chatbot
    chatbot = PaisaloChatbot()
    chatbot.run(debug=True)

