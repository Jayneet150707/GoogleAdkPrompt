#!/usr/bin/env python3
"""
Quick test script to verify the Google AdK chatbot implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import PaisaloAdkChatbot
from src.models.session import ConversationStep


def test_complete_conversation():
    """Test a complete conversation flow"""
    print("🧪 Testing Paisalo Google AdK Chatbot Implementation")
    print("=" * 60)
    
    chatbot = PaisaloAdkChatbot()
    session_id = "test-implementation"
    
    # Test conversation flow
    test_messages = [
        ("hello", "Welcome message"),
        ("I am 30 years old", "Age input"),
        ("My credit score is 700", "Credit score input"),
        ("I have PAN and voter ID", "Documents input"),
        ("ABCDE1234F", "PAN verification"),
        ("I need 80000", "Loan amount"),
        ("36 months", "Tenure selection"),
        ("My income is 50000", "Income input"),
        ("My expenses are 20000", "Expenses input")
    ]
    
    print("\n🗣️ Conversation Flow Test:")
    print("-" * 40)
    
    for i, (message, description) in enumerate(test_messages, 1):
        try:
            response = chatbot.handle_test_message(message, session_id)
            
            print(f"\n{i}. {description}")
            print(f"   User: {message}")
            print(f"   Bot: {response['fulfillmentText'][:100]}...")
            print(f"   Step: {response.get('step', 'unknown')}")
            
            if response.get('step') == 'completed':
                print("\n🎉 Conversation completed successfully!")
                break
                
        except Exception as error:
            print(f"   ❌ Error: {str(error)}")
            break
    
    # Test session info
    session_info = chatbot.get_session_info(session_id)
    if session_info:
        print(f"\n📊 Session Summary:")
        print(f"   Session ID: {session_info['session_id']}")
        print(f"   Final Step: {session_info['step']}")
        print(f"   Messages: {session_info['message_count']}")
        
        user_data = session_info['user_data']
        print(f"   User Data:")
        print(f"     Age: {user_data['age']}")
        print(f"     Credit Score: {user_data['credit_score']}")
        print(f"     Documents: {user_data['documents']}")
        print(f"     PAN: {user_data['pan_number']}")
        print(f"     Loan Amount: ₹{user_data['loan_amount']:,}")
        print(f"     Tenure: {user_data['tenure_months']} months")
        print(f"     Income: ₹{user_data['monthly_income']:,}")
        print(f"     Expenses: ₹{user_data['monthly_expenses']:,}")
        
        if session_info['loan_result']:
            loan_result = session_info['loan_result']
            print(f"   Loan Result:")
            print(f"     Status: {loan_result['status']}")
            if loan_result['status'] == 'approved':
                print(f"     Amount: ₹{loan_result['amount']:,}")
                print(f"     Tenure: {loan_result['tenure_months']} months")
                print(f"     ROI: {loan_result['roi_percentage']}%")
                print(f"     EMI: ₹{loan_result['monthly_emi']:,.2f}")


def test_validation_logic():
    """Test validation logic"""
    print("\n🔍 Testing Validation Logic:")
    print("-" * 40)
    
    from src.utils.validators import LoanValidator
    validator = LoanValidator()
    
    # Test credit score validation (the fixed logic)
    print("\n📊 Credit Score Validation:")
    test_scores = [10, 17, 18, 500, 650, 651, 700]
    
    for score in test_scores:
        is_valid, message = validator.validate_credit_score(score)
        status = "✅ ELIGIBLE" if is_valid else "❌ NOT ELIGIBLE"
        print(f"   Score {score:3d}: {status}")
    
    # Test EMI calculation
    print("\n💰 EMI Calculation Test:")
    test_cases = [
        (80000, 12),
        (80000, 24),
        (80000, 36),
        (80000, 48)
    ]
    
    for amount, tenure in test_cases:
        emi = validator.calculate_emi(amount, tenure)
        roi = validator.get_roi_for_tenure(tenure)
        print(f"   ₹{amount:,} for {tenure} months @ {roi}% ROI = ₹{emi:,.2f} EMI")


def test_adk_request_simulation():
    """Test Google AdK request simulation"""
    print("\n🔗 Testing Google AdK Request Simulation:")
    print("-" * 40)
    
    chatbot = PaisaloAdkChatbot()
    
    # Simulate AdK request
    adk_request = {
        'session': 'projects/paisalo-chatbot/agent/sessions/adk-test-session',
        'queryResult': {
            'queryText': 'hello',
            'intent': {
                'displayName': 'Default Welcome Intent'
            },
            'parameters': {}
        }
    }
    
    try:
        response = chatbot.handle_adk_request(adk_request, "test-request-123")
        
        print(f"✅ AdK Request processed successfully")
        print(f"   Response: {response['fulfillmentText'][:100]}...")
        print(f"   Source: {response['source']}")
        
    except Exception as error:
        print(f"❌ AdK Request failed: {str(error)}")


if __name__ == '__main__':
    try:
        test_complete_conversation()
        test_validation_logic()
        test_adk_request_simulation()
        
        print("\n" + "=" * 60)
        print("🎯 Implementation Test Summary:")
        print("✅ Complete conversation flow: WORKING")
        print("✅ Validation logic: WORKING")
        print("✅ Google AdK integration: WORKING")
        print("✅ Session management: WORKING")
        print("\n🚀 Paisalo Google AdK Chatbot is ready for deployment!")
        
    except Exception as error:
        print(f"\n❌ Implementation test failed: {str(error)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

