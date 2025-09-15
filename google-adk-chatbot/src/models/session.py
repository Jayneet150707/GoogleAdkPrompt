"""
Session management models for Paisalo Google AdK Chatbot
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List
import uuid


class ConversationStep(Enum):
    """Conversation flow steps"""
    WELCOME = "welcome"
    AGE = "age"
    CREDIT_SCORE = "credit_score"
    DOCUMENTS = "documents"
    PAN_VERIFICATION = "pan_verification"
    LOAN_AMOUNT = "loan_amount"
    TENURE = "tenure"
    INCOME = "income"
    EXPENSES = "expenses"
    PROCESSING = "processing"
    COMPLETED = "completed"


class LoanStatus(Enum):
    """Loan application status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class UserData:
    """User information collected during conversation"""
    age: Optional[int] = None
    credit_score: Optional[int] = None
    documents: List[str] = field(default_factory=list)
    pan_number: Optional[str] = None
    loan_amount: Optional[int] = None
    tenure_months: Optional[int] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'age': self.age,
            'credit_score': self.credit_score,
            'documents': self.documents,
            'pan_number': self.pan_number,
            'loan_amount': self.loan_amount,
            'tenure_months': self.tenure_months,
            'monthly_income': self.monthly_income,
            'monthly_expenses': self.monthly_expenses
        }
    
    def is_complete(self) -> bool:
        """Check if all required data is collected"""
        return all([
            self.age is not None,
            self.credit_score is not None,
            len(self.documents) >= 2,
            self.pan_number is not None,
            self.loan_amount is not None,
            self.tenure_months is not None,
            self.monthly_income is not None,
            self.monthly_expenses is not None
        ])


@dataclass
class LoanResult:
    """Loan eligibility result"""
    status: LoanStatus
    amount: Optional[int] = None
    tenure_months: Optional[int] = None
    roi_percentage: Optional[float] = None
    monthly_emi: Optional[float] = None
    rejection_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'status': self.status.value,
            'amount': self.amount,
            'tenure_months': self.tenure_months,
            'roi_percentage': self.roi_percentage,
            'monthly_emi': self.monthly_emi,
            'rejection_reason': self.rejection_reason
        }


@dataclass
class ChatSession:
    """Chat session state management"""
    session_id: str
    step: ConversationStep = ConversationStep.WELCOME
    user_data: UserData = field(default_factory=UserData)
    loan_result: Optional[LoanResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post initialization"""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.message_count += 1
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired"""
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        return datetime.utcnow() > expiry_time
    
    def advance_step(self):
        """Advance to next conversation step"""
        step_order = [
            ConversationStep.WELCOME,
            ConversationStep.AGE,
            ConversationStep.CREDIT_SCORE,
            ConversationStep.DOCUMENTS,
            ConversationStep.PAN_VERIFICATION,
            ConversationStep.LOAN_AMOUNT,
            ConversationStep.TENURE,
            ConversationStep.INCOME,
            ConversationStep.EXPENSES,
            ConversationStep.PROCESSING,
            ConversationStep.COMPLETED
        ]
        
        try:
            current_index = step_order.index(self.step)
            if current_index < len(step_order) - 1:
                self.step = step_order[current_index + 1]
        except ValueError:
            # If current step not found, stay at current step
            pass
    
    def set_step(self, step: ConversationStep):
        """Set specific conversation step"""
        self.step = step
        self.update_activity()
    
    def add_context(self, key: str, value: Any):
        """Add context information"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context information"""
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'step': self.step.value,
            'user_data': self.user_data.to_dict(),
            'loan_result': self.loan_result.to_dict() if self.loan_result else None,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': self.message_count,
            'context': self.context
        }
    
    def reset(self):
        """Reset session to initial state"""
        self.step = ConversationStep.WELCOME
        self.user_data = UserData()
        self.loan_result = None
        self.message_count = 0
        self.context = {}
        self.update_activity()

