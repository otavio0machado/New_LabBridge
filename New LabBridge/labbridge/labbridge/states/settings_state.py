"""
SettingsState - Estado de Configuracoes
Gerencia as configuracoes do usuario e laboratorio.
"""
import reflex as rx
from typing import Optional
import logging
from .auth_state import AuthState

logger = logging.getLogger(__name__)


class SettingsState(AuthState):
    """Estado responsavel pelas configuracoes do sistema"""

    # Perfil do Usuario (vazio por padrao - preenchido pelo usuario)
    settings_name: str = ""

    # Dados do Laboratorio (vazio por padrao - preenchido pelo usuario)
    lab_name: str = ""
    lab_cnpj: str = ""
    
    # === METAS ===
    monthly_goal: float = 150000.0  # Meta mensal em R$
    monthly_goal_str: str = "150000"  # Para input

    # Preferencias de Analise
    ignore_small_diff: bool = True  # Ignorar diferencas < R$ 0,05
    auto_detect_typos: bool = True  # Detectar erros de grafia

    # === NOTIFICACOES ===
    notify_email_analysis: bool = True  # Notificar conclusao de analise por email
    notify_email_divergence: bool = True  # Notificar divergencias criticas
    notify_email_reports: bool = False  # Notificar relatorios prontos
    notify_push_enabled: bool = True  # Notificacoes push no navegador
    notify_weekly_summary: bool = True  # Resumo semanal por email
    notify_team_activity: bool = False  # Atividades da equipe

    # === SEGURANCA ===
    two_factor_enabled: bool = False
    session_timeout: str = "30"  # minutos
    # Senhas (transientes - limpas apos uso)
    current_password: str = ""
    new_password: str = ""
    confirm_password: str = ""

    # UI State
    is_saving_settings: bool = False
    settings_message: str = ""
    settings_success: bool = False
    is_changing_password: bool = False
    password_error: str = ""

    # Setters - Perfil
    def set_settings_name(self, value: str):
        self.settings_name = value
        self.settings_message = ""

    def set_lab_name(self, value: str):
        self.lab_name = value
        self.settings_message = ""

    def set_lab_cnpj(self, value: str):
        self.lab_cnpj = value
        self.settings_message = ""

    def set_monthly_goal(self, value: str):
        """Define meta mensal"""
        self.monthly_goal_str = value
        try:
            # Remover formatação
            clean = value.replace("R$", "").replace(".", "").replace(",", ".").strip()
            self.monthly_goal = float(clean) if clean else 150000.0
        except (ValueError, TypeError):
            self.monthly_goal = 150000.0
        self.settings_message = ""

    def toggle_ignore_small_diff(self, value: bool):
        self.ignore_small_diff = value
        self.settings_message = ""

    def toggle_auto_detect_typos(self, value: bool):
        self.auto_detect_typos = value
        self.settings_message = ""

    # Setters - Notificacoes
    def toggle_notify_email_analysis(self, value: bool):
        self.notify_email_analysis = value

    def toggle_notify_email_divergence(self, value: bool):
        self.notify_email_divergence = value

    def toggle_notify_email_reports(self, value: bool):
        self.notify_email_reports = value

    def toggle_notify_push_enabled(self, value: bool):
        self.notify_push_enabled = value

    def toggle_notify_weekly_summary(self, value: bool):
        self.notify_weekly_summary = value

    def toggle_notify_team_activity(self, value: bool):
        self.notify_team_activity = value

    # Setters - Seguranca
    def toggle_two_factor(self, value: bool):
        self.two_factor_enabled = value

    def set_session_timeout(self, value: str):
        self.session_timeout = value

    def set_current_password(self, value: str):
        self.current_password = value
        self.password_error = ""

    def set_new_password(self, value: str):
        self.new_password = value
        self.password_error = ""

    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.password_error = ""

    async def save_settings(self):
        """Salva as configuracoes do usuario"""
        from ..services.local_storage import local_storage

        self.is_saving_settings = True
        self.settings_message = ""
        self.settings_success = False
        yield

        try:
            # Validacao basica
            if not self.settings_name.strip():
                self.settings_message = "Nome e obrigatorio"
                self.is_saving_settings = False
                yield
                return

            if not self.lab_name.strip():
                self.settings_message = "Nome do laboratorio e obrigatorio"
                self.is_saving_settings = False
                yield
                return

            # Preparar dados para salvar
            tenant_id = self.current_user.tenant_id if self.current_user else ""
            user_id = self.current_user.id if self.current_user else ""
            settings_data = {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "settings_name": self.settings_name,
                "lab_name": self.lab_name,
                "lab_cnpj": self.lab_cnpj,
                "ignore_small_diff": self.ignore_small_diff,
                "auto_detect_typos": self.auto_detect_typos,
                "notify_email_analysis": self.notify_email_analysis,
                "notify_email_divergence": self.notify_email_divergence,
                "notify_email_reports": self.notify_email_reports,
                "notify_push_enabled": self.notify_push_enabled,
                "notify_weekly_summary": self.notify_weekly_summary,
                "notify_team_activity": self.notify_team_activity,
                "two_factor_enabled": self.two_factor_enabled,
                "session_timeout": self.session_timeout,
            }

            # Salvar no armazenamento local
            success, error = local_storage.save_user_settings(settings_data)

            if success:
                self.settings_message = "Configuracoes salvas com sucesso!"
                self.settings_success = True
            else:
                self.settings_message = f"Erro ao salvar: {error}"
                self.settings_success = False

        except Exception as e:
            logger.error(f"Erro ao salvar configuracoes: {e}")
            self.settings_message = f"Erro ao salvar: {str(e)}"
            self.settings_success = False
        finally:
            self.is_saving_settings = False

        yield

    def load_settings(self):
        """Carrega configuracoes salvas do banco"""
        from ..services.local_storage import local_storage

        try:
            tenant_id = self.current_user.tenant_id if self.current_user else ""
            user_id = self.current_user.id if self.current_user else ""
            settings = local_storage.get_user_settings(tenant_id, user_id)
            if settings:
                self.settings_name = settings.get("settings_name", self.settings_name)
                self.lab_name = settings.get("lab_name", self.lab_name)
                self.lab_cnpj = settings.get("lab_cnpj", self.lab_cnpj)
                self.ignore_small_diff = settings.get("ignore_small_diff", True)
                self.auto_detect_typos = settings.get("auto_detect_typos", True)
                self.notify_email_analysis = settings.get("notify_email_analysis", True)
                self.notify_email_divergence = settings.get("notify_email_divergence", True)
                self.notify_email_reports = settings.get("notify_email_reports", False)
                self.notify_push_enabled = settings.get("notify_push_enabled", True)
                self.notify_weekly_summary = settings.get("notify_weekly_summary", True)
                self.notify_team_activity = settings.get("notify_team_activity", False)
                self.two_factor_enabled = settings.get("two_factor_enabled", False)
                self.session_timeout = settings.get("session_timeout", "30")
        except Exception as e:
            logger.error(f"Erro ao carregar configuracoes: {e}")

    async def change_password(self):
        """Altera a senha do usuario"""
        self.is_changing_password = True
        self.password_error = ""
        yield

        try:
            # Validacoes
            if not self.current_password:
                self.password_error = "Senha atual e obrigatoria"
                self.is_changing_password = False
                yield
                return

            if not self.new_password:
                self.password_error = "Nova senha e obrigatoria"
                self.is_changing_password = False
                yield
                return

            if len(self.new_password) < 8:
                self.password_error = "A nova senha deve ter pelo menos 8 caracteres"
                self.is_changing_password = False
                yield
                return

            if self.new_password != self.confirm_password:
                self.password_error = "As senhas nao coincidem"
                self.is_changing_password = False
                yield
                return

            if self.new_password == self.current_password:
                self.password_error = "A nova senha deve ser diferente da atual"
                self.is_changing_password = False
                yield
                return

            # Trocar senha via Supabase Auth
            from ..services.auth_service import auth_service

            user_email = self.current_user.email if self.current_user else ""
            if not user_email:
                self.password_error = "Usuario nao autenticado"
                self.is_changing_password = False
                yield
                return

            success, message = auth_service.verify_and_change_password(
                email=user_email,
                current_password=self.current_password,
                new_password=self.new_password
            )

            if success:
                # Limpa campos
                self.current_password = ""
                self.new_password = ""
                self.confirm_password = ""
                self.is_changing_password = False
                self.password_error = ""
                yield rx.toast.success(message)
            else:
                self.password_error = message
                self.is_changing_password = False
                yield

        except Exception as e:
            self.password_error = f"Erro: {str(e)}"
            self.is_changing_password = False
            yield

    def clear_settings_message(self):
        """Limpa a mensagem de feedback"""
        self.settings_message = ""
        self.settings_success = False

    async def request_2fa_setup(self):
        """2FA não está disponível ainda — informa o usuário"""
        return rx.toast.info(
            "Autenticação de dois fatores estará disponível em breve. "
            "Estamos trabalhando na integração com TOTP (Google Authenticator)."
        )

    async def request_data_export(self):
        """Exporta todos os dados do usuário (LGPD compliance)"""
        from datetime import datetime
        try:
            from ..services.local_storage import local_storage
            tenant_id = self.current_tenant.id if self.current_tenant else "local"
            user_id = self.current_user.id if self.current_user else ""

            export_data = {
                "usuario": {
                    "email": self.current_user.email if self.current_user else "",
                    "nome": self.settings_name,
                    "role": self.current_user.role if self.current_user else "",
                },
                "laboratorio": {
                    "nome": self.lab_name,
                    "cnpj": self.lab_cnpj,
                },
                "configuracoes": local_storage.get_user_settings(tenant_id, user_id) or {},
                "analises_salvas": local_storage.get_saved_analyses(tenant_id, limit=9999),
                "membros_equipe": local_storage.get_team_members(tenant_id),
                "logs_atividade": local_storage.get_activity_logs(tenant_id, limit=9999),
                "notificacoes": local_storage.get_notifications(tenant_id, limit=9999),
                "exportado_em": datetime.now().isoformat(),
            }

            import json
            payload = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            filename = f"labbridge_dados_{tenant_id}_{datetime.now().strftime('%Y%m%d')}.json"
            return rx.download(data=payload.encode("utf-8"), filename=filename)

        except Exception as e:
            logger.error(f"Erro na exportação LGPD: {e}")
            return rx.toast.error(f"Erro ao exportar dados: {str(e)}")

    async def request_account_deletion(self):
        """Solicita exclusão de conta (LGPD) — envia email ao suporte"""
        from datetime import datetime
        try:
            from ..services.email_service import email_service

            user_email = self.current_user.email if self.current_user else "desconhecido"
            tenant_name = self.current_tenant.name if self.current_tenant else "desconhecido"
            tenant_id = self.current_tenant.id if self.current_tenant else ""

            content = f"""
            <p><strong>Solicitação de exclusão de conta (LGPD):</strong></p>
            <ul>
                <li><strong>Email:</strong> {user_email}</li>
                <li><strong>Laboratório:</strong> {tenant_name}</li>
                <li><strong>Tenant ID:</strong> {tenant_id}</li>
                <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
            </ul>
            <p>De acordo com a LGPD, esta solicitação deve ser atendida em até 15 dias.</p>
            """

            email_service.send_email(
                to_email="suporte@labbridge.com.br",
                subject=f"[LGPD] Solicitação de exclusão - {user_email}",
                html_content=content,
                from_name="LabBridge LGPD",
            )

            return rx.toast.success(
                "Solicitação de exclusão enviada. "
                "Sua conta será removida em até 15 dias conforme a LGPD."
            )
        except Exception as e:
            logger.error(f"Erro na solicitação de exclusão: {e}")
            return rx.toast.error("Erro ao enviar solicitação. Tente novamente ou contate suporte@labbridge.com.br")
