"""
TeamService - Gerenciamento de Equipe e Permissões
CRUD completo de membros com suporte a Supabase e fallback SQLite local
"""
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import secrets
from .supabase_client import supabase
from .local_storage import local_storage
from ..config import Config


class TeamService:
    """Serviço de gerenciamento de equipe com suporte a Supabase e SQLite local"""

    def __init__(self):
        self.client = supabase
        self.local = local_storage
        self._use_local = self.client is None

    # =========================================================================
    # TEAM MEMBERS
    # =========================================================================

    def get_team_members(self, tenant_id: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Lista todos os membros da equipe de um tenant.

        Returns:
            Tuple[success, members_list, error_message]
        """
        # Usar armazenamento local se Supabase não estiver configurado
        if self._use_local:
            try:
                members = self.local.get_team_members(tenant_id)
                return True, members, ""
            except Exception as e:
                return False, [], f"Erro ao buscar membros: {str(e)}"

        try:
            response = self.client.table("team_members")\
                .select("*")\
                .eq("tenant_id", tenant_id)\
                .order("created_at", desc=True)\
                .execute()

            return True, response.data or [], ""
        except Exception as e:
            print(f"Erro ao buscar membros do Supabase: {e}")
            # Fallback para local
            try:
                members = self.local.get_team_members(tenant_id)
                return True, members, ""
            except:
                return self._get_mock_members()

    def get_member_by_id(self, member_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Busca um membro específico"""
        if self._use_local:
            try:
                member = self.local.get_member_by_id(member_id)
                return True, member, ""
            except Exception as e:
                return False, None, str(e)

        try:
            response = self.client.table("team_members")\
                .select("*")\
                .eq("id", member_id)\
                .single()\
                .execute()

            return True, response.data, ""
        except Exception as e:
            return False, None, str(e)

    def create_member(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Cria um novo membro da equipe.

        Args:
            data: {email, name, role, tenant_id, invited_by}
        """
        if self._use_local:
            return self.local.create_member(data)

        try:
            # Verificar se email já existe no tenant
            existing = self.client.table("team_members")\
                .select("id")\
                .eq("email", data["email"])\
                .eq("tenant_id", data["tenant_id"])\
                .execute()

            if existing.data:
                return False, None, "Este email já está cadastrado na equipe"

            # Criar membro
            member_data = {
                "email": data["email"],
                "name": data.get("name", data["email"].split("@")[0]),
                "role": data.get("role", "viewer"),
                "status": "pending",
                "tenant_id": data["tenant_id"],
                "invited_by": data.get("invited_by", ""),
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("team_members")\
                .insert(member_data)\
                .execute()

            return True, response.data[0] if response.data else None, ""
        except Exception as e:
            return False, None, f"Erro ao criar membro: {str(e)}"

    def update_member(self, member_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza dados de um membro.

        Args:
            member_id: ID do membro
            data: Campos a atualizar {name, role, status}
        """
        if self._use_local:
            return self.local.update_member(member_id, data)

        try:
            update_data = {}
            if "name" in data:
                update_data["name"] = data["name"]
            if "role" in data:
                update_data["role"] = data["role"]
            if "status" in data:
                update_data["status"] = data["status"]
            if "last_active" in data:
                update_data["last_active"] = data["last_active"]

            self.client.table("team_members")\
                .update(update_data)\
                .eq("id", member_id)\
                .execute()

            return True, ""
        except Exception as e:
            return False, f"Erro ao atualizar membro: {str(e)}"

    def delete_member(self, member_id: str) -> Tuple[bool, str]:
        """Remove um membro da equipe"""
        if self._use_local:
            return self.local.delete_member(member_id)

        try:
            self.client.table("team_members")\
                .delete()\
                .eq("id", member_id)\
                .execute()

            return True, ""
        except Exception as e:
            return False, f"Erro ao remover membro: {str(e)}"

    def change_member_status(self, member_id: str, new_status: str) -> Tuple[bool, str]:
        """Altera status do membro (active, inactive, pending)"""
        return self.update_member(member_id, {"status": new_status})

    def change_member_role(self, member_id: str, new_role: str) -> Tuple[bool, str]:
        """Altera papel do membro"""
        valid_roles = ["admin_global", "admin_lab", "analyst", "viewer"]
        if new_role not in valid_roles:
            return False, f"Papel inválido. Use: {', '.join(valid_roles)}"
        return self.update_member(member_id, {"role": new_role})

    # =========================================================================
    # INVITES
    # =========================================================================

    def create_invite(
        self,
        email: str,
        role: str,
        tenant_id: str,
        invited_by: str,
        message: str = ""
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Cria um convite para novo membro.

        Returns:
            Tuple[success, invite_data, error_message]
        """
        if self._use_local:
            return self.local.create_invite(email, role, tenant_id, invited_by, message)

        try:
            # Verificar se já existe membro com este email
            existing = self.client.table("team_members")\
                .select("id")\
                .eq("email", email)\
                .eq("tenant_id", tenant_id)\
                .execute()

            if existing.data:
                return False, None, "Este email já está na equipe"

            # Gerar token único
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

            invite_data = {
                "email": email,
                "role": role,
                "tenant_id": tenant_id,
                "invited_by": invited_by,
                "token": token,
                "message": message,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("team_invites")\
                .insert(invite_data)\
                .execute()

            return True, response.data[0] if response.data else None, ""
        except Exception as e:
            return False, None, f"Erro ao criar convite: {str(e)}"

    def get_pending_invites(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Lista convites pendentes"""
        if self._use_local:
            return []  # Local storage não usa sistema de convites separado

        try:
            response = self.client.table("team_invites")\
                .select("*")\
                .eq("tenant_id", tenant_id)\
                .eq("status", "pending")\
                .execute()

            return response.data or []
        except:
            return []

    def accept_invite(self, token: str, user_name: str = "") -> Tuple[bool, str]:
        """Aceita um convite e cria o membro"""
        if self._use_local:
            return False, "Sistema local não suporta convites via token"

        try:
            # Buscar convite pelo token
            response = self.client.table("team_invites")\
                .select("*")\
                .eq("token", token)\
                .eq("status", "pending")\
                .single()\
                .execute()

            invite = response.data
            if not invite:
                return False, "Convite não encontrado ou já utilizado"

            # Verificar expiração
            expires_at = datetime.fromisoformat(invite["expires_at"].replace("Z", "+00:00"))
            if datetime.utcnow() > expires_at.replace(tzinfo=None):
                return False, "Este convite expirou"

            # Criar membro
            success, _, error = self.create_member({
                "email": invite["email"],
                "name": user_name or invite["email"].split("@")[0],
                "role": invite["role"],
                "tenant_id": invite["tenant_id"],
                "invited_by": invite["invited_by"]
            })

            if not success:
                return False, error

            # Marcar convite como aceito
            self.client.table("team_invites")\
                .update({"status": "accepted"})\
                .eq("id", invite["id"])\
                .execute()

            return True, "Convite aceito com sucesso!"
        except Exception as e:
            return False, f"Erro ao aceitar convite: {str(e)}"

    def resend_invite(self, invite_id: str) -> Tuple[bool, str]:
        """Reenvia um convite (renova expiração)"""
        if self._use_local:
            return self.local.resend_invite(invite_id)

        try:
            new_expires = (datetime.utcnow() + timedelta(days=7)).isoformat()
            new_token = secrets.token_urlsafe(32)

            self.client.table("team_invites")\
                .update({
                    "token": new_token,
                    "expires_at": new_expires
                })\
                .eq("id", invite_id)\
                .execute()

            return True, "Convite reenviado com sucesso"
        except Exception as e:
            return False, f"Erro ao reenviar convite: {str(e)}"

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_team_stats(self, tenant_id: str) -> Dict[str, int]:
        """Retorna estatísticas da equipe"""
        success, members, _ = self.get_team_members(tenant_id)
        if not success:
            return {"total": 0, "active": 0, "pending": 0, "admins": 0}

        stats = {
            "total": len(members),
            "active": sum(1 for m in members if m.get("status") == "active"),
            "pending": sum(1 for m in members if m.get("status") == "pending"),
            "admins": sum(1 for m in members if m.get("role") in ["admin_global", "admin_lab"]),
        }
        return stats

    # =========================================================================
    # MOCK DATA (fallback quando Supabase não está configurado)
    # =========================================================================

    def _get_mock_members(self) -> Tuple[bool, List[Dict[str, Any]], str]:
        """Retorna dados mock para desenvolvimento"""
        mock_members = [
            {
                "id": "1",
                "email": "admin@labbridge.com",
                "name": "Admin Principal",
                "role": "admin_global",
                "status": "active",
                "last_active": datetime.utcnow().isoformat(),
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "2",
                "email": "joao@laboratorio.com",
                "name": "Dr. João Silva",
                "role": "admin_lab",
                "status": "active",
                "last_active": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "created_at": "2024-01-15T00:00:00"
            },
            {
                "id": "3",
                "email": "ana@laboratorio.com",
                "name": "Ana Costa",
                "role": "analyst",
                "status": "active",
                "last_active": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "created_at": "2024-02-01T00:00:00"
            },
            {
                "id": "4",
                "email": "carlos@laboratorio.com",
                "name": "Carlos Souza",
                "role": "analyst",
                "status": "active",
                "last_active": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "created_at": "2024-02-15T00:00:00"
            },
            {
                "id": "5",
                "email": "maria@laboratorio.com",
                "name": "Maria Santos",
                "role": "viewer",
                "status": "active",
                "last_active": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "created_at": "2024-03-01T00:00:00"
            },
            {
                "id": "6",
                "email": "pedro@laboratorio.com",
                "name": "Pedro Lima",
                "role": "viewer",
                "status": "active",
                "last_active": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                "created_at": "2024-03-15T00:00:00"
            },
            {
                "id": "7",
                "email": "julia@laboratorio.com",
                "name": "Julia Oliveira",
                "role": "analyst",
                "status": "pending",
                "last_active": None,
                "created_at": "2024-04-01T00:00:00"
            },
            {
                "id": "8",
                "email": "lucas@laboratorio.com",
                "name": "Lucas Mendes",
                "role": "viewer",
                "status": "pending",
                "last_active": None,
                "created_at": "2024-04-05T00:00:00"
            },
        ]
        return True, mock_members, ""


# Singleton
team_service = TeamService()
