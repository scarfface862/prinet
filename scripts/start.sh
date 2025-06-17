
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
