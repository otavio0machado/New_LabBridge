from typing import Generic, TypeVar, List, Optional, Dict, Any
from ..services.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Classe base para repositórios Supabase.
    Centraliza operações de banco de dados conforme skill 'O Arquivista'.
    Implementa o padrão Singleton reutilizando o cliente existente.
    """
    def __init__(self, table_name: str):
        self.table_name = table_name

    @property
    def client(self):
        """Retorna o cliente Supabase Singleton"""
        return supabase

    def get_all(self, tenant_id: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna registros da tabela filtrados por tenant_id."""
        try:
            query = self.client.table(self.table_name).select("*")
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar dados em {self.table_name}: {e}")
            return []

    def get_by_id(self, id: str, tenant_id: str = "") -> Optional[Dict[str, Any]]:
        """Retorna um registro pelo ID, opcionalmente filtrado por tenant."""
        try:
            query = self.client.table(self.table_name).select("*").eq("id", id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar ID {id} em {self.table_name}: {e}")
            return None

    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria um novo registro."""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao criar registro em {self.table_name}: {e}")
            return None

    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro existente."""
        try:
            response = self.client.table(self.table_name).update(data).eq("id", id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar ID {id} em {self.table_name}: {e}")
            return None

    def delete(self, id: str, tenant_id: str = "") -> bool:
        """Deleta um registro pelo ID, opcionalmente filtrado por tenant."""
        try:
            query = self.client.table(self.table_name).delete().eq("id", id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            query.execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar ID {id} em {self.table_name}: {e}")
            return False
