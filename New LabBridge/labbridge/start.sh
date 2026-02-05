#!/bin/bash
set -e

# Railway atribui PORT dinamicamente; fallback para 8080 local
export PORT="${PORT:-8080}"
echo "=== LabBridge Start ==="
echo "PORT externo: $PORT"
echo "Backend interno: 8000"

# Gerar nginx.conf a partir do template com o PORT correto
# Apenas substitui $PORT (preserva outras vars do nginx como $http_upgrade)
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/nginx.conf
echo "nginx.conf gerado com porta $PORT"

# Iniciar Reflex backend em background
echo "Iniciando Reflex backend..."
reflex run --env prod --backend-only --backend-port 8000 &
REFLEX_PID=$!

# Debug: Verificar estrutura do build
echo "=== Verificando build frontend ==="
if [ -d "/app/.web/build/client" ]; then
    echo "Build frontend encontrado."
    ls -F /app/.web/build/client | head -n 20
else
    echo "AVISO: Build frontend nao encontrado em /app/.web/build/client"
fi

# Aguardar backend estar pronto (maximo 120 segundos)
echo "Aguardando backend (porta 8000)..."
for i in $(seq 1 120); do
    if curl -sf http://127.0.0.1:8000/ping > /dev/null 2>&1; then
        echo "Backend pronto! (${i}s)"
        break
    fi
    if [ $i -eq 120 ]; then
        echo "ERRO: Backend nao respondeu em 120s"
        exit 1
    fi
    sleep 1
done

# Iniciar Nginx em foreground
echo "Iniciando Nginx na porta $PORT..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Trap para shutdown gracioso
trap "kill $REFLEX_PID $NGINX_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Manter container rodando
wait $REFLEX_PID
