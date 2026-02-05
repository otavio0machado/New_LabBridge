"""
RBAC Middleware - Role-Based Access Control
Controle de acesso baseado em roles para LabBridge
"""
from typing import List, Dict, Callable, Any, Optional
from functools import wraps
from datetime import datetime


class RBACMiddleware:
    """Middleware para controle de acesso baseado em roles"""

    # Definicao de roles e hierarquia
    ROLES = {
        "admin_global": 100,  # Acesso total
        "admin_lab": 80,      # Gerencia do lab
        "owner": 80,          # Alias para admin_lab
        "admin": 80,          # Alias para admin_lab
        "analyst": 50,        # Operacoes
        "member": 50,         # Alias para analyst
        "viewer": 10,         # Apenas leitura
    }

    # Rotas protegidas e roles permitidas
    PROTECTED_ROUTES: Dict[str, List[str]] = {
        "/": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member", "viewer"],
        "/dashboard": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member", "viewer"],
        "/analise": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member"],
        "/history": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member", "viewer"],
        "/reports": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member"],
        "/team": ["admin_global", "admin_lab", "owner", "admin"],
        "/settings": ["admin_global", "admin_lab", "owner", "admin"],
        "/integrations": ["admin_global", "admin_lab", "owner", "admin"],
        "/billing": ["admin_global", "admin_lab", "owner"],
    }

    # Acoes e permissoes
    ACTION_PERMISSIONS: Dict[str, List[str]] = {
        "create_analysis": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member"],
        "view_analysis": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member", "viewer"],
        "delete_analysis": ["admin_global", "admin_lab", "owner", "admin"],
        "export_data": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member"],
        "invite_member": ["admin_global", "admin_lab", "owner", "admin"],
        "remove_member": ["admin_global", "admin_lab", "owner", "admin"],
        "change_permissions": ["admin_global", "admin_lab", "owner", "admin"],
        "manage_settings": ["admin_global", "admin_lab", "owner", "admin"],
        "manage_integrations": ["admin_global", "admin_lab", "owner", "admin"],
        "manage_billing": ["admin_global", "admin_lab", "owner"],
        "resolve_item": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member"],
        "annotate_item": ["admin_global", "admin_lab", "owner", "admin", "analyst", "member"],
    }

    @classmethod
    def get_role_level(cls, role: str) -> int:
        """Retorna o nivel hierarquico de uma role"""
        return cls.ROLES.get(role.lower(), 0)

    @classmethod
    def check_route_access(cls, route: str, user_role: str) -> bool:
        """
        Verifica se uma role tem acesso a uma rota

        Args:
            route: Caminho da rota (ex: "/team")
            user_role: Role do usuario

        Returns:
            True se tem acesso, False caso contrario
        """
        if not user_role:
            return False

        # Normalizar role
        role = user_role.lower()

        # Buscar permissoes da rota
        allowed_roles = cls.PROTECTED_ROUTES.get(route)

        # Rota nao protegida = acesso livre
        if allowed_roles is None:
            return True

        # Verificar se role esta na lista
        return role in [r.lower() for r in allowed_roles]

    @classmethod
    def check_action_permission(cls, action: str, user_role: str) -> bool:
        """
        Verifica se uma role pode executar uma acao

        Args:
            action: Nome da acao (ex: "delete_analysis")
            user_role: Role do usuario

        Returns:
            True se pode executar, False caso contrario
        """
        if not user_role:
            return False

        role = user_role.lower()
        allowed_roles = cls.ACTION_PERMISSIONS.get(action)

        if allowed_roles is None:
            return True

        return role in [r.lower() for r in allowed_roles]

    @classmethod
    def has_higher_or_equal_role(cls, user_role: str, required_role: str) -> bool:
        """
        Verifica se user_role tem nivel >= required_role

        Args:
            user_role: Role do usuario
            required_role: Role minima necessaria

        Returns:
            True se nivel suficiente
        """
        user_level = cls.get_role_level(user_role)
        required_level = cls.get_role_level(required_role)
        return user_level >= required_level

    @classmethod
    def get_allowed_routes(cls, user_role: str) -> List[str]:
        """Retorna lista de rotas permitidas para uma role"""
        if not user_role:
            return []

        role = user_role.lower()
        allowed = []

        for route, roles in cls.PROTECTED_ROUTES.items():
            if role in [r.lower() for r in roles]:
                allowed.append(route)

        return allowed

    @classmethod
    def get_allowed_actions(cls, user_role: str) -> List[str]:
        """Retorna lista de acoes permitidas para uma role"""
        if not user_role:
            return []

        role = user_role.lower()
        allowed = []

        for action, roles in cls.ACTION_PERMISSIONS.items():
            if role in [r.lower() for r in roles]:
                allowed.append(action)

        return allowed


def require_role(*required_roles: str):
    """
    Decorator para verificar role antes de executar funcao

    Uso:
        @require_role("admin", "analyst")
        async def my_protected_function(self):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Obter role do usuario do state
            user_role = getattr(self, 'user_role', None)
            if user_role is None and hasattr(self, 'current_user'):
                user = getattr(self, 'current_user', None)
                if user:
                    user_role = getattr(user, 'role', None)

            # Verificar permissao
            has_permission = False
            if user_role:
                role = user_role.lower()
                for required in required_roles:
                    if role == required.lower() or RBACMiddleware.has_higher_or_equal_role(role, required):
                        has_permission = True
                        break

            if not has_permission:
                # Logar tentativa de acesso negado
                log_access_attempt(
                    user_id=getattr(self, 'user_id', 'unknown'),
                    action=func.__name__,
                    granted=False,
                    role=user_role or 'none'
                )

                # Definir mensagem de erro se state tiver
                if hasattr(self, 'error_message'):
                    self.error_message = "Voce nao tem permissao para executar esta acao"

                return None

            # Logar acesso permitido
            log_access_attempt(
                user_id=getattr(self, 'user_id', 'unknown'),
                action=func.__name__,
                granted=True,
                role=user_role
            )

            # Executar funcao
            return await func(self, *args, **kwargs)

        return wrapper
    return decorator


def check_route_access(route: str, user_role: str) -> bool:
    """
    Funcao helper para verificar acesso a rota

    Args:
        route: Caminho da rota
        user_role: Role do usuario

    Returns:
        True se tem acesso
    """
    return RBACMiddleware.check_route_access(route, user_role)


def log_access_attempt(user_id: str, action: str, granted: bool, role: str = ""):
    """
    Loga tentativa de acesso para auditoria

    Args:
        user_id: ID do usuario
        action: Acao tentada
        granted: Se foi permitido
        role: Role do usuario
    """
    timestamp = datetime.now().isoformat()
    status = "GRANTED" if granted else "DENIED"

    # Log simples (pode ser expandido para salvar no banco)
    print(f"[RBAC] {timestamp} | {status} | user={user_id} | role={role} | action={action}")


# Constantes para uso nos templates
ROLE_LABELS = {
    "admin_global": "Administrador Global",
    "admin_lab": "Administrador do Lab",
    "owner": "Proprietario",
    "admin": "Administrador",
    "analyst": "Analista",
    "member": "Membro",
    "viewer": "Visualizador",
}

ROLE_COLORS = {
    "admin_global": "#E53E3E",  # Vermelho
    "admin_lab": "#DD6B20",     # Laranja
    "owner": "#DD6B20",
    "admin": "#DD6B20",
    "analyst": "#3182CE",       # Azul
    "member": "#3182CE",
    "viewer": "#718096",        # Cinza
}
