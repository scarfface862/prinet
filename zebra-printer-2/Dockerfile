# zebra-printer-2/Dockerfile
FROM python:3.9-alpine

# Instalacja narzędzi systemowych
RUN apk add --no-cache \
    netcat-openbsd \
    curl \
    build-base \
    && rm -rf /var/cache/apk/*

# Utworzenie katalogu aplikacji
WORKDIR /app

# Kopiowanie requirements.txt
COPY requirements.txt .

# Instalacja wymaganych pakietów Python
RUN pip install --no-cache-dir -r requirements.txt

# Utworzenie użytkownika
RUN addgroup -g 1001 -S printer && \
    adduser -S printer -u 1001 -G printer

# Kopiowanie aplikacji
COPY --chown=printer:printer . .

# Utworzenie katalogów
RUN mkdir -p logs templates config && \
    chown -R printer:printer logs templates config

# Przełączenie na użytkownika printer
USER printer

# Eksponowanie portów
EXPOSE 9100 8080

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD nc -z localhost 9100 || exit 1

# Uruchomienie aplikacji
CMD ["python", "zebra_mock.py"]