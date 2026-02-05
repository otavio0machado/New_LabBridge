"""
OAuth Callback Page
Processa o retorno da autenticação OAuth (Google/Microsoft)
"""
import reflex as rx
from ..states.auth_state import AuthState
from ..styles import Color


def auth_callback() -> rx.Component:
    """Página de callback OAuth"""
    return rx.center(
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
        min_height="100vh",
        bg=Color.BACKGROUND,
        on_mount=AuthState.handle_oauth_callback,
    )
