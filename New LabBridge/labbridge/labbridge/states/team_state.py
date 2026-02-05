"""
TeamState - Estado para gerenciamento de equipe
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..services.team_service import team_service
from .auth_state import AuthState


class TeamState(AuthState):
    """Estado para página de Usuários & Permissões - herda de AuthState para acesso ao tenant_id"""

    # Lista de membros
    team_members: List[Dict[str, Any]] = []

    # Loading states
    is_loading: bool = False
    is_saving: bool = False

    # Modal states
    show_invite_modal: bool = False
    show_edit_modal: bool = False

    # Form fields
    invite_email: str = ""
    invite_role: str = "viewer"
    invite_message: str = ""

    # Edit fields
    edit_member_id: str = ""
    edit_member_name: str = ""
    edit_member_role: str = ""

    # Feedback
    error_message: str = ""
    success_message: str = ""

    # Remove confirmation
    show_remove_confirm: bool = False
    remove_member_id: str = ""
    remove_member_name: str = ""

    # Search
    search_query: str = ""

    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================

    @rx.var
    def filtered_members(self) -> List[Dict[str, Any]]:
        """Membros filtrados pela busca"""
        if not self.search_query:
            return self.team_members

        query = self.search_query.lower()
        return [
            m for m in self.team_members
            if query in m.get("name", "").lower()
            or query in m.get("email", "").lower()
        ]

    @rx.var
    def total_members(self) -> int:
        """Total de membros"""
        return len(self.team_members)

    @rx.var
    def active_members_count(self) -> int:
        """Membros ativos"""
        return sum(1 for m in self.team_members if m.get("status") == "active")

    @rx.var
    def pending_members_count(self) -> int:
        """Membros pendentes"""
        return sum(1 for m in self.team_members if m.get("status") == "pending")

    @rx.var
    def admin_count(self) -> int:
        """Total de admins"""
        return sum(1 for m in self.team_members if m.get("role") in ["admin_global", "admin_lab"])

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    async def load_team_members(self):
        """Carrega membros da equipe"""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            # Obter tenant_id do usuário logado
            tenant_id = self.current_user.tenant_id if self.current_user else None

            if not tenant_id:
                self.error_message = "Usuário não autenticado"
                self.is_loading = False
                return

            success, members, error = team_service.get_team_members(tenant_id)

            if success:
                self.team_members = members
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = f"Erro ao carregar equipe: {str(e)}"
        finally:
            self.is_loading = False

    # =========================================================================
    # INVITE MEMBER
    # =========================================================================

    def open_invite_modal(self):
        """Abre modal de convite"""
        self.show_invite_modal = True
        self.invite_email = ""
        self.invite_role = "viewer"
        self.invite_message = ""
        self.error_message = ""
        self.success_message = ""

    def close_invite_modal(self):
        """Fecha modal de convite"""
        self.show_invite_modal = False

    def set_invite_email(self, value: str):
        """Atualiza email do convite"""
        self.invite_email = value

    def set_invite_role(self, value: str):
        """Atualiza papel do convite"""
        self.invite_role = value

    def set_invite_role_label(self, label: str):
        """Converte label para valor e seta"""
        label_map = {
            "Visualizador": "viewer",
            "Analista": "analyst",
            "Admin Lab": "admin_lab",
            "Admin Global": "admin_global",
        }
        self.invite_role = label_map.get(label, "viewer")

    def set_invite_message(self, value: str):
        """Atualiza mensagem do convite"""
        self.invite_message = value

    async def send_invite(self):
        """Envia convite para novo membro"""
        from ..services.email_service import email_service
        
        if not self.invite_email:
            self.error_message = "Digite um email válido"
            return

        self.is_saving = True
        self.error_message = ""
        yield

        try:
            # Obter tenant_id do usuário logado
            tenant_id = self.current_user.tenant_id if self.current_user else None

            if not tenant_id:
                self.error_message = "Usuário não autenticado"
                self.is_saving = False
                return

            # Pegar dados do usuario logado
            invited_by = self.current_user.email if self.current_user else "usuario@labbridge.com"
            # Usar full_name ou email como fallback
            inviter_name = (self.current_user.full_name or self.current_user.email.split("@")[0]) if self.current_user else "Equipe LabBridge"

            success, invite, error = team_service.create_invite(
                email=self.invite_email,
                role=self.invite_role,
                tenant_id=tenant_id,
                invited_by=invited_by,
                message=self.invite_message
            )

            if success:
                # Enviar email de convite
                invite_token = invite.get("token", invite.get("id", ""))
                email_success, email_msg = email_service.send_team_invite(
                    to_email=self.invite_email,
                    inviter_name=inviter_name,
                    role=self.invite_role,
                    invite_token=invite_token,
                    message=self.invite_message
                )
                
                if email_success:
                    self.success_message = f"Convite enviado para {self.invite_email}"
                else:
                    self.success_message = f"Convite criado. Email: {email_msg}"
                
                self.show_invite_modal = False
                # Recarregar lista
                async for _ in self.load_team_members():
                    yield
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = f"Erro ao enviar convite: {str(e)}"
        finally:
            self.is_saving = False

    # =========================================================================
    # EDIT MEMBER
    # =========================================================================

    def open_edit_modal(self, member_id: str):
        """Abre modal de edição"""
        member = next((m for m in self.team_members if m["id"] == member_id), None)
        if member:
            self.edit_member_id = member_id
            self.edit_member_name = member.get("name", "")
            self.edit_member_role = member.get("role", "viewer")
            self.show_edit_modal = True
            self.error_message = ""

    def close_edit_modal(self):
        """Fecha modal de edição"""
        self.show_edit_modal = False
        self.edit_member_id = ""

    def set_edit_name(self, value: str):
        """Atualiza nome na edição"""
        self.edit_member_name = value

    def set_edit_role(self, value: str):
        """Atualiza papel na edição"""
        self.edit_member_role = value

    def set_edit_role_label(self, label: str):
        """Converte label para valor e seta"""
        label_map = {
            "Visualizador": "viewer",
            "Analista": "analyst",
            "Admin Lab": "admin_lab",
            "Admin Global": "admin_global",
        }
        self.edit_member_role = label_map.get(label, "viewer")

    async def save_member_edit(self):
        """Salva alterações do membro"""
        if not self.edit_member_id:
            return

        self.is_saving = True
        self.error_message = ""
        yield

        try:
            success, error = team_service.update_member(
                self.edit_member_id,
                {
                    "name": self.edit_member_name,
                    "role": self.edit_member_role
                }
            )

            if success:
                self.success_message = "Membro atualizado com sucesso"
                self.show_edit_modal = False
                async for _ in self.load_team_members():
                    yield
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = f"Erro ao atualizar: {str(e)}"
        finally:
            self.is_saving = False

    # =========================================================================
    # MEMBER ACTIONS
    # =========================================================================

    async def toggle_member_status(self, member_id: str):
        """Alterna status ativo/inativo do membro"""
        member = next((m for m in self.team_members if m["id"] == member_id), None)
        if not member:
            return

        new_status = "inactive" if member.get("status") == "active" else "active"

        self.is_saving = True
        yield

        try:
            success, error = team_service.change_member_status(member_id, new_status)

            if success:
                action = "ativado" if new_status == "active" else "desativado"
                self.success_message = f"Membro {action} com sucesso"
                async for _ in self.load_team_members():
                    yield
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_saving = False

    async def resend_member_invite(self, member_id: str):
        """Reenvia convite para membro pendente"""
        self.is_saving = True
        yield

        try:
            success, message = team_service.resend_invite(member_id)

            if success:
                self.success_message = message
            else:
                self.error_message = message
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_saving = False

    def confirm_remove_member(self, member_id: str):
        """Abre dialogo de confirmacao para remover membro"""
        member = next((m for m in self.team_members if m["id"] == member_id), None)
        self.remove_member_id = member_id
        self.remove_member_name = member.get("name", "") if member else ""
        self.show_remove_confirm = True

    def cancel_remove_member(self):
        """Cancela remocao de membro"""
        self.show_remove_confirm = False
        self.remove_member_id = ""
        self.remove_member_name = ""

    async def remove_member(self):
        """Remove membro da equipe"""
        if not self.remove_member_id:
            return

        self.show_remove_confirm = False
        self.is_saving = True
        yield

        try:
            success, error = team_service.delete_member(self.remove_member_id)

            if success:
                self.success_message = "Membro removido com sucesso"
                self.remove_member_id = ""
                self.remove_member_name = ""
                async for _ in self.load_team_members():
                    yield
            else:
                self.error_message = error
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_saving = False

    # =========================================================================
    # SEARCH
    # =========================================================================

    def set_search_query(self, value: str):
        """Atualiza filtro de busca"""
        self.search_query = value

    def clear_search(self):
        """Limpa busca"""
        self.search_query = ""

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def clear_messages(self):
        """Limpa mensagens de feedback"""
        self.error_message = ""
        self.success_message = ""

    @staticmethod
    def format_last_active(last_active: Optional[str]) -> str:
        """Formata última atividade para exibição"""
        if not last_active:
            return "-"

        try:
            dt = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
            now = datetime.utcnow()
            diff = now - dt.replace(tzinfo=None)

            if diff < timedelta(minutes=1):
                return "Agora"
            elif diff < timedelta(hours=1):
                minutes = int(diff.total_seconds() / 60)
                return f"Há {minutes} min"
            elif diff < timedelta(days=1):
                hours = int(diff.total_seconds() / 3600)
                return f"Há {hours} hora{'s' if hours > 1 else ''}"
            elif diff < timedelta(days=7):
                days = diff.days
                if days == 1:
                    return "Ontem"
                return f"Há {days} dias"
            else:
                return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return "-"

    @staticmethod
    def get_role_display(role: str) -> str:
        """Retorna nome do papel para exibição"""
        roles = {
            "owner": "Proprietario",
            "admin_global": "Admin Global",
            "admin_lab": "Admin Lab",
            "admin": "Administrador",
            "analyst": "Analista",
            "member": "Membro",
            "viewer": "Visualizador",
        }
        return roles.get(role, "Visualizador")
