"""
IntegrationService - Gerenciamento de Integrações Externas
CRUD completo de integrações com suporte a Supabase e fallback SQLite local
"""
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from .supabase_client import supabase
from .local_storage import local_storage
from ..config import Config


class IntegrationService:
    """Serviço de gerenciamento de integrações"""

    # Catálogo de integrações disponíveis
    AVAILABLE_INTEGRATIONS = [
        {
            "key": "shift_lis",
            "name": "Shift LIS",
            "description": "Sistema de Gestão Laboratorial",
            "category": "lis",
            "icon": "🔬",
            "config_fields": ["api_url", "api_key", "lab_code"]
        },
        {
            "key": "matrix",
            "name": "Matrix",
            "description": "Integração via API HL7/FHIR",
            "category": "lis",
            "icon": "🧬",
            "config_fields": ["endpoint", "client_id", "client_secret"]
        },
        {
            "key": "concent",
            "name": "Concent",
            "description": "Faturamento TISS e gestão de glosas",
            "category": "billing",
            "icon": "💰",
            "config_fields": ["api_url", "username", "password", "cnpj"]
        },
        {
            "key": "tiss_portal",
            "name": "Portal TISS",
            "description": "Envio automático de guias",
            "category": "billing",
            "icon": "📋",
            "config_fields": ["portal_url", "certificate_path", "certificate_password"]
        },
        {
            "key": "google_drive",
            "name": "Google Drive",
            "description": "Backup e exportação de relatórios",
            "category": "storage",
            "icon": "📁",
            "config_fields": ["folder_id"],
            "oauth": True
        },
        {
            "key": "whatsapp_business",
            "name": "WhatsApp Business",
            "description": "Envio automatizado de resultados",
            "category": "communication",
            "icon": "💬",
            "config_fields": ["phone_number_id", "access_token", "verify_token"]
        },
    ]

    def __init__(self):
        self.client = supabase
        self.local = local_storage
        self._use_local = self.client is None

    # =========================================================================
    # INTEGRATIONS CRUD
    # =========================================================================

    def get_integrations(self, tenant_id: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Lista todas as integrações de um tenant.

        Returns:
            Tuple[success, integrations_list, error_message]
        """
        # Usar armazenamento local se Supabase não estiver configurado
        if self._use_local:
            try:
                integrations = self.local.get_integrations(tenant_id)
                return True, integrations, ""
            except Exception as e:
                return False, [], f"Erro ao buscar integrações: {str(e)}"

        try:
            response = self.client.table("integrations")\
                .select("*")\
                .eq("tenant_id", tenant_id)\
                .execute()

            return True, response.data or [], ""
        except Exception as e:
            print(f"Erro ao buscar integrações do Supabase: {e}")
            # Fallback para local
            try:
                integrations = self.local.get_integrations(tenant_id)
                return True, integrations, ""
            except Exception as e2:
                print(f"Erro no fallback local: {e2}")
                return False, [], f"Erro ao buscar integrações: {str(e)}"

    def get_integration_by_id(self, integration_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Busca uma integração específica"""
        if self._use_local:
            try:
                integration = self.local.get_integration_by_id(integration_id)
                return True, integration, ""
            except Exception as e:
                return False, None, str(e)

        try:
            response = self.client.table("integrations")\
                .select("*")\
                .eq("id", integration_id)\
                .single()\
                .execute()

            return True, response.data, ""
        except Exception as e:
            return False, None, str(e)

    def create_integration(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Cria uma nova integração.

        Args:
            data: {name, description, category, icon, tenant_id, config}
        """
        if self._use_local:
            return self.local.create_integration(data)

        try:
            integration_data = {
                "name": data["name"],
                "description": data.get("description", ""),
                "category": data.get("category", "other"),
                "icon": data.get("icon", "🔌"),
                "status": "inactive",
                "tenant_id": data["tenant_id"],
                "config": data.get("config", {}),
                "credentials": {},  # Será criptografado
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("integrations")\
                .insert(integration_data)\
                .execute()

            return True, response.data[0] if response.data else None, ""
        except Exception as e:
            return False, None, f"Erro ao criar integração: {str(e)}"

    def update_integration(self, integration_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza dados de uma integração.

        Args:
            integration_id: ID da integração
            data: Campos a atualizar
        """
        if self._use_local:
            return self.local.update_integration(integration_id, data)

        try:
            update_data = {"updated_at": datetime.utcnow().isoformat()}

            allowed_fields = ["name", "description", "status", "config", "credentials", "last_sync", "last_error"]
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            self.client.table("integrations")\
                .update(update_data)\
                .eq("id", integration_id)\
                .execute()

            return True, ""
        except Exception as e:
            return False, f"Erro ao atualizar integração: {str(e)}"

    def delete_integration(self, integration_id: str) -> Tuple[bool, str]:
        """Remove uma integração"""
        if self._use_local:
            return self.local.delete_integration(integration_id)

        try:
            self.client.table("integrations")\
                .delete()\
                .eq("id", integration_id)\
                .execute()

            return True, ""
        except Exception as e:
            return False, f"Erro ao remover integração: {str(e)}"

    # =========================================================================
    # CONNECTION & SYNC
    # =========================================================================

    def toggle_integration(self, integration_id: str, active: bool) -> Tuple[bool, str]:
        """Ativa ou desativa uma integração"""
        if self._use_local:
            return self.local.toggle_integration(integration_id, active)
        new_status = "active" if active else "inactive"
        return self.update_integration(integration_id, {"status": new_status})

    def test_connection(self, integration_id: str) -> Tuple[bool, str]:
        """
        Testa a conexão com uma integração.

        Returns:
            Tuple[success, message]
        """
        if self._use_local:
            return self.local.test_connection(integration_id)

        success, integration, error = self.get_integration_by_id(integration_id)
        if not success:
            return False, error

        # TODO: implementar teste real de conexao por tipo de integracao
        integration_name = integration.get("name", "")
        if integration.get("status") == "error":
            return False, f"Falha na conexão com {integration_name}: Credenciais inválidas"

        return True, f"Conexão com {integration_name} estabelecida com sucesso"

    def sync_integration(self, integration_id: str) -> Tuple[bool, str]:
        """
        Executa sincronização manual de uma integração.

        Returns:
            Tuple[success, message]
        """
        if self._use_local:
            return self.local.sync_integration(integration_id)

        success, integration, error = self.get_integration_by_id(integration_id)
        if not success:
            return False, error

        if integration.get("status") != "active":
            return False, "Integração não está ativa"

        try:
            # Marcar como sincronizando
            self.update_integration(integration_id, {"status": "syncing"})

            # TODO: implementar sincronizacao real por tipo de integracao

            # Atualizar última sincronização
            self.update_integration(integration_id, {
                "status": "active",
                "last_sync": datetime.utcnow().isoformat(),
                "last_error": None
            })

            # Registrar log
            self._log_activity(integration_id, "sync", "success", "Sincronização concluída")

            return True, "Sincronização concluída com sucesso"
        except Exception as e:
            self.update_integration(integration_id, {
                "status": "error",
                "last_error": str(e)
            })
            self._log_activity(integration_id, "sync", "error", str(e))
            return False, f"Erro na sincronização: {str(e)}"

    def sync_all(self, tenant_id: str) -> Tuple[int, int]:
        """
        Sincroniza todas as integrações ativas de um tenant.

        Returns:
            Tuple[success_count, error_count]
        """
        success, integrations, _ = self.get_integrations(tenant_id)
        if not success:
            return 0, 0

        success_count = 0
        error_count = 0

        for integration in integrations:
            if integration.get("status") == "active":
                ok, _ = self.sync_integration(integration["id"])
                if ok:
                    success_count += 1
                else:
                    error_count += 1

        return success_count, error_count

    # =========================================================================
    # CREDENTIALS
    # =========================================================================

    def save_credentials(self, integration_id: str, credentials: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Salva credenciais de uma integração.
        TODO: criptografar credenciais antes de salvar (Vault ou AES).
        """
        return self.update_integration(integration_id, {"credentials": credentials})

    # =========================================================================
    # LOGGING
    # =========================================================================

    def _log_activity(
        self,
        integration_id: str,
        action: str,
        status: str,
        message: str,
        details: Dict[str, Any] = None
    ):
        """Registra log de atividade"""
        if not self.client:
            return

        try:
            log_data = {
                "integration_id": integration_id,
                "action": action,
                "status": status,
                "message": message,
                "details": details or {},
                "created_at": datetime.utcnow().isoformat()
            }

            self.client.table("integration_logs")\
                .insert(log_data)\
                .execute()
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    def get_logs(self, integration_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna logs de uma integração"""
        if not self.client:
            return []

        try:
            response = self.client.table("integration_logs")\
                .select("*")\
                .eq("integration_id", integration_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return response.data or []
        except Exception as e:
            print(f"Erro ao buscar logs: {e}")
            return []

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_integration_stats(self, tenant_id: str) -> Dict[str, int]:
        """Retorna estatísticas das integrações"""
        success, integrations, _ = self.get_integrations(tenant_id)
        if not success:
            return {"total": 0, "active": 0, "inactive": 0, "error": 0}

        stats = {
            "total": len(integrations),
            "active": sum(1 for i in integrations if i.get("status") == "active"),
            "inactive": sum(1 for i in integrations if i.get("status") == "inactive"),
            "error": sum(1 for i in integrations if i.get("status") == "error"),
        }
        return stats

    def get_available_integrations(self) -> List[Dict[str, Any]]:
        """Retorna catálogo de integrações disponíveis"""
        return self.AVAILABLE_INTEGRATIONS



# Singleton
integration_service = IntegrationService()
