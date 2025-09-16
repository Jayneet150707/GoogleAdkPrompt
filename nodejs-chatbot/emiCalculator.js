// EMI Calculator using SLM (Straight Line Method) for Paisalo loans

const { ROI_RATES, VALID_TENURES } = require('./constants');

/**
 * Calculates EMI using Straight Line Method (SLM)
 * SLM Formula: EMI = (Principal + (Principal * ROI * Tenure)) / (Tenure * 12)
 * @param {number} principal - Loan amount
 * @param {number} tenureMonths - Loan tenure in months
 * @returns {object} - EMI calculation result
 */
function calculateEMI(principal, tenureMonths) {
  // Validate inputs
  if (!principal || !tenureMonths) {
    return {
      success: false,
      message: 'Principal amount and tenure are required.'
    };
  }

  const numPrincipal = parseFloat(principal);
  const numTenure = parseInt(tenureMonths);

  if (isNaN(numPrincipal) || numPrincipal <= 0) {
    return {
      success: false,
      message: 'Please provide a valid loan amount.'
    };
  }

  if (!VALID_TENURES.includes(numTenure)) {
    return {
      success: false,
      message: `Invalid tenure. Please choose from: ${VALID_TENURES.join(', ')} months.`
    };
  }

  // Get ROI rate for the tenure
  const roiRate = ROI_RATES[numTenure];
  if (!roiRate) {
    return {
      success: false,
      message: 'ROI rate not found for the selected tenure.'
    };
  }

  // Calculate using SLM method
  const roiDecimal = roiRate / 100; // Convert percentage to decimal
  const totalInterest = numPrincipal * roiDecimal * (numTenure / 12); // Annual interest calculation
  const totalAmount = numPrincipal + totalInterest;
  const emi = totalAmount / numTenure;

  return {
    success: true,
    calculation: {
      principal: numPrincipal,
      tenure: numTenure,
      roiRate: roiRate,
      totalInterest: Math.round(totalInterest * 100) / 100,
      totalAmount: Math.round(totalAmount * 100) / 100,
      emi: Math.round(emi * 100) / 100
    },
    message: `EMI calculated successfully for ${numTenure} months at ${roiRate}% ROI.`
  };
}

/**
 * Gets ROI rate for a specific tenure
 * @param {number} tenureMonths - Loan tenure in months
 * @returns {object} - ROI information
 */
function getROIRate(tenureMonths) {
  const numTenure = parseInt(tenureMonths);
  
  if (!VALID_TENURES.includes(numTenure)) {
    return {
      success: false,
      message: `Invalid tenure. Available tenures: ${VALID_TENURES.join(', ')} months.`
    };
  }

  return {
    success: true,
    tenure: numTenure,
    roiRate: ROI_RATES[numTenure],
    message: `ROI rate for ${numTenure} months is ${ROI_RATES[numTenure]}%.`
  };
}

/**
 * Gets all available tenure options with their ROI rates
 * @returns {object} - All tenure and ROI information
 */
function getAllTenureOptions() {
  const options = VALID_TENURES.map(tenure => ({
    tenure: tenure,
    roiRate: ROI_RATES[tenure],
    description: `${tenure} months at ${ROI_RATES[tenure]}% ROI`
  }));

  return {
    success: true,
    options: options,
    message: 'Available tenure options with ROI rates.'
  };
}

/**
 * Validates tenure selection
 * @param {number} tenureMonths - Selected tenure
 * @returns {object} - Validation result
 */
function validateTenure(tenureMonths) {
  const numTenure = parseInt(tenureMonths);
  
  if (isNaN(numTenure)) {
    return {
      isValid: false,
      message: 'Please provide a valid tenure in months.'
    };
  }

  if (!VALID_TENURES.includes(numTenure)) {
    return {
      isValid: false,
      message: `Invalid tenure. Please choose from: ${VALID_TENURES.join(', ')} months.`,
      availableOptions: getAllTenureOptions().options
    };
  }

  return {
    isValid: true,
    tenure: numTenure,
    roiRate: ROI_RATES[numTenure],
    message: `Valid tenure selected: ${numTenure} months at ${ROI_RATES[numTenure]}% ROI.`
  };
}

/**
 * Formats EMI calculation result for display
 * @param {object} calculation - EMI calculation result
 * @returns {string} - Formatted display string
 */
function formatEMIResult(calculation) {
  if (!calculation || !calculation.success) {
    return 'EMI calculation failed.';
  }

  const calc = calculation.calculation;
  return `
📊 EMI Calculation Summary:
💰 Loan Amount: ₹${calc.principal.toLocaleString()}
📅 Tenure: ${calc.tenure} months
📈 ROI Rate: ${calc.roiRate}%
💸 Monthly EMI: ₹${calc.emi.toLocaleString()}
💵 Total Interest: ₹${calc.totalInterest.toLocaleString()}
💳 Total Amount: ₹${calc.totalAmount.toLocaleString()}
  `.trim();
}

module.exports = {
  calculateEMI,
  getROIRate,
  getAllTenureOptions,
  validateTenure,
  formatEMIResult
};

