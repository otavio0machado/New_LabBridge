#!/bin/bash
set -e

export PORT="${PORT:-8080}"
echo "=== LabBridge Start ==="
echo "PORT=$PORT"

# Gerar nginx.conf
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/nginx.conf

# Mostrar config gerada para debug
echo "=== nginx.conf gerado ==="
cat /etc/nginx/nginx.conf
echo "========================="

# Validar nginx config
echo "Validando nginx config..."
nginx -t 2>&1
echo "nginx config OK"

# Verificar que index.html existe
echo "=== Verificando build ==="
if [ -f "/app/.web/build/client/index.html" ]; then
    echo "index.html encontrado"
    head -3 /app/.web/build/client/index.html
else
    echo "ERRO CRITICO: index.html NAO existe!"
    echo "Conteudo de /app/.web/build/client/:"
    ls -la /app/.web/build/client/ 2>/dev/null || echo "diretorio nao existe"
fi
echo "Total HTML:" $(find /app/.web/build/client -name "*.html" -type f 2>/dev/null | wc -l)
echo "Total arquivos:" $(find /app/.web/build/client -type f 2>/dev/null | wc -l)

# Iniciar Reflex backend
echo "Iniciando Reflex backend..."
reflex run --env prod --backend-only --backend-port 8000 &
REFLEX_PID=$!

# Aguardar backend
echo "Aguardando backend..."
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

# Testar que nginx serve index.html ANTES de declarar pronto
echo "Iniciando Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!
sleep 2

# Verificar que nginx responde
echo "Testando nginx..."
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:${PORT}/ 2>/dev/null || echo "000")
echo "GET / retornou: $HTTP_CODE"

HTTP_CODE2=$(curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:${PORT}/healthz 2>/dev/null || echo "000")
echo "GET /healthz retornou: $HTTP_CODE2"

if [ "$HTTP_CODE" = "000" ]; then
    echo "ERRO: nginx nao esta respondendo na porta $PORT!"
    echo "Verificando processo nginx..."
    ps aux | grep nginx || true
fi

echo "=== LabBridge rodando na porta $PORT ==="

# Trap para shutdown
trap "kill $REFLEX_PID $NGINX_PID 2>/dev/null; exit 0" SIGTERM SIGINT

wait $REFLEX_PID
