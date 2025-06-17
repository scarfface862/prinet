#!/bin/bash

# Ustawienie katalogu głównego
ROOT="wapro-network-mock"

# Lista katalogów do utworzenia
DIRS=(
  "$ROOT/docs"
  "$ROOT/monitoring/grafana/dashboards"
  "$ROOT/monitoring/grafana/datasources"
  "$ROOT/monitoring/prometheus"
  "$ROOT/mssql-wapromag/backup"
  "$ROOT/mssql-wapromag/config"
  "$ROOT/rpi-server/logs"
  "$ROOT/rpi-server/public/css"
  "$ROOT/rpi-server/public/js"
  "$ROOT/rpi-server/routes"
  "$ROOT/rpi-server/services"
  "$ROOT/rpi-server/tests"
  "$ROOT/scripts"
  "$ROOT/test-runner/config"
  "$ROOT/test-runner/reports"
  "$ROOT/test-runner/tests"
  "$ROOT/zebra-printer-1/config"
  "$ROOT/zebra-printer-1/logs"
  "$ROOT/zebra-printer-1/templates"
  "$ROOT/zebra-printer-2/config"
  "$ROOT/zebra-printer-2/logs"
  "$ROOT/zebra-printer-2/templates"
)

# Lista plików do utworzenia
FILES=(
  "$ROOT/.env.example"
  "$ROOT/.gitignore"
  "$ROOT/Makefile"
  "$ROOT/README.md"
  "$ROOT/docker-compose.yml"

  "$ROOT/docs/API.md"
  "$ROOT/docs/SQL_Schema.md"
  "$ROOT/docs/Testing.md"
  "$ROOT/docs/Troubleshooting.md"
  "$ROOT/docs/ZEBRA_Commands.md"

  "$ROOT/monitoring/docker-compose.monitoring.yml"
  "$ROOT/monitoring/grafana/dashboards/database_metrics.json"
  "$ROOT/monitoring/grafana/dashboards/network_overview.json"
  "$ROOT/monitoring/grafana/dashboards/printer_status.json"
  "$ROOT/monitoring/grafana/datasources/prometheus.yaml"
  "$ROOT/monitoring/prometheus/alerts.yml"
  "$ROOT/monitoring/prometheus/prometheus.yml"

  "$ROOT/mssql-wapromag/Dockerfile"
  "$ROOT/mssql-wapromag/init.sql"

  "$ROOT/rpi-server/.env"
  "$ROOT/rpi-server/Dockerfile"
  "$ROOT/rpi-server/package.json"
  "$ROOT/rpi-server/server.js"
  "$ROOT/rpi-server/public/css/style.css"
  "$ROOT/rpi-server/public/index.html"
  "$ROOT/rpi-server/public/js/app.js"
  "$ROOT/rpi-server/routes/diagnosticRoutes.js"
  "$ROOT/rpi-server/routes/healthRoutes.js"
  "$ROOT/rpi-server/routes/sqlRoutes.js"
  "$ROOT/rpi-server/routes/zebraRoutes.js"
  "$ROOT/rpi-server/services/diagnosticService.js"
  "$ROOT/rpi-server/services/healthService.js"
  "$ROOT/rpi-server/services/sqlService.js"
  "$ROOT/rpi-server/services/zebraService.js"
  "$ROOT/rpi-server/tests/integration.test.js"
  "$ROOT/rpi-server/tests/sql.test.js"
  "$ROOT/rpi-server/tests/zebra.test.js"

  "$ROOT/scripts/backup-db.sh"
  "$ROOT/scripts/restore-db.sh"
  "$ROOT/scripts/setup.sh"
  "$ROOT/scripts/start.sh"
  "$ROOT/scripts/stop.sh"
  "$ROOT/scripts/test-all.sh"

  "$ROOT/test-runner/Dockerfile"
  "$ROOT/test-runner/requirements.txt"
  "$ROOT/test-runner/test_suite.py"
  "$ROOT/test-runner/config/test_config.yaml"
  "$ROOT/test-runner/tests/test_integration.py"
  "$ROOT/test-runner/tests/test_rpi_sql.py"
  "$ROOT/test-runner/tests/test_rpi_zebra.py"
  "$ROOT/test-runner/tests/test_zebra_connectivity.py"

  "$ROOT/zebra-printer-1/Dockerfile"
  "$ROOT/zebra-printer-1/requirements.txt"
  "$ROOT/zebra-printer-1/zebra_mock.py"
  "$ROOT/zebra-printer-1/config/printer_config.json"
  "$ROOT/zebra-printer-1/templates/interface.html"

  "$ROOT/zebra-printer-2/Dockerfile"
  "$ROOT/zebra-printer-2/requirements.txt"
  "$ROOT/zebra-printer-2/zebra_mock.py"
  "$ROOT/zebra-printer-2/config/printer_config.json"
  "$ROOT/zebra-printer-2/templates/interface.html"
)

# Tworzenie katalogów
for dir in "${DIRS[@]}"; do
  mkdir -p "$dir"
done

# Tworzenie pustych plików
for file in "${FILES[@]}"; do
  touch "$file"
done

echo "Struktura projektu '$ROOT' została utworzona."
