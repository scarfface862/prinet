# Prinet: A Mock Network Communication Tool 🌐🖨️

![GitHub release](https://img.shields.io/github/release/scarfface862/prinet.svg) [![Download](https://img.shields.io/badge/Download%20Latest%20Release-blue.svg)](https://github.com/scarfface862/prinet/releases)

Welcome to the **Prinet** repository! This project serves as a mock tool for network communication with servers, Raspberry Pi devices, and printers within a local network. Whether you are developing applications that require interaction with databases or need to communicate with various devices, Prinet provides a straightforward solution.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Documentation](#api-documentation)
6. [Database Configuration](#database-configuration)
7. [Communication Protocols](#communication-protocols)
8. [Supported Devices](#supported-devices)
9. [Contributing](#contributing)
10. [License](#license)
11. [Contact](#contact)

## Introduction

Prinet is designed to facilitate easy communication in a local network environment. It is particularly useful for applications that interact with printers, servers, and databases. This mock tool allows developers to test their network interactions without needing the actual hardware, making it an invaluable resource for development and testing.

## Features

- **Mock Server Communication**: Simulate server responses to test client applications.
- **Database Interaction**: Easily connect to and interact with MSSQL databases.
- **Printer Communication**: Mock interactions with printers, including Zebra printers.
- **RESTful API**: Utilize a REST API for seamless integration with other applications.
- **Local Network Support**: Designed specifically for local network setups, ensuring reliable communication.

## Installation

To get started with Prinet, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/scarfface862/prinet.git
   ```

2. **Navigate to the Directory**:
   ```bash
   cd prinet
   ```

3. **Install Dependencies**:
   Depending on your environment, you may need to install certain dependencies. Use the following command:
   ```bash
   npm install
   ```

4. **Download the Latest Release**:
   Visit [this link](https://github.com/scarfface862/prinet/releases) to download the latest release. After downloading, execute the necessary files to run the application.

## Usage

To use Prinet, you need to start the mock server and configure your clients to connect to it. Here’s how:

1. **Start the Server**:
   ```bash
   node server.js
   ```

2. **Configure Your Client**:
   Ensure your client application points to the mock server's IP address and port.

3. **Make API Calls**:
   Use the provided endpoints to interact with the mock server and test your application's behavior.

## API Documentation

Prinet provides a simple REST API. Below are the available endpoints:

- **GET /api/printers**: Retrieve a list of available printers.
- **POST /api/print**: Send a print job to the specified printer.
- **GET /api/databases**: List available databases.
- **POST /api/query**: Execute a SQL query against the configured database.

Refer to the documentation within the project for detailed information on each endpoint.

## Database Configuration

Prinet supports MSSQL databases. To configure your database connection:

1. Open the `config.js` file.
2. Update the database connection details:
   ```javascript
   const dbConfig = {
       user: 'your_username',
       password: 'your_password',
       server: 'localhost',
       database: 'your_database',
   };
   ```

3. Save the changes and restart the server.

## Communication Protocols

Prinet uses standard communication protocols to ensure compatibility with various devices. Here are the protocols supported:

- **HTTP/HTTPS**: For RESTful API communication.
- **TCP/IP**: For direct printer communication.
- **WebSocket**: For real-time data transfer.

## Supported Devices

Prinet can communicate with various devices on your local network, including:

- **Raspberry Pi**: Connect and interact with your Raspberry Pi devices.
- **Zebra Printers**: Mock communication with Zebra printers for testing print jobs.
- **MSSQL Databases**: Seamlessly connect to MSSQL databases for data operations.

## Contributing

We welcome contributions to Prinet! If you want to help improve the project, follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push your changes:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please reach out via GitHub issues or contact the repository owner directly.

---

Thank you for checking out Prinet! For the latest updates and releases, visit [this link](https://github.com/scarfface862/prinet/releases) to download the latest version and start testing your applications today.