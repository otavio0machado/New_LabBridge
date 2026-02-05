"""
FloatingChat - Botao flutuante de chat com Bio IA
Painel compacto acessivel em todas as paginas autenticadas.
Reutiliza DetectiveState e componentes de insight_chat.
"""
import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design
from ..pages.insight_chat import chat_bubble, thinking_trace


def _compact_input_area() -> rx.Component:
    """Area de input compacta (sem upload de imagem)."""
    return rx.hstack(
        rx.input(
            value=State.input_text,
            on_change=State.set_input_text,
            placeholder="Pergunte a Bio IA...",
            border_radius="full",
            padding_x=Spacing.MD,
            height="2.5rem",
            width="100%",
            border=f"1px solid {Color.BORDER}",
            bg=Color.SURFACE,
            font_size="0.85rem",
            _focus={
                "border_color": Color.PRIMARY,
                "box_shadow": f"0 0 0 3px {Color.PRIMARY_LIGHT}",
                "outline": "none",
            },
            on_key_down=State.handle_keys,
            disabled=State.is_loading,
        ),
        rx.button(
            rx.cond(
                State.is_loading,
                rx.spinner(color="white", size="1"),
                rx.icon("send", size=16),
            ),
            on_click=State.send_message,
            bg=Color.GRADIENT_PRIMARY,
            color="white",
            border_radius="full",
            width="2.5rem",
            height="2.5rem",
            min_width="2.5rem",
            box_shadow=Design.SHADOW_SM,
            _hover={"transform": "scale(1.05)", "box_shadow": Design.SHADOW_MD},
            cursor="pointer",
            disabled=State.is_loading,
            padding="0",
        ),
        width="100%",
        spacing="2",
        align_items="center",
        padding=Spacing.SM,
    )


def _panel_header() -> rx.Component:
    """Header do painel com titulo e controles."""
    return rx.hstack(
        rx.hstack(
            rx.icon("bot", size=20, color=Color.PRIMARY),
            rx.text(
                "Bio IA",
                font_weight="600",
                font_size="0.95rem",
                color=Color.DEEP,
            ),
            spacing="2",
            align="center",
        ),
        rx.spacer(),
        rx.link(
            rx.icon_button(
                rx.icon("maximize-2", size=14),
                variant="ghost",
                size="1",
                color=Color.TEXT_SECONDARY,
                cursor="pointer",
            ),
            href="/detetive",
            title="Abrir chat completo",
        ),
        rx.icon_button(
            rx.icon("x", size=16),
            variant="ghost",
            size="1",
            color=Color.TEXT_SECONDARY,
            cursor="pointer",
            on_click=State.close_chat_panel,
            title="Fechar",
        ),
        width="100%",
        align="center",
        padding_x=Spacing.MD,
        padding_y=Spacing.SM,
        border_bottom=f"1px solid {Color.BORDER}",
        bg=Color.SURFACE,
    )


def _message_area() -> rx.Component:
    """Area de mensagens com scroll."""
    return rx.scroll_area(
        rx.cond(
            State.messages.length() > 0,
            rx.vstack(
                rx.foreach(State.messages, chat_bubble),
                width="100%",
                spacing="3",
                padding=Spacing.SM,
            ),
            rx.center(
                rx.vstack(
                    rx.icon("message-circle", size=36, color=Color.TEXT_SECONDARY),
                    rx.text(
                        "Pergunte sobre seus dados",
                        color=Color.TEXT_SECONDARY,
                        font_size="0.85rem",
                    ),
                    align="center",
                    spacing="2",
                ),
                height="100%",
            ),
        ),
        flex="1",
        width="100%",
        type="always",
        scrollbars="vertical",
        style={"paddingRight": "0.5rem"},
    )


def _compact_suggestions() -> rx.Component:
    """Sugestoes compactas."""
    return rx.cond(
        State.messages.length() <= 1,
        rx.flex(
            rx.foreach(
                State.suggested_actions,
                lambda action: rx.badge(
                    action,
                    variant="outline",
                    color_scheme="blue",
                    padding_x="8px",
                    padding_y="4px",
                    border_radius="full",
                    cursor="pointer",
                    font_size="0.7rem",
                    _hover={
                        "bg": Color.PRIMARY,
                        "color": "white",
                    },
                    on_click=State.select_suggested_action(action),
                    style={"transition": "all 0.2s ease"},
                ),
            ),
            spacing="1",
            flex_wrap="wrap",
            padding_x=Spacing.SM,
            padding_y=Spacing.XS,
            width="100%",
        ),
        rx.fragment(),
    )


def floating_chat_panel() -> rx.Component:
    """Painel de chat que aparece acima do botao."""
    return rx.cond(
        State.show_chat_panel,
        rx.box(
            rx.vstack(
                _panel_header(),
                _message_area(),
                thinking_trace(),
                _compact_suggestions(),
                _compact_input_area(),
                spacing="0",
                height="100%",
            ),
            position="fixed",
            bottom=["80px", "80px", "96px"],
            right=[Spacing.MD, Spacing.MD, Spacing.LG],
            width=["calc(100vw - 32px)", "380px", "400px"],
            height=["60vh", "500px", "520px"],
            max_height="70vh",
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_LG,
            box_shadow=Design.SHADOW_LG,
            z_index="90",
            class_name="animate-scale-up",
            overflow="hidden",
        ),
        rx.fragment(),
    )


def floating_chat_button() -> rx.Component:
    """Botao circular flutuante no canto inferior direito."""
    return rx.box(
        rx.button(
            rx.cond(
                State.show_chat_panel,
                rx.icon("x", size=24, color="white"),
                rx.icon("bot", size=24, color="white"),
            ),
            on_click=State.toggle_chat_panel,
            bg=Color.GRADIENT_PRIMARY,
            width="56px",
            height="56px",
            min_width="56px",
            border_radius="full",
            box_shadow=Design.SHADOW_LG,
            cursor="pointer",
            _hover={
                "transform": "scale(1.08)",
                "box_shadow": "0 8px 25px rgba(37, 99, 235, 0.35)",
            },
            _active={"transform": "scale(0.95)"},
            transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
            display="flex",
            align_items="center",
            justify_content="center",
            padding="0",
            border="none",
        ),
        position="fixed",
        bottom=[Spacing.MD, Spacing.MD, Spacing.LG],
        right=[Spacing.MD, Spacing.MD, Spacing.LG],
        z_index="90",
    )


def floating_chat() -> rx.Component:
    """Componente combinado: botao + painel. Usar em authenticated_layout."""
    return rx.fragment(
        floating_chat_panel(),
        floating_chat_button(),
    )
