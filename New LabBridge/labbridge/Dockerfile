# Dockerfile para LabBridge - Reflex + Nginx (Railway-ready)
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    git \
    unzip \
    curl \
    ca-certificates \
    nginx \
    gettext-base \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python (cache layer separado)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo da aplicacao
COPY . .

# Aumentar limite de memoria do Node para build do frontend
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Inicializar e buildar frontend
RUN rm -rf .web/build .web/dev-server
RUN reflex init
RUN reflex export --frontend-only --no-zip --loglevel debug

# Copiar template do nginx (sera processado pelo start.sh com envsubst)
COPY nginx.conf.template /app/nginx.conf.template

# Preparar start.sh (converter CRLF -> LF para Windows compatibility)
RUN dos2unix start.sh && chmod +x start.sh

# Criar diretorio para uploads
RUN mkdir -p /app/uploaded_files

# Railway define PORT dinamicamente; EXPOSE e apenas documentacao
EXPOSE ${PORT:-8080}

CMD ["./start.sh"]
