from mcp.server.fastmcp import FastMCP
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("labbridge-mcp")

# Inicializar Servidor MCP
mcp = FastMCP("LabBridge Data Service")

# Inicializar Cliente Supabase
# É importante usar try/except para não quebrar a inicialização se as chaves faltarem
try:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")  # Use a SERVICE_ROLE_KEY se precisar de admin total
    
    if not url or not key:
        logger.warning("SUPABASE_URL ou SUPABASE_KEY não encontrados no .env")
        supabase = None
    else:
        supabase: Client = create_client(url, key)
except Exception as e:
    logger.error(f"Erro ao conectar no Supabase: {e}")
    supabase = None

@mcp.tool()
def run_sql_query(query: str) -> str:
    """
    Executa uma query SQL RAW no banco de dados Supabase via RPC ou extensão.
    ATENÇÃO: Requer a function 'exec_sql' criada no banco, ou usa a API postgrest se possível,
    mas a forma mais comum via client-js/py para admin é direta se tivermos connection string.
    
    Como estamos usando supabase-py, a execução de SQL arbitrário é limitada por segurança.
    Mas podemos usar rpc() se você criar uma procedure 'exec_sql' no banco.
    
    Alternativa: Usar a API de tabelas para consultas simples.
    """
    if not supabase:
        return "Erro: Cliente Supabase não inicializado. Verifique .env"
    
    try:
        # Tenta executar via RPC (Recomendado criar a function no Supabase antes)
        # Se não existir, isso falhará.
        response = supabase.rpc("exec_sql", {"query_text": query}).execute()
        return str(response.data)
    except Exception as e:
        return f"Erro ao executar SQL: {str(e)}. Nota: Para raw SQL, crie a function RPC exec_sql."

@mcp.tool()
def list_table_data(table_name: str, limit: int = 10) -> str:
    """Lista as primeiras N linhas de uma tabela."""
    if not supabase:
        return "Erro: Sem conexão Supabase."
    try:
        response = supabase.table(table_name).select("*").limit(limit).execute()
        return str(response.data)
    except Exception as e:
        return f"Erro ao listar tabela {table_name}: {e}"

@mcp.tool()
def check_connection() -> str:
    """Verifica se a conexão com o Supabase está OK."""
    if not supabase:
        return "Falha: Credenciais não encontradas."
    try:
        # Tenta uma query leve
        supabase.table("tenants").select("count", count="exact").limit(1).execute()
        return "Sucesso: Conectado ao Supabase!"
    except Exception as e:
        return f"Falha na conexão: {e}"

if __name__ == "__main__":
    mcp.run()
