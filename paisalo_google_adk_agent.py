#!/usr/bin/env python3.13
"""
Paisalo Google ADK Agent
Loan Processing System for Android Integration

Company: Paisalo
Business Rules Implementation:
- Age: 21-57 years
- Credit Score: <18 or >650 (OK), otherwise NO
- Documents: (Voter + PAN) OR (PAN + DL)
- PAN Validation: Regex pattern
- Loan Amount: 50,000 - 100,000
- Expense Ratio: ≤50% of total income
- EMI: SLM method with ROI mapping
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoanStatus(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass
class LoanRequest:
    """Loan request data structure"""
    age: int
    credit_score: int
    income: float
    expense: float
    family_income: float
    family_expense: float
    documents: List[str]
    pan_number: str
    loan_amount: float
    tenure_months: int

@dataclass
class LoanResponse:
    """Loan response data structure"""
    status: str
    message: str
    emi: Optional[float] = None
    roi: Optional[float] = None
    total_amount: Optional[float] = None
    monthly_emi: Optional[float] = None

class PaisaloGoogleADKAgent:
    """
    Paisalo Google ADK Agent for Loan Processing
    Implements all business rules for loan eligibility
    """
    
    # Company Information
    COMPANY_NAME = "Paisalo"
    
    # Business Rules Constants
    MIN_AGE = 21
    MAX_AGE = 57
    MIN_CREDIT_SCORE = 18
    MAX_CREDIT_SCORE = 650
    MIN_LOAN_AMOUNT = 50000
    MAX_LOAN_AMOUNT = 100000
    MAX_EXPENSE_RATIO = 50  # 50%
    
    # ROI Mapping based on tenure
    ROI_RATES = {
        12: 7,   # 7% for 12 months
        24: 9,   # 9% for 24 months
        36: 12,  # 12% for 36 months
        48: 18   # 18% for 48 months
    }
    
    # PAN Number Regex Pattern (AAAAA9999A)
    PAN_PATTERN = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    # Valid Document Combinations
    VALID_DOC_COMBINATIONS = [
        {"VOTER", "PAN"},
        {"PAN", "DL"}
    ]
    
    def __init__(self):
        """Initialize Paisalo Google ADK Agent"""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for Android ADK
        self.setup_routes()
        logger.info(f"{self.COMPANY_NAME} Google ADK Agent initialized")
    
    def validate_age(self, age: int) -> Tuple[bool, str]:
        """Validate user age (21-57 years)"""
        if self.MIN_AGE <= age <= self.MAX_AGE:
            return True, f"Age {age} is valid"
        return False, f"Age must be between {self.MIN_AGE} and {self.MAX_AGE} years"
    
    def validate_credit_score(self, score: int) -> Tuple[bool, str]:
        """Validate credit score (<18 or >650 = OK)"""
        if score < self.MIN_CREDIT_SCORE or score > self.MAX_CREDIT_SCORE:
            return True, f"Credit score {score} is acceptable"
        return False, f"Credit score {score} is not acceptable. Must be <{self.MIN_CREDIT_SCORE} or >{self.MAX_CREDIT_SCORE}"
    
    def validate_documents(self, documents: List[str]) -> Tuple[bool, str]:
        """Validate document combination (Voter+PAN or PAN+DL)"""
        doc_set = set(doc.upper() for doc in documents)
        
        for valid_combo in self.VALID_DOC_COMBINATIONS:
            if valid_combo.issubset(doc_set):
                return True, f"Valid documents: {', '.join(valid_combo)}"
        
        return False, "Invalid documents. Required: (Voter ID + PAN) OR (PAN + Driving License)"
    
    def validate_pan(self, pan: str) -> Tuple[bool, str]:
        """Validate PAN using regex pattern"""
        if not pan:
            return False, "PAN number is required"
        
        if re.match(self.PAN_PATTERN, pan.upper()):
            return True, f"PAN {pan} is valid"
        return False, f"Invalid PAN format. Required: AAAAA9999A (5 letters + 4 digits + 1 letter)"
    
    def validate_loan_amount(self, amount: float) -> Tuple[bool, str]:
        """Validate loan amount (50,000 - 100,000)"""
        if self.MIN_LOAN_AMOUNT <= amount <= self.MAX_LOAN_AMOUNT:
            return True, f"Loan amount ₹{amount:,.0f} is valid"
        return False, f"Loan amount must be between ₹{self.MIN_LOAN_AMOUNT:,} and ₹{self.MAX_LOAN_AMOUNT:,}"
    
    def validate_expense_ratio(self, income: float, expense: float, 
                             family_income: float, family_expense: float) -> Tuple[bool, str]:
        """Validate expense ratio (≤50% of total income)"""
        total_income = income + family_income
        total_expense = expense + family_expense
        
        if total_income <= 0:
            return False, "Total income must be greater than 0"
        
        expense_ratio = (total_expense / total_income) * 100
        
        if expense_ratio <= self.MAX_EXPENSE_RATIO:
            return True, f"Expense ratio {expense_ratio:.1f}% is acceptable"
        return False, f"Expense ratio {expense_ratio:.1f}% exceeds {self.MAX_EXPENSE_RATIO}% limit"
    
    def calculate_emi_slm(self, principal: float, roi: float, tenure_months: int) -> float:
        """
        Calculate EMI using SLM (Simple Interest Method)
        Formula: EMI = (Principal + Simple Interest) / Tenure
        Simple Interest = (Principal × ROI × Time) / 100
        """
        # Convert tenure to years for interest calculation
        time_years = tenure_months / 12
        
        # Calculate simple interest
        simple_interest = (principal * roi * time_years) / 100
        
        # Total amount to be paid
        total_amount = principal + simple_interest
        
        # Monthly EMI
        emi = total_amount / tenure_months
        
        return round(emi, 2)
    
    def process_loan_application(self, loan_request: LoanRequest) -> LoanResponse:
        """Process complete loan application with all validations"""
        
        # Step 1: Validate Age
        age_valid, age_msg = self.validate_age(loan_request.age)
        if not age_valid:
            return LoanResponse(LoanStatus.REJECTED.value, age_msg)
        
        # Step 2: Validate Credit Score
        credit_valid, credit_msg = self.validate_credit_score(loan_request.credit_score)
        if not credit_valid:
            return LoanResponse(LoanStatus.REJECTED.value, credit_msg)
        
        # Step 3: Validate Documents
        doc_valid, doc_msg = self.validate_documents(loan_request.documents)
        if not doc_valid:
            return LoanResponse(LoanStatus.REJECTED.value, doc_msg)
        
        # Step 4: Validate PAN
        pan_valid, pan_msg = self.validate_pan(loan_request.pan_number)
        if not pan_valid:
            return LoanResponse(LoanStatus.REJECTED.value, pan_msg)
        
        # Step 5: Validate Loan Amount
        amount_valid, amount_msg = self.validate_loan_amount(loan_request.loan_amount)
        if not amount_valid:
            return LoanResponse(LoanStatus.REJECTED.value, amount_msg)
        
        # Step 6: Validate Expense Ratio
        expense_valid, expense_msg = self.validate_expense_ratio(
            loan_request.income, loan_request.expense,
            loan_request.family_income, loan_request.family_expense
        )
        if not expense_valid:
            return LoanResponse(LoanStatus.REJECTED.value, expense_msg)
        
        # Step 7: Get ROI for tenure
        roi = self.ROI_RATES.get(loan_request.tenure_months)
        if roi is None:
            available_tenures = list(self.ROI_RATES.keys())
            return LoanResponse(
                LoanStatus.REJECTED.value,
                f"Invalid tenure {loan_request.tenure_months} months. Available: {available_tenures}"
            )
        
        # Step 8: Calculate EMI
        emi = self.calculate_emi_slm(loan_request.loan_amount, roi, loan_request.tenure_months)
        total_amount = emi * loan_request.tenure_months
        
        # Loan Approved
        return LoanResponse(
            status=LoanStatus.APPROVED.value,
            message="Loan approved successfully",
            emi=emi,
            roi=roi,
            total_amount=total_amount,
            monthly_emi=emi
        )
    
    def setup_routes(self):
        """Setup Google ADK API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check for Google ADK"""
            return jsonify({
                "status": "healthy",
                "service": f"{self.COMPANY_NAME} Google ADK Agent",
                "version": "1.0.0"
            })
        
        @self.app.route('/api/loan/process', methods=['POST'])
        def process_loan():
            """Main loan processing endpoint for Google ADK"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "status": "error",
                        "message": "No data provided"
                    }), 400
                
                # Create loan request object
                loan_request = LoanRequest(
                    age=data.get('age'),
                    credit_score=data.get('credit_score'),
                    income=data.get('income', 0),
                    expense=data.get('expense', 0),
                    family_income=data.get('family_income', 0),
                    family_expense=data.get('family_expense', 0),
                    documents=data.get('documents', []),
                    pan_number=data.get('pan_number', ''),
                    loan_amount=data.get('loan_amount'),
                    tenure_months=data.get('tenure_months')
                )
                
                # Process loan application
                result = self.process_loan_application(loan_request)
                
                return jsonify({
                    "status": "success",
                    "data": asdict(result),
                    "company": self.COMPANY_NAME
                })
                
            except Exception as e:
                logger.error(f"Error processing loan: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Processing error: {str(e)}"
                }), 500
        
        @self.app.route('/api/loan/calculate-emi', methods=['POST'])
        def calculate_emi():
            """Calculate EMI for Google ADK"""
            try:
                data = request.get_json()
                
                principal = data.get('principal')
                tenure = data.get('tenure_months')
                
                if not principal or not tenure:
                    return jsonify({
                        "status": "error",
                        "message": "Principal and tenure are required"
                    }), 400
                
                roi = self.ROI_RATES.get(tenure)
                if roi is None:
                    return jsonify({
                        "status": "error",
                        "message": f"Invalid tenure. Available: {list(self.ROI_RATES.keys())}"
                    }), 400
                
                emi = self.calculate_emi_slm(principal, roi, tenure)
                total_amount = emi * tenure
                interest = total_amount - principal
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "principal": principal,
                        "tenure_months": tenure,
                        "roi_percent": roi,
                        "monthly_emi": emi,
                        "total_amount": total_amount,
                        "total_interest": interest
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/validate/pan', methods=['POST'])
        def validate_pan_endpoint():
            """PAN validation endpoint for Google ADK"""
            try:
                data = request.get_json()
                pan = data.get('pan_number', '')
                
                is_valid, message = self.validate_pan(pan)
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "pan_number": pan,
                        "is_valid": is_valid,
                        "message": message
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/loan/rules', methods=['GET'])
        def get_loan_rules():
            """Get all loan rules for Google ADK"""
            return jsonify({
                "status": "success",
                "data": {
                    "company": self.COMPANY_NAME,
                    "age_range": {"min": self.MIN_AGE, "max": self.MAX_AGE},
                    "credit_score_rule": f"Must be <{self.MIN_CREDIT_SCORE} or >{self.MAX_CREDIT_SCORE}",
                    "loan_amount_range": {"min": self.MIN_LOAN_AMOUNT, "max": self.MAX_LOAN_AMOUNT},
                    "expense_ratio_limit": f"≤{self.MAX_EXPENSE_RATIO}%",
                    "roi_rates": self.ROI_RATES,
                    "valid_documents": ["(Voter ID + PAN)", "(PAN + Driving License)"],
                    "pan_format": "AAAAA9999A",
                    "emi_method": "SLM (Simple Interest Method)"
                }
            })
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Google ADK Agent server"""
        logger.info(f"Starting {self.COMPANY_NAME} Google ADK Agent on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Example usage and testing
def test_loan_application():
    """Test the loan application with sample data"""
    agent = PaisaloGoogleADKAgent()
    
    # Sample loan request
    sample_request = LoanRequest(
        age=35,
        credit_score=700,  # >650, so valid
        income=60000,
        expense=25000,
        family_income=40000,
        family_expense=15000,  # Total expense: 40000, Total income: 100000, Ratio: 40%
        documents=["VOTER", "PAN"],
        pan_number="ABCDE1234F",
        loan_amount=75000,
        tenure_months=24
    )
    
    result = agent.process_loan_application(sample_request)
    
    print(f"\n🏦 {agent.COMPANY_NAME} Loan Processing Result:")
    print("=" * 50)
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    
    if result.status == LoanStatus.APPROVED.value:
        print(f"💰 Monthly EMI: ₹{result.emi:,.2f}")
        print(f"📊 ROI: {result.roi}%")
        print(f"💳 Total Amount: ₹{result.total_amount:,.2f}")
    
    return result

def main():
    """Main function to run Google ADK Agent"""
    print(f"🚀 Starting {PaisaloGoogleADKAgent.COMPANY_NAME} Google ADK Agent")
    print("=" * 60)
    
    # Test the loan processing
    test_result = test_loan_application()
    
    # Start the server
    agent = PaisaloGoogleADKAgent()
    agent.run(debug=True)

if __name__ == "__main__":
    main()
