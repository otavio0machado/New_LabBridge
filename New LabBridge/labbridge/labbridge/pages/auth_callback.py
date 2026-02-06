"""
OAuth Callback Page
Processa o retorno da autenticação OAuth (Google/Microsoft)
"""
import reflex as rx
from ..states.auth_state import AuthState
from ..styles import Color, Design, Spacing


def auth_callback() -> rx.Component:
    """Página de callback OAuth com tratamento de erros"""
    return rx.center(
        rx.cond(
            AuthState.oauth_error != "",
            # Error state
            rx.vstack(
                rx.icon(tag="circle-x", size=48, color=Color.ERROR),
                rx.text(
                    "Erro na autenticação",
                    font_weight="700",
                    font_size="1.25rem",
                    color=Color.TEXT_PRIMARY,
                ),
                rx.text(
                    AuthState.oauth_error,
                    color=Color.TEXT_SECONDARY,
                    font_size="0.95rem",
                    text_align="center",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon(tag="arrow-left", size=16),
                        rx.text("Voltar ao Login"),
                        spacing="2",
                    ),
                    on_click=rx.redirect("/login"),
                    bg=Color.PRIMARY,
                    color="white",
                    border_radius=Design.RADIUS_MD,
                    margin_top=Spacing.MD,
                ),
                spacing="4",
                align="center",
                bg=Color.SURFACE,
                padding=Spacing.XL,
                border_radius=Design.RADIUS_XL,
                border=f"1px solid {Color.BORDER}",
                max_width="400px",
            ),
            # Loading state
            rx.vstack(
                rx.spinner(size="3"),
                rx.text(
                    "Processando autenticação...",
                    color=Color.TEXT_SECONDARY,
                    font_size="1rem",
                ),
                rx.text(
                    "Você será redirecionado em breve.",
                    color=Color.TEXT_SECONDARY,
                    font_size="0.875rem",
                ),
                spacing="4",
                align="center",
            ),
        ),
        min_height="100vh",
        bg=Color.BACKGROUND,
        on_mount=AuthState.handle_oauth_callback,
    )
