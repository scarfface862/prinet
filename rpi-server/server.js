/**
 * RPI Server Mock for WAPRO Network
 * Main server file
 */

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const dotenv = require('dotenv');
const promClient = require('prom-client');

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const PORT_GUI = process.env.RPI_GUI_PORT || 8080;
const PORT_API = process.env.RPI_API_PORT || 8081;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(morgan('dev'));
app.use(express.static(path.join(__dirname, 'public')));

// Setup Prometheus metrics
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API metrics endpoint
app.get('/api/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// Basic API endpoint
app.get('/api/status', (req, res) => {
  res.json({
    name: 'RPI Server Mock',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString()
  });
});

// GUI homepage
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>RPI Server Mock</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #333; }
        .status { padding: 10px; background-color: #e7f7e7; border-radius: 5px; }
      </style>
    </head>
    <body>
      <h1>RPI Server Mock Interface</h1>
      <div class="status">
        <p><strong>Status:</strong> Running</p>
        <p><strong>Time:</strong> ${new Date().toLocaleString()}</p>
      </div>
      <h2>Available Endpoints:</h2>
      <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/api/status">API Status</a></li>
        <li><a href="/api/metrics">Metrics</a></li>
      </ul>
    </body>
    </html>
  `);
});

// Start servers
const guiServer = app.listen(PORT_GUI, () => {
  console.log(`GUI server running on port ${PORT_GUI}`);
});

const apiServer = app.listen(PORT_API, () => {
  console.log(`API server running on port ${PORT_API}`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP servers');
  guiServer.close(() => console.log('GUI server closed'));
  apiServer.close(() => console.log('API server closed'));
  process.exit(0);
});

module.exports = { app, guiServer, apiServer };