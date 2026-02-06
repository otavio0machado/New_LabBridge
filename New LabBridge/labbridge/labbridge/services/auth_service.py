"""
AuthService - Servico de Autenticacao com Supabase
Gerencia login, logout, registro e sessao de usuarios.
Com fallback para login local via .env
"""
from typing import Dict, Any, Optional, Tuple
from .supabase_client import supabase
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Servico de autenticacao usando Supabase Auth com fallback local"""

    def __init__(self):
        self.client = supabase

    def _try_local_login(self, email: str, password: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Tenta login local usando credenciais do .env
        Apenas para desenvolvimento - desabilitado em producao
        """
        if Config.IS_PRODUCTION:
            return False, {}, ""
        if Config.AUTH_EMAIL and Config.AUTH_PASSWORD:
            if email == Config.AUTH_EMAIL and password == Config.AUTH_PASSWORD:
                return True, {
                    "user": {
                        "id": "local-admin",
                        "email": email,
                        "created_at": ""
                    },
                    "profile": {
                        "tenant_id": "dev-tenant",
                        "role": "admin"
                    },
                    "tenant": {
                        "id": "dev-tenant",
                        "name": "LabBridge Dev",
                        "plan_type": "enterprise",
                        "subscription_status": "active"
                    },
                    "session": {
                        "access_token": "local-token",
                        "refresh_token": None
                    }
                }, ""
        return False, {}, ""

    def sign_in(self, email: str, password: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Realiza login com email e senha.
        Primeiro tenta login local (.env), depois Supabase.

        Returns:
            Tuple[success, user_data, error_message]
        """
        # 1. Tentar login local primeiro (credenciais do .env)
        local_success, local_data, _ = self._try_local_login(email, password)
        if local_success:
            return True, local_data, ""

        # 2. Se não houver cliente Supabase, retornar erro
        if not self.client:
            return False, {}, "Email ou senha incorretos"

        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                # Carregar profile do usuario
                profile_data = self._load_profile(response.user.id)
                tenant_data = None

                if profile_data and profile_data.get("tenant_id"):
                    tenant_data = self._load_tenant(profile_data["tenant_id"])

                return True, {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": str(response.user.created_at) if response.user.created_at else ""
                    },
                    "profile": profile_data,
                    "tenant": tenant_data,
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None
                    }
                }, ""
            else:
                return False, {}, "Credenciais invalidas"

        except Exception as e:
            # Fallback para login local em dev se Supabase falhar
            local_success, local_data, _ = self._try_local_login(email, password)
            if local_success:
                return True, local_data, ""

            error_msg = str(e)
            # Traduzir mensagens comuns
            if "Invalid login credentials" in error_msg:
                error_msg = "Email ou senha incorretos"
            elif "Email not confirmed" in error_msg:
                error_msg = "Email nao confirmado. Verifique sua caixa de entrada."
            elif "rate limit" in error_msg.lower():
                error_msg = "Muitas tentativas. Aguarde alguns minutos."

            return False, {}, error_msg

    def sign_up(self, email: str, password: str, lab_name: str = "", full_name: str = "") -> Tuple[bool, Dict[str, Any], str]:
        """
        Registra novo usuario e cria tenant automaticamente.

        Returns:
            Tuple[success, user_data, error_message]
        """
        if not self.client:
            return False, {}, "Cliente Supabase nao configurado"

        try:
            # Registrar usuario com metadados
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "lab_name": lab_name or "Meu Laboratorio",
                        "full_name": full_name or email.split("@")[0],
                        "role": "owner"
                    }
                }
            })

            if response.user:
                return True, {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email
                    },
                    "message": "Conta criada com sucesso! Verifique seu email para confirmar."
                }, ""
            else:
                return False, {}, "Erro ao criar conta"

        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                error_msg = "Este email ja esta cadastrado"
            elif "password" in error_msg.lower() and "weak" in error_msg.lower():
                error_msg = "Senha muito fraca. Use pelo menos 6 caracteres."

            return False, {}, error_msg

    def sign_out(self) -> bool:
        """Realiza logout do usuario"""
        if not self.client:
            return True

        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Erro no logout: {e}")
            return True  # Considera sucesso mesmo com erro

    def refresh_session(self) -> bool:
        """Atualiza a sessao do usuario"""
        if not self.client:
            return False

        try:
            response = self.client.auth.refresh_session()
            return response.session is not None
        except Exception:
            return False

    def _load_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Carrega profile do usuario do banco"""
        if not self.client:
            return None

        try:
            response = self.client.table("profiles")\
                .select("*")\
                .eq("id", user_id)\
                .single()\
                .execute()

            return response.data
        except Exception as e:
            logger.error(f"Erro ao carregar profile: {e}")
            return None

    def _load_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Carrega dados do tenant"""
        if not self.client:
            return None

        try:
            response = self.client.table("tenants")\
                .select("*")\
                .eq("id", tenant_id)\
                .single()\
                .execute()

            return response.data
        except Exception as e:
            logger.error(f"Erro ao carregar tenant: {e}")
            return None

    def update_profile(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza dados do profile"""
        if not self.client:
            return False

        try:
            self.client.table("profiles")\
                .update(data)\
                .eq("id", user_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar profile: {e}")
            return False

    def update_tenant(self, tenant_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza dados do tenant"""
        if not self.client:
            return False

        try:
            self.client.table("tenants")\
                .update(data)\
                .eq("id", tenant_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar tenant: {e}")
            return False

    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Solicita redefinicao de senha via email.

        Returns:
            Tuple[success, message]
        """
        if not self.client:
            return False, "Cliente Supabase nao configurado"

        if not email or not email.strip():
            return False, "Informe seu email"

        try:
            # Supabase envia email com link de reset
            self.client.auth.reset_password_email(email.strip())
            return True, "Email de recuperacao enviado! Verifique sua caixa de entrada."
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower():
                return False, "Muitas tentativas. Aguarde alguns minutos."
            elif "user not found" in error_msg.lower():
                # Por seguranca, nao revelar se o email existe
                return True, "Se o email estiver cadastrado, voce recebera um link de recuperacao."
            return False, f"Erro ao enviar email: {error_msg}"

    def update_password(self, new_password: str) -> Tuple[bool, str]:
        """
        Atualiza a senha do usuario logado.

        Returns:
            Tuple[success, message]
        """
        if not self.client:
            return False, "Cliente Supabase nao configurado"

        if not new_password or len(new_password) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres"

        try:
            self.client.auth.update_user({"password": new_password})
            return True, "Senha atualizada com sucesso!"
        except Exception as e:
            error_msg = str(e)
            if "weak" in error_msg.lower():
                return False, "Senha muito fraca. Use uma senha mais forte."
            return False, f"Erro ao atualizar senha: {error_msg}"

    def verify_and_change_password(self, email: str, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Verifica a senha atual re-autenticando e depois atualiza para a nova senha.

        Returns:
            Tuple[success, message]
        """
        if not self.client:
            return False, "Cliente Supabase nao configurado"

        if not new_password or len(new_password) < 8:
            return False, "Nova senha deve ter pelo menos 8 caracteres"

        try:
            # 1. Verificar senha atual re-autenticando
            self.client.auth.sign_in_with_password({
                "email": email,
                "password": current_password
            })
        except Exception as e:
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                return False, "Senha atual incorreta"
            return False, f"Erro ao verificar senha atual: {error_msg}"

        try:
            # 2. Atualizar para nova senha
            self.client.auth.update_user({"password": new_password})
            return True, "Senha alterada com sucesso!"
        except Exception as e:
            error_msg = str(e)
            if "weak" in error_msg.lower():
                return False, "Nova senha muito fraca. Use uma senha mais forte."
            if "same" in error_msg.lower():
                return False, "A nova senha deve ser diferente da atual."
            return False, f"Erro ao atualizar senha: {error_msg}"

    # =========================================================================
    # OAUTH SOCIAL LOGIN
    # =========================================================================

    def sign_in_with_oauth(self, provider: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Inicia fluxo de login OAuth com provedor social.
        
        Args:
            provider: "google", "azure" (Microsoft), "github"
            
        Returns:
            Tuple[success, data_with_url, error_message]
        """
        if not self.client:
            return False, {}, "Cliente Supabase não configurado. Use login com email."

        try:
            # Definir URL de callback
            redirect_url = f"{Config.SITE_URL}/auth/callback" if hasattr(Config, 'SITE_URL') else "http://localhost:3000/auth/callback"
            
            # Iniciar OAuth
            response = self.client.auth.sign_in_with_oauth({
                "provider": provider,
                "options": {
                    "redirect_to": redirect_url,
                    "scopes": "email profile" if provider == "google" else "email"
                }
            })
            
            if response and response.url:
                return True, {"url": response.url}, ""
            else:
                return False, {}, f"Provedor {provider} não retornou URL de autenticação"
                
        except Exception as e:
            error_msg = str(e)
            if "provider not enabled" in error_msg.lower():
                return False, {}, f"Provedor {provider} não está habilitado no Supabase"
            return False, {}, f"Erro OAuth: {error_msg}"

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obtém usuário atual da sessão.
        
        Returns:
            Dict com dados do usuário ou None
        """
        if not self.client:
            return None
            
        try:
            response = self.client.auth.get_user()
            if response and response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": str(response.user.created_at) if response.user.created_at else ""
                }
        except Exception as e:
            logger.error(f"Erro ao obter usuario: {e}")
        
        return None

    def get_or_create_profile(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Obtém ou cria perfil para usuário OAuth.
        
        Args:
            user: Dados do usuário do Supabase Auth
            
        Returns:
            Dict com dados do perfil
        """
        user_id = user.get("id")
        if not user_id:
            return None
            
        # Primeiro tentar carregar perfil existente
        profile = self._load_profile(user_id)
        
        if profile:
            return profile
            
        # Se não existe, criar perfil e tenant para usuário OAuth
        if not self.client:
            return {"tenant_id": "dev-tenant", "role": "admin"}
            
        try:
            email = user.get("email", "")
            
            # Criar tenant baseado no email
            tenant_name = email.split("@")[0] if email else "Novo Lab"
            
            # Inserir tenant
            tenant_response = self.client.table("tenants").insert({
                "name": tenant_name,
                "email": email,
                "plan_type": "starter",
                "subscription_status": "active"
            }).execute()
            
            tenant_id = tenant_response.data[0]["id"] if tenant_response.data else None
            
            if tenant_id:
                # Inserir profile
                self.client.table("profiles").insert({
                    "id": user_id,
                    "tenant_id": tenant_id,
                    "email": email,
                    "full_name": tenant_name,
                    "role": "owner"
                }).execute()
                
                return {
                    "tenant_id": tenant_id,
                    "role": "owner",
                    "email": email
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar perfil OAuth: {e}")
            
        return {"tenant_id": "dev-tenant", "role": "member"}


# Singleton
auth_service = AuthService()
