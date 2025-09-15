/**
 * Paisalo Google ADK Integration Example
 * Android Client for Loan Processing API
 * 
 * Company: Paisalo
 * This example shows how to integrate with the Paisalo Google ADK Agent
 */

package com.paisalo.loanagent;

import android.os.AsyncTask;
import android.util.Log;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class PaisaloLoanClient {
    
    private static final String TAG = "PaisaloLoanClient";
    private static final String BASE_URL = "http://your-server:5000/api";
    
    // Loan request data model
    public static class LoanRequest {
        public int age;
        public int creditScore;
        public double income;
        public double expense;
        public double familyIncome;
        public double familyExpense;
        public List<String> documents;
        public String panNumber;
        public double loanAmount;
        public int tenureMonths;
        
        public LoanRequest() {
            this.documents = new ArrayList<>();
        }
        
        public JSONObject toJSON() throws JSONException {
            JSONObject json = new JSONObject();
            json.put("age", age);
            json.put("credit_score", creditScore);
            json.put("income", income);
            json.put("expense", expense);
            json.put("family_income", familyIncome);
            json.put("family_expense", familyExpense);
            json.put("documents", new org.json.JSONArray(documents));
            json.put("pan_number", panNumber);
            json.put("loan_amount", loanAmount);
            json.put("tenure_months", tenureMonths);
            return json;
        }
    }
    
    // Loan response data model
    public static class LoanResponse {
        public String status;
        public String message;
        public Double emi;
        public Double roi;
        public Double totalAmount;
        
        public static LoanResponse fromJSON(JSONObject json) throws JSONException {
            LoanResponse response = new LoanResponse();
            JSONObject data = json.getJSONObject("data");
            
            response.status = data.getString("status");
            response.message = data.getString("message");
            
            if (data.has("emi") && !data.isNull("emi")) {
                response.emi = data.getDouble("emi");
            }
            if (data.has("roi") && !data.isNull("roi")) {
                response.roi = data.getDouble("roi");
            }
            if (data.has("total_amount") && !data.isNull("total_amount")) {
                response.totalAmount = data.getDouble("total_amount");
            }
            
            return response;
        }
    }
    
    // Interface for loan processing callbacks
    public interface LoanProcessingCallback {
        void onSuccess(LoanResponse response);
        void onError(String error);
    }
    
    // Interface for EMI calculation callbacks
    public interface EMICalculationCallback {
        void onSuccess(double emi, double totalAmount, double interest);
        void onError(String error);
    }
    
    // Interface for PAN validation callbacks
    public interface PANValidationCallback {
        void onResult(boolean isValid, String message);
        void onError(String error);
    }
    
    /**
     * Process loan application
     */
    public void processLoanApplication(LoanRequest request, LoanProcessingCallback callback) {
        new ProcessLoanTask(callback).execute(request);
    }
    
    /**
     * Calculate EMI for given amount and tenure
     */
    public void calculateEMI(double principal, int tenureMonths, EMICalculationCallback callback) {
        new CalculateEMITask(callback).execute(principal, (double) tenureMonths);
    }
    
    /**
     * Validate PAN number
     */
    public void validatePAN(String panNumber, PANValidationCallback callback) {
        new ValidatePANTask(callback).execute(panNumber);
    }
    
    /**
     * Get loan rules from server
     */
    public void getLoanRules(LoanRulesCallback callback) {
        new GetLoanRulesTask(callback).execute();
    }
    
    public interface LoanRulesCallback {
        void onSuccess(JSONObject rules);
        void onError(String error);
    }
    
    // AsyncTask for processing loan application
    private class ProcessLoanTask extends AsyncTask<LoanRequest, Void, String> {
        private LoanProcessingCallback callback;
        private Exception exception;
        
        public ProcessLoanTask(LoanProcessingCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected String doInBackground(LoanRequest... requests) {
            try {
                LoanRequest request = requests[0];
                return makePostRequest("/loan/process", request.toJSON().toString());
            } catch (Exception e) {
                this.exception = e;
                return null;
            }
        }
        
        @Override
        protected void onPostExecute(String result) {
            if (exception != null) {
                callback.onError("Network error: " + exception.getMessage());
                return;
            }
            
            try {
                JSONObject json = new JSONObject(result);
                if ("success".equals(json.getString("status"))) {
                    LoanResponse response = LoanResponse.fromJSON(json);
                    callback.onSuccess(response);
                } else {
                    callback.onError(json.getString("message"));
                }
            } catch (JSONException e) {
                callback.onError("JSON parsing error: " + e.getMessage());
            }
        }
    }
    
    // AsyncTask for EMI calculation
    private class CalculateEMITask extends AsyncTask<Double, Void, String> {
        private EMICalculationCallback callback;
        private Exception exception;
        
        public CalculateEMITask(EMICalculationCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected String doInBackground(Double... params) {
            try {
                double principal = params[0];
                int tenure = params[1].intValue();
                
                JSONObject requestData = new JSONObject();
                requestData.put("principal", principal);
                requestData.put("tenure_months", tenure);
                
                return makePostRequest("/loan/calculate-emi", requestData.toString());
            } catch (Exception e) {
                this.exception = e;
                return null;
            }
        }
        
        @Override
        protected void onPostExecute(String result) {
            if (exception != null) {
                callback.onError("Network error: " + exception.getMessage());
                return;
            }
            
            try {
                JSONObject json = new JSONObject(result);
                if ("success".equals(json.getString("status"))) {
                    JSONObject data = json.getJSONObject("data");
                    double emi = data.getDouble("monthly_emi");
                    double totalAmount = data.getDouble("total_amount");
                    double interest = data.getDouble("total_interest");
                    callback.onSuccess(emi, totalAmount, interest);
                } else {
                    callback.onError(json.getString("message"));
                }
            } catch (JSONException e) {
                callback.onError("JSON parsing error: " + e.getMessage());
            }
        }
    }
    
    // AsyncTask for PAN validation
    private class ValidatePANTask extends AsyncTask<String, Void, String> {
        private PANValidationCallback callback;
        private Exception exception;
        
        public ValidatePANTask(PANValidationCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected String doInBackground(String... params) {
            try {
                String panNumber = params[0];
                
                JSONObject requestData = new JSONObject();
                requestData.put("pan_number", panNumber);
                
                return makePostRequest("/validate/pan", requestData.toString());
            } catch (Exception e) {
                this.exception = e;
                return null;
            }
        }
        
        @Override
        protected void onPostExecute(String result) {
            if (exception != null) {
                callback.onError("Network error: " + exception.getMessage());
                return;
            }
            
            try {
                JSONObject json = new JSONObject(result);
                if ("success".equals(json.getString("status"))) {
                    JSONObject data = json.getJSONObject("data");
                    boolean isValid = data.getBoolean("is_valid");
                    String message = data.getString("message");
                    callback.onResult(isValid, message);
                } else {
                    callback.onError(json.getString("message"));
                }
            } catch (JSONException e) {
                callback.onError("JSON parsing error: " + e.getMessage());
            }
        }
    }
    
    // AsyncTask for getting loan rules
    private class GetLoanRulesTask extends AsyncTask<Void, Void, String> {
        private LoanRulesCallback callback;
        private Exception exception;
        
        public GetLoanRulesTask(LoanRulesCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected String doInBackground(Void... params) {
            try {
                return makeGetRequest("/loan/rules");
            } catch (Exception e) {
                this.exception = e;
                return null;
            }
        }
        
        @Override
        protected void onPostExecute(String result) {
            if (exception != null) {
                callback.onError("Network error: " + exception.getMessage());
                return;
            }
            
            try {
                JSONObject json = new JSONObject(result);
                if ("success".equals(json.getString("status"))) {
                    callback.onSuccess(json.getJSONObject("data"));
                } else {
                    callback.onError(json.getString("message"));
                }
            } catch (JSONException e) {
                callback.onError("JSON parsing error: " + e.getMessage());
            }
        }
    }
    
    // Helper method for POST requests
    private String makePostRequest(String endpoint, String jsonData) throws IOException {
        URL url = new URL(BASE_URL + endpoint);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        
        // Send request
        try (OutputStream os = connection.getOutputStream()) {
            byte[] input = jsonData.getBytes("utf-8");
            os.write(input, 0, input.length);
        }
        
        // Read response
        StringBuilder response = new StringBuilder();
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(connection.getInputStream(), "utf-8"))) {
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
        }
        
        return response.toString();
    }
    
    // Helper method for GET requests
    private String makeGetRequest(String endpoint) throws IOException {
        URL url = new URL(BASE_URL + endpoint);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        
        connection.setRequestMethod("GET");
        connection.setRequestProperty("Accept", "application/json");
        
        // Read response
        StringBuilder response = new StringBuilder();
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(connection.getInputStream(), "utf-8"))) {
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
        }
        
        return response.toString();
    }
}

/**
 * Example usage in Android Activity
 */
class ExampleActivity {
    
    private PaisaloLoanClient loanClient;
    
    public void initializeLoanClient() {
        loanClient = new PaisaloLoanClient();
    }
    
    public void processLoanExample() {
        // Create loan request
        PaisaloLoanClient.LoanRequest request = new PaisaloLoanClient.LoanRequest();
        request.age = 35;
        request.creditScore = 700; // >650, so valid
        request.income = 60000;
        request.expense = 25000;
        request.familyIncome = 40000;
        request.familyExpense = 15000;
        request.documents.add("VOTER");
        request.documents.add("PAN");
        request.panNumber = "ABCDE1234F";
        request.loanAmount = 75000;
        request.tenureMonths = 24;
        
        // Process loan application
        loanClient.processLoanApplication(request, new PaisaloLoanClient.LoanProcessingCallback() {
            @Override
            public void onSuccess(PaisaloLoanClient.LoanResponse response) {
                Log.d("LoanResult", "Status: " + response.status);
                Log.d("LoanResult", "Message: " + response.message);
                
                if ("APPROVED".equals(response.status)) {
                    Log.d("LoanResult", "EMI: ₹" + response.emi);
                    Log.d("LoanResult", "ROI: " + response.roi + "%");
                    Log.d("LoanResult", "Total: ₹" + response.totalAmount);
                    
                    // Update UI with loan approval details
                    updateUIWithApproval(response);
                } else {
                    // Show rejection message
                    showRejectionMessage(response.message);
                }
            }
            
            @Override
            public void onError(String error) {
                Log.e("LoanResult", "Error: " + error);
                showErrorMessage(error);
            }
        });
    }
    
    public void calculateEMIExample() {
        loanClient.calculateEMI(75000, 24, new PaisaloLoanClient.EMICalculationCallback() {
            @Override
            public void onSuccess(double emi, double totalAmount, double interest) {
                Log.d("EMIResult", "EMI: ₹" + emi);
                Log.d("EMIResult", "Total: ₹" + totalAmount);
                Log.d("EMIResult", "Interest: ₹" + interest);
                
                // Update UI with EMI details
                updateEMIDisplay(emi, totalAmount, interest);
            }
            
            @Override
            public void onError(String error) {
                Log.e("EMIResult", "Error: " + error);
                showErrorMessage(error);
            }
        });
    }
    
    public void validatePANExample() {
        loanClient.validatePAN("ABCDE1234F", new PaisaloLoanClient.PANValidationCallback() {
            @Override
            public void onResult(boolean isValid, String message) {
                Log.d("PANResult", "Valid: " + isValid + ", Message: " + message);
                
                if (isValid) {
                    showPANValidMessage();
                } else {
                    showPANInvalidMessage(message);
                }
            }
            
            @Override
            public void onError(String error) {
                Log.e("PANResult", "Error: " + error);
                showErrorMessage(error);
            }
        });
    }
    
    // UI update methods (implement based on your UI framework)
    private void updateUIWithApproval(PaisaloLoanClient.LoanResponse response) {
        // Update your Android UI with loan approval details
    }
    
    private void showRejectionMessage(String message) {
        // Show rejection message in your Android UI
    }
    
    private void showErrorMessage(String error) {
        // Show error message in your Android UI
    }
    
    private void updateEMIDisplay(double emi, double totalAmount, double interest) {
        // Update EMI display in your Android UI
    }
    
    private void showPANValidMessage() {
        // Show PAN valid message in your Android UI
    }
    
    private void showPANInvalidMessage(String message) {
        // Show PAN invalid message in your Android UI
    }
}
