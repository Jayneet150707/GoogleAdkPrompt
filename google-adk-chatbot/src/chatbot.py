"""
Paisalo Google AdK Chatbot - Main chatbot implementation
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from src.models.session import ChatSession, ConversationStep, UserData, LoanResult, LoanStatus
from src.utils.validators import LoanValidator
from src.utils.logger import ChatbotLogger
from src.config import Config
from src.middleware.validation import (
    extract_session_id, 
    extract_intent_name, 
    extract_user_message,
    sanitize_user_input
)


class PaisaloAdkChatbot:
    """Main chatbot class for handling Google AdK conversations"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.validator = LoanValidator()
        self.logger = ChatbotLogger()
        self.config = Config()
        self.messages = Config.get_conversation_messages()
        
        # Session management
        self.session_timeout = self.config.SESSION_TIMEOUT_MINUTES
        self.max_sessions = self.config.MAX_ACTIVE_SESSIONS
    
    def handle_adk_request(self, request_data: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """
        Handle Google AdK webhook request
        
        Args:
            request_data: AdK request payload
            request_id: Unique request identifier
            
        Returns:
            AdK response payload
        """
        try:
            # Extract request information
            session_id = extract_session_id(request_data)
            intent_name = extract_intent_name(request_data)
            user_message = extract_user_message(request_data)
            
            self.logger.log_adk_request(request_id, session_id, intent_name)
            
            # Get or create session
            session = self.get_or_create_session(session_id)
            
            # Handle the conversation
            response = self.handle_conversation_flow(user_message, session)
            
            self.logger.log_adk_response(request_id, session_id, response['fulfillmentText'])
            
            return response
            
        except Exception as error:
            self.logger.log_error(session_id if 'session_id' in locals() else 'unknown', error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_test_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Handle test message (for development/debugging)
        
        Args:
            message: User message
            session_id: Session identifier
            
        Returns:
            Response payload
        """
        try:
            # Get or create session
            session = self.get_or_create_session(session_id)
            
            # Handle the conversation
            response = self.handle_conversation_flow(message, session)
            
            # Add debug information
            response['step'] = session.step.value
            response['data'] = session.user_data.to_dict()
            
            return response
            
        except Exception as error:
            self.logger.log_error(session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'step': session.step.value if 'session' in locals() else 'unknown',
                'data': {}
            }
    
    def handle_conversation_flow(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """
        Handle conversation flow based on current step
        
        Args:
            user_message: User's message
            session: Chat session
            
        Returns:
            Response payload
        """
        user_message = sanitize_user_input(user_message).lower().strip()
        
        # Handle welcome/restart commands
        if any(keyword in user_message for keyword in ['hello', 'hi', 'start', 'restart', 'begin']):
            return self.handle_welcome(session)
        
        # Handle current conversation step
        if session.step == ConversationStep.WELCOME:
            return self.handle_welcome(session)
        elif session.step == ConversationStep.AGE:
            return self.handle_age_input(user_message, session)
        elif session.step == ConversationStep.CREDIT_SCORE:
            return self.handle_credit_score_input(user_message, session)
        elif session.step == ConversationStep.DOCUMENTS:
            return self.handle_documents_input(user_message, session)
        elif session.step == ConversationStep.PAN_VERIFICATION:
            return self.handle_pan_input(user_message, session)
        elif session.step == ConversationStep.LOAN_AMOUNT:
            return self.handle_loan_amount_input(user_message, session)
        elif session.step == ConversationStep.TENURE:
            return self.handle_tenure_input(user_message, session)
        elif session.step == ConversationStep.INCOME:
            return self.handle_income_input(user_message, session)
        elif session.step == ConversationStep.EXPENSES:
            return self.handle_expenses_input(user_message, session)
        elif session.step == ConversationStep.COMPLETED:
            return self.handle_completed(session)
        else:
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_welcome(self, session: ChatSession) -> Dict[str, Any]:
        """Handle welcome step"""
        session.set_step(ConversationStep.AGE)
        self.logger.log_conversation_start(session.session_id, "welcome")
        
        return {
            'fulfillmentText': self.messages['welcome'],
            'source': 'paisalo-adk-chatbot'
        }
    
    def handle_age_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle age input step"""
        try:
            # Extract age from message
            age = self.extract_number(user_message)
            if age is None:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='age'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate age
            is_valid, message = self.validator.validate_age(age)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'age', str(age), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot',
                    'endInteraction': True
                }
            
            # Store age and advance
            session.user_data.age = age
            session.set_step(ConversationStep.CREDIT_SCORE)
            
            return {
                'fulfillmentText': self.messages['credit_score_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_credit_score_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle credit score input step"""
        try:
            # Extract credit score from message
            score = self.extract_number(user_message)
            if score is None:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='credit score'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate credit score
            is_valid, message = self.validator.validate_credit_score(score)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'credit_score', str(score), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot',
                    'endInteraction': True
                }
            
            # Store credit score and advance
            session.user_data.credit_score = score
            session.set_step(ConversationStep.DOCUMENTS)
            
            return {
                'fulfillmentText': self.messages['documents_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_documents_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle documents input step"""
        try:
            # Extract document types from message
            documents = self.extract_documents(user_message)
            
            # Validate documents
            is_valid, message = self.validator.validate_documents(documents)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'documents', str(documents), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot',
                    'endInteraction': True
                }
            
            # Store documents and advance
            session.user_data.documents = documents
            session.set_step(ConversationStep.PAN_VERIFICATION)
            
            return {
                'fulfillmentText': self.messages['pan_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_pan_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle PAN input step"""
        try:
            # Extract PAN from message
            pan = self.extract_pan(user_message)
            if not pan:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='PAN number'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate PAN
            is_valid, message = self.validator.validate_pan(pan)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'pan', pan, message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Store PAN and advance
            session.user_data.pan_number = pan
            session.set_step(ConversationStep.LOAN_AMOUNT)
            
            return {
                'fulfillmentText': self.messages['loan_amount_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_loan_amount_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle loan amount input step"""
        try:
            # Extract amount from message
            amount = self.extract_number(user_message)
            if amount is None:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='loan amount'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate loan amount
            is_valid, message = self.validator.validate_loan_amount(amount)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'loan_amount', str(amount), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot',
                    'endInteraction': True
                }
            
            # Store loan amount and advance
            session.user_data.loan_amount = amount
            session.set_step(ConversationStep.TENURE)
            
            return {
                'fulfillmentText': self.messages['tenure_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_tenure_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle tenure input step"""
        try:
            # Extract tenure from message
            tenure = self.extract_number(user_message)
            if tenure is None:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='tenure'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate tenure
            is_valid, message = self.validator.validate_tenure(tenure)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'tenure', str(tenure), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Store tenure and advance
            session.user_data.tenure_months = tenure
            session.set_step(ConversationStep.INCOME)
            
            return {
                'fulfillmentText': self.messages['income_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_income_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle income input step"""
        try:
            # Extract income from message
            income = self.extract_number(user_message)
            if income is None:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='income'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate income
            is_valid, message = self.validator.validate_income(float(income))
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'income', str(income), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot',
                    'endInteraction': True
                }
            
            # Store income and advance
            session.user_data.monthly_income = float(income)
            session.set_step(ConversationStep.EXPENSES)
            
            return {
                'fulfillmentText': self.messages['expenses_prompt'],
                'source': 'paisalo-adk-chatbot'
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_expenses_input(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Handle expenses input step"""
        try:
            # Extract expenses from message
            expenses = self.extract_number(user_message)
            if expenses is None:
                return {
                    'fulfillmentText': self.messages['invalid_input'].format(field='expenses'),
                    'source': 'paisalo-adk-chatbot'
                }
            
            # Validate expenses
            is_valid, message = self.validator.validate_expenses(float(expenses), session.user_data.monthly_income)
            
            if not is_valid:
                self.logger.log_validation_error(session.session_id, 'expenses', str(expenses), message)
                return {
                    'fulfillmentText': message,
                    'source': 'paisalo-adk-chatbot',
                    'endInteraction': True
                }
            
            # Store expenses and process loan
            session.user_data.monthly_expenses = float(expenses)
            
            # Calculate loan eligibility
            loan_result = self.calculate_loan_eligibility(session.user_data)
            session.loan_result = loan_result
            session.set_step(ConversationStep.COMPLETED)
            
            # Log decision
            self.logger.log_loan_decision(
                session.session_id, 
                loan_result.status.value, 
                loan_result.rejection_reason
            )
            
            # Generate response
            if loan_result.status == LoanStatus.APPROVED:
                response_text = self.messages['approved'].format(
                    amount=loan_result.amount,
                    tenure=loan_result.tenure_months,
                    roi=loan_result.roi_percentage,
                    emi=loan_result.monthly_emi
                )
            else:
                response_text = self.messages['rejected'].format(
                    reason=loan_result.rejection_reason
                )
            
            return {
                'fulfillmentText': response_text,
                'source': 'paisalo-adk-chatbot',
                'endInteraction': True
            }
            
        except Exception as error:
            self.logger.log_error(session.session_id, error)
            return {
                'fulfillmentText': self.messages['error'],
                'source': 'paisalo-adk-chatbot'
            }
    
    def handle_completed(self, session: ChatSession) -> Dict[str, Any]:
        """Handle completed conversation"""
        return {
            'fulfillmentText': "Your loan application has been processed. Say 'hello' to start a new application.",
            'source': 'paisalo-adk-chatbot'
        }
    
    def calculate_loan_eligibility(self, user_data: UserData) -> LoanResult:
        """Calculate final loan eligibility"""
        try:
            # All validations should have passed by now, but double-check
            
            # Calculate EMI
            emi = self.validator.calculate_emi(
                user_data.loan_amount, 
                user_data.tenure_months
            )
            
            roi = self.validator.get_roi_for_tenure(user_data.tenure_months)
            
            return LoanResult(
                status=LoanStatus.APPROVED,
                amount=user_data.loan_amount,
                tenure_months=user_data.tenure_months,
                roi_percentage=roi,
                monthly_emi=emi
            )
            
        except Exception as error:
            return LoanResult(
                status=LoanStatus.REJECTED,
                rejection_reason=f"Error in loan calculation: {str(error)}"
            )
    
    def extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        # Remove common currency symbols and commas
        cleaned = re.sub(r'[₹,\s]', '', text)
        
        # Find numbers in text
        numbers = re.findall(r'\d+', cleaned)
        
        if numbers:
            return int(numbers[0])
        
        return None
    
    def extract_documents(self, text: str) -> List[str]:
        """Extract document types from text"""
        documents = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['pan', 'pancard', 'pan card']):
            documents.append('pan')
        
        if any(word in text_lower for word in ['voter', 'voter id', 'voter card']):
            documents.append('voter_id')
        
        if any(word in text_lower for word in ['dl', 'driving license', 'driving licence', 'license']):
            documents.append('driving_license')
        
        return documents
    
    def extract_pan(self, text: str) -> Optional[str]:
        """Extract PAN number from text"""
        # PAN pattern: 5 letters, 4 digits, 1 letter
        pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
        
        # Convert to uppercase and remove spaces
        cleaned = re.sub(r'\s+', '', text.upper())
        
        match = re.search(pan_pattern, cleaned)
        if match:
            return match.group(0)
        
        return None
    
    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        # Clean up expired sessions
        self.cleanup_expired_sessions()
        
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.update_activity()
            return session
        
        # Create new session
        session = ChatSession(session_id=session_id)
        self.sessions[session_id] = session
        
        return session
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.logger.log_session_cleanup(session_id, "expired")
            del self.sessions[session_id]
        
        # Also limit total sessions
        if len(self.sessions) > self.max_sessions:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.sessions.items(), 
                key=lambda x: x[1].last_activity
            )
            
            sessions_to_remove = len(self.sessions) - self.max_sessions
            for i in range(sessions_to_remove):
                session_id = sorted_sessions[i][0]
                self.logger.log_session_cleanup(session_id, "capacity_limit")
                del self.sessions[session_id]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id in self.sessions:
            return self.sessions[session_id].to_dict()
        return None
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        self.cleanup_expired_sessions()
        return [session.to_dict() for session in self.sessions.values()]

