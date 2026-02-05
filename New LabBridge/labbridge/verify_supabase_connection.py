from mcp_server import check_connection, logger
import logging

# Configurar logger para ver erros no console
logging.basicConfig(level=logging.INFO)

print("--- Testando Conexão com Supabase ---")
try:
    result = check_connection()
    print(f"Resultado: {result}")
except Exception as e:
    print(f"Erro fatal: {e}")
