"""
Validation utilities for Paisalo loan eligibility
"""

import re
from typing import Tuple, List, Optional, Dict, Any
from src.config import Config


class LoanValidator:
    """Loan eligibility validation utilities"""
    
    def __init__(self):
        self.rules = Config.get_loan_rules()
        self.pan_pattern = re.compile(Config.get_pan_regex())
    
    def validate_age(self, age: int) -> Tuple[bool, str]:
        """
        Validate user age
        
        Args:
            age: User's age
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(age, int) or age <= 0:
            return False, "Please provide a valid age"
        
        min_age = self.rules['age']['min']
        max_age = self.rules['age']['max']
        
        if age < min_age or age > max_age:
            return False, f"Age must be between {min_age} and {max_age} years for loan eligibility"
        
        return True, f"Age {age} is eligible for loan"
    
    def validate_credit_score(self, score: int) -> Tuple[bool, str]:
        """
        Validate credit score according to Paisalo rules
        ELIGIBLE if score < 18 OR score > 650
        NOT ELIGIBLE if score is between 18-650 (inclusive)
        
        Args:
            score: Credit score
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(score, int) or score < 0:
            return False, "Please provide a valid credit score"
        
        min_threshold = self.rules['credit_score']['min_threshold']  # 18
        max_threshold = self.rules['credit_score']['max_threshold']  # 650
        
        # Credit score is ELIGIBLE if < 18 OR > 650
        # Credit score is NOT ELIGIBLE if between 18-650 (inclusive)
        if score < min_threshold or score > max_threshold:
            return True, f"Credit score {score} is eligible (outside {min_threshold}-{max_threshold} range)"
        
        return False, f"Credit score {score} is not eligible. Score must be less than {min_threshold} or greater than {max_threshold}"
    
    def validate_documents(self, documents: List[str]) -> Tuple[bool, str]:
        """
        Validate document combination
        
        Args:
            documents: List of document types
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not documents or len(documents) < 2:
            return False, "Please provide at least 2 documents"
        
        # Normalize document names
        doc_map = {
            'pan': ['pan', 'pan card', 'pancard'],
            'voter_id': ['voter', 'voter id', 'voter card', 'voterid'],
            'driving_license': ['dl', 'driving license', 'driving licence', 'license']
        }
        
        normalized_docs = []
        for doc in documents:
            doc_lower = doc.lower().strip()
            for key, variants in doc_map.items():
                if any(variant in doc_lower for variant in variants):
                    if key not in normalized_docs:
                        normalized_docs.append(key)
                    break
        
        # Check required combinations
        required_combinations = self.rules['documents']['required_combinations']
        
        for combination in required_combinations:
            if all(doc in normalized_docs for doc in combination):
                return True, f"Document combination is valid: {', '.join(combination)}"
        
        return False, "Please provide either (PAN + Voter ID) or (PAN + Driving License)"
    
    def validate_pan(self, pan: str) -> Tuple[bool, str]:
        """
        Validate PAN number format
        
        Args:
            pan: PAN number
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not pan or not isinstance(pan, str):
            return False, "Please provide a valid PAN number"
        
        pan = pan.upper().strip()
        
        if not self.pan_pattern.match(pan):
            return False, "Invalid PAN format. PAN should be in format: ABCDE1234F"
        
        return True, f"PAN {pan} is valid"
    
    def validate_loan_amount(self, amount: int) -> Tuple[bool, str]:
        """
        Validate loan amount
        
        Args:
            amount: Requested loan amount
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(amount, int) or amount <= 0:
            return False, "Please provide a valid loan amount"
        
        min_amount = self.rules['loan_amount']['min']
        max_amount = self.rules['loan_amount']['max']
        
        if amount < min_amount or amount > max_amount:
            return False, f"Loan amount must be between ₹{min_amount:,} and ₹{max_amount:,}"
        
        return True, f"Loan amount ₹{amount:,} is valid"
    
    def validate_tenure(self, tenure: int) -> Tuple[bool, str]:
        """
        Validate loan tenure
        
        Args:
            tenure: Loan tenure in months
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(tenure, int) or tenure <= 0:
            return False, "Please provide a valid tenure"
        
        valid_tenures = self.rules['tenure_options']
        
        if tenure not in valid_tenures:
            return False, f"Please select from available tenures: {', '.join(map(str, valid_tenures))} months"
        
        roi = self.rules['roi_rates'][tenure]
        return True, f"Tenure {tenure} months is valid (ROI: {roi}%)"
    
    def validate_income(self, income: float) -> Tuple[bool, str]:
        """
        Validate monthly income
        
        Args:
            income: Monthly income
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(income, (int, float)) or income <= 0:
            return False, "Please provide a valid monthly income"
        
        if income < 10000:  # Minimum income threshold
            return False, "Monthly income should be at least ₹10,000"
        
        return True, f"Monthly income ₹{income:,.2f} is valid"
    
    def validate_expenses(self, expenses: float, income: float) -> Tuple[bool, str]:
        """
        Validate monthly expenses against income
        
        Args:
            expenses: Monthly expenses
            income: Monthly income
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(expenses, (int, float)) or expenses < 0:
            return False, "Please provide valid monthly expenses"
        
        if expenses > income:
            return False, "Monthly expenses cannot exceed monthly income"
        
        expense_ratio = (expenses / income) * 100
        max_ratio = self.rules['expense_ratio']['max_percentage']
        
        if expense_ratio > max_ratio:
            return False, f"Expenses are {expense_ratio:.1f}% of income. Maximum allowed is {max_ratio}%"
        
        return True, f"Expense ratio {expense_ratio:.1f}% is acceptable"
    
    def calculate_emi(self, principal: float, tenure_months: int) -> float:
        """
        Calculate EMI using Simple Interest Method (SLM)
        
        Args:
            principal: Loan amount
            tenure_months: Loan tenure in months
            
        Returns:
            Monthly EMI amount
        """
        roi_annual = self.rules['roi_rates'][tenure_months]
        
        # Simple Interest Method calculation
        # SI = (P * R * T) / 100
        # Total Amount = P + SI
        # EMI = Total Amount / Number of months
        
        simple_interest = (principal * roi_annual * (tenure_months / 12)) / 100
        total_amount = principal + simple_interest
        emi = total_amount / tenure_months
        
        return round(emi, 2)
    
    def get_roi_for_tenure(self, tenure_months: int) -> float:
        """
        Get ROI for given tenure
        
        Args:
            tenure_months: Loan tenure in months
            
        Returns:
            ROI percentage
        """
        return self.rules['roi_rates'].get(tenure_months, 0.0)

