// Main server file for Paisalo Google AdK Chatbot

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { handleConversation } = require('./conversationHandler');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'success',
    message: 'Paisalo Loan Chatbot is running!',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Health check endpoint for monitoring
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'paisalo-loan-chatbot',
    timestamp: new Date().toISOString()
  });
});

// Main webhook endpoint for Google Assistant
app.post('/webhook', (req, res) => {
  try {
    console.log('Received webhook request:', JSON.stringify(req.body, null, 2));
    
    // Handle the conversation
    const response = handleConversation(req.body);
    
    console.log('Sending response:', JSON.stringify(response, null, 2));
    
    res.json(response);
  } catch (error) {
    console.error('Error in webhook:', error);
    
    res.status(500).json({
      fulfillmentText: 'Sorry, I encountered an error. Please try again.',
      fulfillmentMessages: [
        {
          text: {
            text: ['Sorry, I encountered an error. Please try again.']
          }
        }
      ]
    });
  }
});

// Test endpoint for manual testing
app.post('/test', (req, res) => {
  try {
    const { message, sessionId = 'test-session' } = req.body;
    
    if (!message) {
      return res.status(400).json({
        error: 'Message is required',
        example: {
          message: 'Hello',
          sessionId: 'optional-session-id'
        }
      });
    }
    
    // Create a mock request similar to Google Assistant format
    const mockRequest = {
      session: sessionId,
      queryResult: {
        queryText: message,
        intent: {
          displayName: message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi') ? 'Default Welcome Intent' : ''
        }
      }
    };
    
    const response = handleConversation(mockRequest);
    
    res.json({
      userMessage: message,
      botResponse: response.fulfillmentText,
      fullResponse: response
    });
    
  } catch (error) {
    console.error('Error in test endpoint:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// API documentation endpoint
app.get('/api-docs', (req, res) => {
  res.json({
    title: 'Paisalo Loan Chatbot API',
    version: '1.0.0',
    description: 'Google AdK chatbot for loan eligibility and EMI calculation',
    endpoints: {
      'GET /': 'Service status',
      'GET /health': 'Health check',
      'POST /webhook': 'Google Assistant webhook (main endpoint)',
      'POST /test': 'Test endpoint for manual testing',
      'GET /api-docs': 'This documentation'
    },
    testEndpoint: {
      url: '/test',
      method: 'POST',
      body: {
        message: 'Hello',
        sessionId: 'optional-session-id'
      }
    },
    features: [
      'Age validation (21-57 years)',
      'Credit score validation (18-650)',
      'Document verification (Voter+PAN or PAN+DL)',
      'PAN number validation with regex',
      'Loan amount validation (₹50,000 - ₹1,00,000)',
      'EMI calculation using SLM method',
      'Income/expense ratio validation (max 50%)',
      'Multiple tenure options with different ROI rates'
    ],
    roiRates: {
      '12 months': '7%',
      '24 months': '9%',
      '36 months': '12%',
      '48 months': '18%'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: 'Something went wrong!'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: 'Endpoint not found',
    availableEndpoints: ['/', '/health', '/webhook', '/test', '/api-docs']
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Paisalo Loan Chatbot server is running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🧪 Test endpoint: http://localhost:${PORT}/test`);
  console.log(`📚 API docs: http://localhost:${PORT}/api-docs`);
  console.log(`🤖 Webhook endpoint: http://localhost:${PORT}/webhook`);
});

module.exports = app;

