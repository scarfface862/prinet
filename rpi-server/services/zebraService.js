
// rpi-server/services/zebraService.js
const net = require('net');
const axios = require('axios');
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()]
});

class ZebraService {
  constructor() {
    this.printers = new Map();
    this.setupPrinters();
  }

  setupPrinters() {
    this.printers.set('zebra-1', {
      name: 'ZEBRA-001',
      host: 'zebra-printer-1',
      port: 9100,
      webPort: 8080,
      status: 'unknown'
    });

    this.printers.set('zebra-2', {
      name: 'ZEBRA-002',
      host: 'zebra-printer-2',
      port: 9100,
      webPort: 8080,
      status: 'unknown'
    });
  }

  async testConnection(printerId) {
    const printer = this.printers.get(printerId);
    if (!printer) throw new Error(`Unknown printer: ${printerId}`);

    return new Promise((resolve) => {
      const client = new net.Socket();
      const timeout = setTimeout(() => {
        client.destroy();
        resolve({ success: false, error: 'Connection timeout' });
      }, 5000);

      client.connect(printer.port, printer.host, () => {
        clearTimeout(timeout);
        client.destroy();
        printer.status = 'online';
        resolve({ success: true, message: 'Connection successful' });
      });

      client.on('error', (error) => {
        clearTimeout(timeout);
        printer.status = 'offline';
        resolve({ success: false, error: error.message });
      });
    });
  }

  async sendCommand(printerId, command) {
    const printer = this.printers.get(printerId);
    if (!printer) throw new Error(`Unknown printer: ${printerId}`);

    return new Promise((resolve, reject) => {
      const client = new net.Socket();
      let response = '';

      const timeout = setTimeout(() => {
        client.destroy();
        reject(new Error('Command timeout'));
      }, 10000);

      client.connect(printer.port, printer.host, () => {
        client.write(command);
      });

      client.on('data', (data) => {
        response += data.toString();
      });

      client.on('close', () => {
        clearTimeout(timeout);
        logger.info(`Command sent to ${printerId}: ${command.substring(0, 50)}...`);
        resolve({ success: true, response: response.trim() });
      });

      client.on('error', (error) => {
        clearTimeout(timeout);
        logger.error(`Command failed for ${printerId}:`, error);
        reject(error);
      });
    });
  }

  async getPrinterStatus(printerId) {
    try {
      const printer = this.printers.get(printerId);
      if (!printer) throw new Error(`Unknown printer: ${printerId}`);

      const webUrl = `http://${printer.host}:${printer.webPort}/api/status`;
      const response = await axios.get(webUrl, { timeout: 5000 });

      return {
        success: true,
        status: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async getAllPrintersStatus() {
    const results = {};

    for (const [id, printer] of this.printers) {
      try {
        const connectionTest = await this.testConnection(id);
        const webStatus = await this.getPrinterStatus(id);

        results[id] = {
          printer: printer.name,
          host: printer.host,
          connection: connectionTest,
          webStatus: webStatus
        };
      } catch (error) {
        results[id] = {
          printer: printer.name,
          host: printer.host,
          error: error.message
        };
      }
    }

    return results;
  }

  async printTestLabel(printerId) {
    const testLabel = `
^XA
^FO50,50^A0N,50,50^FDTest Label^FS
^FO50,120^A0N,30,30^FDPrinter: ${printerId}^FS
^FO50,170^A0N,30,30^FDTime: ${new Date().toISOString()}^FS
^FO50,220^BY3
^BCN,100,Y,N,N
^FD${Date.now()}^FS
^XZ
    `;

    return await this.sendCommand(printerId, testLabel);
  }
}

module.exports = new ZebraService();