
// rpi-server/routes/zebraRoutes.js
const express = require('express');
const router = express.Router();
const zebraService = require('../services/zebraService');
const Joi = require('joi');

// Validation schemas
const commandSchema = Joi.object({
  printerId: Joi.string().valid('zebra-1', 'zebra-2').required(),
  command: Joi.string().required().min(1).max(10000)
});

const printerIdSchema = Joi.object({
  printerId: Joi.string().valid('zebra-1', 'zebra-2').required()
});

// Test connection to printer
router.get('/test/:printerId', async (req, res) => {
  try {
    const { error, value } = printerIdSchema.validate(req.params);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await zebraService.testConnection(value.printerId);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Send command to printer
router.post('/command', async (req, res) => {
  try {
    const { error, value } = commandSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await zebraService.sendCommand(value.printerId, value.command);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get printer status
router.get('/status/:printerId', async (req, res) => {
  try {
    const { error, value } = printerIdSchema.validate(req.params);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await zebraService.getPrinterStatus(value.printerId);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all printers status
router.get('/status', async (req, res) => {
  try {
    const result = await zebraService.getAllPrintersStatus();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Print test label
router.post('/test-print/:printerId', async (req, res) => {
  try {
    const { error, value } = printerIdSchema.validate(req.params);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await zebraService.printTestLabel(value.printerId);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Common ZPL commands
router.get('/commands', (req, res) => {
  const commands = {
    'host_identification': '~HI',
    'host_status': '~HS',
    'configuration': '^WD',
    'ping': 'PING',
    'test_label': `^XA
^FO50,50^A0N,50,50^FDTest Label^FS
^FO50,120^A0N,30,30^FDTimestamp: ${new Date().toISOString()}^FS
^XZ`,
    'barcode_test': `^XA
^FO50,50^BY3
^BCN,100,Y,N,N
^FD123456789^FS
^XZ`
  };

  res.json(commands);
});

module.exports = router;
