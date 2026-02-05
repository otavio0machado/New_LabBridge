"""
NotificationState - Estado de Notificações In-App
Centro de notificações do LabBridge
"""
import reflex as rx
from typing import List, Dict, Any
from datetime import datetime


class NotificationState(rx.State):
    """Estado responsável pelas notificações in-app"""

    # Lista de notificações
    notifications: List[Dict[str, Any]] = []
    
    # UI State
    show_notifications: bool = False
    is_loading: bool = False

    # =========================================================================
    # COMPUTED VARS
    # =========================================================================

    @rx.var
    def unread_count(self) -> int:
        """Contagem de não lidas"""
        return sum(1 for n in self.notifications if not n.get("read", False))

    @rx.var
    def has_unread(self) -> bool:
        """Se tem notificações não lidas"""
        return self.unread_count > 0

    @rx.var
    def recent_notifications(self) -> List[Dict[str, Any]]:
        """Últimas 10 notificações"""
        return self.notifications[:10]

    # =========================================================================
    # ACTIONS
    # =========================================================================

    def toggle_notifications(self):
        """Abre/fecha painel de notificações"""
        self.show_notifications = not self.show_notifications

    def close_notifications(self):
        """Fecha painel de notificações"""
        self.show_notifications = False

    async def load_notifications(self):
        """Carrega notificações do banco"""
        from ..services.local_storage import local_storage
        
        self.is_loading = True
        
        try:
            tenant_id = "local"
            notifications = local_storage.get_notifications(tenant_id, limit=50)
            self.notifications = notifications
        except Exception as e:
            print(f"Erro ao carregar notificações: {e}")
            self.notifications = []
        finally:
            self.is_loading = False

    def mark_as_read(self, notification_id: str):
        """Marca notificação como lida"""
        from ..services.local_storage import local_storage
        
        try:
            local_storage.mark_notification_read(notification_id)
            
            # Atualizar lista local
            for n in self.notifications:
                if n.get("id") == notification_id:
                    n["read"] = True
                    break
        except Exception as e:
            print(f"Erro ao marcar como lida: {e}")

    def mark_all_read(self):
        """Marca todas como lidas"""
        from ..services.local_storage import local_storage
        
        try:
            tenant_id = "local"
            local_storage.mark_all_notifications_read(tenant_id)
            
            # Atualizar lista local
            for n in self.notifications:
                n["read"] = True
        except Exception as e:
            print(f"Erro ao marcar todas: {e}")

    def clear_notifications(self):
        """Limpa todas as notificações"""
        from ..services.local_storage import local_storage
        
        try:
            tenant_id = "local"
            local_storage.clear_notifications(tenant_id)
            self.notifications = []
        except Exception as e:
            print(f"Erro ao limpar: {e}")

    # =========================================================================
    # HELPER: CRIAR NOTIFICAÇÕES
    # =========================================================================

    @staticmethod
    def create_notification(
        title: str,
        message: str,
        type: str = "info",  # info, success, warning, error
        action_url: str = None,
        tenant_id: str = "local"
    ):
        """Cria uma nova notificação"""
        from ..services.local_storage import local_storage
        
        try:
            local_storage.add_notification(
                tenant_id=tenant_id,
                title=title,
                message=message,
                type=type,
                action_url=action_url
            )
        except Exception as e:
            print(f"Erro ao criar notificação: {e}")

    # Notificações pré-definidas
    @staticmethod
    def notify_analysis_complete(analysis_name: str, divergences: int):
        """Notifica conclusão de análise"""
        NotificationState.create_notification(
            title="Análise Concluída",
            message=f"A análise '{analysis_name}' foi concluída com {divergences} divergências.",
            type="success",
            action_url="/analise"
        )

    @staticmethod
    def notify_critical_divergence(value: float, patient: str = None):
        """Notifica divergência crítica"""
        msg = f"Divergência crítica de R$ {value:,.2f}"
        if patient:
            msg += f" detectada para {patient}"
        
        NotificationState.create_notification(
            title="⚠️ Divergência Crítica",
            message=msg,
            type="warning",
            action_url="/analise"
        )

    @staticmethod
    def notify_team_invite(email: str):
        """Notifica convite enviado"""
        NotificationState.create_notification(
            title="Convite Enviado",
            message=f"Convite enviado para {email}",
            type="info",
            action_url="/team"
        )

    @staticmethod
    def notify_export_ready(filename: str, format: str):
        """Notifica exportação pronta"""
        NotificationState.create_notification(
            title="Exportação Pronta",
            message=f"O arquivo {filename} ({format}) está pronto para download.",
            type="success",
            action_url="/reports"
        )
