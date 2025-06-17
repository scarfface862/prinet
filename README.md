# prinet
mock dla sieci, do komunikacji z serwerem, rpi, drukarek w sieci


# README.md
# WAPRO Network Mock - Test Environment

Kompletne środowisko testowe do symulacji sieci WAPRO z bazą danych MSSQL, serwerem RPI i drukarkami ZEBRA.

## 🚀 Szybki start

```bash
# Konfiguracja środowiska
make setup

# Uruchomienie wszystkich serwisów
make start

# Sprawdzenie statusu
make status

# Uruchomienie testów
make test
```

## 📁 Struktura projektu

```
wapro-network-mock/
├── docker-compose.yml          # Główna konfiguracja Docker
├── Makefile                   # Automatyzacja zadań
├── mssql-wapromag/           # Baza danych WAPROMAG
├── rpi-server/               # Serwer RPI z GUI i API
├── zebra-printer-1/          # Mock drukarki ZEBRA-001
├── zebra-printer-2/          # Mock drukarki ZEBRA-002
├── test-runner/              # Automatyczne testy
└── scripts/                  # Skrypty pomocnicze
```

## 🌐 Dostępne interfejsy

- **RPI Server GUI**: http://localhost:8080
- **RPI Server API**: http://localhost:8081
- **ZEBRA Printer 1**: http://localhost:8091
- **ZEBRA Printer 2**: http://localhost:8092
- **Monitoring**: http://localhost:3000
- **MSSQL WAPROMAG**: localhost:1433

## 🧪 Testowanie

```bash
# Wszystkie testy
make test

# Testy bazy danych
make test-sql

# Testy drukarek
make test-zebra

# Testy integracyjne
make test-integration
```

## 🏥 Monitoring i diagnostyka

```bash
# Stan zdrowia systemu
make health

# Logi wszystkich serwisów
make logs

# Logi konkretnego serwisu
make logs-rpi
make logs-zebra1
make logs-sql
```

## 🛠️ Zarządzanie

```bash
# Restart systemu
make restart

# Czyszczenie środowiska
make clean

# Backup bazy danych
make backup-db

# Przywracanie bazy danych
make restore-db
```

## 📊 Funkcjonalności

### RPI Server
- ✅ GUI do zarządzania systemem
- ✅ REST API do komunikacji
- ✅ Testy połączeń z bazą danych
- ✅ Wysyłanie komend do drukarek ZEBRA
- ✅ Diagnostyka systemu
- ✅ Monitoring w czasie rzeczywistym

### Baza danych WAPROMAG
- ✅ Tabele: Kontrahenci, Produkty, Dokumenty Magazynowe
- ✅ Stany magazynowe i ruch magazynowy
- ✅ Konfiguracja drukarek
- ✅ Szablony etykiet ZPL
- ✅ Procedury magazynowe

### Drukarki ZEBRA Mock
- ✅ Symulacja protokołu ZPL
- ✅ Interfejs web do monitorowania
- ✅ Obsługa podstawowych komend (~HI, ~HS, PING)
- ✅ Drukowanie etykiet testowych
- ✅ Logi operacji

### System testowy
- ✅ Testy połączeń sieciowych
- ✅ Testy komunikacji RPI ↔ SQL
- ✅ Testy komunikacji RPI ↔ ZEBRA
- ✅ Testy integracyjne end-to-end
- ✅ Testy wydajnościowe
- ✅ Automatyczne raporty

## 🔧 Konfiguracja

Wszystkie ustawienia można zmienić w pliku `.env`:

```bash
# Database
MSSQL_WAPROMAG_PASSWORD=WapromagPass123!

# Printers
ZEBRA_1_NAME=ZEBRA-001
ZEBRA_2_NAME=ZEBRA-002

# Ports
RPI_GUI_PORT=8080
RPI_API_PORT=8081
```

## 🎯 Przypadki użycia

1. **Test komunikacji z WAPROMAG**: Weryfikacja połączeń i zapytań SQL
2. **Test drukarek ZEBRA**: Sprawdzenie dostępności i drukowania etykiet
3. **Test workflow**: Pobranie danych z bazy → generowanie etykiety → drukowanie
4. **Test wydajności**: Obciążenie systemu wieloma równoczesnymi operacjami
5. **Test diagnostyki**: Monitorowanie stanu wszystkich komponentów

## 📝 Wymagania

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM (zalecane 8GB)
- 10GB przestrzeni dyskowej

## 🆘 Rozwiązywanie problemów

```bash
# Sprawdzenie logów
make logs

# Reset środowiska
make clean && make setup && make start

# Test połączeń
make health

# Terminal do debugowania
make shell-rpi
make shell-sql
```
