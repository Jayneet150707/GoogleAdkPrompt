#!/usr/bin/env python3.13
"""
Paisalo Loan Eligibility Agent
Google ADK Integration for Loan Processing

Company: Paisalo
Author: Codegen Agent
Python Version: 3.13
"""

import re
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoanStatus(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"

class DocumentType(Enum):
    PAN = "PAN"
    VOTER_ID = "VOTER_ID"
    DRIVING_LICENSE = "DL"

@dataclass
class UserProfile:
    """User profile data structure"""
    age: int
    credit_score: int
    income: float
    expense: float
    family_income: float
    family_expense: float
    documents: List[str]
    pan_number: Optional[str] = None

@dataclass
class LoanApplication:
    """Loan application data structure"""
    amount: float
    tenure_months: int
    user_profile: UserProfile

@dataclass
class LoanResult:
    """Loan processing result"""
    status: LoanStatus
    reason: str
    emi: Optional[float] = None
    roi: Optional[float] = None
    total_amount: Optional[float] = None

class PaisaloLoanAgent:
    """
    Paisalo Loan Processing Agent
    Implements all business rules for loan eligibility
    """
    
    COMPANY_NAME = "Paisalo"
    
    # Age limits
    MIN_AGE = 21
    MAX_AGE = 57
    
    # Credit score limits
    MIN_CREDIT_SCORE = 18
    MAX_CREDIT_SCORE = 650
    
    # Loan amount limits
    MIN_LOAN_AMOUNT = 50000
    MAX_LOAN_AMOUNT = 100000
    
    # ROI based on tenure
    ROI_MAPPING = {
        12: 7.0,   # 7% for 12 months
        24: 9.0,   # 9% for 24 months
        36: 12.0,  # 12% for 36 months
        48: 18.0   # 18% for 48 months
    }
    
    # PAN number regex pattern
    PAN_REGEX = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    # Required document combinations
    VALID_DOC_COMBINATIONS = [
        {DocumentType.VOTER_ID.value, DocumentType.PAN.value},
        {DocumentType.PAN.value, DocumentType.DRIVING_LICENSE.value}
    ]
    
    def __init__(self):
        """Initialize the Paisalo Loan Agent"""
        logger.info(f"Initializing {self.COMPANY_NAME} Loan Agent")
    
    def validate_age(self, age: int) -> Tuple[bool, str]:
        """
        Validate user age
        Rule: Age must be between 21 to 57 (inclusive)
        """
        if self.MIN_AGE <= age <= self.MAX_AGE:
            return True, f"Age {age} is valid"
        return False, f"Age {age} is invalid. Must be between {self.MIN_AGE} and {self.MAX_AGE}"
    
    def validate_credit_score(self, credit_score: int) -> Tuple[bool, str]:
        """
        Validate credit score
        Rule: Credit score must be >= 18 or <= 650
        """
        if credit_score >= self.MIN_CREDIT_SCORE or credit_score <= self.MAX_CREDIT_SCORE:
            return True, f"Credit score {credit_score} is valid"
        return False, f"Credit score {credit_score} is invalid. Must be >= {self.MIN_CREDIT_SCORE} or <= {self.MAX_CREDIT_SCORE}"
    
    def validate_documents(self, documents: List[str]) -> Tuple[bool, str]:
        """
        Validate document combination
        Rule: User must have (Voter ID + PAN) OR (PAN + DL)
        """
        doc_set = set(documents)
        
        for valid_combination in self.VALID_DOC_COMBINATIONS:
            if valid_combination.issubset(doc_set):
                return True, f"Valid document combination: {', '.join(valid_combination)}"
        
        return False, "Invalid document combination. Required: (Voter ID + PAN) OR (PAN + DL)"
    
    def validate_pan_number(self, pan_number: str) -> Tuple[bool, str]:
        """
        Validate PAN number using regex
        Rule: PAN format should be AAAAA9999A
        """
        if not pan_number:
            return False, "PAN number is required"
        
        if re.match(self.PAN_REGEX, pan_number.upper()):
            return True, f"PAN number {pan_number} is valid"
        return False, f"PAN number {pan_number} is invalid. Format should be AAAAA9999A"
    
    def validate_loan_amount(self, amount: float) -> Tuple[bool, str]:
        """
        Validate loan amount
        Rule: Amount must be between 50,000 and 1,00,000
        """
        if self.MIN_LOAN_AMOUNT <= amount <= self.MAX_LOAN_AMOUNT:
            return True, f"Loan amount ₹{amount:,.2f} is valid"
        return False, f"Loan amount ₹{amount:,.2f} is invalid. Must be between ₹{self.MIN_LOAN_AMOUNT:,} and ₹{self.MAX_LOAN_AMOUNT:,}"
    
    def validate_expense_ratio(self, income: float, expense: float, family_income: float, family_expense: float) -> Tuple[bool, str]:
        """
        Validate expense ratio
        Rule: User's expense should not be more than 50% of income
        """
        total_income = income + family_income
        total_expense = expense + family_expense
        
        if total_income <= 0:
            return False, "Total income must be greater than 0"
        
        expense_ratio = (total_expense / total_income) * 100
        
        if expense_ratio <= 50:
            return True, f"Expense ratio {expense_ratio:.2f}% is acceptable"
        return False, f"Expense ratio {expense_ratio:.2f}% exceeds 50% limit"
    
    def get_roi_for_tenure(self, tenure_months: int) -> Optional[float]:
        """
        Get ROI based on tenure
        """
        return self.ROI_MAPPING.get(tenure_months)
    
    def calculate_emi_slm(self, principal: float, roi: float, tenure_months: int) -> float:
        """
        Calculate EMI using SLM (Simple Interest Method)
        Formula: EMI = (P + (P * R * T / 100)) / T
        Where:
        P = Principal amount
        R = Rate of interest per annum
        T = Tenure in months
        """
        # Convert annual ROI to monthly and calculate simple interest
        total_interest = (principal * roi * (tenure_months / 12)) / 100
        total_amount = principal + total_interest
        emi = total_amount / tenure_months
        
        return round(emi, 2)
    
    def process_loan_application(self, application: LoanApplication) -> LoanResult:
        """
        Process complete loan application
        """
        logger.info(f"Processing loan application for amount: ₹{application.amount:,.2f}")
        
        user = application.user_profile
        
        # Step 1: Validate age
        age_valid, age_msg = self.validate_age(user.age)
        if not age_valid:
            return LoanResult(LoanStatus.REJECTED, age_msg)
        
        # Step 2: Validate credit score
        credit_valid, credit_msg = self.validate_credit_score(user.credit_score)
        if not credit_valid:
            return LoanResult(LoanStatus.REJECTED, credit_msg)
        
        # Step 3: Validate documents
        doc_valid, doc_msg = self.validate_documents(user.documents)
        if not doc_valid:
            return LoanResult(LoanStatus.REJECTED, doc_msg)
        
        # Step 4: Validate PAN if provided
        if user.pan_number:
            pan_valid, pan_msg = self.validate_pan_number(user.pan_number)
            if not pan_valid:
                return LoanResult(LoanStatus.REJECTED, pan_msg)
        
        # Step 5: Validate loan amount
        amount_valid, amount_msg = self.validate_loan_amount(application.amount)
        if not amount_valid:
            return LoanResult(LoanStatus.REJECTED, amount_msg)
        
        # Step 6: Validate expense ratio
        expense_valid, expense_msg = self.validate_expense_ratio(
            user.income, user.expense, user.family_income, user.family_expense
        )
        if not expense_valid:
            return LoanResult(LoanStatus.REJECTED, expense_msg)
        
        # Step 7: Get ROI for tenure
        roi = self.get_roi_for_tenure(application.tenure_months)
        if roi is None:
            return LoanResult(
                LoanStatus.REJECTED, 
                f"Invalid tenure {application.tenure_months} months. Available: {list(self.ROI_MAPPING.keys())}"
            )
        
        # Step 8: Calculate EMI
        emi = self.calculate_emi_slm(application.amount, roi, application.tenure_months)
        total_amount = emi * application.tenure_months
        
        return LoanResult(
            status=LoanStatus.APPROVED,
            reason="All eligibility criteria met",
            emi=emi,
            roi=roi,
            total_amount=total_amount
        )
    
    def generate_loan_summary(self, application: LoanApplication, result: LoanResult) -> Dict:
        """
        Generate comprehensive loan summary
        """
        summary = {
            "company": self.COMPANY_NAME,
            "application": {
                "loan_amount": application.amount,
                "tenure_months": application.tenure_months,
                "applicant_age": application.user_profile.age,
                "credit_score": application.user_profile.credit_score,
                "documents": application.user_profile.documents,
                "pan_number": application.user_profile.pan_number
            },
            "result": {
                "status": result.status.value,
                "reason": result.reason,
                "emi": result.emi,
                "roi": result.roi,
                "total_amount": result.total_amount
            },
            "financial_details": {
                "income": application.user_profile.income,
                "expense": application.user_profile.expense,
                "family_income": application.user_profile.family_income,
                "family_expense": application.user_profile.family_expense,
                "total_income": application.user_profile.income + application.user_profile.family_income,
                "total_expense": application.user_profile.expense + application.user_profile.family_expense
            }
        }
        
        if result.status == LoanStatus.APPROVED:
            summary["emi_breakdown"] = {
                "monthly_emi": result.emi,
                "total_interest": result.total_amount - application.amount,
                "total_payable": result.total_amount,
                "roi_percent": result.roi
            }
        
        return summary

def main():
    """
    Main function to demonstrate the Paisalo Loan Agent
    """
    print(f"🏦 Welcome to {PaisaloLoanAgent.COMPANY_NAME} Loan Processing System")
    print("=" * 60)
    
    # Initialize the agent
    agent = PaisaloLoanAgent()
    
    # Example loan application
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
    
    # Process the application
    result = agent.process_loan_application(loan_application)
    
    # Generate summary
    summary = agent.generate_loan_summary(loan_application, result)
    
    # Display results
    print(json.dumps(summary, indent=2))
    
    if result.status == LoanStatus.APPROVED:
        print(f"\n✅ LOAN APPROVED!")
        print(f"💰 EMI: ₹{result.emi:,.2f}")
        print(f"📊 ROI: {result.roi}%")
        print(f"💳 Total Amount: ₹{result.total_amount:,.2f}")
    else:
        print(f"\n❌ LOAN REJECTED!")
        print(f"📝 Reason: {result.reason}")

if __name__ == "__main__":
    main()
