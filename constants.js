// Business rules and constants for Paisalo loan eligibility

const LOAN_RULES = {
  AGE: {
    MIN: 21,
    MAX: 57
  },
  CREDIT_SCORE: {
    MIN: 18,
    MAX: 650
  },
  LOAN_AMOUNT: {
    MIN: 50000,
    MAX: 100000
  },
  INCOME_EXPENSE_RATIO: {
    MAX_EXPENSE_PERCENTAGE: 50
  }
};

const ROI_RATES = {
  12: 7,   // 12 months - 7% ROI
  24: 9,   // 24 months - 9% ROI
  36: 12,  // 36 months - 12% ROI
  48: 18   // 48 months - 18% ROI
};

const VALID_TENURES = [12, 24, 36, 48];

const DOCUMENT_COMBINATIONS = {
  VALID: [
    ['VOTER', 'PAN'],
    ['PAN', 'DL'],
    ['DL', 'PAN'],
    ['VOTER_ID', 'PAN']
  ]
};

const COMPANY_INFO = {
  NAME: 'Paisalo',
  FULL_NAME: 'Paisalo Digital Limited'
};

const MESSAGES = {
  WELCOME: `Welcome to ${COMPANY_INFO.NAME}! I'm here to help you check your loan eligibility and calculate EMI. Let's get started!`,
  AGE_PROMPT: 'Please tell me your age.',
  CREDIT_SCORE_PROMPT: 'What is your credit score?',
  DOCUMENTS_PROMPT: 'Which documents do you have? Please mention if you have: Voter ID, PAN Card, or Driving License (DL).',
  PAN_PROMPT: 'Please provide your PAN number.',
  LOAN_AMOUNT_PROMPT: 'How much loan amount do you need? (Between ₹50,000 to ₹1,00,000)',
  TENURE_PROMPT: 'For how many months do you want the loan? Choose from: 12, 24, 36, or 48 months.',
  INCOME_PROMPT: 'What is your monthly income?',
  FAMILY_INCOME_PROMPT: 'What is your family\'s monthly income?',
  EXPENSE_PROMPT: 'What are your monthly expenses?',
  FAMILY_EXPENSE_PROMPT: 'What are your family\'s monthly expenses?',
  
  ERRORS: {
    AGE_INVALID: `Sorry, you must be between ${LOAN_RULES.AGE.MIN} and ${LOAN_RULES.AGE.MAX} years old to be eligible for a loan.`,
    CREDIT_SCORE_INVALID: `Your credit score should be between ${LOAN_RULES.CREDIT_SCORE.MIN} and ${LOAN_RULES.CREDIT_SCORE.MAX} to be eligible.`,
    DOCUMENTS_INVALID: 'You need to have either (Voter ID + PAN) or (PAN + Driving License) to proceed.',
    PAN_INVALID: 'Please provide a valid PAN number in the format: AAAAA9999A',
    LOAN_AMOUNT_INVALID: `Loan amount should be between ₹${LOAN_RULES.LOAN_AMOUNT.MIN.toLocaleString()} and ₹${LOAN_RULES.LOAN_AMOUNT.MAX.toLocaleString()}.`,
    TENURE_INVALID: 'Please choose a valid tenure: 12, 24, 36, or 48 months.',
    EXPENSE_HIGH: 'Your expenses are more than 50% of your income. This may affect loan eligibility.',
    GENERAL_ERROR: 'I didn\'t understand that. Could you please try again?'
  }
};

module.exports = {
  LOAN_RULES,
  ROI_RATES,
  VALID_TENURES,
  DOCUMENT_COMBINATIONS,
  COMPANY_INFO,
  MESSAGES
};

