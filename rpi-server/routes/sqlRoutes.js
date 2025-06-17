// rpi-server/routes/sqlRoutes.js
const express = require('express');
const router = express.Router();
const sqlService = require('../services/sqlService');
const Joi = require('joi');

// Validation schemas
const querySchema = Joi.object({
  database: Joi.string().valid('wapromag').default('wapromag'),
  query: Joi.string().required().min(1).max(5000)
});

const tableSchema = Joi.object({
  database: Joi.string().valid('wapromag').default('wapromag'),
  tableName: Joi.string().required().pattern(/^[a-zA-Z_][a-zA-Z0-9_]*$/)
});

// Test connection
router.get('/test/:database?', async (req, res) => {
  try {
    const database = req.params.database || 'wapromag';
    const result = await sqlService.testConnection(database);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Execute query
router.post('/query', async (req, res) => {
  try {
    const { error, value } = querySchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await sqlService.executeQuery(value.database, value.query);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get tables list
router.get('/tables/:database?', async (req, res) => {
  try {
    const database = req.params.database || 'wapromag';
    const result = await sqlService.getTablesList(database);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get table schema
router.get('/schema/:database/:tableName', async (req, res) => {
  try {
    const { error, value } = tableSchema.validate(req.params);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await sqlService.getTableSchema(value.database, value.tableName);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get sample data
router.get('/sample/:database/:tableName', async (req, res) => {
  try {
    const { error, value } = tableSchema.validate(req.params);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const limit = parseInt(req.query.limit) || 10;
    const query = `SELECT TOP ${limit} * FROM ${value.tableName}`;
    const result = await sqlService.executeQuery(value.database, query);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
