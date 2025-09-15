// Income and expense validation for loan eligibility

const { LOAN_RULES } = require('./constants');

/**
 * Validates income amount
 * @param {number} income - Monthly income amount
 * @returns {object} - Validation result
 */
function validateIncome(income) {
  const numIncome = parseFloat(income);
  
  if (isNaN(numIncome) || numIncome <= 0) {
    return {
      isValid: false,
      message: 'Please provide a valid monthly income amount.'
    };
  }

  return {
    isValid: true,
    income: numIncome,
    message: 'Income amount is valid.'
  };
}

/**
 * Validates expense amount
 * @param {number} expense - Monthly expense amount
 * @returns {object} - Validation result
 */
function validateExpense(expense) {
  const numExpense = parseFloat(expense);
  
  if (isNaN(numExpense) || numExpense < 0) {
    return {
      isValid: false,
      message: 'Please provide a valid monthly expense amount.'
    };
  }

  return {
    isValid: true,
    expense: numExpense,
    message: 'Expense amount is valid.'
  };
}

/**
 * Validates income to expense ratio according to company rules
 * @param {number} income - Monthly income
 * @param {number} expense - Monthly expense
 * @returns {object} - Validation result
 */
function validateIncomeExpenseRatio(income, expense) {
  const incomeValidation = validateIncome(income);
  const expenseValidation = validateExpense(expense);

  if (!incomeValidation.isValid) {
    return incomeValidation;
  }

  if (!expenseValidation.isValid) {
    return expenseValidation;
  }

  const numIncome = incomeValidation.income;
  const numExpense = expenseValidation.expense;

  // Calculate expense percentage
  const expensePercentage = (numExpense / numIncome) * 100;
  const maxAllowedPercentage = LOAN_RULES.INCOME_EXPENSE_RATIO.MAX_EXPENSE_PERCENTAGE;

  if (expensePercentage > maxAllowedPercentage) {
    return {
      isValid: false,
      income: numIncome,
      expense: numExpense,
      expensePercentage: Math.round(expensePercentage * 100) / 100,
      maxAllowedPercentage: maxAllowedPercentage,
      message: `Your expenses (${Math.round(expensePercentage)}%) exceed ${maxAllowedPercentage}% of your income. This may affect loan eligibility.`,
      warning: true
    };
  }

  return {
    isValid: true,
    income: numIncome,
    expense: numExpense,
    expensePercentage: Math.round(expensePercentage * 100) / 100,
    maxAllowedPercentage: maxAllowedPercentage,
    message: `Income to expense ratio is healthy (${Math.round(expensePercentage)}% of income).`
  };
}

/**
 * Calculates disposable income after expenses
 * @param {number} income - Monthly income
 * @param {number} expense - Monthly expense
 * @returns {object} - Disposable income calculation
 */
function calculateDisposableIncome(income, expense) {
  const validation = validateIncomeExpenseRatio(income, expense);
  
  if (!validation.isValid && !validation.warning) {
    return validation;
  }

  const disposableIncome = validation.income - validation.expense;
  const disposablePercentage = (disposableIncome / validation.income) * 100;

  return {
    success: true,
    income: validation.income,
    expense: validation.expense,
    disposableIncome: disposableIncome,
    disposablePercentage: Math.round(disposablePercentage * 100) / 100,
    expensePercentage: validation.expensePercentage,
    isHealthyRatio: validation.isValid,
    message: `Disposable income: ₹${disposableIncome.toLocaleString()} (${Math.round(disposablePercentage)}% of income)`
  };
}

/**
 * Suggests maximum EMI based on disposable income
 * @param {number} income - Monthly income
 * @param {number} expense - Monthly expense
 * @param {number} safetyMargin - Safety margin percentage (default 20%)
 * @returns {object} - EMI suggestion
 */
function suggestMaxEMI(income, expense, safetyMargin = 20) {
  const disposableCalc = calculateDisposableIncome(income, expense);
  
  if (!disposableCalc.success) {
    return disposableCalc;
  }

  // Calculate safe EMI amount (disposable income minus safety margin)
  const safetyAmount = (disposableCalc.disposableIncome * safetyMargin) / 100;
  const suggestedMaxEMI = disposableCalc.disposableIncome - safetyAmount;

  return {
    success: true,
    disposableIncome: disposableCalc.disposableIncome,
    safetyMargin: safetyMargin,
    safetyAmount: Math.round(safetyAmount * 100) / 100,
    suggestedMaxEMI: Math.round(suggestedMaxEMI * 100) / 100,
    message: `Based on your income, suggested maximum EMI: ₹${Math.round(suggestedMaxEMI).toLocaleString()} (with ${safetyMargin}% safety margin)`
  };
}

/**
 * Formats income/expense analysis for display
 * @param {object} analysis - Income/expense analysis result
 * @returns {string} - Formatted display string
 */
function formatIncomeAnalysis(analysis) {
  if (!analysis.success && !analysis.warning) {
    return analysis.message;
  }

  return `
💰 Income Analysis:
📊 Monthly Income: ₹${analysis.income.toLocaleString()}
💸 Monthly Expenses: ₹${analysis.expense.toLocaleString()}
📈 Expense Ratio: ${analysis.expensePercentage}%
💵 Disposable Income: ₹${(analysis.income - analysis.expense).toLocaleString()}
${analysis.isValid ? '✅ Healthy income-expense ratio' : '⚠️ High expense ratio - may affect eligibility'}
  `.trim();
}

module.exports = {
  validateIncome,
  validateExpense,
  validateIncomeExpenseRatio,
  calculateDisposableIncome,
  suggestMaxEMI,
  formatIncomeAnalysis
};

