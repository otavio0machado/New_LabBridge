#!/bin/bash
set -e

export PORT="${PORT:-8080}"
echo "=== LabBridge Start ==="
echo "PORT=$PORT"

# Gerar nginx.conf
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/nginx.conf

# Validar nginx config
echo "Validando nginx..."
nginx -t 2>&1
echo "nginx config OK"

# Verificar build
echo "=== Build Check ==="
for f in index.html 404.html dashboard/index.html; do
    if [ -f "/app/.web/build/client/$f" ]; then
        echo "OK: $f"
    else
        echo "FALTA: $f"
    fi
done
echo "HTML files:" $(find /app/.web/build/client -name "*.html" -type f | wc -l)
echo "Total files:" $(find /app/.web/build/client -type f | wc -l)

# Permissoes (garantir que nginx/www-data possa ler)
chmod -R 755 /app/.web/build/client

# Iniciar Reflex backend
echo "Iniciando backend..."
reflex run --env prod --backend-only --backend-port 8000 &
REFLEX_PID=$!

# Aguardar backend
echo "Aguardando backend..."
for i in $(seq 1 120); do
    if curl -sf http://127.0.0.1:8000/ping > /dev/null 2>&1; then
        echo "Backend OK (${i}s)"
        break
    fi
    if [ $i -eq 120 ]; then
        echo "ERRO: Backend timeout 120s"
        exit 1
    fi
    sleep 1
done

# Iniciar Nginx
echo "Iniciando nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!
sleep 2

# Self-test
echo "=== Self-test ==="
echo "--- GET /healthz ---"
curl -s http://127.0.0.1:${PORT}/healthz 2>&1 || echo "(falhou)"
echo ""

echo "--- GET / (status + primeiros 200 chars) ---"
STATUS=$(curl -s -o /tmp/resp.html -w "%{http_code}" http://127.0.0.1:${PORT}/ 2>/dev/null || echo "000")
echo "Status: $STATUS"
head -c 200 /tmp/resp.html 2>/dev/null || true
echo ""

echo "--- GET /dashboard (status) ---"
STATUS2=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:${PORT}/dashboard 2>/dev/null || echo "000")
echo "Status: $STATUS2"

echo "=== LabBridge PRONTO na porta $PORT ==="

trap "kill $REFLEX_PID $NGINX_PID 2>/dev/null; exit 0" SIGTERM SIGINT
wait $REFLEX_PID
