# 🏦 Paisalo Loan Agent - Google ADK Integration

A comprehensive loan eligibility processing system built with Python 3.13 for Google Android Development Kit (ADK) integration.

## 🚀 Features

### Loan Eligibility Rules
- **Age Validation**: 21-57 years (inclusive)
- **Credit Score**: ≥18 or ≤650
- **Document Verification**: 
  - Valid combinations: (Voter ID + PAN) OR (PAN + DL)
  - PAN number regex validation
- **Loan Amount**: ₹50,000 - ₹1,00,000
- **Expense Ratio**: ≤50% of total income
- **EMI Calculation**: Simple Interest Method (SLM)

### Interest Rates (ROI)
| Tenure | Rate of Interest |
|--------|------------------|
| 12 months | 7% |
| 24 months | 9% |
| 36 months | 12% |
| 48 months | 18% |

## 📋 Requirements

- Python 3.13+
- Flask 3.0.0
- Flask-CORS 4.0.0
- See `requirements.txt` for complete list

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd GoogleAdkPrompt
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
# Run the main loan agent
python paisalo_loan_agent.py

# Run the Google ADK Integration API server
python google_adk_integration.py
```

## 🔧 API Endpoints

### Health Check
```http
GET /health
```

### Check Loan Eligibility
```http
POST /api/loan/eligibility
Content-Type: application/json

{
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
```

### Calculate EMI
```http
POST /api/loan/calculate-emi
Content-Type: application/json

{
  "principal": 75000,
  "tenure_months": 24
}
```

### Validate PAN
```http
POST /api/validate/pan
Content-Type: application/json

{
  "pan_number": "ABCDE1234F"
}
```

### Get Loan Rules
```http
GET /api/loan/rules
```

## 📊 Example Usage

### Python Code Example
```python
from paisalo_loan_agent import PaisaloLoanAgent, UserProfile, LoanApplication

# Initialize the agent
agent = PaisaloLoanAgent()

# Create user profile
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

# Create loan application
loan_application = LoanApplication(
    amount=75000,
    tenure_months=24,
    user_profile=user_profile
)

# Process the application
result = agent.process_loan_application(loan_application)

if result.status.value == "APPROVED":
    print(f"✅ Loan Approved!")
    print(f"💰 EMI: ₹{result.emi:,.2f}")
    print(f"📊 ROI: {result.roi}%")
    print(f"💳 Total Amount: ₹{result.total_amount:,.2f}")
else:
    print(f"❌ Loan Rejected: {result.reason}")
```

### cURL Example
```bash
# Check loan eligibility
curl -X POST http://localhost:5000/api/loan/eligibility \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest test_paisalo_agent.py -v

# Run with coverage
python -m pytest test_paisalo_agent.py --cov=paisalo_loan_agent --cov=google_adk_integration -v
```

## 📱 Android Integration

The API is designed to work seamlessly with Android applications:

1. **CORS Enabled**: Cross-origin requests supported
2. **JSON API**: RESTful endpoints with JSON responses
3. **Error Handling**: Comprehensive error responses
4. **Validation**: Input validation with detailed error messages

### Android HTTP Client Example
```java
// Example Android code to call the API
OkHttpClient client = new OkHttpClient();
MediaType JSON = MediaType.get("application/json; charset=utf-8");

String json = "{"
    + "\"user_profile\": {"
    + "\"age\": 35,"
    + "\"credit_score\": 600,"
    + "\"income\": 50000,"
    + "\"expense\": 20000,"
    + "\"family_income\": 30000,"
    + "\"family_expense\": 10000,"
    + "\"documents\": [\"PAN\", \"VOTER_ID\"],"
    + "\"pan_number\": \"ABCDE1234F\""
    + "},"
    + "\"loan_amount\": 75000,"
    + "\"tenure_months\": 24"
    + "}";

RequestBody body = RequestBody.create(json, JSON);
Request request = new Request.Builder()
    .url("http://your-server:5000/api/loan/eligibility")
    .post(body)
    .build();

try (Response response = client.newCall(request).execute()) {
    return response.body().string();
}
```

## 🏗️ Architecture

```
├── paisalo_loan_agent.py      # Core loan processing logic
├── google_adk_integration.py  # Flask API server for Android
├── test_paisalo_agent.py      # Comprehensive test suite
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔍 Business Rules Implementation

### Age Validation
- Minimum: 21 years
- Maximum: 57 years
- Both inclusive

### Credit Score Validation
- Valid if score ≥ 18 OR score ≤ 650
- Invalid range: 19-649 (exclusive)

### Document Validation
- **Option 1**: Voter ID + PAN
- **Option 2**: PAN + Driving License
- PAN format: `AAAAA9999A` (5 letters + 4 digits + 1 letter)

### Financial Validation
- Total expenses ≤ 50% of total income
- Total income = personal income + family income
- Total expenses = personal expenses + family expenses

### EMI Calculation (SLM Method)
```
Total Interest = (Principal × ROI × Tenure in years) / 100
Total Amount = Principal + Total Interest
EMI = Total Amount / Tenure in months
```

## 🚀 Deployment

### Development
```bash
python google_adk_integration.py
```

### Production (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 google_adk_integration:app
```

### Docker (Optional)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "google_adk_integration:app"]
```

## 📞 Support

For support and questions, please contact the Paisalo development team.

## 📄 License

This project is proprietary to Paisalo Digital Limited.

---

**Company**: Paisalo  
**Version**: 1.0.0  
**Python**: 3.13+  
**Framework**: Flask 3.0.0
