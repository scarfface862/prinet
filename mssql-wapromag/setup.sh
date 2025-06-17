# mssql-wapromag/setup.sh
#!/bin/bash

# Uruchomienie SQL Server w tle
echo "Starting SQL Server..."
/opt/mssql/bin/sqlservr &

# Oczekiwanie na uruchomienie SQL Server
echo "Waiting for SQL Server to start..."
sleep 30

# Sprawdzenie czy SQL Server działa
until /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -Q "SELECT 1" > /dev/null 2>&1
do
    echo "Waiting for SQL Server to be ready..."
    sleep 5
done

echo "SQL Server is ready. Running initialization script..."

# Uruchomienie skryptu inicjalizacyjnego
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -i /usr/src/app/init.sql

if [ $? -eq 0 ]; then
    echo "Database initialization completed successfully"
else
    echo "Database initialization failed"
fi

# Utrzymanie kontenera
echo "SQL Server is ready and initialized"
wait
