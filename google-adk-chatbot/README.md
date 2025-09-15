# Paisalo Google AdK Chatbot 🏦🤖

A comprehensive Python-based chatbot for Paisalo Digital Limited's loan eligibility assessment, designed for Google AdK (Actions Development Kit) integration.

## 🚀 Features

### Loan Eligibility Assessment
- **Age Validation**: 21-57 years eligibility range
- **Credit Score Evaluation**: 
  - ✅ Eligible: < 18 or > 650
  - ❌ Not Eligible: 18-650 (inclusive)
- **Document Verification**: PAN + Voter ID or PAN + Driving License
- **PAN Validation**: Regex-based format verification
- **Loan Amount**: ₹50,000 - ₹1,00,000 range
- **Tenure Options**: 12, 24, 36, 48 months with different ROI rates
- **Income/Expense Analysis**: Expense ratio validation (max 50% of income)

### Technical Features
- **Google AdK Integration**: Full webhook support
- **Session Management**: Persistent conversation state
- **Input Validation**: Comprehensive data sanitization
- **Error Handling**: Robust error management with logging
- **RESTful API**: Multiple endpoints for different use cases
- **Structured Logging**: JSON-based logging with request tracking

## 📋 Business Rules

### Paisalo Loan Eligibility Criteria

| Criteria | Rule | Details |
|----------|------|---------|
| **Age** | 21-57 years | Outside range = Not eligible |
| **Credit Score** | < 18 OR > 650 | 18-650 range = Not eligible |
| **Documents** | PAN + (Voter ID OR DL) | Must have valid combination |
| **PAN Format** | ABCDE1234F | 5 letters + 4 digits + 1 letter |
| **Loan Amount** | ₹50,000 - ₹1,00,000 | Outside range = Not eligible |
| **Tenure & ROI** | 12m: 7%, 24m: 9%, 36m: 12%, 48m: 18% | Fixed rates |
| **Expense Ratio** | Max 50% of income | Higher ratio = Not eligible |
| **EMI Calculation** | Simple Interest Method (SLM) | SI = (P×R×T)/100 |

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Google Cloud account (for AdK integration)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd google-adk-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# Google Cloud Configuration
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Session Management
SESSION_TIMEOUT_MINUTES=30
MAX_ACTIVE_SESSIONS=1000
```

## 📡 API Endpoints

### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Paisalo Google AdK Chatbot",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Google AdK Webhook
```http
POST /webhook
Content-Type: application/json
```
**Request:**
```json
{
  "session": "projects/PROJECT_ID/agent/sessions/SESSION_ID",
  "queryResult": {
    "queryText": "I am 30 years old",
    "intent": {
      "displayName": "age.input"
    }
  }
}
```

**Response:**
```json
{
  "fulfillmentText": "Great! Now, please tell me your credit score.",
  "source": "paisalo-adk-chatbot"
}
```

### 3. Test Endpoint
```http
POST /test
Content-Type: application/json
```
**Request:**
```json
{
  "message": "hello",
  "sessionId": "test-session-123"
}
```

**Response:**
```json
{
  "sessionId": "test-session-123",
  "response": "🏦 Welcome to Paisalo Digital Limited! 🏦...",
  "step": "age",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 4. Session Management
```http
GET /session/{sessionId}
GET /sessions
```

## 🗣️ Conversation Flow

### Step-by-Step Process

1. **Welcome** → User greets the bot
2. **Age Input** → "I am 30 years old"
3. **Credit Score** → "My credit score is 700"
4. **Documents** → "I have PAN and voter ID"
5. **PAN Verification** → "ABCDE1234F"
6. **Loan Amount** → "I need 80000"
7. **Tenure Selection** → "36 months"
8. **Income** → "My income is 50000"
9. **Expenses** → "My expenses are 20000"
10. **Result** → Approval/Rejection with details

### Example Conversation

```
Bot: 🏦 Welcome to Paisalo Digital Limited! 🏦
     I'm here to help you check your loan eligibility quickly and easily.
     To get started, please tell me your age.

User: I am 30 years old

Bot: Great! Now, please tell me your credit score.

User: My credit score is 700

Bot: Perfect! Now I need to verify your documents.
     Please tell me which documents you have:
     • PAN Card and Voter ID
     • PAN Card and Driving License
     Which combination do you have?

User: I have PAN and voter ID

Bot: Please provide your PAN card number for verification.

User: ABCDE1234F

Bot: Excellent! Now, how much loan amount do you need?
     (Minimum: ₹50,000, Maximum: ₹1,00,000)

User: I need 80000

Bot: Great! Please select your preferred loan tenure:
     • 12 months (7% ROI)
     • 24 months (9% ROI)
     • 36 months (12% ROI)
     • 48 months (18% ROI)

User: 36 months

Bot: Please tell me your monthly income.

User: My income is 50000

Bot: Finally, please tell me your monthly expenses.

User: My expenses are 20000

Bot: 🎉 Congratulations! You are eligible for the loan! 🎉

     Your loan details:
     💰 Amount: ₹80,000
     📅 Tenure: 36 months
     📊 ROI: 12%
     💳 Monthly EMI: ₹2,488.89

     Thank you for choosing Paisalo! 🏦
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

### Manual Testing
```bash
# Start the server
python app.py

# Test with curl
curl -X POST http://localhost:5000/test \\
  -H "Content-Type: application/json" \\
  -d '{"message": "hello", "sessionId": "test-123"}'
```

## 📊 Logging

The application uses structured logging with the following events:
- `conversation_start`: New conversation initiated
- `step_transition`: Movement between conversation steps
- `validation_error`: Input validation failures
- `loan_decision`: Final eligibility decision
- `session_cleanup`: Session management events
- `adk_request`/`adk_response`: Google AdK interactions

## 🔒 Security Features

- **Input Sanitization**: XSS and injection prevention
- **Request Validation**: Comprehensive payload validation
- **Session Management**: Secure session handling
- **Rate Limiting**: Protection against abuse
- **Error Handling**: Secure error responses

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Google Cloud Run
```bash
gcloud run deploy paisalo-chatbot \\
  --source . \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated
```

## 📈 Monitoring

- **Health Checks**: `/health` endpoint
- **Session Metrics**: Active session tracking
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Request/response timing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- **Company**: Paisalo Digital Limited
- **Email**: support@paisalo.in
- **Documentation**: [Internal Wiki]

---

**Built with ❤️ for Paisalo Digital Limited**

