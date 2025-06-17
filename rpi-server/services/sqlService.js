// rpi-server/services/sqlService.js
const sql = require('mssql');
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()]
});

class SqlService {
  constructor() {
    this.connections = new Map();
    this.setupConnections();
  }

  setupConnections() {
    // Konfiguracja połączenia WAPROMAG
    this.connections.set('wapromag', {
      user: process.env.MSSQL_WAPROMAG_USER || 'sa',
      password: process.env.MSSQL_WAPROMAG_PASSWORD,
      server: process.env.MSSQL_WAPROMAG_HOST || 'mssql-wapromag',
      port: parseInt(process.env.MSSQL_WAPROMAG_PORT) || 1433,
      database: 'WAPROMAG_TEST',
      options: {
        encrypt: false,
        trustServerCertificate: true,
        connectTimeout: 30000,
        requestTimeout: 30000
      }
    });
  }

  async testConnection(database = 'wapromag') {
    try {
      const config = this.connections.get(database);
      if (!config) throw new Error(`Unknown database: ${database}`);

      const pool = await sql.connect(config);
      const result = await pool.request().query('SELECT 1 as test');
      await pool.close();

      logger.info(`Connection to ${database} successful`);
      return { success: true, message: 'Connection successful' };
    } catch (error) {
      logger.error(`Connection to ${database} failed:`, error);
      return { success: false, error: error.message };
    }
  }

  async executeQuery(database, query) {
    try {
      const config = this.connections.get(database);
      if (!config) throw new Error(`Unknown database: ${database}`);

      const pool = await sql.connect(config);
      const result = await pool.request().query(query);
      await pool.close();

      logger.info(`Query executed on ${database}: ${query.substring(0, 50)}...`);
      return {
        success: true,
        recordset: result.recordset,
        rowsAffected: result.rowsAffected
      };
    } catch (error) {
      logger.error(`Query failed on ${database}:`, error);
      throw error;
    }
  }

  async getTablesList(database = 'wapromag') {
    const query = `
      SELECT
        TABLE_SCHEMA,
        TABLE_NAME,
        TABLE_TYPE
      FROM INFORMATION_SCHEMA.TABLES
      WHERE TABLE_TYPE = 'BASE TABLE'
      ORDER BY TABLE_SCHEMA, TABLE_NAME
    `;
    return await this.executeQuery(database, query);
  }

  async getTableSchema(database, tableName) {
    const query = `
      SELECT
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT,
        CHARACTER_MAXIMUM_LENGTH
      FROM INFORMATION_SCHEMA.COLUMNS
      WHERE TABLE_NAME = '${tableName}'
      ORDER BY ORDINAL_POSITION
    `;
    return await this.executeQuery(database, query);
  }
}

module.exports = new SqlService();
