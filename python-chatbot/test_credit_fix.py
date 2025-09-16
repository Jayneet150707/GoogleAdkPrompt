#!/usr/bin/env python3
"""
Quick test to verify credit score validation fix
"""

import re
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field

@dataclass
class LoanRules:
    """Paisalo loan business rules"""
    MIN_AGE: int = 21
    MAX_AGE: int = 57
    MIN_CREDIT_SCORE: int = 18
    MAX_CREDIT_SCORE: int = 650

class LoanValidator:
    """Loan eligibility validation utilities"""
    
    def __init__(self, rules: LoanRules):
        self.rules = rules
    
    def validate_credit_score(self, score: int) -> Tuple[bool, str]:
        """Validate credit score - ELIGIBLE if score < 18 OR score > 650"""
        if not isinstance(score, int) or score < 0:
            return False, "Please provide a valid credit score"
        
        # Credit score is ELIGIBLE if < 18 OR > 650
        # Credit score is NOT ELIGIBLE if between 18-650 (inclusive)
        if score < self.rules.MIN_CREDIT_SCORE or score > self.rules.MAX_CREDIT_SCORE:
            return True, f"Credit score {score} is eligible (outside 18-650 range)"
        
        return False, f"Credit score {score} is not eligible. Score must be less than 18 or greater than 650"

def test_credit_score_validation():
    """Test the fixed credit score validation"""
    validator = LoanValidator(LoanRules())
    
    print("🧪 Testing Credit Score Validation Fix")
    print("=" * 50)
    
    # Test cases that should be ELIGIBLE (< 18 or > 650)
    print("✅ ELIGIBLE Scores (< 18 or > 650):")
    eligible_scores = [0, 5, 10, 17, 651, 700, 800, 1000]
    for score in eligible_scores:
        is_valid, message = validator.validate_credit_score(score)
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"  Score {score:4d}: {status} - {message}")
    
    print("\n❌ NOT ELIGIBLE Scores (18-650 inclusive):")
    # Test cases that should be NOT ELIGIBLE (18-650 inclusive)
    not_eligible_scores = [18, 50, 100, 300, 500, 650]
    for score in not_eligible_scores:
        is_valid, message = validator.validate_credit_score(score)
        status = "✅ PASS" if not is_valid else "❌ FAIL"
        print(f"  Score {score:4d}: {status} - {message}")
    
    print("\n🔍 Edge Cases:")
    # Test edge cases
    edge_cases = [-10, -1]
    for score in edge_cases:
        is_valid, message = validator.validate_credit_score(score)
        status = "✅ PASS" if not is_valid else "❌ FAIL"
        print(f"  Score {score:4d}: {status} - {message}")
    
    print("\n🎯 Summary:")
    print("- Scores < 18: ELIGIBLE for loan")
    print("- Scores > 650: ELIGIBLE for loan") 
    print("- Scores 18-650: NOT ELIGIBLE for loan")
    print("- Negative scores: Invalid format")

if __name__ == '__main__':
    test_credit_score_validation()

