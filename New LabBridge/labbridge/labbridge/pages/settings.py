"""
LabBridge - Configuracoes
Gerencia configuracoes do usuario e laboratorio.
"""
import reflex as rx
from ..states.auth_state import AuthState
from ..states.settings_state import SettingsState
from ..components import ui
from ..styles import Color, Spacing, Design


def settings_section(title: str, description: str, children: list[rx.Component]) -> rx.Component:
    """Secao de configuracao reutilizavel"""
    return rx.vstack(
        rx.heading(title, size="4", color=Color.DEEP),
        rx.text(description, size="2", color=Color.TEXT_SECONDARY, margin_bottom=Spacing.SM),
        rx.vstack(
            *children,
            spacing="4",
            width="100%",
            align_items="start",
            bg="white",
            padding=Spacing.LG,
            border_radius=Design.RADIUS_LG,
            border=f"1px solid {Color.BORDER}",
        ),
        spacing="1",
        width="100%",
        align_items="start",
        margin_bottom=Spacing.LG,
    )


def notification_row(label: str, description: str, checked: rx.Var, on_change) -> rx.Component:
    """Linha de configuracao de notificacao"""
    return rx.hstack(
        rx.vstack(
            rx.text(label, font_weight="500", color=Color.TEXT_PRIMARY),
            rx.text(description, font_size="0.8rem", color=Color.TEXT_SECONDARY),
            spacing="0",
            align_items="start",
        ),
        rx.spacer(),
        rx.switch(
            checked=checked,
            on_change=on_change,
        ),
        width="100%",
        padding_y=Spacing.SM,
        border_bottom=f"1px solid {Color.BORDER}",
    )


def settings_page() -> rx.Component:
    """Pagina de Configuracoes"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.vstack(
                    ui.page_header(
                        title="Configuracoes",
                        description="Personalize sua experiencia no LabBridge",
                        actions=rx.hstack(
                            # Mensagem de feedback
                            rx.cond(
                                SettingsState.settings_message != "",
                                rx.badge(
                                    SettingsState.settings_message,
                                    color_scheme=rx.cond(
                                        SettingsState.settings_success,
                                        "green",
                                        "red"
                                    ),
                                    size="2",
                                ),
                                rx.fragment(),
                            ),
                            # Botao de Salvar com loading
                            rx.button(
                                rx.cond(
                                    SettingsState.is_saving_settings,
                                    rx.hstack(
                                        rx.spinner(size="1"),
                                        rx.text("Salvando..."),
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        rx.icon(tag="save", size=16),
                                        rx.text("Salvar Alteracoes"),
                                        spacing="2",
                                    ),
                                ),
                                variant="solid",
                                size="2",
                                bg=Color.PRIMARY,
                                color="white",
                                cursor="pointer",
                                disabled=SettingsState.is_saving_settings,
                                on_click=SettingsState.save_settings,
                                _hover={"bg": Color.PRIMARY_HOVER},
                            ),
                            spacing="3",
                            align="center",
                        ),
                    ),

                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Perfil", value="profile"),
                            rx.tabs.trigger("Laboratorio", value="laboratorio"),
                            rx.tabs.trigger("Notificacoes", value="notifications"),
                            rx.tabs.trigger("Seguranca", value="security"),
                        ),

                        # Tab Perfil
                        rx.tabs.content(
                            rx.vstack(
                                settings_section(
                                    "Informacoes Pessoais",
                                    "Atualize seus dados de identificacao.",
                                    [
                                        rx.text("Nome Completo", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="Seu nome",
                                            value=SettingsState.settings_name,
                                            on_change=SettingsState.set_settings_name,
                                            width="100%",
                                            size="3",
                                        ),
                                        rx.text("Email", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="seu@email.com",
                                            value=SettingsState.user_email,
                                            width="100%",
                                            size="3",
                                            disabled=True,
                                        ),
                                    ]
                                ),
                                margin_top=Spacing.LG,
                                width="100%"
                            ),
                            value="profile",
                        ),

                        # Tab Laboratorio
                        rx.tabs.content(
                            rx.vstack(
                                settings_section(
                                    "Dados da Empresa",
                                    "Informacoes fiscais e de contato do laboratorio.",
                                    [
                                        rx.text("Nome do Laboratorio", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="Nome Fantasia",
                                            value=SettingsState.lab_name,
                                            on_change=SettingsState.set_lab_name,
                                            width="100%",
                                            size="3",
                                        ),
                                        rx.text("CNPJ", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="00.000.000/0001-00",
                                            value=SettingsState.lab_cnpj,
                                            on_change=SettingsState.set_lab_cnpj,
                                            width="100%",
                                            size="3",
                                        ),
                                    ]
                                ),
                                settings_section(
                                    "Preferencias de Analise",
                                    "Ajuste os parametros padrao para analises.",
                                    [
                                        rx.hstack(
                                            rx.switch(
                                                checked=SettingsState.ignore_small_diff,
                                                on_change=SettingsState.toggle_ignore_small_diff,
                                            ),
                                            rx.text("Ignorar diferencas menores que R$ 0,05"),
                                            spacing="3",
                                        ),
                                        rx.hstack(
                                            rx.switch(
                                                checked=SettingsState.auto_detect_typos,
                                                on_change=SettingsState.toggle_auto_detect_typos,
                                            ),
                                            rx.text("Detectar erros de grafia automaticamente"),
                                            spacing="3",
                                        ),
                                    ]
                                ),
                                margin_top=Spacing.LG,
                                width="100%"
                            ),
                            value="laboratorio",
                        ),

                        # Tab Notificacoes
                        rx.tabs.content(
                            rx.vstack(
                                settings_section(
                                    "Notificacoes por Email",
                                    "Configure quais emails deseja receber.",
                                    [
                                        notification_row(
                                            "Conclusao de Analise",
                                            "Receber email quando uma analise for concluida",
                                            SettingsState.notify_email_analysis,
                                            SettingsState.toggle_notify_email_analysis,
                                        ),
                                        notification_row(
                                            "Divergencias Criticas",
                                            "Alertas imediatos sobre divergencias importantes",
                                            SettingsState.notify_email_divergence,
                                            SettingsState.toggle_notify_email_divergence,
                                        ),
                                        notification_row(
                                            "Relatorios Prontos",
                                            "Notificar quando relatorios estiverem disponiveis",
                                            SettingsState.notify_email_reports,
                                            SettingsState.toggle_notify_email_reports,
                                        ),
                                        notification_row(
                                            "Resumo Semanal",
                                            "Receber um resumo das atividades toda semana",
                                            SettingsState.notify_weekly_summary,
                                            SettingsState.toggle_notify_weekly_summary,
                                        ),
                                    ]
                                ),
                                settings_section(
                                    "Outras Notificacoes",
                                    "Configuracoes adicionais de alertas.",
                                    [
                                        notification_row(
                                            "Notificacoes Push",
                                            "Receber notificacoes no navegador",
                                            SettingsState.notify_push_enabled,
                                            SettingsState.toggle_notify_push_enabled,
                                        ),
                                        notification_row(
                                            "Atividades da Equipe",
                                            "Notificar sobre acoes de outros membros",
                                            SettingsState.notify_team_activity,
                                            SettingsState.toggle_notify_team_activity,
                                        ),
                                    ]
                                ),
                                margin_top=Spacing.LG,
                                width="100%"
                            ),
                            value="notifications",
                        ),

                        # Tab Seguranca
                        rx.tabs.content(
                            rx.vstack(
                                settings_section(
                                    "Autenticacao",
                                    "Configure opcoes de seguranca da sua conta.",
                                    [
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text("Autenticacao de Dois Fatores (2FA)", font_weight="500"),
                                                rx.text(
                                                    "Adicione uma camada extra de seguranca",
                                                    font_size="0.8rem",
                                                    color=Color.TEXT_SECONDARY
                                                ),
                                                spacing="0",
                                                align_items="start",
                                            ),
                                            rx.spacer(),
                                            rx.hstack(
                                                rx.cond(
                                                    SettingsState.two_factor_enabled,
                                                    rx.badge("Ativo", color_scheme="green"),
                                                    rx.badge("Inativo", color_scheme="gray"),
                                                ),
                                                rx.button(
                                                    rx.cond(
                                                        SettingsState.two_factor_enabled,
                                                        "Desabilitar",
                                                        "Habilitar"
                                                    ),
                                                    variant="outline",
                                                    size="1",
                                                    on_click=SettingsState.request_2fa_setup,
                                                ),
                                                spacing="2",
                                            ),
                                            width="100%",
                                            padding_y=Spacing.SM,
                                        ),
                                        rx.divider(),
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text("Tempo de Sessao", font_weight="500"),
                                                rx.text(
                                                    "Tempo ate logout automatico por inatividade",
                                                    font_size="0.8rem",
                                                    color=Color.TEXT_SECONDARY
                                                ),
                                                spacing="0",
                                                align_items="start",
                                            ),
                                            rx.spacer(),
                                            rx.select(
                                                ["15", "30", "60", "120"],
                                                value=SettingsState.session_timeout,
                                                on_change=SettingsState.set_session_timeout,
                                                width="120px",
                                            ),
                                            rx.text("minutos", font_size="0.8rem", color=Color.TEXT_SECONDARY),
                                            width="100%",
                                            padding_y=Spacing.SM,
                                        ),
                                    ]
                                ),
                                settings_section(
                                    "Alterar Senha",
                                    "Atualize sua senha de acesso.",
                                    [
                                        rx.text("Senha Atual", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="Digite sua senha atual",
                                            type="password",
                                            value=SettingsState.current_password,
                                            on_change=SettingsState.set_current_password,
                                            width="100%",
                                        ),
                                        rx.text("Nova Senha", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="Digite a nova senha",
                                            type="password",
                                            value=SettingsState.new_password,
                                            on_change=SettingsState.set_new_password,
                                            width="100%",
                                        ),
                                        rx.text("Confirmar Nova Senha", size="2", weight="bold"),
                                        rx.input(
                                            placeholder="Confirme a nova senha",
                                            type="password",
                                            value=SettingsState.confirm_password,
                                            on_change=SettingsState.set_confirm_password,
                                            width="100%",
                                        ),
                                        rx.cond(
                                            SettingsState.password_error != "",
                                            rx.text(SettingsState.password_error, color=Color.ERROR, font_size="0.85rem"),
                                            rx.fragment(),
                                        ),
                                        rx.button(
                                            rx.cond(
                                                SettingsState.is_changing_password,
                                                rx.hstack(rx.spinner(size="1"), rx.text("Alterando..."), spacing="2"),
                                                rx.text("Alterar Senha"),
                                            ),
                                            variant="solid",
                                            bg=Color.PRIMARY,
                                            color="white",
                                            on_click=SettingsState.change_password,
                                            disabled=SettingsState.is_changing_password,
                                            margin_top=Spacing.SM,
                                        ),
                                    ]
                                ),
                                settings_section(
                                    "Privacidade e Dados (LGPD)",
                                    "Gerencie seus dados pessoais.",
                                    [
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text("Exportar Meus Dados", font_weight="500"),
                                                rx.text(
                                                    "Solicite uma copia de todos os seus dados",
                                                    font_size="0.8rem",
                                                    color=Color.TEXT_SECONDARY
                                                ),
                                                spacing="0",
                                                align_items="start",
                                            ),
                                            rx.spacer(),
                                            rx.button(
                                                rx.icon(tag="download", size=14),
                                                rx.text("Exportar"),
                                                variant="outline",
                                                size="1",
                                                on_click=SettingsState.request_data_export,
                                            ),
                                            width="100%",
                                            padding_y=Spacing.SM,
                                        ),
                                        rx.divider(),
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text("Excluir Conta", font_weight="500", color=Color.ERROR),
                                                rx.text(
                                                    "Esta acao e irreversivel",
                                                    font_size="0.8rem",
                                                    color=Color.TEXT_SECONDARY
                                                ),
                                                spacing="0",
                                                align_items="start",
                                            ),
                                            rx.spacer(),
                                            rx.alert_dialog.root(
                                                rx.alert_dialog.trigger(
                                                    rx.button(
                                                        rx.icon(tag="trash-2", size=14),
                                                        rx.text("Solicitar Exclusao"),
                                                        variant="outline",
                                                        color_scheme="red",
                                                        size="1",
                                                    ),
                                                ),
                                                rx.alert_dialog.content(
                                                    rx.alert_dialog.title("Excluir Conta"),
                                                    rx.alert_dialog.description(
                                                        "ATENCAO: Esta acao e irreversivel. Todos os seus dados serao permanentemente excluidos. Deseja continuar?"
                                                    ),
                                                    rx.flex(
                                                        rx.alert_dialog.cancel(
                                                            rx.button("Cancelar", variant="soft", color_scheme="gray"),
                                                        ),
                                                        rx.alert_dialog.action(
                                                            rx.button(
                                                                "Excluir Conta",
                                                                color_scheme="red",
                                                                on_click=SettingsState.request_account_deletion,
                                                            ),
                                                        ),
                                                        spacing="3",
                                                        justify="end",
                                                        margin_top=Spacing.MD,
                                                    ),
                                                ),
                                            ),
                                            width="100%",
                                            padding_y=Spacing.SM,
                                        ),
                                    ]
                                ),
                                margin_top=Spacing.LG,
                                width="100%"
                            ),
                            value="security",
                        ),
                        default_value="profile",
                        width="100%",
                    ),

                    max_width="1200px",
                    width="100%",
                    margin_x="auto",
                    padding=Spacing.XL,
                ),
                width="100%",
                min_height="calc(100vh - 80px)",
                bg=Color.BACKGROUND,
            ),
            width="100%",
        ),
        width="100%",
        on_mount=SettingsState.load_settings,
    )
