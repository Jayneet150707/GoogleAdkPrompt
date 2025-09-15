# Paisalo Loan Chatbot - Python 3.13 Implementation

A comprehensive Google Actions on Google (AdK) chatbot for **Paisalo Digital Limited** built with Python 3.13, featuring advanced type hints, dataclasses, and modern Python features for loan eligibility assessment and EMI calculations.

## 🐍 Python 3.13 Features Used

- **Enhanced Type Hints**: Full type annotation support with `typing` module
- **Dataclasses**: Clean data structures with `@dataclass` decorator
- **Enum Classes**: Type-safe enumeration for conversation steps
- **Pattern Matching**: Modern Python syntax for cleaner code
- **Improved Error Handling**: Better exception management
- **Performance Optimizations**: Faster execution with Python 3.13 improvements

## 🏦 About Paisalo

Paisalo Digital Limited is a leading financial services company providing accessible loan solutions with transparent processes and competitive rates.

## 🤖 Chatbot Features

### Loan Eligibility Validation
- **Age Verification**: Must be between 21-57 years
- **Credit Score Check**: Score must be between 18-650
- **Document Verification**: Requires either (Voter ID + PAN) or (PAN + Driving License)
- **PAN Validation**: Validates PAN format using regex (AAAAA9999A)
- **Loan Amount**: Between ₹50,000 to ₹1,00,000
- **Income/Expense Ratio**: Expenses should not exceed 50% of income

### EMI Calculation (SLM Method)
- **12 months**: 7% ROI
- **24 months**: 9% ROI  
- **36 months**: 12% ROI
- **48 months**: 18% ROI

### Conversation Flow
1. **Welcome** & Age verification
2. **Credit Score** validation
3. **Document** verification
4. **PAN Number** validation
5. **Loan Amount** specification
6. **Tenure** selection
7. **Income** details
8. **Expense** analysis
9. **Final Eligibility** & EMI calculation

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** (Required for latest features)
- pip package manager
- Google Actions Console account

### Installation

1. **Navigate to the python-chatbot directory**
   ```bash
   cd python-chatbot
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the chatbot**
   ```bash
   python paisalo_chatbot.py
   ```

5. **For production with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:3000 paisalo_chatbot:app
   ```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
pytest test_paisalo_chatbot.py -v

# Run with coverage
pytest test_paisalo_chatbot.py --cov=paisalo_chatbot --cov-report=html

# Run specific test class
pytest test_paisalo_chatbot.py::TestLoanValidator -v
```

### Manual Testing
Use the test endpoint to interact with the chatbot:

```bash
curl -X POST http://localhost:3000/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "sessionId": "test-123"
  }'
```

### Test Conversation Flow
1. Start: "Hello" or "Hi"
2. Age: "I am 25 years old"
3. Credit Score: "My credit score is 650"
4. Documents: "I have PAN and voter ID"
5. PAN: "ABCDE1234F"
6. Loan Amount: "I need 75000"
7. Tenure: "24 months"
8. Income: "My income is 50000"
9. Expenses: "My expenses are 20000"

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and service status |
| `/webhook` | POST | Google Assistant webhook |
| `/test` | POST | Manual testing endpoint |

### Health Check Response
```json
{
  "status": "healthy",
  "service": "Paisalo Loan Chatbot",
  "version": "1.0.0",
  "python_version": "3.13"
}
```

### Test Endpoint Request/Response
```bash
# Request
POST /test
{
  "message": "I am 30 years old",
  "sessionId": "test-session-123"
}

# Response
{
  "sessionId": "test-session-123",
  "response": "Great! Now, what is your credit score?",
  "step": "credit_score"
}
```

## 🏗️ Project Structure

```
python-chatbot/
├── paisalo_chatbot.py          # Main chatbot application
├── test_paisalo_chatbot.py     # Comprehensive test suite
├── requirements.txt            # Python dependencies
├── actions.json               # Google Actions configuration
├── README.md                  # This documentation
└── .env.example              # Environment variables template
```

## 🔧 Architecture & Design

### Class Structure

```python
# Core Classes
├── LoanRules (dataclass)           # Business rules configuration
├── UserProfile (dataclass)        # User data structure
├── UserSession (dataclass)        # Session management
├── ConversationStep (Enum)        # Conversation flow states
├── PANValidator                    # PAN number validation
├── LoanValidator                   # Business rule validation
├── EMICalculator                   # SLM-based EMI calculation
├── ResponseGenerator               # Google AdK response formatting
└── PaisaloChatbot                 # Main application class
```

### Key Features

#### 🎯 Type Safety with Python 3.13
```python
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class UserProfile:
    age: Optional[int] = None
    credit_score: Optional[int] = None
    documents: List[str] = field(default_factory=list)
    # ... more fields with proper typing
```

#### 🔍 Advanced Validation
```python
def validate_age(self, age: int) -> Tuple[bool, str]:
    """Validate user age with detailed error messages"""
    if not isinstance(age, int) or age <= 0:
        return False, "Please provide a valid age"
    
    if age < self.rules.MIN_AGE or age > self.rules.MAX_AGE:
        return False, f"Age must be between {self.rules.MIN_AGE} and {self.rules.MAX_AGE} years"
    
    return True, "Age is valid"
```

#### 💰 SLM EMI Calculation
```python
def calculate_emi_slm(self, principal: int, tenure_months: int) -> Dict[str, float]:
    """
    Calculate EMI using Straight Line Method (SLM)
    Formula: 
    - Total Interest = Principal × ROI × (Tenure in years)
    - Total Amount = Principal + Total Interest
    - EMI = Total Amount ÷ Tenure in months
    """
    roi_percentage = self.rules.ROI_RATES[tenure_months]
    tenure_years = tenure_months / 12
    
    total_interest = principal * (roi_percentage / 100) * tenure_years
    total_amount = principal + total_interest
    emi = total_amount / tenure_months
    
    return {
        'principal': float(principal),
        'roi_percentage': roi_percentage,
        'tenure_months': tenure_months,
        'total_interest': round(total_interest, 2),
        'total_amount': round(total_amount, 2),
        'emi': round(emi, 2)
    }
```

## 🚀 Deployment

### Google Actions Console Setup

1. **Create New Project**
   - Go to [Google Actions Console](https://console.actions.google.com/)
   - Create a new project
   - Choose "Custom" project type

2. **Upload Configuration**
   ```bash
   # Install Google CLI
   npm install -g @google/clasp
   
   # Upload actions.json
   gactions push --project-id your-project-id
   ```

3. **Configure Webhook**
   - Update `actions.json` with your webhook URL
   - Deploy your Python app to cloud platform
   - Test with Actions Console simulator

### Cloud Deployment Options

#### Google Cloud Platform
```bash
# Deploy to Google Cloud Run
gcloud run deploy paisalo-chatbot \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated
```

#### Heroku
```bash
# Create Heroku app
heroku create paisalo-chatbot-python

# Deploy
git push heroku main
```

#### AWS Lambda (with Zappa)
```bash
pip install zappa
zappa init
zappa deploy production
```

### Environment Variables
Create `.env` file:
```bash
FLASK_ENV=production
PORT=3000
LOG_LEVEL=INFO
```

## 🧮 EMI Calculation Examples

### Example 1: 12 Months Loan
- **Principal**: ₹60,000
- **Tenure**: 12 months
- **ROI**: 7% per annum

```
Total Interest = 60,000 × 0.07 × 1 = ₹4,200
Total Amount = 60,000 + 4,200 = ₹64,200
EMI = 64,200 ÷ 12 = ₹5,350
```

### Example 2: 24 Months Loan
- **Principal**: ₹75,000
- **Tenure**: 24 months
- **ROI**: 9% per annum

```
Total Interest = 75,000 × 0.09 × 2 = ₹13,500
Total Amount = 75,000 + 13,500 = ₹88,500
EMI = 88,500 ÷ 24 = ₹3,687.50
```

## 🔍 Validation Rules

### PAN Number Validation
```python
# Regex Pattern
PAN_PATTERN = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'

# Valid Examples
✅ ABCDE1234F
✅ XYZAB9876C
✅ PQRST5432M

# Invalid Examples
❌ ABCD1234F  (Only 4 letters)
❌ ABCDE123F  (Only 3 digits)
❌ 12345ABCD  (Numbers first)
```

### Document Combinations
```python
# Valid Combinations
✅ ['VOTER', 'PAN']
✅ ['PAN', 'DL']
✅ ['VOTER_ID', 'PAN']
✅ ['DL', 'PAN']

# Invalid Combinations
❌ ['VOTER', 'DL']     # Missing PAN
❌ ['VOTER']           # Only one document
❌ ['PASSPORT', 'PAN'] # Invalid document type
```

### Income/Expense Validation
```python
# Expense Ratio Calculation
expense_percentage = (expense / income) * 100

# Valid Cases (≤ 50%)
✅ Income: ₹50,000, Expense: ₹20,000 (40%)
✅ Income: ₹60,000, Expense: ₹30,000 (50%)

# Invalid Cases (> 50%)
❌ Income: ₹40,000, Expense: ₹25,000 (62.5%)
❌ Income: ₹50,000, Expense: ₹30,000 (60%)
```

## 🛠️ Development

### Code Quality Tools
```bash
# Format code with Black
black paisalo_chatbot.py test_paisalo_chatbot.py

# Lint with Flake8
flake8 paisalo_chatbot.py

# Type checking with MyPy
mypy paisalo_chatbot.py
```

### Adding New Features

1. **Update Business Rules**
   ```python
   # Modify LoanRules dataclass
   @dataclass
   class LoanRules:
       NEW_RULE: int = 100
   ```

2. **Add Validation Logic**
   ```python
   # Add to LoanValidator class
   def validate_new_rule(self, value: int) -> Tuple[bool, str]:
       # Implementation here
       pass
   ```

3. **Update Conversation Flow**
   ```python
   # Add new step to ConversationStep enum
   class ConversationStep(Enum):
       NEW_STEP = "new_step"
   ```

4. **Add Tests**
   ```python
   # Add to test_paisalo_chatbot.py
   def test_new_feature(self):
       # Test implementation
       pass
   ```

## 📈 Performance & Monitoring

### Logging
```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usage in code
logger.info("User started loan application")
logger.error(f"Validation failed: {error_message}")
```

### Metrics to Monitor
- Response time per conversation step
- Eligibility success/failure rates
- Most common failure reasons
- User drop-off points in conversation

## 🔒 Security Considerations

- **Input Validation**: All user inputs are validated and sanitized
- **PAN Masking**: PAN numbers are masked in logs
- **Session Security**: Session data is not persisted permanently
- **HTTPS Only**: All webhook communications use HTTPS
- **Rate Limiting**: Implement rate limiting for production

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes with proper tests
4. Run the test suite (`pytest`)
5. Format code (`black .`)
6. Submit a pull request

## 📞 Support

For technical support or business inquiries:
- **Email**: support@paisalo.in
- **Website**: https://paisalo.in
- **Technical Issues**: Create an issue in the repository

## 🎯 Roadmap

- [ ] Multi-language support (Hindi, regional languages)
- [ ] Voice-only interaction optimization
- [ ] Integration with Paisalo's loan management system
- [ ] Advanced analytics and reporting
- [ ] Machine learning for better eligibility prediction
- [ ] WhatsApp Business API integration

---

**Built with ❤️ and Python 3.13 for Paisalo Digital Limited**

