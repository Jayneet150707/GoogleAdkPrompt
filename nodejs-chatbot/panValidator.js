// PAN number validation using regex for Indian PAN format

/**
 * Validates Indian PAN number format
 * Format: AAAAA9999A (5 letters + 4 digits + 1 letter)
 * @param {string} pan - PAN number to validate
 * @returns {boolean} - true if valid, false otherwise
 */
function validatePAN(pan) {
  if (!pan || typeof pan !== 'string') {
    return false;
  }

  // Remove spaces and convert to uppercase
  const cleanPAN = pan.replace(/\s/g, '').toUpperCase();
  
  // Indian PAN regex pattern: 5 letters + 4 digits + 1 letter
  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
  
  return panRegex.test(cleanPAN);
}

/**
 * Formats PAN number for display
 * @param {string} pan - PAN number to format
 * @returns {string} - formatted PAN number
 */
function formatPAN(pan) {
  if (!validatePAN(pan)) {
    return pan;
  }
  
  const cleanPAN = pan.replace(/\s/g, '').toUpperCase();
  return cleanPAN;
}

/**
 * Gets detailed PAN validation result with error message
 * @param {string} pan - PAN number to validate
 * @returns {object} - validation result with isValid and message
 */
function validatePANDetailed(pan) {
  if (!pan || typeof pan !== 'string') {
    return {
      isValid: false,
      message: 'PAN number is required'
    };
  }

  const cleanPAN = pan.replace(/\s/g, '').toUpperCase();
  
  if (cleanPAN.length !== 10) {
    return {
      isValid: false,
      message: 'PAN number must be exactly 10 characters long'
    };
  }

  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
  
  if (!panRegex.test(cleanPAN)) {
    return {
      isValid: false,
      message: 'PAN number format is invalid. It should be in format: AAAAA9999A (5 letters + 4 digits + 1 letter)'
    };
  }

  return {
    isValid: true,
    message: 'Valid PAN number',
    formattedPAN: cleanPAN
  };
}

module.exports = {
  validatePAN,
  formatPAN,
  validatePANDetailed
};

