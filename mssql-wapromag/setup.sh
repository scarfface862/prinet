# mssql-wapromag/setup.sh
#!/bin/bash

# Uruchomienie SQL Server w tle
/opt/mssql/bin/sqlservr &

# Oczekiwanie na uruchomienie SQL Server
sleep 30

# Uruchomienie skryptu inicjalizacyjnego
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -i /usr/src/app/init.sql

# Utrzymanie kontenera
wait

# scripts/setup.sh
#!/bin/bash
set -e

echo "🚀 Konfiguracja środowiska WAPRO Network Mock..."

# Sprawdzenie czy Docker jest uruchomiony
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker nie jest zainstalowany lub nie działa"
    exit 1
fi

if ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Docker Compose nie jest zainstalowany"
    exit 1
fi

# Utworzenie wymaganych katalogów
echo "📁 Tworzenie struktury katalogów..."
mkdir -p {logs,reports,backups}
mkdir -p mssql-wapromag/{backup,config}
mkdir -p rpi-server/{logs,public/css,public/js}
mkdir -p zebra-printer-1/{logs,templates,config}
mkdir -p zebra-printer-2/{logs,templates,config}
mkdir -p test-runner/{reports,logs}
mkdir -p monitoring/{grafana,prometheus}

# Kopiowanie plików konfiguracyjnych
echo "⚙️  Kopiowanie konfiguracji..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📋 Utworzono plik .env z domyślną konfiguracją"
fi

# Budowanie obrazów
echo "🔨 Budowanie obrazów Docker..."
docker-compose build

echo "✅ Konfiguracja zakończona pomyślnie!"
echo "🎯 Użyj 'make start' lub './scripts/start.sh' aby uruchomić środowisko"

# scripts/start.sh
#!/bin/bash
set -e

echo "🚀 Uruchamianie WAPRO Network Mock..."

# Sprawdzenie konfiguracji
if [ ! -f .env ]; then
    echo "❌ Brak pliku .env - uruchom './scripts/setup.sh' najpierw"
    exit 1
fi

# Uruchomienie wszystkich serwisów
echo "🐳 Uruchamianie kontenerów..."
docker-compose up -d

# Oczekiwanie na uruchomienie serwisów
echo "⏳ Oczekiwanie na uruchomienie serwisów..."
sleep 10

# Sprawdzenie statusu
echo "📊 Status serwisów:"
docker-compose ps

# Wyświetlenie informacji o dostępnych interfejsach
echo ""
echo "🌐 Dostępne interfejsy:"
echo "   RPI Server GUI:      http://localhost:8080"
echo "   RPI Server API:      http://localhost:8081"
echo "   ZEBRA Printer 1:     http://localhost:8091"
echo "   ZEBRA Printer 2:     http://localhost:8092"
echo "   Monitoring:          http://localhost:3000"
echo "   MSSQL WAPROMAG:      localhost:1433"

echo ""
echo "✅ Środowisko uruchomione pomyślnie!"
echo "📝 Sprawdź logi: docker-compose logs -f"

# scripts/stop.sh
#!/bin/bash
set -e

echo "🛑 Zatrzymywanie WAPRO Network Mock..."

docker-compose down

echo "✅ Wszystkie serwisy zatrzymane"
