"""
AuthState - Estado de Autenticacao
Gerencia login, logout e contexto do usuario/tenant usando Supabase Auth.
"""
import reflex as rx
from typing import Optional
from ..config import Config
from ..models import User, Tenant
import logging

logger = logging.getLogger(__name__)


class AuthState(rx.State):
    """Estado responsavel pela autenticacao e controle de acesso"""

    # Autenticacao
    is_authenticated: bool = False
    login_email: str = ""
    login_password: str = ""
    login_error: str = ""
    login_loading: bool = False

    # Rate limiting: track failed login attempts
    _login_attempts: int = 0
    _login_lockout_until: float = 0.0  # timestamp

    # Registro
    register_lab_name: str = ""
    register_email: str = ""
    register_password: str = ""
    register_confirm_password: str = ""
    register_error: str = ""
    register_success: str = ""
    register_loading: bool = False
    show_register: bool = False

    # Recuperacao de senha
    reset_email: str = ""
    reset_error: str = ""
    reset_success: str = ""
    reset_loading: bool = False
    show_reset_password: bool = False

    # Multi-tenant Context
    current_user: Optional[User] = None
    current_tenant: Optional[Tenant] = None

    # Setters para formularios
    def set_login_email(self, email: str):
        self.login_email = email
        self.login_error = ""

    def set_login_password(self, password: str):
        self.login_password = password
        self.login_error = ""

    def set_register_lab_name(self, value: str):
        self.register_lab_name = value
        self.register_error = ""

    def set_register_email(self, value: str):
        self.register_email = value
        self.register_error = ""

    def set_register_password(self, value: str):
        self.register_password = value
        self.register_error = ""

    def set_register_confirm_password(self, value: str):
        self.register_confirm_password = value
        self.register_error = ""

    def set_reset_email(self, value: str):
        self.reset_email = value
        self.reset_error = ""

    def toggle_register_view(self):
        """Alterna entre login e registro"""
        self.show_register = not self.show_register
        self.show_reset_password = False
        self.login_error = ""
        self.register_error = ""
        self.register_success = ""

    def toggle_reset_password_view(self):
        """Alterna para a view de recuperacao de senha"""
        self.show_reset_password = not self.show_reset_password
        self.show_register = False
        self.login_error = ""
        self.reset_error = ""
        self.reset_success = ""
        self.reset_email = ""

    async def request_password_reset(self):
        """Solicita redefinicao de senha via email"""
        from ..services.auth_service import auth_service

        if not self.reset_email.strip():
            self.reset_error = "Informe seu email"
            return

        self.reset_loading = True
        self.reset_error = ""
        self.reset_success = ""
        yield

        try:
            success, message = auth_service.request_password_reset(self.reset_email)

            if success:
                self.reset_success = message
                self.reset_error = ""
            else:
                self.reset_error = message

        except Exception as e:
            logger.error(f"Erro na recuperacao de senha: {e}")
            self.reset_error = f"Erro de conexao: {str(e)}"

        finally:
            self.reset_loading = False

    async def attempt_login(self):
        """Tenta realizar login com as credenciais fornecidas"""
        from ..services.auth_service import auth_service
        import time

        # Validacao basica
        if not self.login_email or not self.login_password:
            self.login_error = "Preencha email e senha"
            return

        # Rate limiting: bloquear após 5 tentativas falhas por 60 segundos
        now = time.time()
        if self._login_lockout_until > now:
            remaining = int(self._login_lockout_until - now)
            self.login_error = f"Muitas tentativas. Aguarde {remaining}s antes de tentar novamente."
            return

        self.login_loading = True
        self.login_error = ""
        yield

        try:
            # Tentar login com Supabase
            success, data, error = auth_service.sign_in(
                email=self.login_email,
                password=self.login_password
            )

            if success:
                # Reset rate limiter on success
                self._login_attempts = 0
                self._login_lockout_until = 0.0

                # Extrair dados
                user_data = data.get("user", {})
                profile_data = data.get("profile", {})
                tenant_data = data.get("tenant", {})

                # Criar User model
                self.current_user = User(
                    id=user_data.get("id", ""),
                    email=user_data.get("email", self.login_email),
                    full_name=profile_data.get("full_name", "") if profile_data else "",
                    tenant_id=profile_data.get("tenant_id", "") if profile_data else "",
                    role=profile_data.get("role", "member") if profile_data else "member",
                    created_at=user_data.get("created_at", "")
                )

                # Criar Tenant model
                if tenant_data:
                    self.current_tenant = Tenant(
                        id=tenant_data.get("id", ""),
                        name=tenant_data.get("name", ""),
                        cnpj=tenant_data.get("cnpj"),
                        email=tenant_data.get("email"),
                        phone=tenant_data.get("phone"),
                        plan_type=tenant_data.get("plan_type", "starter"),
                        subscription_status=tenant_data.get("subscription_status", "active"),
                        stripe_customer_id=tenant_data.get("stripe_customer_id"),
                        settings=tenant_data.get("settings", {}),
                        created_at=str(tenant_data.get("created_at", ""))
                    )
                else:
                    # Sem tenant - usar dados minimos do login local/dev
                    self.current_tenant = Tenant(
                        id=self.current_user.tenant_id or "dev-tenant",
                        name="LabBridge",
                        plan_type="starter",
                        subscription_status="active"
                    )

                self.is_authenticated = True
                self.login_error = ""
                self.login_password = ""  # Limpar senha por seguranca

                logger.info(f"Login bem-sucedido: {self.current_user.email} (tenant: {self.current_tenant.name})")

                self.login_loading = False
                yield rx.redirect("/")

            else:
                # Check if this is an email verification error (don't count as rate limit attempt)
                if error and ("nao confirmado" in error.lower() or "not confirmed" in error.lower()):
                    self.login_error = "Email nao verificado. Verifique sua caixa de entrada (e spam) para ativar sua conta."
                    self.is_authenticated = False
                    return

                # Increment rate limiter on failure
                self._login_attempts += 1
                if self._login_attempts >= 5:
                    self._login_lockout_until = time.time() + 60  # Lock for 60 seconds
                    self._login_attempts = 0
                    self.login_error = "Muitas tentativas falhas. Conta bloqueada por 60 segundos."
                else:
                    remaining = 5 - self._login_attempts
                    self.login_error = error or f"Credenciais inválidas. {remaining} tentativa(s) restante(s)."
                self.is_authenticated = False

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            self.login_error = f"Erro de conexao: {str(e)}"
            self.is_authenticated = False

        finally:
            self.login_loading = False

    async def register_tenant(self):
        """Registra um novo laboratorio (Tenant) e o primeiro usuario (Admin)."""
        from ..services.auth_service import auth_service

        # Validacoes
        if not self.register_lab_name.strip():
            self.register_error = "Informe o nome do laboratorio"
            return

        if not self.register_email.strip():
            self.register_error = "Informe seu email"
            return

        if not self.register_password:
            self.register_error = "Informe uma senha"
            return

        if len(self.register_password) < 6:
            self.register_error = "Senha deve ter pelo menos 6 caracteres"
            return

        if self.register_password != self.register_confirm_password:
            self.register_error = "Senhas nao conferem"
            return

        self.register_loading = True
        self.register_error = ""
        self.register_success = ""
        yield

        try:
            # Registrar no Supabase
            success, data, error = auth_service.sign_up(
                email=self.register_email,
                password=self.register_password,
                lab_name=self.register_lab_name,
                full_name=self.register_lab_name  # Usar nome do lab como nome inicial
            )

            if success:
                self.register_success = (
                    "Conta criada com sucesso! Verifique seu email para confirmar o cadastro. "
                    "Voce recebera um link de ativacao em instantes."
                )
                self.register_error = ""

                # Limpar campos
                self.register_lab_name = ""
                self.register_email = ""
                self.register_password = ""
                self.register_confirm_password = ""

                # Alternar para view de login apos 3 segundos (mais tempo para ler mensagem)
                yield
                import asyncio
                await asyncio.sleep(3)
                self.show_register = False

            else:
                self.register_error = error or "Erro ao criar conta"

        except Exception as e:
            logger.error(f"Erro no registro: {e}")
            self.register_error = f"Erro de conexao: {str(e)}"

        finally:
            self.register_loading = False

    def logout(self):
        """Realiza logout do usuario"""
        from ..services.auth_service import auth_service

        try:
            auth_service.sign_out()
        except Exception as e:
            logger.error(f"Erro no logout: {e}")

        # Limpar estado
        self.is_authenticated = False
        self.login_email = ""
        self.login_password = ""
        self.login_error = ""
        self.current_user = None
        self.current_tenant = None

        return rx.redirect("/login")

    def check_auth(self):
        """Verifica se o usuario esta autenticado e redireciona se nao estiver"""
        if not self.is_authenticated:
            return rx.redirect("/login")

    @rx.var
    def user_email(self) -> str:
        """Email do usuario atual"""
        if self.current_user:
            return self.current_user.email
        return ""

    @rx.var
    def user_role(self) -> str:
        """Role do usuario atual"""
        if self.current_user:
            return self.current_user.role
        return "member"

    @rx.var
    def tenant_name(self) -> str:
        """Nome do tenant atual"""
        if self.current_tenant:
            return self.current_tenant.name
        return "LabBridge"

    @rx.var
    def tenant_plan(self) -> str:
        """Plano do tenant atual"""
        if self.current_tenant:
            return self.current_tenant.plan_type
        return "starter"

    @rx.var
    def is_owner(self) -> bool:
        """Verifica se usuario e owner do tenant"""
        return self.user_role == "owner"

    @rx.var
    def is_admin(self) -> bool:
        """Verifica se usuario e admin ou owner"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab"]

    @rx.var
    def is_analyst(self) -> bool:
        """Verifica se usuario e analyst ou superior"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab", "analyst", "member"]

    @rx.var
    def is_viewer(self) -> bool:
        """Verifica se usuario e viewer ou superior (todos autenticados)"""
        return self.is_authenticated

    @rx.var
    def can_create_analysis(self) -> bool:
        """Verifica se pode criar analises"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab", "analyst", "member"]

    @rx.var
    def can_delete_analysis(self) -> bool:
        """Verifica se pode deletar analises"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab"]

    @rx.var
    def can_export_data(self) -> bool:
        """Verifica se pode exportar dados"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab", "analyst", "member"]

    @rx.var
    def can_manage_team(self) -> bool:
        """Verifica se pode gerenciar equipe"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab"]

    @rx.var
    def can_manage_settings(self) -> bool:
        """Verifica se pode gerenciar configuracoes"""
        return self.user_role in ["owner", "admin", "admin_global", "admin_lab"]

    # =========================================================================
    # OAUTH SOCIAL LOGIN
    # =========================================================================

    oauth_loading: bool = False
    oauth_error: str = ""

    async def login_with_google(self):
        """Inicia login com Google OAuth"""
        from ..services.auth_service import auth_service
        
        self.oauth_loading = True
        self.oauth_error = ""
        yield
        
        try:
            # Iniciar fluxo OAuth com Google
            success, data, error = auth_service.sign_in_with_oauth("google")
            
            if success and data:
                # Supabase retorna URL para redirecionamento
                redirect_url = data.get("url")
                if redirect_url:
                    self.oauth_loading = False
                    yield rx.redirect(redirect_url)
                else:
                    self.oauth_error = "Erro ao obter URL de autenticação"
            else:
                self.oauth_error = error or "Erro ao iniciar login com Google"
                
        except Exception as e:
            logger.error(f"Erro OAuth Google: {e}")
            self.oauth_error = f"Erro: {str(e)}"
        
        finally:
            self.oauth_loading = False

    async def login_with_microsoft(self):
        """Inicia login com Microsoft OAuth"""
        from ..services.auth_service import auth_service
        
        self.oauth_loading = True
        self.oauth_error = ""
        yield
        
        try:
            # Iniciar fluxo OAuth com Microsoft (Azure)
            success, data, error = auth_service.sign_in_with_oauth("azure")
            
            if success and data:
                redirect_url = data.get("url")
                if redirect_url:
                    self.oauth_loading = False
                    yield rx.redirect(redirect_url)
                else:
                    self.oauth_error = "Erro ao obter URL de autenticação"
            else:
                self.oauth_error = error or "Erro ao iniciar login com Microsoft"
                
        except Exception as e:
            logger.error(f"Erro OAuth Microsoft: {e}")
            self.oauth_error = f"Erro: {str(e)}"
        
        finally:
            self.oauth_loading = False

    async def handle_oauth_callback(self):
        """Processa callback do OAuth após autenticação"""
        from ..services.auth_service import auth_service

        self.oauth_error = ""

        try:
            # Verificar se há sessão válida
            user = auth_service.get_current_user()

            if user:
                # Buscar ou criar perfil
                profile = auth_service.get_or_create_profile(user)

                tenant_id = profile.get("tenant_id", "") if profile else ""

                self.current_user = User(
                    id=user.get("id", ""),
                    email=user.get("email", ""),
                    full_name=profile.get("full_name", "") if profile else "",
                    tenant_id=tenant_id,
                    role=profile.get("role", "member") if profile else "member",
                    created_at=user.get("created_at", "")
                )

                # Carregar tenant para o contexto
                if tenant_id:
                    tenant_data = auth_service._load_tenant(tenant_id)
                    if tenant_data:
                        self.current_tenant = Tenant(
                            id=tenant_data.get("id", ""),
                            name=tenant_data.get("name", ""),
                            cnpj=tenant_data.get("cnpj"),
                            email=tenant_data.get("email"),
                            phone=tenant_data.get("phone"),
                            plan_type=tenant_data.get("plan_type", "starter"),
                            subscription_status=tenant_data.get("subscription_status", "active"),
                            stripe_customer_id=tenant_data.get("stripe_customer_id"),
                            settings=tenant_data.get("settings", {}),
                            created_at=str(tenant_data.get("created_at", ""))
                        )

                self.is_authenticated = True
                return rx.redirect("/")
            else:
                self.oauth_error = "Sessão não encontrada. Tente fazer login novamente."

        except Exception as e:
            logger.error(f"Erro no callback OAuth: {e}")
            self.oauth_error = f"Erro ao processar autenticação: {str(e)}"
