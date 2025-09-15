#!/usr/bin/env node
/**
 * Quick test to verify credit score validation fix in Node.js
 */

const LOAN_RULES = {
  CREDIT_SCORE: {
    MIN: 18,
    MAX: 650
  }
};

/**
 * Validates credit score according to loan eligibility rules
 * ELIGIBLE if score < 18 OR score > 650
 * NOT ELIGIBLE if score is between 18-650 (inclusive)
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

function testCreditScoreValidation() {
  console.log('🧪 Testing Credit Score Validation Fix (Node.js)');
  console.log('='.repeat(50));
  
  // Test cases that should be ELIGIBLE (< 18 or > 650)
  console.log('✅ ELIGIBLE Scores (< 18 or > 650):');
  const eligibleScores = [0, 5, 10, 17, 651, 700, 800, 1000];
  eligibleScores.forEach(score => {
    const result = validateCreditScore(score);
    const status = result.isValid ? '✅ PASS' : '❌ FAIL';
    console.log(`  Score ${score.toString().padStart(4)}: ${status} - ${result.message}`);
  });
  
  console.log('\n❌ NOT ELIGIBLE Scores (18-650 inclusive):');
  // Test cases that should be NOT ELIGIBLE (18-650 inclusive)
  const notEligibleScores = [18, 50, 100, 300, 500, 650];
  notEligibleScores.forEach(score => {
    const result = validateCreditScore(score);
    const status = !result.isValid ? '✅ PASS' : '❌ FAIL';
    console.log(`  Score ${score.toString().padStart(4)}: ${status} - ${result.message}`);
  });
  
  console.log('\n🔍 Edge Cases:');
  // Test edge cases
  const edgeCases = [-10, -1, 'abc', ''];
  edgeCases.forEach(score => {
    const result = validateCreditScore(score);
    const status = !result.isValid ? '✅ PASS' : '❌ FAIL';
    console.log(`  Score ${score.toString().padStart(4)}: ${status} - ${result.message}`);
  });
  
  console.log('\n🎯 Summary:');
  console.log('- Scores < 18: ELIGIBLE for loan');
  console.log('- Scores > 650: ELIGIBLE for loan');
  console.log('- Scores 18-650: NOT ELIGIBLE for loan');
  console.log('- Invalid scores: Invalid format');
}

if (require.main === module) {
  testCreditScoreValidation();
}

