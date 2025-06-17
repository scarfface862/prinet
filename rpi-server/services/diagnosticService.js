// rpi-server/services/diagnosticService.js
const sqlService = require('./sqlService');
const zebraService = require('./zebraService');
const winston = require('winston');
const ping = require('ping');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()]
});

class DiagnosticService {
  constructor() {
    this.lastResults = {};
    this.scheduleInterval = 5 * 60 * 1000; // 5 minut
  }

  async runFullDiagnostics() {
    logger.info('Running full diagnostics...');

    const results = {
      timestamp: new Date().toISOString(),
      network: await this.testNetworkConnectivity(),
      database: await this.testDatabaseConnections(),
      printers: await this.testPrinterConnections(),
      system: await this.getSystemInfo()
    };

    this.lastResults = results;
    return results;
  }

  async testNetworkConnectivity() {
    const hosts = [
      'mssql-wapromag',
      'zebra-printer-1',
      'zebra-printer-2'
    ];

    const results = {};

    for (const host of hosts) {
      try {
        const result = await ping.promise.probe(host, {
          timeout: 5,
          extra: ['-c', '3']
        });

        results[host] = {
          alive: result.alive,
          time: result.time,
          min: result.min,
          max: result.max,
          avg: result.avg
        };
      } catch (error) {
        results[host] = {
          alive: false,
          error: error.message
        };
      }
    }

    return results;
  }

  async testDatabaseConnections() {
    const results = {};

    try {
      const wapromag = await sqlService.testConnection('wapromag');
      results.wapromag = wapromag;
    } catch (error) {
      results.wapromag = {
        success: false,
        error: error.message
      };
    }

    return results;
  }

  async testPrinterConnections() {
    try {
      return await zebraService.getAllPrintersStatus();
    } catch (error) {
      return {
        error: error.message
      };
    }
  }

  async getSystemInfo() {
    const os = require('os');

    return {
      hostname: os.hostname(),
      platform: os.platform(),
      arch: os.arch(),
      uptime: os.uptime(),
      loadavg: os.loadavg(),
      memory: {
        total: os.totalmem(),
        free: os.freemem(),
        used: os.totalmem() - os.freemem()
      },
      cpus: os.cpus().length
    };
  }

  async runScheduledChecks() {
    try {
      const quickCheck = {
        timestamp: new Date().toISOString(),
        database: await sqlService.testConnection('wapromag'),
        printers: {}
      };

      // Szybki test drukarek
      const printers = ['zebra-1', 'zebra-2'];
      for (const printer of printers) {
        quickCheck.printers[printer] = await zebraService.testConnection(printer);
      }

      logger.info('Scheduled check completed', quickCheck);
      return quickCheck;
    } catch (error) {
      logger.error('Scheduled check failed:', error);
      throw error;
    }
  }

  getLastResults() {
    return this.lastResults;
  }

  async generateReport() {
    const diagnostics = await this.runFullDiagnostics();

    const report = {
      generated: new Date().toISOString(),
      summary: {
        overall_status: this.calculateOverallStatus(diagnostics),
        total_checks: this.countTotalChecks(diagnostics),
        passed_checks: this.countPassedChecks(diagnostics),
        failed_checks: this.countFailedChecks(diagnostics)
      },
      details: diagnostics,
      recommendations: this.generateRecommendations(diagnostics)
    };

    return report;
  }

  calculateOverallStatus(diagnostics) {
    const dbOk = diagnostics.database.wapromag?.success || false;
    const printersOk = Object.values(diagnostics.printers)
      .every(p => p.connection?.success || false);

    if (dbOk && printersOk) return 'HEALTHY';
    if (dbOk || printersOk) return 'DEGRADED';
    return 'CRITICAL';
  }

  countTotalChecks(diagnostics) {
    let count = 0;
    count += Object.keys(diagnostics.network).length;
    count += Object.keys(diagnostics.database).length;
    count += Object.keys(diagnostics.printers).length;
    return count;
  }

  countPassedChecks(diagnostics) {
    let count = 0;

    // Network checks
    count += Object.values(diagnostics.network)
      .filter(n => n.alive).length;

    // Database checks
    count += Object.values(diagnostics.database)
      .filter(d => d.success).length;

    // Printer checks
    count += Object.values(diagnostics.printers)
      .filter(p => p.connection?.success).length;

    return count;
  }

  countFailedChecks(diagnostics) {
    return this.countTotalChecks(diagnostics) - this.countPassedChecks(diagnostics);
  }

  generateRecommendations(diagnostics) {
    const recommendations = [];

    // Database recommendations
    if (!diagnostics.database.wapromag?.success) {
      recommendations.push({
        type: 'CRITICAL',
        component: 'Database',
        message: 'Brak połączenia z bazą WAPROMAG - sprawdź konfigurację i dostępność serwera'
      });
    }

    // Printer recommendations
    Object.entries(diagnostics.printers).forEach(([id, printer]) => {
      if (!printer.connection?.success) {
        recommendations.push({
          type: 'WARNING',
          component: 'Printer',
          message: `Drukarka ${id} jest niedostępna - sprawdź połączenie sieciowe`
        });
      }
    });

    // Network recommendations
    Object.entries(diagnostics.network).forEach(([host, result]) => {
      if (!result.alive) {
        recommendations.push({
          type: 'ERROR',
          component: 'Network',
          message: `Host ${host} nie odpowiada na ping - sprawdź łączność sieciową`
        });
      }
    });

    return recommendations;
  }
}

module.exports = new DiagnosticService();
