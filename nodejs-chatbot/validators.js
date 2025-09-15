// Core business logic validators for Paisalo loan eligibility

const { LOAN_RULES, DOCUMENT_COMBINATIONS, MESSAGES } = require('./constants');
const { validatePAN } = require('./panValidator');

/**
 * Validates user age according to loan eligibility rules
 * @param {number} age - User's age
 * @returns {object} - Validation result
 */
function validateAge(age) {
  const numAge = parseInt(age);
  
  if (isNaN(numAge) || numAge < 0) {
    return {
      isValid: false,
      message: 'Please provide a valid age.'
    };
  }

  if (numAge < LOAN_RULES.AGE.MIN || numAge > LOAN_RULES.AGE.MAX) {
    return {
      isValid: false,
      message: MESSAGES.ERRORS.AGE_INVALID
    };
  }

  return {
    isValid: true,
    message: 'Age is eligible for loan.'
  };
}

/**
 * Validates credit score according to loan eligibility rules
 * ELIGIBLE if score < 18 OR score > 650
 * NOT ELIGIBLE if score is between 18-650 (inclusive)
 * @param {number} creditScore - User's credit score
 * @returns {object} - Validation result
 */
function validateCreditScore(creditScore) {
  const numScore = parseInt(creditScore);
  
  if (isNaN(numScore) || numScore < 0) {
    return {
      isValid: false,
      message: 'Please provide a valid credit score.'
    };
  }

  // Credit score is ELIGIBLE if < 18 OR > 650
  // Credit score is NOT ELIGIBLE if between 18-650 (inclusive)
  if (numScore < LOAN_RULES.CREDIT_SCORE.MIN || numScore > LOAN_RULES.CREDIT_SCORE.MAX) {
    return {
      isValid: true,
      message: `Credit score ${numScore} is eligible (outside 18-650 range).`
    };
  }

  return {
    isValid: false,
    message: `Credit score ${numScore} is not eligible. Score must be less than 18 or greater than 650.`
  };
}

/**
 * Validates loan amount according to company rules
 * @param {number} amount - Requested loan amount
 * @returns {object} - Validation result
 */
function validateLoanAmount(amount) {
  const numAmount = parseFloat(amount);
  
  if (isNaN(numAmount) || numAmount <= 0) {
    return {
      isValid: false,
      message: 'Please provide a valid loan amount.'
    };
  }

  if (numAmount < LOAN_RULES.LOAN_AMOUNT.MIN || numAmount > LOAN_RULES.LOAN_AMOUNT.MAX) {
    return {
      isValid: false,
      message: MESSAGES.ERRORS.LOAN_AMOUNT_INVALID
    };
  }

  return {
    isValid: true,
    message: 'Loan amount is within eligible range.'
  };
}

/**
 * Validates document combination according to company rules
 * @param {Array} documents - Array of document types user has
 * @returns {object} - Validation result
 */
function validateDocuments(documents) {
  if (!Array.isArray(documents) || documents.length === 0) {
    return {
      isValid: false,
      message: 'Please specify which documents you have.'
    };
  }

  // Normalize document names
  const normalizedDocs = documents.map(doc => 
    doc.toUpperCase().replace(/\s+/g, '_')
  );

  // Check if any valid combination exists
  const hasValidCombination = DOCUMENT_COMBINATIONS.VALID.some(validCombo => {
    return validCombo.every(requiredDoc => 
      normalizedDocs.some(userDoc => 
        userDoc.includes(requiredDoc) || requiredDoc.includes(userDoc)
      )
    );
  });

  if (!hasValidCombination) {
    return {
      isValid: false,
      message: MESSAGES.ERRORS.DOCUMENTS_INVALID
    };
  }

  return {
    isValid: true,
    message: 'Document combination is valid.'
  };
}

/**
 * Validates if user has PAN and validates PAN format if provided
 * @param {Array} documents - Array of document types
 * @param {string} panNumber - PAN number if provided
 * @returns {object} - Validation result
 */
function validatePANRequirement(documents, panNumber = null) {
  const normalizedDocs = documents.map(doc => 
    doc.toUpperCase().replace(/\s+/g, '_')
  );

  const hasPAN = normalizedDocs.some(doc => doc.includes('PAN'));

  if (!hasPAN) {
    return {
      isValid: false,
      message: 'PAN card is required for loan application.'
    };
  }

  if (panNumber) {
    if (!validatePAN(panNumber)) {
      return {
        isValid: false,
        message: MESSAGES.ERRORS.PAN_INVALID
      };
    }
  }

  return {
    isValid: true,
    message: panNumber ? 'PAN number is valid.' : 'PAN card requirement satisfied.'
  };
}

/**
 * Parses document list from user input
 * @param {string} input - User input containing document names
 * @returns {Array} - Array of document types
 */
function parseDocuments(input) {
  if (!input || typeof input !== 'string') {
    return [];
  }

  const documents = [];
  const lowerInput = input.toLowerCase();

  if (lowerInput.includes('voter') || lowerInput.includes('voter id')) {
    documents.push('VOTER_ID');
  }
  if (lowerInput.includes('pan')) {
    documents.push('PAN');
  }
  if (lowerInput.includes('dl') || lowerInput.includes('driving') || lowerInput.includes('license')) {
    documents.push('DL');
  }

  return documents;
}

module.exports = {
  validateAge,
  validateCreditScore,
  validateLoanAmount,
  validateDocuments,
  validatePANRequirement,
  parseDocuments
};
