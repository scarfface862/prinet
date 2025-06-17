FROM node:18-alpine

# Instalacja narzędzi systemowych
RUN apk add --no-cache \
    curl \
    netcat-openbsd \
    python3 \
    py3-pip \
    build-base \
    iputils \
    && rm -rf /var/cache/apk/*

# Utworzenie katalogu aplikacji
WORKDIR /app

# Kopiowanie plików konfiguracyjnych
COPY package*.json ./

# Instalacja zależności
RUN npm ci --only=production

# Utworzenie użytkownika bez uprawnień root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

# Kopiowanie kodu aplikacji
COPY --chown=nodejs:nodejs . .

# Utworzenie katalogów
RUN mkdir -p logs public/css public/js && \
    chown -R nodejs:nodejs logs public

# Przełączenie na użytkownika nodejs
USER nodejs

# Eksponowanie portów
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Uruchomienie aplikacji
CMD ["npm", "start"]
