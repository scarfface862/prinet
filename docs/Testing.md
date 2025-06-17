# docs/Testing.md
# Testing Guide

## Uruchamianie testów

### Wszystkie testy
```bash
make test
```

### Testy kategorii
```bash
make test-sql        # Testy bazy danych
make test-zebra      # Testy drukarek
make test-integration # Testy integracyjne
```

### Testy manualne
```bash
# Test połączenia RPI → SQL
curl http://localhost:8081/api/sql/test/wapromag

# Test połączenia RPI → ZEBRA
curl http://localhost:8081/api/zebra/test/zebra-1

# Test komendy ZPL
curl -X POST http://localhost:8081/api/zebra/command \
  -H "Content-Type: application/json" \
  -d '{"printerId":"zebra-1","command":"~HI"}'

# Bezpośredni test drukarki
echo "~HI" | nc zebra-printer-1 9100
```

## Struktura testów

### test_rpi_sql.py
- Testy połączenia z bazą danych
- Testy zapytań SQL
- Testy wydajności

### test_zebra_connectivity.py
- Testy połączeń socket
- Testy komend ZPL
- Testy interfejsów web

### test_integration.py
- Testy end-to-end workflow
- Testy równoczesnej pracy
- Testy obsługi błędów

## Raporty testów

Raporty generowane w katalogu `reports/`:
- `test_report_YYYYMMDD_HHMMSS.html` - Raport HTML
- `test_results_YYYYMMDD_HHMMSS.json` - Wyniki JSON
- `summary_YYYYMMDD_HHMMSS.json` - Podsumowanie
- `health_report.json` - Stan systemu
