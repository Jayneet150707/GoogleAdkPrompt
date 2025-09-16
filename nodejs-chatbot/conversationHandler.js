// Main conversation handler for Paisalo loan chatbot

const { validateAge, validateCreditScore, validateLoanAmount, validateDocuments, validatePANRequirement, parseDocuments } = require('./validators');
const { validatePANDetailed } = require('./panValidator');
const { calculateEMI, validateTenure, getAllTenureOptions } = require('./emiCalculator');
const { validateIncomeExpenseRatio, suggestMaxEMI } = require('./incomeValidator');
const { MESSAGES } = require('./constants');
const responses = require('./responses');

// User session storage (in production, use proper session management)
const userSessions = new Map();

/**
 * Main conversation handler
 * @param {object} request - Webhook request from Google Assistant
 * @returns {object} - Response for Google Assistant
 */
function handleConversation(request) {
  try {
    const sessionId = request.session || 'default-session';
    const queryText = request.queryResult?.queryText?.toLowerCase() || '';
    const intent = request.queryResult?.intent?.displayName || '';
    
    // Initialize user session if not exists
    if (!userSessions.has(sessionId)) {
      userSessions.set(sessionId, {
        step: 'welcome',
        profile: {}
      });
    }
    
    const userSession = userSessions.get(sessionId);
    
    // Handle different intents and conversation flow
    switch (intent) {
      case 'Default Welcome Intent':
        return handleWelcome(userSession);
      
      case 'help':
      case 'Help Intent':
        return responses.createHelpResponse();
      
      default:
        return handleUserInput(queryText, userSession, sessionId);
    }
    
  } catch (error) {
    console.error('Error in conversation handler:', error);
    return responses.createErrorResponse('Sorry, something went wrong. Please try again.');
  }
}

/**
 * Handles welcome intent
 * @param {object} userSession - User session data
 * @returns {object} - Welcome response
 */
function handleWelcome(userSession) {
  userSession.step = 'age';
  return responses.createWelcomeResponse();
}

/**
 * Handles user input based on current conversation step
 * @param {string} input - User input text
 * @param {object} userSession - User session data
 * @param {string} sessionId - Session ID
 * @returns {object} - Response based on current step
 */
function handleUserInput(input, userSession, sessionId) {
  switch (userSession.step) {
    case 'age':
      return handleAgeInput(input, userSession);
    
    case 'credit_score':
      return handleCreditScoreInput(input, userSession);
    
    case 'documents':
      return handleDocumentsInput(input, userSession);
    
    case 'pan_number':
      return handlePANInput(input, userSession);
    
    case 'loan_amount':
      return handleLoanAmountInput(input, userSession);
    
    case 'tenure':
      return handleTenureInput(input, userSession);
    
    case 'income':
      return handleIncomeInput(input, userSession);
    
    case 'expense':
      return handleExpenseInput(input, userSession);
    
    case 'family_income':
      return handleFamilyIncomeInput(input, userSession);
    
    case 'family_expense':
      return handleFamilyExpenseInput(input, userSession);
    
    case 'complete':
      return handleCompleteFlow(input, userSession);
    
    default:
      return handleGeneralInput(input, userSession);
  }
}

/**
 * Handles age input
 */
function handleAgeInput(input, userSession) {
  const ageMatch = input.match(/\d+/);
  if (!ageMatch) {
    return responses.createValidationErrorResponse(
      'Please provide your age as a number.',
      MESSAGES.AGE_PROMPT
    );
  }
  
  const age = parseInt(ageMatch[0]);
  const validation = validateAge(age);
  
  if (!validation.isValid) {
    return responses.createEligibilityFailureResponse(validation.message);
  }
  
  userSession.profile.age = age;
  userSession.step = 'credit_score';
  
  return responses.createInfoRequestResponse(MESSAGES.CREDIT_SCORE_PROMPT);
}

/**
 * Handles credit score input
 */
function handleCreditScoreInput(input, userSession) {
  const scoreMatch = input.match(/\d+/);
  if (!scoreMatch) {
    return responses.createValidationErrorResponse(
      'Please provide your credit score as a number.',
      MESSAGES.CREDIT_SCORE_PROMPT
    );
  }
  
  const creditScore = parseInt(scoreMatch[0]);
  const validation = validateCreditScore(creditScore);
  
  if (!validation.isValid) {
    return responses.createEligibilityFailureResponse(validation.message);
  }
  
  userSession.profile.creditScore = creditScore;
  userSession.step = 'documents';
  
  return responses.createInfoRequestResponse(MESSAGES.DOCUMENTS_PROMPT);
}

/**
 * Handles documents input
 */
function handleDocumentsInput(input, userSession) {
  const documents = parseDocuments(input);
  const validation = validateDocuments(documents);
  
  if (!validation.isValid) {
    return responses.createValidationErrorResponse(
      validation.message,
      MESSAGES.DOCUMENTS_PROMPT
    );
  }
  
  userSession.profile.documents = documents;
  
  // Check if PAN is required and ask for PAN number
  const panValidation = validatePANRequirement(documents);
  if (panValidation.isValid) {
    userSession.step = 'pan_number';
    return responses.createInfoRequestResponse(MESSAGES.PAN_PROMPT);
  }
  
  return responses.createValidationErrorResponse(
    panValidation.message,
    MESSAGES.DOCUMENTS_PROMPT
  );
}

/**
 * Handles PAN number input
 */
function handlePANInput(input, userSession) {
  const panMatch = input.match(/[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}/);
  if (!panMatch) {
    return responses.createValidationErrorResponse(
      'Please provide a valid PAN number.',
      MESSAGES.PAN_PROMPT
    );
  }
  
  const panNumber = panMatch[0].toUpperCase();
  const validation = validatePANDetailed(panNumber);
  
  if (!validation.isValid) {
    return responses.createValidationErrorResponse(
      validation.message,
      MESSAGES.PAN_PROMPT
    );
  }
  
  userSession.profile.panNumber = validation.formattedPAN;
  userSession.step = 'loan_amount';
  
  return responses.createInfoRequestResponse(MESSAGES.LOAN_AMOUNT_PROMPT);
}

/**
 * Handles loan amount input
 */
function handleLoanAmountInput(input, userSession) {
  const amountMatch = input.match(/\d+/);
  if (!amountMatch) {
    return responses.createValidationErrorResponse(
      'Please provide a valid loan amount.',
      MESSAGES.LOAN_AMOUNT_PROMPT
    );
  }
  
  const loanAmount = parseInt(amountMatch[0]);
  const validation = validateLoanAmount(loanAmount);
  
  if (!validation.isValid) {
    return responses.createValidationErrorResponse(
      validation.message,
      MESSAGES.LOAN_AMOUNT_PROMPT
    );
  }
  
  userSession.profile.loanAmount = loanAmount;
  userSession.step = 'tenure';
  
  const tenureOptions = getAllTenureOptions();
  const optionsText = tenureOptions.options.map(opt => opt.description).join('\n• ');
  
  return responses.createInfoRequestResponse(
    MESSAGES.TENURE_PROMPT,
    `Available options:\n• ${optionsText}`
  );
}

/**
 * Handles tenure input
 */
function handleTenureInput(input, userSession) {
  const tenureMatch = input.match(/\d+/);
  if (!tenureMatch) {
    return responses.createValidationErrorResponse(
      'Please provide tenure in months.',
      MESSAGES.TENURE_PROMPT
    );
  }
  
  const tenure = parseInt(tenureMatch[0]);
  const validation = validateTenure(tenure);
  
  if (!validation.isValid) {
    return responses.createValidationErrorResponse(
      validation.message,
      MESSAGES.TENURE_PROMPT
    );
  }
  
  userSession.profile.tenure = tenure;
  userSession.step = 'income';
  
  return responses.createInfoRequestResponse(MESSAGES.INCOME_PROMPT);
}

/**
 * Handles income input
 */
function handleIncomeInput(input, userSession) {
  const incomeMatch = input.match(/\d+/);
  if (!incomeMatch) {
    return responses.createValidationErrorResponse(
      'Please provide your monthly income amount.',
      MESSAGES.INCOME_PROMPT
    );
  }
  
  userSession.profile.income = parseInt(incomeMatch[0]);
  userSession.step = 'expense';
  
  return responses.createInfoRequestResponse(MESSAGES.EXPENSE_PROMPT);
}

/**
 * Handles expense input and completes the flow
 */
function handleExpenseInput(input, userSession) {
  const expenseMatch = input.match(/\d+/);
  if (!expenseMatch) {
    return responses.createValidationErrorResponse(
      'Please provide your monthly expense amount.',
      MESSAGES.EXPENSE_PROMPT
    );
  }
  
  userSession.profile.expense = parseInt(expenseMatch[0]);
  
  // Validate income-expense ratio
  const ratioValidation = validateIncomeExpenseRatio(
    userSession.profile.income,
    userSession.profile.expense
  );
  
  if (!ratioValidation.isValid && !ratioValidation.warning) {
    return responses.createEligibilityFailureResponse(ratioValidation.message);
  }
  
  // Calculate EMI
  const emiCalculation = calculateEMI(
    userSession.profile.loanAmount,
    userSession.profile.tenure
  );
  
  if (!emiCalculation.success) {
    return responses.createErrorResponse(emiCalculation.message);
  }
  
  userSession.step = 'complete';
  
  // If expense ratio is high but not disqualifying, show warning
  if (ratioValidation.warning) {
    const warningResponse = responses.createIncomeAnalysisResponse(ratioValidation);
    // Add EMI calculation to the response
    warningResponse.fulfillmentText += '\n\n' + responses.createEMIDisplayResponse(emiCalculation).fulfillmentText;
    return warningResponse;
  }
  
  return responses.createEligibilitySuccessResponse(userSession.profile, emiCalculation);
}

/**
 * Handles general input when conversation is complete
 */
function handleCompleteFlow(input, userSession) {
  if (input.includes('new') || input.includes('again') || input.includes('restart')) {
    // Reset session for new calculation
    userSession.step = 'age';
    userSession.profile = {};
    return responses.createWelcomeResponse();
  }
  
  return responses.createInfoRequestResponse(
    'Would you like to start a new loan application or calculate EMI for different parameters?',
    'Type "new" to start over or "help" for assistance.'
  );
}

/**
 * Handles general input that doesn't match current step
 */
function handleGeneralInput(input, userSession) {
  if (input.includes('help')) {
    return responses.createHelpResponse();
  }
  
  if (input.includes('start') || input.includes('begin') || input.includes('loan')) {
    userSession.step = 'age';
    userSession.profile = {};
    return responses.createWelcomeResponse();
  }
  
  return responses.createErrorResponse();
}

module.exports = {
  handleConversation,
  userSessions // Export for testing purposes
};

