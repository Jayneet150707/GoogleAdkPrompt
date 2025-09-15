#!/usr/bin/env python3.13
"""
Test Suite for Paisalo Loan Agent
Comprehensive testing for all loan eligibility rules

Company: Paisalo
Author: Codegen Agent
Python Version: 3.13
"""

import pytest
import json
from paisalo_loan_agent import PaisaloLoanAgent, UserProfile, LoanApplication, LoanStatus
from google_adk_integration import GoogleADKIntegration

class TestPaisaloLoanAgent:
    """Test cases for Paisalo Loan Agent"""
    
    def setup_method(self):
        """Setup test environment"""
        self.agent = PaisaloLoanAgent()
    
    def test_age_validation_valid(self):
        """Test valid age ranges"""
        # Test minimum age
        valid, msg = self.agent.validate_age(21)
        assert valid == True
        
        # Test maximum age
        valid, msg = self.agent.validate_age(57)
        assert valid == True
        
        # Test middle age
        valid, msg = self.agent.validate_age(35)
        assert valid == True
    
    def test_age_validation_invalid(self):
        """Test invalid age ranges"""
        # Test below minimum age
        valid, msg = self.agent.validate_age(20)
        assert valid == False
        
        # Test above maximum age
        valid, msg = self.agent.validate_age(58)
        assert valid == False
    
    def test_credit_score_validation_valid(self):
        """Test valid credit scores"""
        # Test minimum credit score
        valid, msg = self.agent.validate_credit_score(18)
        assert valid == True
        
        # Test maximum credit score
        valid, msg = self.agent.validate_credit_score(650)
        assert valid == True
        
        # Test middle range
        valid, msg = self.agent.validate_credit_score(500)
        assert valid == True
    
    def test_credit_score_validation_invalid(self):
        """Test invalid credit scores"""
        # Test score in invalid range (between 18 and 650 exclusive)
        valid, msg = self.agent.validate_credit_score(700)
        assert valid == False
    
    def test_document_validation_valid(self):
        """Test valid document combinations"""
        # Test Voter ID + PAN
        valid, msg = self.agent.validate_documents(["VOTER_ID", "PAN"])
        assert valid == True
        
        # Test PAN + DL
        valid, msg = self.agent.validate_documents(["PAN", "DL"])
        assert valid == True
        
        # Test with additional documents
        valid, msg = self.agent.validate_documents(["VOTER_ID", "PAN", "DL"])
        assert valid == True
    
    def test_document_validation_invalid(self):
        """Test invalid document combinations"""
        # Test only PAN
        valid, msg = self.agent.validate_documents(["PAN"])
        assert valid == False
        
        # Test Voter ID + DL (without PAN)
        valid, msg = self.agent.validate_documents(["VOTER_ID", "DL"])
        assert valid == False
        
        # Test empty documents
        valid, msg = self.agent.validate_documents([])
        assert valid == False
    
    def test_pan_validation_valid(self):
        """Test valid PAN numbers"""
        valid_pans = [
            "ABCDE1234F",
            "AAAAA0000A",
            "ZZZZZ9999Z"
        ]
        
        for pan in valid_pans:
            valid, msg = self.agent.validate_pan_number(pan)
            assert valid == True, f"PAN {pan} should be valid"
    
    def test_pan_validation_invalid(self):
        """Test invalid PAN numbers"""
        invalid_pans = [
            "ABCDE123F",    # Too short
            "ABCDE12345F",  # Too long
            "12345ABCDF",   # Numbers at start
            "ABCDEFGHIJ",   # All letters
            "1234567890",   # All numbers
            "",             # Empty
            "abcde1234f"    # Lowercase
        ]
        
        for pan in invalid_pans:
            valid, msg = self.agent.validate_pan_number(pan)
            assert valid == False, f"PAN {pan} should be invalid"
    
    def test_loan_amount_validation_valid(self):
        """Test valid loan amounts"""
        # Test minimum amount
        valid, msg = self.agent.validate_loan_amount(50000)
        assert valid == True
        
        # Test maximum amount
        valid, msg = self.agent.validate_loan_amount(100000)
        assert valid == True
        
        # Test middle amount
        valid, msg = self.agent.validate_loan_amount(75000)
        assert valid == True
    
    def test_loan_amount_validation_invalid(self):
        """Test invalid loan amounts"""
        # Test below minimum
        valid, msg = self.agent.validate_loan_amount(49999)
        assert valid == False
        
        # Test above maximum
        valid, msg = self.agent.validate_loan_amount(100001)
        assert valid == False
    
    def test_expense_ratio_validation_valid(self):
        """Test valid expense ratios"""
        # Test 50% exactly
        valid, msg = self.agent.validate_expense_ratio(50000, 20000, 30000, 20000)
        assert valid == True
        
        # Test below 50%
        valid, msg = self.agent.validate_expense_ratio(60000, 20000, 40000, 20000)
        assert valid == True
    
    def test_expense_ratio_validation_invalid(self):
        """Test invalid expense ratios"""
        # Test above 50%
        valid, msg = self.agent.validate_expense_ratio(40000, 25000, 30000, 20000)
        assert valid == False
    
    def test_roi_mapping(self):
        """Test ROI mapping for different tenures"""
        assert self.agent.get_roi_for_tenure(12) == 7.0
        assert self.agent.get_roi_for_tenure(24) == 9.0
        assert self.agent.get_roi_for_tenure(36) == 12.0
        assert self.agent.get_roi_for_tenure(48) == 18.0
        assert self.agent.get_roi_for_tenure(60) is None  # Invalid tenure
    
    def test_emi_calculation(self):
        """Test EMI calculation using SLM method"""
        # Test case: 75000 for 24 months at 9% ROI
        principal = 75000
        roi = 9.0
        tenure = 24
        
        emi = self.agent.calculate_emi_slm(principal, roi, tenure)
        
        # Expected calculation:
        # Total interest = (75000 * 9 * 2) / 100 = 13500
        # Total amount = 75000 + 13500 = 88500
        # EMI = 88500 / 24 = 3687.5
        
        expected_emi = 3687.5
        assert emi == expected_emi
    
    def test_complete_loan_application_approved(self):
        """Test complete loan application that should be approved"""
        user_profile = UserProfile(
            age=35,
            credit_score=600,
            income=50000,
            expense=20000,
            family_income=30000,
            family_expense=10000,
            documents=["PAN", "VOTER_ID"],
            pan_number="ABCDE1234F"
        )
        
        loan_application = LoanApplication(
            amount=75000,
            tenure_months=24,
            user_profile=user_profile
        )
        
        result = self.agent.process_loan_application(loan_application)
        
        assert result.status == LoanStatus.APPROVED
        assert result.emi is not None
        assert result.roi == 9.0
        assert result.total_amount is not None
    
    def test_complete_loan_application_rejected_age(self):
        """Test loan application rejected due to age"""
        user_profile = UserProfile(
            age=20,  # Invalid age
            credit_score=600,
            income=50000,
            expense=20000,
            family_income=30000,
            family_expense=10000,
            documents=["PAN", "VOTER_ID"],
            pan_number="ABCDE1234F"
        )
        
        loan_application = LoanApplication(
            amount=75000,
            tenure_months=24,
            user_profile=user_profile
        )
        
        result = self.agent.process_loan_application(loan_application)
        
        assert result.status == LoanStatus.REJECTED
        assert "age" in result.reason.lower()
    
    def test_complete_loan_application_rejected_documents(self):
        """Test loan application rejected due to invalid documents"""
        user_profile = UserProfile(
            age=35,
            credit_score=600,
            income=50000,
            expense=20000,
            family_income=30000,
            family_expense=10000,
            documents=["VOTER_ID"],  # Missing PAN or DL
            pan_number="ABCDE1234F"
        )
        
        loan_application = LoanApplication(
            amount=75000,
            tenure_months=24,
            user_profile=user_profile
        )
        
        result = self.agent.process_loan_application(loan_application)
        
        assert result.status == LoanStatus.REJECTED
        assert "document" in result.reason.lower()
    
    def test_complete_loan_application_rejected_expense_ratio(self):
        """Test loan application rejected due to high expense ratio"""
        user_profile = UserProfile(
            age=35,
            credit_score=600,
            income=30000,
            expense=20000,
            family_income=20000,
            family_expense=20000,  # Total expense > 50% of total income
            documents=["PAN", "VOTER_ID"],
            pan_number="ABCDE1234F"
        )
        
        loan_application = LoanApplication(
            amount=75000,
            tenure_months=24,
            user_profile=user_profile
        )
        
        result = self.agent.process_loan_application(loan_application)
        
        assert result.status == LoanStatus.REJECTED
        assert "expense" in result.reason.lower()

class TestGoogleADKIntegration:
    """Test cases for Google ADK Integration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.integration = GoogleADKIntegration()
        self.client = self.integration.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Paisalo Loan Agent'
    
    def test_loan_eligibility_endpoint_success(self):
        """Test successful loan eligibility check"""
        payload = {
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
        
        response = self.client.post('/api/loan/eligibility',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert data['data']['result']['status'] == 'APPROVED'
    
    def test_loan_eligibility_endpoint_missing_data(self):
        """Test loan eligibility with missing data"""
        payload = {
            "user_profile": {
                "age": 35,
                "credit_score": 600
                # Missing required fields
            }
        }
        
        response = self.client.post('/api/loan/eligibility',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_calculate_emi_endpoint(self):
        """Test EMI calculation endpoint"""
        payload = {
            "principal": 75000,
            "tenure_months": 24
        }
        
        response = self.client.post('/api/loan/calculate-emi',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['monthly_emi'] == 3687.5
        assert data['data']['roi_percent'] == 9.0
    
    def test_validate_pan_endpoint(self):
        """Test PAN validation endpoint"""
        payload = {
            "pan_number": "ABCDE1234F"
        }
        
        response = self.client.post('/api/validate/pan',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['is_valid'] == True
    
    def test_get_loan_rules_endpoint(self):
        """Test loan rules endpoint"""
        response = self.client.get('/api/loan/rules')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'age_limits' in data['data']
        assert 'roi_mapping' in data['data']
        assert data['data']['age_limits']['min_age'] == 21
        assert data['data']['age_limits']['max_age'] == 57

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
