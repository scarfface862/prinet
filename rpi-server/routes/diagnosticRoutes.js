
// rpi-server/routes/diagnosticRoutes.js
const express = require('express');
const router = express.Router();
const diagnosticService = require('../services/diagnosticService');

// Run full diagnostics
router.get('/full', async (req, res) => {
  try {
    const result = await diagnosticService.runFullDiagnostics();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get last diagnostic results
router.get('/last', (req, res) => {
  try {
    const result = diagnosticService.getLastResults();
    if (!result || Object.keys(result).length === 0) {
      return res.status(404).json({ message: 'No diagnostic results available' });
    }
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Generate diagnostic report
router.get('/report', async (req, res) => {
  try {
    const result = await diagnosticService.generateReport();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Test network connectivity
router.get('/network', async (req, res) => {
  try {
    const result = await diagnosticService.testNetworkConnectivity();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Test database connections
router.get('/database', async (req, res) => {
  try {
    const result = await diagnosticService.testDatabaseConnections();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Test printer connections
router.get('/printers', async (req, res) => {
  try {
    const result = await diagnosticService.testPrinterConnections();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get system information
router.get('/system', async (req, res) => {
  try {
    const result = await diagnosticService.getSystemInfo();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
