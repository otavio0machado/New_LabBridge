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
    procps \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python (cache layer separado)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo da aplicacao
COPY . .

# Aumentar limite de memoria do Node para build do frontend
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Build do frontend
RUN rm -rf .web/build .web/dev-server
RUN reflex init
RUN reflex export --frontend-only --no-zip --loglevel debug

# Verificar que o build produziu os arquivos esperados
RUN test -f /app/.web/build/client/index.html || (echo "BUILD FAILED: index.html not found" && exit 1)
RUN echo "Build OK: $(find /app/.web/build/client -name '*.html' -type f | wc -l) HTML files"

# Preparar start.sh
RUN dos2unix start.sh && chmod +x start.sh
RUN dos2unix nginx.conf.template

# Criar diretorio para uploads
RUN mkdir -p /app/uploaded_files

EXPOSE 8080

CMD ["./start.sh"]
