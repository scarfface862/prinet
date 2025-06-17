
# docs/Troubleshooting.md
# Troubleshooting Guide

## Problemy z kontenerami

### Kontenery nie startują
```bash
# Sprawdź logi
make logs

# Sprawdź status
docker-compose ps

# Restart
make restart
```

### Problemy z portami
```bash
# Sprawdź zajętość portów
netstat -tulpn | grep :8080
netstat -tulpn | grep :1433

# Zmień porty w .env
```

## Problemy z bazą danych

### Brak połączenia z MSSQL
```bash
# Sprawdź logi SQL Server
make logs-sql

# Test połączenia
docker-compose exec mssql-wapromag /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P WapromagPass123! -Q "SELECT 1"

# Restart kontenera
docker-compose restart mssql-wapromag
```

### Baza danych nie została utworzona
```bash
# Sprawdź inicjalizację
make logs-sql

# Ręczne uruchomienie skryptu
docker-compose exec mssql-wapromag /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P WapromagPass123! \
  -i /usr/src/app/init.sql
```

## Problemy z drukarkami

### Drukarki nie odpowiadają
```bash
# Test połączenia
nc -v zebra-printer-1 9100

# Sprawdź logi
make logs-zebra1

# Restart drukarki
docker-compose restart zebra-printer-1
```

### Błędy komend ZPL
```bash
# Test podstawowych komend
echo "~HI" | nc zebra-printer-1 9100
echo "PING" | nc zebra-printer-1 9100

# Sprawdź interfejs web
curl http://localhost:8091/api/status
```

## Problemy z RPI Server

### GUI nie ładuje się
```bash
# Sprawdź logi
make logs-rpi

# Test API
curl http://localhost:8081/api/health

# Sprawdź pliki statyczne
docker-compose exec rpi-server ls -la public/
```

### Błędy API
```bash
# Sprawdź health check
curl -v http://localhost:8080/health

# Test z verbose
curl -v http://localhost:8081/api/sql/test/wapromag
```

## Problemy z testami

### Testy nie przechodzą
```bash
# Uruchom z verbose
docker-compose --profile testing run test-runner python -m pytest -v

# Sprawdź połączenia
make health

# Sprawdź konfigurację
cat test-runner/config/test_config.yaml
```

### Timeout błędy
```bash
# Zwiększ timeouts w test_config.yaml
# Sprawdź obciążenie systemu
docker stats
```

## Ogólne problemy

### Brak miejsca na dysku
```bash
# Wyczyść Docker
make clean
docker system prune -a

# Sprawdź miejsce
df -h
```

### Problemy z uprawnieniami
```bash
# Napraw uprawnienia
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

### Reset całego środowiska
```bash
# Pełne czyszczenie i restart
make clean
make setup
make start
```