# docs/API.md
# WAPRO Network Mock - API Documentation

## RPI Server API

Base URL: `http://localhost:8081/api`

### Health Endpoints

#### GET /health
Podstawowy health check
```json
{
  "status": "HEALTHY",
  "timestamp": "2025-06-17T10:00:00.000Z",
  "uptime": 3600,
  "memory": {...},
  "checks": {...}
}
```

#### GET /health/detailed
Szczegółowy raport zdrowia
```json
{
  "summary": {
    "overall_status": "HEALTHY",
    "total_checks": 10,
    "passed_checks": 9,
    "failed_checks": 1
  },
  "details": {...},
  "recommendations": [...]
}
```

### SQL Endpoints

#### GET /sql/test/{database}
Test połączenia z bazą danych
- `database`: wapromag

#### POST /sql/query
Wykonanie zapytania SQL
```json
{
  "database": "wapromag",
  "query": "SELECT * FROM Produkty"
}
```

#### GET /sql/tables/{database}
Lista tabel w bazie danych

#### GET /sql/schema/{database}/{tableName}
Schemat tabeli

### ZEBRA Printer Endpoints

#### GET /zebra/test/{printerId}
Test połączenia z drukarką
- `printerId`: zebra-1, zebra-2

#### POST /zebra/command
Wysłanie komendy ZPL
```json
{
  "printerId": "zebra-1",
  "command": "~HI"
}
```

#### GET /zebra/status/{printerId}
Status drukarki

#### GET /zebra/status
Status wszystkich drukarek

#### POST /zebra/test-print/{printerId}
Drukowanie etykiety testowej

#### GET /zebra/commands
Lista dostępnych komend ZPL

### Diagnostic Endpoints

#### GET /diagnostic/full
Pełna diagnostyka systemu

#### GET /diagnostic/report
Raport diagnostyczny

#### GET /diagnostic/network
Test łączności sieciowej

#### GET /diagnostic/database
Test połączeń z bazami danych

#### GET /diagnostic/printers
Test połączeń z drukarkami

## ZEBRA Printer Mock API

Base URL: `http://localhost:8091` (printer-1), `http://localhost:8092` (printer-2)

### Endpoints

#### GET /api/status
Status drukarki
```json
{
  "name": "ZEBRA-001",
  "model": "ZT230",
  "status": "READY",
  "jobs_printed": 42,
  "last_command": "~HI",
  "timestamp": "2025-06-17T10:00:00.000Z"
}
```

#### POST /api/reset
Reset drukarki

### Socket Communication

Port: 9100
Protokół: Raw TCP Socket

Obsługiwane komendy ZPL:
- `~HI` - Host Identification
- `~HS` - Host Status
- `^WD` - Configuration
- `PING` - Ping test
- `^XA...^XZ` - Print Label

