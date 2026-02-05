"""
IntegrationState - Estado para gerenciamento de integrações
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..services.integration_service import integration_service


class IntegrationState(rx.State):
    """Estado para página de Integrações"""

    # Lista de integrações
    integrations: List[Dict[str, Any]] = []

    # Catálogo de integrações disponíveis
    available_integrations: List[Dict[str, Any]] = []

    # Loading states
    is_loading: bool = False
    is_syncing: bool = False
    is_testing: bool = False

    # Modal states
    show_config_modal: bool = False
    show_add_modal: bool = False

    # Current integration being configured
    current_integration_id: str = ""
    current_integration_name: str = ""
    config_fields: Dict[str, str] = {}

    # Feedback
    error_message: str = ""
    success_message: str = ""

    # Test result
    test_selected: str = "all"
    test_result: str = ""
    test_success: bool = False

    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================

    @rx.var
    def total_integrations(self) -> int:
        """Total de integrações"""
        return len(self.integrations)

    @rx.var
    def active_count(self) -> int:
        """Integrações ativas"""
        return sum(1 for i in self.integrations if i.get("status") == "active")

    @rx.var
    def inactive_count(self) -> int:
        """Integrações inativas"""
        return sum(1 for i in self.integrations if i.get("status") == "inactive")

    @rx.var
    def error_count(self) -> int:
        """Integrações com erro"""
        return sum(1 for i in self.integrations if i.get("status") == "error")

    @rx.var
    def lis_integrations(self) -> List[Dict[str, Any]]:
        """Integrações de LIS"""
        return [i for i in self.integrations if i.get("category") == "lis"]

    @rx.var
    def billing_integrations(self) -> List[Dict[str, Any]]:
        """Integrações de faturamento"""
        return [i for i in self.integrations if i.get("category") == "billing"]

    @rx.var
    def other_integrations(self) -> List[Dict[str, Any]]:
        """Outras integrações (storage, communication)"""
        return [i for i in self.integrations if i.get("category") not in ["lis", "billing"]]

    @rx.var
    def active_integration_names(self) -> List[str]:
        """Nomes das integrações ativas para select de teste"""
        names = ["Todas as Integrações"]
        names.extend([i["name"] for i in self.integrations if i.get("status") == "active"])
        return names

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    async def load_integrations(self):
        """Carrega integrações do tenant"""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            tenant_id = "local"

            success, integrations, error = integration_service.get_integrations(tenant_id)

            if success:
                self.integrations = integrations
            else:
                self.error_message = error

            # Carregar catálogo
            self.available_integrations = integration_service.get_available_integrations()
        except Exception as e:
            self.error_message = f"Erro ao carregar integrações: {str(e)}"
        finally:
            self.is_loading = False

    # =========================================================================
    # TOGGLE INTEGRATION
    # =========================================================================

    async def toggle_integration(self, integration_id: str, active: bool):
        """Ativa ou desativa uma integração"""
        self.is_loading = True
        yield

        try:
            success, error = integration_service.toggle_integration(integration_id, active)

            if success:
                action = "ativada" if active else "desativada"
                self.success_message = f"Integração {action} com sucesso"
                await self.load_integrations()
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False

    # =========================================================================
    # SYNC
    # =========================================================================

    async def sync_integration(self, integration_id: str):
        """Sincroniza uma integração específica"""
        self.is_syncing = True
        self.error_message = ""
        yield

        try:
            success, message = integration_service.sync_integration(integration_id)

            if success:
                self.success_message = message
                await self.load_integrations()
            else:
                self.error_message = message
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_syncing = False

    async def sync_all_integrations(self):
        """Sincroniza todas as integrações ativas"""
        self.is_syncing = True
        self.error_message = ""
        yield

        try:
            tenant_id = "local"
            success_count, error_count = integration_service.sync_all(tenant_id)

            if error_count == 0:
                self.success_message = f"{success_count} integração(ões) sincronizada(s) com sucesso"
            else:
                self.success_message = f"{success_count} sucesso, {error_count} erro(s)"

            await self.load_integrations()
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_syncing = False

    # =========================================================================
    # CONNECTION TEST
    # =========================================================================

    def set_test_selected(self, value: str):
        """Define integração selecionada para teste"""
        self.test_selected = value

    async def run_connection_test(self):
        """Executa teste de conexão"""
        self.is_testing = True
        self.test_result = ""
        self.test_success = False
        self.error_message = ""
        yield

        try:
            if self.test_selected == "all" or self.test_selected == "Todas as Integrações":
                # Testar todas as ativas
                results = []
                for integration in self.integrations:
                    if integration.get("status") == "active":
                        success, message = integration_service.test_connection(integration["id"])
                        results.append(f"{'✓' if success else '✗'} {integration['name']}: {message}")

                if results:
                    self.test_result = "\n".join(results)
                    self.test_success = all("✓" in r for r in results)
                else:
                    self.test_result = "Nenhuma integração ativa para testar"
                    self.test_success = False
            else:
                # Testar integração específica
                integration = next(
                    (i for i in self.integrations if i["name"] == self.test_selected),
                    None
                )
                if integration:
                    success, message = integration_service.test_connection(integration["id"])
                    self.test_result = message
                    self.test_success = success
                else:
                    self.test_result = "Integração não encontrada"
                    self.test_success = False
        except Exception as e:
            self.test_result = f"Erro no teste: {str(e)}"
            self.test_success = False
        finally:
            self.is_testing = False

    # =========================================================================
    # CONFIGURATION MODAL
    # =========================================================================

    def open_config_modal(self, integration_id: str):
        """Abre modal de configuração"""
        integration = next((i for i in self.integrations if i["id"] == integration_id), None)
        if integration:
            self.current_integration_id = integration_id
            self.current_integration_name = integration.get("name", "")
            self.config_fields = integration.get("config", {})
            self.show_config_modal = True
            self.error_message = ""

    def close_config_modal(self):
        """Fecha modal de configuração"""
        self.show_config_modal = False
        self.current_integration_id = ""
        self.config_fields = {}

    def update_config_field(self, field: str, value: str):
        """Atualiza campo de configuração"""
        self.config_fields[field] = value

    async def save_config(self):
        """Salva configuração da integração"""
        if not self.current_integration_id:
            return

        self.is_loading = True
        yield

        try:
            success, error = integration_service.update_integration(
                self.current_integration_id,
                {"config": self.config_fields}
            )

            if success:
                self.success_message = "Configuração salva com sucesso"
                self.show_config_modal = False
                await self.load_integrations()
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False

    # =========================================================================
    # ADD INTEGRATION
    # =========================================================================

    def open_add_modal(self):
        """Abre modal para adicionar integração"""
        self.show_add_modal = True
        self.error_message = ""

    def close_add_modal(self):
        """Fecha modal de adicionar"""
        self.show_add_modal = False

    async def add_integration(self, integration_key: str):
        """Adiciona uma nova integração do catálogo"""
        catalog_item = next(
            (i for i in self.available_integrations if i["key"] == integration_key),
            None
        )
        if not catalog_item:
            self.error_message = "Integração não encontrada no catálogo"
            return

        self.is_loading = True
        yield

        try:
            tenant_id = "local"

            success, integration, error = integration_service.create_integration({
                "name": catalog_item["name"],
                "description": catalog_item["description"],
                "category": catalog_item["category"],
                "icon": catalog_item["icon"],
                "tenant_id": tenant_id,
                "config": {}
            })

            if success:
                self.success_message = f"{catalog_item['name']} adicionada com sucesso"
                self.show_add_modal = False
                await self.load_integrations()
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False

    # =========================================================================
    # DELETE INTEGRATION
    # =========================================================================

    async def remove_integration(self, integration_id: str):
        """Remove uma integração"""
        self.is_loading = True
        yield

        try:
            success, error = integration_service.delete_integration(integration_id)

            if success:
                self.success_message = "Integração removida com sucesso"
                await self.load_integrations()
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def clear_messages(self):
        """Limpa mensagens de feedback"""
        self.error_message = ""
        self.success_message = ""
        self.test_result = ""

    @staticmethod
    def format_last_sync(last_sync: Optional[str]) -> str:
        """Formata última sincronização para exibição"""
        if not last_sync:
            return None

        try:
            dt = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
            now = datetime.utcnow()
            diff = now - dt.replace(tzinfo=None)

            if diff < timedelta(minutes=1):
                return "Agora"
            elif diff < timedelta(hours=1):
                minutes = int(diff.total_seconds() / 60)
                return f"Há {minutes} min"
            elif diff < timedelta(hours=24):
                hours = int(diff.total_seconds() / 3600)
                return f"Há {hours} hora{'s' if hours > 1 else ''}"
            else:
                return dt.strftime("%d/%m às %H:%M")
        except:
            return None

    @staticmethod
    def get_category_display(category: str) -> str:
        """Retorna nome da categoria para exibição"""
        categories = {
            "lis": "LIS",
            "billing": "Faturamento",
            "storage": "Storage",
            "communication": "Comunicação"
        }
        return categories.get(category, "Outro")
