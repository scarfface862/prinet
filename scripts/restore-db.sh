#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    echo "❌ Użycie: $0 <nazwa_pliku_backupu>"
    echo "Dostępne backupy:"
    ls -la backups/*.bak 2>/dev/null || echo "Brak dostępnych backupów"
    exit 1
fi

BACKUP_FILE=$1
BACKUP_DIR="backups"

if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    echo "❌ Nie znaleziono pliku backupu: ${BACKUP_DIR}/${BACKUP_FILE}"
    exit 1
fi

echo "🔄 Przywracanie bazy danych z backupu: ${BACKUP_FILE}..."

# Kopiowanie backupu do kontenera
docker cp "${BACKUP_DIR}/${BACKUP_FILE}" \
    "$(docker-compose ps -q mssql-wapromag):/var/opt/mssql/backup/${BACKUP_FILE}"

# Przywracanie bazy danych
docker-compose exec mssql-wapromag /opt/mssql-tools/bin/sqlcmd \
    -S localhost -U sa -P WapromagPass123! \
    -Q "RESTORE DATABASE WAPROMAG_TEST FROM DISK = '/var/opt/mssql/backup/${BACKUP_FILE}' WITH REPLACE"

echo "✅ Baza danych przywrócona pomyślnie"