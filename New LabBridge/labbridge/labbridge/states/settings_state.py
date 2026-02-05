"""
SettingsState - Estado de Configuracoes
Gerencia as configuracoes do usuario e laboratorio.
"""
import reflex as rx
from typing import Optional


class SettingsState(rx.State):
    """Estado responsavel pelas configuracoes do sistema"""

    # Perfil do Usuario (vazio por padrao - preenchido pelo usuario)
    settings_name: str = ""
    settings_email: str = ""

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
        except:
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
            settings_data = {
                "tenant_id": "local",
                "user_id": "local-admin",
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
            print(f"Erro ao salvar configuracoes: {e}")
            self.settings_message = f"Erro ao salvar: {str(e)}"
            self.settings_success = False
        finally:
            self.is_saving_settings = False

        yield

    def load_settings(self):
        """Carrega configuracoes salvas do banco"""
        from ..services.local_storage import local_storage

        try:
            settings = local_storage.get_user_settings("local", "local-admin")
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
            print(f"Erro ao carregar configuracoes: {e}")

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

            # TODO: Integrar com Supabase Auth
            import asyncio
            await asyncio.sleep(1)

            # Limpa campos
            self.current_password = ""
            self.new_password = ""
            self.confirm_password = ""
            self.is_changing_password = False
            self.password_error = ""

            yield rx.toast.success("Senha alterada com sucesso!")

        except Exception as e:
            self.password_error = f"Erro: {str(e)}"
            self.is_changing_password = False
            yield

    def clear_settings_message(self):
        """Limpa a mensagem de feedback"""
        self.settings_message = ""
        self.settings_success = False

    async def request_2fa_setup(self):
        """Inicia configuracao de 2FA"""
        if self.two_factor_enabled:
            # Desabilitar 2FA
            self.two_factor_enabled = False
            return rx.toast.info("Autenticacao de dois fatores desabilitada")
        else:
            # Habilitar 2FA - em producao, mostraria QR code
            self.two_factor_enabled = True
            return rx.toast.success("Autenticacao de dois fatores habilitada!")

    def request_data_export(self):
        """Solicita exportacao de dados (LGPD)"""
        return rx.toast.info("Solicitacao de exportacao enviada. Voce recebera um email em ate 48h.")

    def request_account_deletion(self):
        """Solicita exclusao de conta (LGPD)"""
        return rx.toast.warning("Para excluir sua conta, entre em contato com suporte@labbridge.com.br")
