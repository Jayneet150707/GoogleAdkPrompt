/**
 * Paisalo Google AdK Chatbot Server
 * Handles loan eligibility conversations with Google AdK integration
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const PaisaloAdkChatbot = require('./src/chatbot');
const logger = require('./src/utils/logger');
const { validateRequest } = require('./src/middleware/validation');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize chatbot
const chatbot = new PaisaloAdkChatbot();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  req.requestId = uuidv4();
  logger.info(`${req.method} ${req.path}`, {
    requestId: req.requestId,
    userAgent: req.get('User-Agent'),
    ip: req.ip
  });
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Paisalo Google AdK Chatbot',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Google AdK webhook endpoint
app.post('/webhook', validateRequest, async (req, res) => {
  try {
    const response = await chatbot.handleAdkRequest(req.body, req.requestId);
    
    logger.info('AdK request processed successfully', {
      requestId: req.requestId,
      sessionId: req.body.sessionId || 'unknown'
    });
    
    res.json(response);
  } catch (error) {
    logger.error('Error processing AdK request', {
      requestId: req.requestId,
      error: error.message,
      stack: error.stack
    });
    
    res.status(500).json({
      fulfillmentText: 'Sorry, I encountered an error. Please try again.',
      source: 'paisalo-adk-chatbot'
    });
  }
});

// Test endpoint for development
app.post('/test', async (req, res) => {
  try {
    const { message, sessionId = uuidv4() } = req.body;
    
    const response = await chatbot.handleTestMessage(message, sessionId);
    
    res.json({
      sessionId,
      response: response.fulfillmentText,
      step: response.step,
      data: response.data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Error in test endpoint', {
      requestId: req.requestId,
      error: error.message
    });
    
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error', {
    requestId: req.requestId,
    error: error.message,
    stack: error.stack
  });
  
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.requestId
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.path,
    method: req.method
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Paisalo Google AdK Chatbot server running on port ${PORT}`);
  console.log(`🚀 Paisalo Google AdK Chatbot server running on port ${PORT}`);
  console.log(`📋 Health check: http://localhost:${PORT}/health`);
  console.log(`🧪 Test endpoint: http://localhost:${PORT}/test`);
  console.log(`🔗 AdK webhook: http://localhost:${PORT}/webhook`);
});

module.exports = app;

