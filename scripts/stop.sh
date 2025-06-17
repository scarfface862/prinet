# scripts/stop.sh
#!/bin/bash
set -e

echo "🛑 Zatrzymywanie WAPRO Network Mock..."

docker-compose down

echo "✅ Wszystkie serwisy zatrzymane"
