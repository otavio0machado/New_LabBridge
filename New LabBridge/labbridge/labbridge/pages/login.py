import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design
from ..components import ui
from ..states.auth_state import AuthState


def oauth_buttons() -> rx.Component:
    """Botões de login social (Google e Microsoft)"""
    return rx.vstack(
        # Separador "ou"
        rx.hstack(
            rx.divider(width="100%", color=Color.BORDER),
            rx.text("ou", color=Color.TEXT_SECONDARY, font_size="0.875rem", padding_x="12px", white_space="nowrap"),
            rx.divider(width="100%", color=Color.BORDER),
            width="100%",
            align="center",
            margin_y=Spacing.MD,
        ),
        
        # Botão Google
        rx.button(
            rx.hstack(
                rx.image(
                    src="https://www.google.com/favicon.ico",
                    width="18px",
                    height="18px",
                ),
                rx.text("Continuar com Google"),
                spacing="3",
                align="center",
            ),
            variant="outline",
            width="100%",
            size="3",
            cursor="pointer",
            on_click=AuthState.login_with_google,
            disabled=AuthState.oauth_loading,
            _hover={"bg": Color.BACKGROUND},
        ),
        
        # Botão Microsoft
        rx.button(
            rx.hstack(
                rx.image(
                    src="https://www.microsoft.com/favicon.ico",
                    width="18px",
                    height="18px",
                ),
                rx.text("Continuar com Microsoft"),
                spacing="3",
                align="center",
            ),
            variant="outline",
            width="100%",
            size="3",
            cursor="pointer",
            on_click=AuthState.login_with_microsoft,
            disabled=AuthState.oauth_loading,
            _hover={"bg": Color.BACKGROUND},
        ),
        
        # Erro OAuth
        rx.cond(
            AuthState.oauth_error != "",
            rx.box(
                rx.text(AuthState.oauth_error, color=Color.ERROR, font_size="0.75rem"),
                margin_top=Spacing.SM,
            ),
        ),
        
        # Loading OAuth
        rx.cond(
            AuthState.oauth_loading,
            rx.center(
                rx.spinner(size="2"),
                width="100%",
                padding_y="8px",
            ),
        ),
        
        spacing="2",
        width="100%",
    )


def login_form() -> rx.Component:
    """Formulario de login"""
    return rx.vstack(
        ui.heading("Bem-vindo de volta", level=2, text_align="center"),
        ui.text(
            "Digite suas credenciais para acessar o painel.",
            size="body_secondary",
            text_align="center",
            margin_bottom=Spacing.LG,
        ),
        # Card Wrapper
        ui.card(
            rx.vstack(
                ui.form_field(
                    "E-mail",
                    ui.input(
                        placeholder="seu@laboratorio.com",
                        value=State.login_email,
                        on_change=State.set_login_email,
                        type="email",
                        size="large",
                    ),
                ),
                ui.form_field(
                    "Senha",
                    ui.input(
                        placeholder="********",
                        value=State.login_password,
                        on_change=State.set_login_password,
                        type="password",
                        size="large",
                    ),
                ),
                rx.cond(
                    State.login_error != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-alert", size=16, color=Color.ERROR),
                            rx.text(State.login_error, color=Color.ERROR, font_size="0.875rem"),
                            align_items="center",
                            gap="8px",
                        ),
                        bg=Color.ERROR_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                rx.cond(
                    State.login_loading,
                    rx.center(
                        rx.hstack(
                            rx.spinner(size="3"),
                            rx.text("Autenticando...", color=Color.TEXT_SECONDARY),
                            gap="12px",
                        ),
                        width="100%",
                        padding_y="12px",
                    ),
                    ui.button(
                        "Entrar",
                        icon="log-in",
                        on_click=State.attempt_login,
                        width="100%",
                        size="large",
                        margin_top=Spacing.SM,
                    ),
                ),
                # Botões OAuth (Google / Microsoft)
                oauth_buttons(),
                gap=Spacing.LG,
                width="100%",
            ),
            width="100%",
            max_width="420px",
            padding=Spacing.XL,
            box_shadow=Design.SHADOW_LG,
        ),
        # Link para esqueci senha
        rx.link(
            "Esqueceu sua senha?",
            on_click=State.toggle_reset_password_view,
            color=Color.TEXT_SECONDARY,
            font_size="0.875rem",
            cursor="pointer",
            margin_top=Spacing.SM,
            _hover={"text_decoration": "underline", "color": Color.PRIMARY},
        ),
        # Link para registro
        rx.hstack(
            ui.text("Novo por aqui?", size="small"),
            rx.link(
                "Criar conta",
                on_click=State.toggle_register_view,
                color=Color.PRIMARY,
                font_weight="600",
                cursor="pointer",
                _hover={"text_decoration": "underline"},
            ),
            gap="8px",
            margin_top=Spacing.LG,
        ),
        align_items="center",
        width="100%",
    )


def register_form() -> rx.Component:
    """Formulario de registro"""
    return rx.vstack(
        ui.heading("Criar Conta", level=2, text_align="center"),
        ui.text(
            "Cadastre seu laboratorio para comecar.",
            size="body_secondary",
            text_align="center",
            margin_bottom=Spacing.LG,
        ),
        # Card Wrapper
        ui.card(
            rx.vstack(
                ui.form_field(
                    "Nome do Laboratorio",
                    ui.input(
                        placeholder="Biodiagnostico Ltda",
                        value=State.register_lab_name,
                        on_change=State.set_register_lab_name,
                        size="large",
                    ),
                ),
                ui.form_field(
                    "E-mail",
                    ui.input(
                        placeholder="contato@laboratorio.com",
                        value=State.register_email,
                        on_change=State.set_register_email,
                        type="email",
                        size="large",
                    ),
                ),
                ui.form_field(
                    "Senha",
                    ui.input(
                        placeholder="Minimo 6 caracteres",
                        value=State.register_password,
                        on_change=State.set_register_password,
                        type="password",
                        size="large",
                    ),
                ),
                ui.form_field(
                    "Confirmar Senha",
                    ui.input(
                        placeholder="Repita a senha",
                        value=State.register_confirm_password,
                        on_change=State.set_register_confirm_password,
                        type="password",
                        size="large",
                    ),
                ),
                # Mensagem de erro
                rx.cond(
                    State.register_error != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-alert", size=16, color=Color.ERROR),
                            rx.text(State.register_error, color=Color.ERROR, font_size="0.875rem"),
                            align_items="center",
                            gap="8px",
                        ),
                        bg=Color.ERROR_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                # Mensagem de sucesso
                rx.cond(
                    State.register_success != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-check", size=16, color=Color.SUCCESS),
                            rx.text(State.register_success, color=Color.SUCCESS, font_size="0.875rem"),
                            align_items="center",
                            gap="8px",
                        ),
                        bg=Color.SUCCESS_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                # Botao
                rx.cond(
                    State.register_loading,
                    rx.center(
                        rx.hstack(
                            rx.spinner(size="3"),
                            rx.text("Criando conta...", color=Color.TEXT_SECONDARY),
                            gap="12px",
                        ),
                        width="100%",
                        padding_y="12px",
                    ),
                    ui.button(
                        "Criar Conta",
                        icon="user-plus",
                        on_click=State.register_tenant,
                        width="100%",
                        size="large",
                        margin_top=Spacing.SM,
                    ),
                ),
                gap=Spacing.MD,
                width="100%",
            ),
            width="100%",
            max_width="420px",
            padding=Spacing.XL,
            box_shadow=Design.SHADOW_LG,
        ),
        # Link para login
        rx.hstack(
            ui.text("Ja tem conta?", size="small"),
            rx.link(
                "Fazer login",
                on_click=State.toggle_register_view,
                color=Color.PRIMARY,
                font_weight="600",
                cursor="pointer",
                _hover={"text_decoration": "underline"},
            ),
            gap="8px",
            margin_top=Spacing.LG,
        ),
        align_items="center",
        width="100%",
    )


def reset_password_form() -> rx.Component:
    """Formulario de recuperacao de senha"""
    return rx.vstack(
        ui.heading("Recuperar Senha", level=2, text_align="center"),
        ui.text(
            "Digite seu email para receber o link de recuperacao.",
            size="body_secondary",
            text_align="center",
            margin_bottom=Spacing.LG,
        ),
        # Card Wrapper
        ui.card(
            rx.vstack(
                ui.form_field(
                    "E-mail",
                    ui.input(
                        placeholder="seu@laboratorio.com",
                        value=State.reset_email,
                        on_change=State.set_reset_email,
                        type="email",
                        size="large",
                    ),
                ),
                # Mensagem de erro
                rx.cond(
                    State.reset_error != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-alert", size=16, color=Color.ERROR),
                            rx.text(State.reset_error, color=Color.ERROR, font_size="0.875rem"),
                            align_items="center",
                            gap="8px",
                        ),
                        bg=Color.ERROR_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                # Mensagem de sucesso
                rx.cond(
                    State.reset_success != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-check", size=16, color=Color.SUCCESS),
                            rx.text(State.reset_success, color=Color.SUCCESS, font_size="0.875rem"),
                            align_items="center",
                            gap="8px",
                        ),
                        bg=Color.SUCCESS_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                # Botao
                rx.cond(
                    State.reset_loading,
                    rx.center(
                        rx.hstack(
                            rx.spinner(size="3"),
                            rx.text("Enviando...", color=Color.TEXT_SECONDARY),
                            gap="12px",
                        ),
                        width="100%",
                        padding_y="12px",
                    ),
                    ui.button(
                        "Enviar Link de Recuperacao",
                        icon="mail",
                        on_click=State.request_password_reset,
                        width="100%",
                        size="large",
                        margin_top=Spacing.SM,
                    ),
                ),
                gap=Spacing.MD,
                width="100%",
            ),
            width="100%",
            max_width="420px",
            padding=Spacing.XL,
            box_shadow=Design.SHADOW_LG,
        ),
        # Link para voltar ao login
        rx.hstack(
            ui.text("Lembrou a senha?", size="small"),
            rx.link(
                "Fazer login",
                on_click=State.toggle_reset_password_view,
                color=Color.PRIMARY,
                font_weight="600",
                cursor="pointer",
                _hover={"text_decoration": "underline"},
            ),
            gap="8px",
            margin_top=Spacing.LG,
        ),
        align_items="center",
        width="100%",
    )


def login_page() -> rx.Component:
    """Pagina de login - Experiencia Premium com Login/Registro"""

    return rx.flex(
        # === LADO ESQUERDO - Hero Visual ===
        rx.box(
            rx.vstack(
                rx.box(
                    rx.icon(tag="flask-conical", size=48, color="white"),
                    bg="rgba(255, 255, 255, 0.2)",
                    p="4",
                    border_radius=Design.RADIUS_XL,
                    backdrop_filter="blur(12px)",
                    margin_bottom=Spacing.LG,
                ),
                rx.heading("LABBRIDGE", size="3", color="white", letter_spacing="0.1em"),
                rx.heading(
                    "Sistema de Auditoria & Inteligencia Laboratorial",
                    size="8",
                    color="white",
                    font_weight="800",
                    line_height="1.2",
                ),
                rx.text(
                    "Seguranca e precisao em cada analise.",
                    size="4",
                    color="white",
                    opacity="0.9",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="circle-check", size=20, color="white"),
                        rx.text("Auditoria financeira automatizada", color="white"),
                        gap="10px",
                    ),
                    rx.hstack(
                        rx.icon(tag="circle-check", size=20, color="white"),
                        rx.text("IA Detective para insights", color="white"),
                        gap="10px",
                    ),
                    rx.hstack(
                        rx.icon(tag="circle-check", size=20, color="white"),
                        rx.text("Relatorios em tempo real", color="white"),
                        gap="10px",
                    ),
                    align_items="start",
                    gap="12px",
                    margin_top=Spacing.XL,
                    opacity="0.9",
                ),
                align_items="start",
                justify_content="center",
                height="100%",
                padding="80px",
                max_width="800px",
            ),
            width=["0%", "0%", "50%"],
            background=f"linear-gradient(135deg, {Color.PRIMARY} 0%, {Color.DEEP} 100%), url('/login_bg.png')",
            background_size="cover",
            background_position="center",
            display=["none", "none", "flex"],
            align_items="center",
            justify_content="center",
            position="relative",
        ),
        # === LADO DIREITO - Formulario ===
        rx.center(
            rx.vstack(
                # Logo
                rx.box(
                    rx.image(src="/labbridge_logo.png", height="100px"),
                    margin_bottom=Spacing.XL,
                ),
                # Formulario (login, registro ou reset)
                rx.cond(
                    State.show_reset_password,
                    reset_password_form(),
                    rx.cond(
                        State.show_register,
                        register_form(),
                        login_form(),
                    ),
                ),
                # Footer
                rx.hstack(
                    rx.icon(tag="shield-check", size=14, color=Color.TEXT_SECONDARY),
                    ui.text("Ambiente Seguro e Monitorado", size="caption"),
                    align_items="center",
                    gap="6px",
                    margin_top=Spacing.XXL,
                ),
                align_items="center",
                width="100%",
                padding=Spacing.LG,
            ),
            width=["100%", "100%", "50%"],
            height="100vh",
            bg=Color.BACKGROUND,
        ),
        width="100%",
        min_height="100vh",
        display="flex",
        flex_direction=["column", "column", "row"],
    )
