# Paisalo Loan Chatbot - Node.js Implementation

A comprehensive Google Actions on Google (AdK) chatbot for Paisalo Digital Limited that handles loan eligibility assessment and EMI calculations using the Straight Line Method (SLM).

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
1. Welcome & Age verification
2. Credit score validation
3. Document verification
4. PAN number validation
5. Loan amount specification
6. Tenure selection
7. Income details
8. Expense analysis
9. Final eligibility & EMI calculation

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Google Actions Console account

### Installation

1. **Navigate to the nodejs-chatbot directory**
   ```bash
   cd nodejs-chatbot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **For production**
   ```bash
   npm start
   ```

## 🧪 Testing

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
| `/` | GET | Service status |
| `/health` | GET | Health check |
| `/webhook` | POST | Google Assistant webhook |
| `/test` | POST | Manual testing endpoint |
| `/api-docs` | GET | API documentation |

## 🏗️ Project Structure

```
nodejs-chatbot/
├── index.js                 # Main server file
├── conversationHandler.js   # Main conversation logic
├── validators.js            # Business rule validators
├── panValidator.js          # PAN number validation
├── emiCalculator.js         # EMI calculation (SLM method)
├── incomeValidator.js       # Income/expense validation
├── responses.js             # Response templates
├── constants.js             # Business rules and constants
├── actions.json             # Google Actions configuration
├── package.json             # Dependencies and scripts
├── test.js                  # Test file
└── README.md               # This file
```

## 🔧 Configuration

### Business Rules (constants.js)
- Modify age limits, credit score ranges, loan amounts
- Update ROI rates for different tenures
- Customize validation messages

### Webhook URL
Update the webhook URL in `actions.json` for Google Actions deployment:
```json
{
  "conversations": {
    "paisalo-loan-assistant": {
      "url": "https://your-domain.com/webhook"
    }
  }
}
```

## 🚀 Deployment

### Google Actions Console
1. Create a new project in Google Actions Console
2. Upload the `actions.json` file
3. Configure the webhook URL to point to your deployed server
4. Test using the Actions Console simulator

### Server Deployment
Deploy to any Node.js hosting platform:
- Heroku
- Google Cloud Platform
- AWS
- Vercel
- Railway

### Environment Variables
```bash
PORT=3000  # Server port (optional, defaults to 3000)
```

## 🧮 EMI Calculation Formula (SLM Method)

The Straight Line Method (SLM) is used for EMI calculation:

```
Total Interest = Principal × ROI × (Tenure in years)
Total Amount = Principal + Total Interest  
EMI = Total Amount ÷ Tenure in months
```

### Example Calculation
- Loan Amount: ₹75,000
- Tenure: 24 months (2 years)
- ROI: 9% per annum

```
Total Interest = 75,000 × 0.09 × 2 = ₹13,500
Total Amount = 75,000 + 13,500 = ₹88,500
EMI = 88,500 ÷ 24 = ₹3,687.50
```

## 🔍 Validation Rules

### PAN Number Regex
```javascript
/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/
```
Format: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)

### Document Combinations
Valid combinations:
- Voter ID + PAN Card
- PAN Card + Driving License

### Income/Expense Validation
- Expenses must not exceed 50% of income
- Both individual and family income/expenses are considered

## 🛠️ Development

### Adding New Features
1. Update business rules in `constants.js`
2. Add validation logic in appropriate validator files
3. Update conversation flow in `conversationHandler.js`
4. Add response templates in `responses.js`

### Testing New Rules
Use the `/test` endpoint to validate new business logic without deploying to Google Actions.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For technical support or business inquiries, please contact:
- Email: support@paisalo.in
- Website: https://paisalo.in

---

**Built with ❤️ for Paisalo Digital Limited**

