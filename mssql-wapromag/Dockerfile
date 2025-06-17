# mssql-wapromag/Dockerfile
FROM mcr.microsoft.com/mssql/server:2019-latest

# Ustawienie zmiennych środowiskowych
ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=WapromagPass123!
ENV MSSQL_PID=Express

# Utworzenie katalogu dla skryptów inicjalizacyjnych
RUN mkdir -p /usr/src/app

# Kopiowanie skryptów inicjalizacyjnych
COPY init.sql /usr/src/app/
COPY setup.sh /usr/src/app/

# Nadanie uprawnień wykonywania
RUN chmod +x /usr/src/app/setup.sh

# Eksponowanie portu
EXPOSE 1433

# Uruchomienie skryptu setup
CMD ["/usr/src/app/setup.sh"]