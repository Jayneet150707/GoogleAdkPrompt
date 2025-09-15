#!/usr/bin/env python3.13
"""
Test Suite for Paisalo Loan Chatbot - Python 3.13
Comprehensive testing for all business rules and functionality

Author: Codegen for Paisalo Digital Limited
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from paisalo_chatbot import (
    PaisaloChatbot, LoanRules, LoanValidator, EMICalculator, 
    PANValidator, UserProfile, UserSession, ConversationStep
)

class TestLoanRules:
    """Test loan business rules"""
    
    def test_loan_rules_initialization(self):
        """Test loan rules are properly initialized"""
        rules = LoanRules()
        
        assert rules.MIN_AGE == 21
        assert rules.MAX_AGE == 57
        assert rules.MIN_CREDIT_SCORE == 18
        assert rules.MAX_CREDIT_SCORE == 650
        assert rules.MIN_LOAN_AMOUNT == 50000
        assert rules.MAX_LOAN_AMOUNT == 100000
        assert rules.MAX_EXPENSE_PERCENTAGE == 50.0
        
        # Test ROI rates
        expected_roi = {12: 7.0, 24: 9.0, 36: 12.0, 48: 18.0}
        assert rules.ROI_RATES == expected_roi
        
        # Test valid tenures
        assert rules.VALID_TENURES == [12, 24, 36, 48]

class TestPANValidator:
    """Test PAN validation functionality"""
    
    def test_valid_pan_formats(self):
        """Test valid PAN number formats"""
        valid_pans = [
            "ABCDE1234F",
            "XYZAB9876C",
            "PQRST5432M"
        ]
        
        for pan in valid_pans:
            is_valid, message = PANValidator.validate_pan_format(pan)
            assert is_valid, f"PAN {pan} should be valid"
            assert "Valid PAN format" in message
    
    def test_invalid_pan_formats(self):
        """Test invalid PAN number formats"""
        invalid_pans = [
            "ABCD1234F",      # Only 4 letters at start
            "ABCDE123F",      # Only 3 digits
            "ABCDE12345",     # No letter at end
            "12345ABCDF",     # Numbers at start
            "ABCDE1234FF",    # Too many characters
            "ABC1234F",       # Too short
            "",               # Empty string
            "abcde1234f"      # Lowercase (should be handled by upper())
        ]
        
        for pan in invalid_pans:
            is_valid, message = PANValidator.validate_pan_format(pan)
            if pan.lower() == "abcde1234f":
                # This should be valid after uppercase conversion
                assert is_valid
            else:
                assert not is_valid, f"PAN {pan} should be invalid"
                assert "Invalid PAN format" in message

class TestLoanValidator:
    """Test loan validation functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.rules = LoanRules()
        self.validator = LoanValidator(self.rules)
    
    def test_age_validation(self):
        """Test age validation"""
        # Valid ages
        valid_ages = [21, 25, 35, 45, 57]
        for age in valid_ages:
            is_valid, message = self.validator.validate_age(age)
            assert is_valid, f"Age {age} should be valid"
        
        # Invalid ages
        invalid_ages = [20, 58, 0, -5, 100]
        for age in invalid_ages:
            is_valid, message = self.validator.validate_age(age)
            assert not is_valid, f"Age {age} should be invalid"
    
    def test_credit_score_validation(self):
        """Test credit score validation"""
        # Valid scores
        valid_scores = [18, 100, 300, 650]
        for score in valid_scores:
            is_valid, message = self.validator.validate_credit_score(score)
            assert is_valid, f"Credit score {score} should be valid"
        
        # Invalid scores
        invalid_scores = [17, 651, -10, 1000]
        for score in invalid_scores:
            is_valid, message = self.validator.validate_credit_score(score)
            assert not is_valid, f"Credit score {score} should be invalid"
    
    def test_document_validation(self):
        """Test document combination validation"""
        # Valid combinations
        valid_combinations = [
            ['VOTER', 'PAN'],
            ['PAN', 'DL'],
            ['VOTER_ID', 'PAN'],
            ['DL', 'PAN']
        ]
        
        for docs in valid_combinations:
            is_valid, message = self.validator.validate_documents(docs)
            assert is_valid, f"Document combination {docs} should be valid"
        
        # Invalid combinations
        invalid_combinations = [
            ['VOTER'],           # Only one document
            ['DL'],              # Only one document
            ['VOTER', 'DL'],     # Missing PAN
            [],                  # No documents
            ['PASSPORT', 'PAN']  # Invalid document type
        ]
        
        for docs in invalid_combinations:
            is_valid, message = self.validator.validate_documents(docs)
            assert not is_valid, f"Document combination {docs} should be invalid"
    
    def test_loan_amount_validation(self):
        """Test loan amount validation"""
        # Valid amounts
        valid_amounts = [50000, 75000, 100000]
        for amount in valid_amounts:
            is_valid, message = self.validator.validate_loan_amount(amount)
            assert is_valid, f"Loan amount {amount} should be valid"
        
        # Invalid amounts
        invalid_amounts = [49999, 100001, 0, -5000]
        for amount in invalid_amounts:
            is_valid, message = self.validator.validate_loan_amount(amount)
            assert not is_valid, f"Loan amount {amount} should be invalid"
    
    def test_tenure_validation(self):
        """Test tenure validation"""
        # Valid tenures
        valid_tenures = [12, 24, 36, 48]
        for tenure in valid_tenures:
            is_valid, message = self.validator.validate_tenure(tenure)
            assert is_valid, f"Tenure {tenure} should be valid"
        
        # Invalid tenures
        invalid_tenures = [6, 18, 60, 0]
        for tenure in invalid_tenures:
            is_valid, message = self.validator.validate_tenure(tenure)
            assert not is_valid, f"Tenure {tenure} should be invalid"
    
    def test_income_expense_validation(self):
        """Test income to expense ratio validation"""
        # Valid ratios (expense <= 50% of income)
        valid_cases = [
            (50000, 20000),  # 40% ratio
            (100000, 50000), # 50% ratio (exactly at limit)
            (60000, 25000),  # ~41.7% ratio
        ]
        
        for income, expense in valid_cases:
            is_valid, message = self.validator.validate_income_expense_ratio(income, expense)
            assert is_valid, f"Income {income}, Expense {expense} should be valid"
        
        # Invalid ratios (expense > 50% of income)
        invalid_cases = [
            (50000, 30000),  # 60% ratio
            (40000, 25000),  # 62.5% ratio
            (0, 1000),       # Invalid income
            (50000, -1000),  # Negative expense
        ]
        
        for income, expense in invalid_cases:
            is_valid, message = self.validator.validate_income_expense_ratio(income, expense)
            assert not is_valid, f"Income {income}, Expense {expense} should be invalid"

class TestEMICalculator:
    """Test EMI calculation functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.rules = LoanRules()
        self.calculator = EMICalculator(self.rules)
    
    def test_emi_calculation_12_months(self):
        """Test EMI calculation for 12 months"""
        principal = 60000
        tenure = 12
        
        result = self.calculator.calculate_emi_slm(principal, tenure)
        
        # Expected calculation:
        # ROI = 7%, Tenure = 1 year
        # Total Interest = 60000 * 0.07 * 1 = 4200
        # Total Amount = 60000 + 4200 = 64200
        # EMI = 64200 / 12 = 5350
        
        assert result['principal'] == 60000
        assert result['roi_percentage'] == 7.0
        assert result['tenure_months'] == 12
        assert result['tenure_years'] == 1.0
        assert result['total_interest'] == 4200.0
        assert result['total_amount'] == 64200.0
        assert result['emi'] == 5350.0
    
    def test_emi_calculation_24_months(self):
        """Test EMI calculation for 24 months"""
        principal = 75000
        tenure = 24
        
        result = self.calculator.calculate_emi_slm(principal, tenure)
        
        # Expected calculation:
        # ROI = 9%, Tenure = 2 years
        # Total Interest = 75000 * 0.09 * 2 = 13500
        # Total Amount = 75000 + 13500 = 88500
        # EMI = 88500 / 24 = 3687.50
        
        assert result['principal'] == 75000
        assert result['roi_percentage'] == 9.0
        assert result['tenure_months'] == 24
        assert result['tenure_years'] == 2.0
        assert result['total_interest'] == 13500.0
        assert result['total_amount'] == 88500.0
        assert result['emi'] == 3687.5
    
    def test_emi_calculation_all_tenures(self):
        """Test EMI calculation for all valid tenures"""
        principal = 80000
        expected_results = {
            12: {'roi': 7.0, 'years': 1.0},
            24: {'roi': 9.0, 'years': 2.0},
            36: {'roi': 12.0, 'years': 3.0},
            48: {'roi': 18.0, 'years': 4.0}
        }
        
        for tenure, expected in expected_results.items():
            result = self.calculator.calculate_emi_slm(principal, tenure)
            
            assert result['principal'] == principal
            assert result['roi_percentage'] == expected['roi']
            assert result['tenure_months'] == tenure
            assert result['tenure_years'] == expected['years']
            
            # Verify calculation
            expected_interest = principal * (expected['roi'] / 100) * expected['years']
            expected_total = principal + expected_interest
            expected_emi = expected_total / tenure
            
            assert result['total_interest'] == expected_interest
            assert result['total_amount'] == expected_total
            assert result['emi'] == round(expected_emi, 2)

class TestPaisaloChatbot:
    """Test main chatbot functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.chatbot = PaisaloChatbot()
    
    def test_chatbot_initialization(self):
        """Test chatbot initialization"""
        assert self.chatbot.rules is not None
        assert self.chatbot.validator is not None
        assert self.chatbot.emi_calculator is not None
        assert self.chatbot.response_generator is not None
        assert isinstance(self.chatbot.sessions, dict)
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        with self.chatbot.app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert data['service'] == 'Paisalo Loan Chatbot'
            assert data['python_version'] == '3.13'
    
    def test_welcome_flow(self):
        """Test welcome conversation flow"""
        session_id = "test-session-123"
        
        # Test welcome intent
        mock_request = {
            'session': session_id,
            'queryResult': {
                'queryText': 'hello',
                'intent': {
                    'displayName': 'Default Welcome Intent'
                }
            }
        }
        
        response = self.chatbot.handle_webhook_request(mock_request)
        
        assert 'Welcome to Paisalo Digital Limited' in response['fulfillmentText']
        assert session_id in self.chatbot.sessions
        assert self.chatbot.sessions[session_id].step == ConversationStep.AGE
    
    def test_complete_conversation_flow(self):
        """Test complete conversation flow with valid inputs"""
        session_id = "test-complete-flow"
        
        # Step 1: Welcome
        self.chatbot.handle_webhook_request({
            'session': session_id,
            'queryResult': {
                'queryText': 'hello',
                'intent': {'displayName': 'Default Welcome Intent'}
            }
        })
        
        # Step 2: Age input
        response = self.chatbot.handle_conversation_flow("I am 30 years old", self.chatbot.sessions[session_id])
        assert "credit score" in response['fulfillmentText'].lower()
        
        # Step 3: Credit score input
        response = self.chatbot.handle_conversation_flow("My credit score is 650", self.chatbot.sessions[session_id])
        assert "documents" in response['fulfillmentText'].lower()
        
        # Step 4: Documents input
        response = self.chatbot.handle_conversation_flow("I have PAN and voter ID", self.chatbot.sessions[session_id])
        assert "PAN number" in response['fulfillmentText']
        
        # Step 5: PAN input
        response = self.chatbot.handle_conversation_flow("ABCDE1234F", self.chatbot.sessions[session_id])
        assert "loan amount" in response['fulfillmentText'].lower()
        
        # Step 6: Loan amount input
        response = self.chatbot.handle_conversation_flow("I need 75000", self.chatbot.sessions[session_id])
        assert "months" in response['fulfillmentText'].lower()
        
        # Step 7: Tenure input
        response = self.chatbot.handle_conversation_flow("24 months", self.chatbot.sessions[session_id])
        assert "income" in response['fulfillmentText'].lower()
        
        # Step 8: Income input
        response = self.chatbot.handle_conversation_flow("My income is 50000", self.chatbot.sessions[session_id])
        assert "expenses" in response['fulfillmentText'].lower()
        
        # Step 9: Expense input (final step)
        response = self.chatbot.handle_conversation_flow("My expenses are 20000", self.chatbot.sessions[session_id])
        assert "Congratulations" in response['fulfillmentText']
        assert "₹3,687.50" in response['fulfillmentText']  # Expected EMI
    
    def test_eligibility_failure_scenarios(self):
        """Test scenarios where user fails eligibility"""
        session_id = "test-failure"
        
        # Initialize session
        self.chatbot.handle_webhook_request({
            'session': session_id,
            'queryResult': {
                'queryText': 'hello',
                'intent': {'displayName': 'Default Welcome Intent'}
            }
        })
        
        # Test age failure
        response = self.chatbot.handle_conversation_flow("I am 20 years old", self.chatbot.sessions[session_id])
        assert "not eligible" in response['fulfillmentText']
        assert response.get('endInteraction', False)
    
    def test_test_endpoint(self):
        """Test the manual testing endpoint"""
        with self.chatbot.app.test_client() as client:
            # Test welcome message
            response = client.post('/test', 
                json={'message': 'hello', 'sessionId': 'test-123'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'sessionId' in data
            assert 'response' in data
            assert 'step' in data
            assert 'Welcome to Paisalo' in data['response']

class TestIntegrationScenarios:
    """Integration tests for complete user scenarios"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.chatbot = PaisaloChatbot()
    
    def test_successful_loan_application(self):
        """Test a complete successful loan application"""
        with self.chatbot.app.test_client() as client:
            session_id = "integration-test-success"
            
            # Complete conversation flow
            test_inputs = [
                "hello",
                "I am 35 years old",
                "My credit score is 600",
                "I have PAN and voter ID",
                "ABCDE1234F",
                "I need 80000",
                "36 months",
                "My income is 60000",
                "My expenses are 25000"
            ]
            
            responses = []
            for message in test_inputs:
                response = client.post('/test', 
                    json={'message': message, 'sessionId': session_id})
                data = json.loads(response.data)
                responses.append(data['response'])
            
            # Final response should contain eligibility confirmation
            final_response = responses[-1]
            assert "Congratulations" in final_response
            assert "eligible" in final_response
            assert "EMI" in final_response
    
    def test_failed_loan_application_high_expenses(self):
        """Test loan application failure due to high expenses"""
        with self.chatbot.app.test_client() as client:
            session_id = "integration-test-failure"
            
            test_inputs = [
                "hello",
                "I am 35 years old", 
                "My credit score is 600",
                "I have PAN and voter ID",
                "ABCDE1234F",
                "I need 80000",
                "36 months",
                "My income is 40000",
                "My expenses are 25000"  # 62.5% of income - should fail
            ]
            
            responses = []
            for message in test_inputs:
                response = client.post('/test',
                    json={'message': message, 'sessionId': session_id})
                data = json.loads(response.data)
                responses.append(data['response'])
            
            # Final response should indicate failure
            final_response = responses[-1]
            assert "not eligible" in final_response
            assert "expenses" in final_response.lower()

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])

