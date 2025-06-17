
// rpi-server/services/healthService.js
const diagnosticService = require('./diagnosticService');

class HealthService {
  async getSystemStatus() {
    try {
      const diagnostics = await diagnosticService.runFullDiagnostics();
      const status = diagnosticService.calculateOverallStatus(diagnostics);

      return {
        status: status,
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        version: process.version,
        checks: {
          database: diagnostics.database.wapromag?.success || false,
          printers: Object.values(diagnostics.printers)
            .every(p => p.connection?.success || false),
          network: Object.values(diagnostics.network)
            .every(n => n.alive || false)
        }
      };
    } catch (error) {
      return {
        status: 'ERROR',
        timestamp: new Date().toISOString(),
        error: error.message
      };
    }
  }

  async getDetailedHealth() {
    try {
      return await diagnosticService.generateReport();
    } catch (error) {
      return {
        status: 'ERROR',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}

module.exports = new HealthService();