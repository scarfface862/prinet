
// rpi-server/routes/healthRoutes.js
const express = require('express');
const router = express.Router();
const healthService = require('../services/healthService');

// Basic health check
router.get('/', async (req, res) => {
  try {
    const result = await healthService.getSystemStatus();
    const statusCode = result.status === 'HEALTHY' ? 200 :
                      result.status === 'DEGRADED' ? 200 : 503;
    res.status(statusCode).json(result);
  } catch (error) {
    res.status(503).json({
      status: 'ERROR',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Detailed health check
router.get('/detailed', async (req, res) => {
  try {
    const result = await healthService.getDetailedHealth();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Readiness probe (for Kubernetes)
router.get('/ready', async (req, res) => {
  try {
    const result = await healthService.getSystemStatus();
    if (result.status === 'HEALTHY' || result.status === 'DEGRADED') {
      res.status(200).json({ ready: true });
    } else {
      res.status(503).json({ ready: false, reason: result.status });
    }
  } catch (error) {
    res.status(503).json({ ready: false, error: error.message });
  }
});

// Liveness probe (for Kubernetes)
router.get('/live', (req, res) => {
  res.status(200).json({
    alive: true,
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

module.exports = router;