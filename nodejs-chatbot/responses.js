// Response templates and messages for the Paisalo loan chatbot

const { MESSAGES, COMPANY_INFO } = require('./constants');
const { formatEMIResult } = require('./emiCalculator');
const { formatIncomeAnalysis } = require('./incomeValidator');

/**
 * Creates a welcome response for new users
 * @returns {object} - Welcome response
 */
function createWelcomeResponse() {
  return {
    fulfillmentText: MESSAGES.WELCOME,
    fulfillmentMessages: [
      {
        text: {
          text: [MESSAGES.WELCOME]
        }
      },
      {
        text: {
          text: [`To check your loan eligibility, I'll need some information from you. ${MESSAGES.AGE_PROMPT}`]
        }
      }
    ]
  };
}

/**
 * Creates a response for successful loan eligibility
 * @param {object} userProfile - User's complete profile
 * @param {object} emiCalculation - EMI calculation result
 * @returns {object} - Success response
 */
function createEligibilitySuccessResponse(userProfile, emiCalculation) {
  const emiDetails = formatEMIResult(emiCalculation);
  
  const successMessage = `🎉 Congratulations! You are eligible for a loan from ${COMPANY_INFO.NAME}!\n\n${emiDetails}`;
  
  return {
    fulfillmentText: successMessage,
    fulfillmentMessages: [
      {
        text: {
          text: [successMessage]
        }
      },
      {
        text: {
          text: ['Would you like to proceed with the loan application or calculate EMI for a different amount/tenure?']
        }
      }
    ]
  };
}

/**
 * Creates a response for loan eligibility failure
 * @param {string} reason - Reason for eligibility failure
 * @returns {object} - Failure response
 */
function createEligibilityFailureResponse(reason) {
  const failureMessage = `❌ Sorry, you are not eligible for a loan at this time.\n\nReason: ${reason}`;
  
  return {
    fulfillmentText: failureMessage,
    fulfillmentMessages: [
      {
        text: {
          text: [failureMessage]
        }
      },
      {
        text: {
          text: [`Please contact our customer service for more information about improving your eligibility. Thank you for choosing ${COMPANY_INFO.NAME}!`]
        }
      }
    ]
  };
}

/**
 * Creates a response asking for specific information
 * @param {string} prompt - The prompt message
 * @param {string} context - Additional context if needed
 * @returns {object} - Information request response
 */
function createInfoRequestResponse(prompt, context = '') {
  const message = context ? `${context}\n\n${prompt}` : prompt;
  
  return {
    fulfillmentText: message,
    fulfillmentMessages: [
      {
        text: {
          text: [message]
        }
      }
    ]
  };
}

/**
 * Creates a response for validation errors
 * @param {string} errorMessage - Error message
 * @param {string} retryPrompt - Prompt to retry
 * @returns {object} - Error response
 */
function createValidationErrorResponse(errorMessage, retryPrompt) {
  const message = `${errorMessage}\n\n${retryPrompt}`;
  
  return {
    fulfillmentText: message,
    fulfillmentMessages: [
      {
        text: {
          text: [message]
        }
      }
    ]
  };
}

/**
 * Creates a response showing EMI calculation
 * @param {object} emiCalculation - EMI calculation result
 * @returns {object} - EMI display response
 */
function createEMIDisplayResponse(emiCalculation) {
  const emiDetails = formatEMIResult(emiCalculation);
  
  return {
    fulfillmentText: emiDetails,
    fulfillmentMessages: [
      {
        text: {
          text: [emiDetails]
        }
      },
      {
        text: {
          text: ['Would you like to calculate EMI for a different amount or tenure?']
        }
      }
    ]
  };
}

/**
 * Creates a response showing income analysis
 * @param {object} incomeAnalysis - Income analysis result
 * @returns {object} - Income analysis response
 */
function createIncomeAnalysisResponse(incomeAnalysis) {
  const analysisDetails = formatIncomeAnalysis(incomeAnalysis);
  
  return {
    fulfillmentText: analysisDetails,
    fulfillmentMessages: [
      {
        text: {
          text: [analysisDetails]
        }
      }
    ]
  };
}

/**
 * Creates a response for document verification
 * @param {boolean} isValid - Whether documents are valid
 * @param {string} message - Validation message
 * @returns {object} - Document verification response
 */
function createDocumentVerificationResponse(isValid, message) {
  const emoji = isValid ? '✅' : '❌';
  const responseMessage = `${emoji} ${message}`;
  
  return {
    fulfillmentText: responseMessage,
    fulfillmentMessages: [
      {
        text: {
          text: [responseMessage]
        }
      }
    ]
  };
}

/**
 * Creates a help response with available commands
 * @returns {object} - Help response
 */
function createHelpResponse() {
  const helpMessage = `
🤖 ${COMPANY_INFO.NAME} Loan Assistant Help

I can help you with:
• Check loan eligibility
• Calculate EMI using SLM method
• Validate your documents
• Analyze income vs expenses

Available loan tenures:
• 12 months (7% ROI)
• 24 months (9% ROI)
• 36 months (12% ROI)
• 48 months (18% ROI)

Loan amount: ₹50,000 to ₹1,00,000

Just tell me what you'd like to do!
  `.trim();
  
  return {
    fulfillmentText: helpMessage,
    fulfillmentMessages: [
      {
        text: {
          text: [helpMessage]
        }
      }
    ]
  };
}

/**
 * Creates a generic error response
 * @param {string} customMessage - Custom error message
 * @returns {object} - Error response
 */
function createErrorResponse(customMessage = null) {
  const message = customMessage || MESSAGES.ERRORS.GENERAL_ERROR;
  
  return {
    fulfillmentText: message,
    fulfillmentMessages: [
      {
        text: {
          text: [message]
        }
      },
      {
        text: {
          text: ['Type "help" to see what I can do for you.']
        }
      }
    ]
  };
}

module.exports = {
  createWelcomeResponse,
  createEligibilitySuccessResponse,
  createEligibilityFailureResponse,
  createInfoRequestResponse,
  createValidationErrorResponse,
  createEMIDisplayResponse,
  createIncomeAnalysisResponse,
  createDocumentVerificationResponse,
  createHelpResponse,
  createErrorResponse
};

