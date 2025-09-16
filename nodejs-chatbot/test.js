// Simple test file to demonstrate Paisalo loan chatbot functionality

const { handleConversation } = require('./conversationHandler');
const { validatePAN } = require('./panValidator');
const { calculateEMI } = require('./emiCalculator');
const { validateIncomeExpenseRatio } = require('./incomeValidator');

console.log('🧪 Testing Paisalo Loan Chatbot Components\n');

// Test 1: PAN Validation
console.log('1. Testing PAN Validation:');
console.log('Valid PAN (ABCDE1234F):', validatePAN('ABCDE1234F'));
console.log('Invalid PAN (ABC123):', validatePAN('ABC123'));
console.log('');

// Test 2: EMI Calculation
console.log('2. Testing EMI Calculation (SLM Method):');
const emiResult = calculateEMI(75000, 24);
if (emiResult.success) {
  console.log('Loan Amount: ₹75,000');
  console.log('Tenure: 24 months');
  console.log('ROI: 9%');
  console.log('EMI:', emiResult.calculation.emi);
  console.log('Total Interest:', emiResult.calculation.totalInterest);
  console.log('Total Amount:', emiResult.calculation.totalAmount);
} else {
  console.log('EMI Calculation failed:', emiResult.message);
}
console.log('');

// Test 3: Income/Expense Validation
console.log('3. Testing Income/Expense Validation:');
const incomeTest1 = validateIncomeExpenseRatio(50000, 20000); // 40% - Good
const incomeTest2 = validateIncomeExpenseRatio(50000, 30000); // 60% - High

console.log('Income: ₹50,000, Expense: ₹20,000');
console.log('Valid:', incomeTest1.isValid, '- Expense %:', incomeTest1.expensePercentage + '%');

console.log('Income: ₹50,000, Expense: ₹30,000');
console.log('Valid:', incomeTest2.isValid, '- Expense %:', incomeTest2.expensePercentage + '%');
console.log('');

// Test 4: Conversation Flow Simulation
console.log('4. Testing Conversation Flow:');

function testConversation() {
  const sessionId = 'test-session-' + Date.now();
  
  const testMessages = [
    'Hello',
    '25',           // Age
    '650',          // Credit Score
    'I have PAN and voter ID',  // Documents
    'ABCDE1234F',   // PAN Number
    '75000',        // Loan Amount
    '24',           // Tenure
    '50000',        // Income
    '20000'         // Expense
  ];
  
  testMessages.forEach((message, index) => {
    const mockRequest = {
      session: sessionId,
      queryResult: {
        queryText: message,
        intent: {
          displayName: index === 0 ? 'Default Welcome Intent' : ''
        }
      }
    };
    
    const response = handleConversation(mockRequest);
    console.log(`Step ${index + 1} - User: "${message}"`);
    console.log(`Bot: ${response.fulfillmentText.substring(0, 100)}...`);
    console.log('---');
  });
}

testConversation();

console.log('\n✅ All tests completed!');
console.log('\n🚀 To run the server: npm start');
console.log('🧪 To test manually: POST to http://localhost:3000/test');
console.log('📚 API docs: http://localhost:3000/api-docs');

