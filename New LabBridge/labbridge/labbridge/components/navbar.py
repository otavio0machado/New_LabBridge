"""
LabBridge - Sistema de Navegação
Sidebar lateral fixa (desktop) + Top bar para ações globais
Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md
"""
import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design
from .notification_bell import notification_bell

# =============================================================================
# NAVIGATION ITEMS - Ordem fixa conforme especificação
# =============================================================================
NAV_ITEMS = [
    {"id": "dashboard", "label": "Dashboard", "icon": "layout-dashboard", "route": "/dashboard"},
    {"id": "analise", "label": "Auditorias", "icon": "file-search", "route": "/analise"},
    {"id": "conversor", "label": "Importador de Dados", "icon": "upload", "route": "/conversor"},
    {"id": "reports", "label": "Relatórios", "icon": "file-bar-chart", "route": "/reports"},
    {"id": "history", "label": "Histórico", "icon": "history", "route": "/history"},
    {"id": "subscription", "label": "Assinaturas & Planos", "icon": "credit-card", "route": "/subscription"},
    {"id": "team", "label": "Usuários & Permissões", "icon": "users", "route": "/team"},
    {"id": "integrations", "label": "Integrações", "icon": "plug", "route": "/integrations"},
    {"id": "help", "label": "Central de Ajuda", "icon": "circle-help", "route": "/help"},
    {"id": "settings", "label": "Configurações", "icon": "settings", "route": "/settings"},
]

def sidebar_link(item: dict) -> rx.Component:
    """Link de navegação da sidebar com estados visuais claros"""
    href = item["route"]
    is_active = rx.State.router.page.path == href

    return rx.link(
        rx.hstack(
            rx.icon(
                tag=item["icon"],
                size=20,
                color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
            ),
            rx.text(
                item["label"],
                font_weight=rx.cond(is_active, "600", "400"),
                font_size="0.9rem",
                color=rx.cond(is_active, Color.TEXT_PRIMARY, Color.TEXT_SECONDARY),
                white_space="nowrap",
                overflow="hidden",
                text_overflow="ellipsis",
            ),
            spacing="3",
            align="center",
            width="100%",
            padding_x=Spacing.MD,
            padding_y=Spacing.SM,
            border_radius=Design.RADIUS_MD,
            bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
            border_left=rx.cond(is_active, f"3px solid {Color.PRIMARY}", "3px solid transparent"),
            transition="all 0.2s ease",
            _hover={
                "bg": Color.PRIMARY_LIGHT,
                "color": Color.PRIMARY,
            },
        ),
        href=href,
        text_decoration="none",
        width="100%",
        _focus_visible={
            "outline": f"2px solid {Color.PRIMARY}",
            "outline_offset": "2px",
        },
    )


def sidebar() -> rx.Component:
    """Sidebar lateral fixa para desktop"""
    return rx.box(
        rx.vstack(
            # Logo
            rx.box(
                rx.hstack(
                    rx.image(
                        src="/labbridge_icon.png",
                        height="45px",
                        width="45px",
                        alt="LabBridge",
                        object_fit="contain",
                    ),
                    rx.text(
                        "LabBridge",
                        font_size="1.35rem",
                        font_weight="700",
                        color=Color.DEEP,
                    ),
                    spacing="3",
                    align="center",
                ),
                padding=Spacing.LG,
                padding_bottom=Spacing.MD,
                border_bottom=f"1px solid {Color.BORDER}",
                width="100%",
            ),

            # Navigation Items
            rx.vstack(
                *[sidebar_link(item) for item in NAV_ITEMS],
                spacing="1",
                width="100%",
                padding=Spacing.SM,
                flex="1",
                overflow_y="auto",
            ),

            # User Section (Bottom)
            rx.box(
                rx.vstack(
                    rx.divider(color=Color.BORDER),
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.hstack(
                                rx.avatar(
                                    fallback="AD",
                                    size="2",
                                    radius="full",
                                    bg=Color.PRIMARY,
                                    color="white",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "Admin",
                                        font_size="0.875rem",
                                        font_weight="600",
                                        color=Color.TEXT_PRIMARY,
                                    ),
                                    rx.text(
                                        "Administrador",
                                        font_size="0.75rem",
                                        color=Color.TEXT_SECONDARY,
                                    ),
                                    spacing="0",
                                    align_items="start",
                                ),
                                rx.spacer(),
                                rx.icon(tag="chevron-up", size=16, color=Color.TEXT_SECONDARY),
                                spacing="3",
                                align="center",
                                width="100%",
                                padding=Spacing.SM,
                                border_radius=Design.RADIUS_MD,
                                cursor="pointer",
                                _hover={"bg": Color.BACKGROUND},
                            ),
                        ),
                        rx.menu.content(
                            rx.menu.item("Meu Perfil", on_select=State.navigate_to("settings")),
                            rx.menu.item("Configurações", on_select=State.navigate_to("settings")),
                            rx.menu.separator(),
                            rx.menu.item("Sair", color="red", on_select=State.logout),
                        ),
                    ),
                    width="100%",
                    spacing="2",
                ),
                padding=Spacing.SM,
                width="100%",
            ),

            width="100%",
            height="100vh",
            spacing="0",
            align_items="stretch",
        ),
        width=["0", "0", "240px", "260px"],
        min_width=["0", "0", "240px", "260px"],
        height="100vh",
        position="fixed",
        left="0",
        top="0",
        bg=Color.SURFACE,
        border_right=f"1px solid {Color.BORDER}",
        display=["none", "none", "flex", "flex"],
        flex_direction="column",
        z_index="100",
        overflow="hidden",
    )


def top_bar() -> rx.Component:
    """Barra superior para ações globais"""
    return rx.box(
        rx.hstack(
            # Mobile Menu Trigger
            rx.box(
                mobile_nav_trigger(),
                display=["flex", "flex", "none", "none"],
            ),

            # Mobile Logo
            rx.box(
                rx.image(
                    src="/labbridge_icon.png",
                    height="45px",
                    width="auto",
                    alt="LabBridge",
                    object_fit="contain",
                ),
                display=["flex", "flex", "none", "none"],
            ),

            rx.spacer(),

            # Search (Desktop)
            rx.box(
                rx.hstack(
                    rx.icon(tag="search", size=18, color=Color.TEXT_SECONDARY),
                    rx.input(
                        placeholder="Buscar...",
                        variant="soft",
                        size="2",
                        width="200px",
                        border="none",
                        bg="transparent",
                    ),
                    bg=Color.BACKGROUND,
                    padding_x=Spacing.MD,
                    padding_y=Spacing.XS,
                    border_radius=Design.RADIUS_LG,
                    border=f"1px solid {Color.BORDER}",
                    align="center",
                    _focus_within={
                        "border_color": Color.PRIMARY,
                        "box_shadow": f"0 0 0 3px {Color.PRIMARY_LIGHT}",
                    },
                ),
                display=["none", "none", "none", "flex"],
            ),

            rx.spacer(),

            # Right Actions
            rx.hstack(
                # Notifications - Centro de Notificações funcional
                notification_bell(),

                # Quick Actions
                rx.button(
                    rx.icon(tag="plus", size=16),
                    rx.text("Nova Auditoria", display=["none", "none", "inline"]),
                    variant="solid",
                    size="2",
                    bg=Color.PRIMARY,
                    color="white",
                    border_radius=Design.RADIUS_MD,
                    cursor="pointer",
                    aria_label="Criar Nova Auditoria",
                    _hover={"bg": Color.PRIMARY_HOVER},
                    on_click=State.navigate_to("analise"),
                ),

                # User Avatar (Desktop - shown in sidebar, hidden here)
                rx.box(
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.avatar(
                                fallback="AD",
                                size="2",
                                radius="full",
                                bg=Color.PRIMARY,
                                color="white",
                                cursor="pointer",
                            ),
                        ),
                        rx.menu.content(
                            rx.menu.item("Meu Perfil", on_select=State.navigate_to("settings")),
                            rx.menu.item("Configurações", on_select=State.navigate_to("settings")),
                            rx.menu.separator(),
                            rx.menu.item("Sair", color="red", on_select=State.logout),
                        ),
                    ),
                    display=["flex", "flex", "none", "none"],
                ),

                spacing="3",
                align="center",
            ),

            width="100%",
            align="center",
            padding_x=[Spacing.MD, Spacing.LG],
            padding_y=Spacing.SM,
        ),
        width="100%",
        bg=Color.SURFACE,
        border_bottom=f"1px solid {Color.BORDER}",
        position="sticky",
        top="0",
        z_index="50",
    )


def mobile_nav_trigger() -> rx.Component:
    """Menu hambúrguer para mobile"""
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon(tag="menu", size=24, color=Color.TEXT_PRIMARY),
                padding=Spacing.SM,
                border_radius=Design.RADIUS_MD,
                cursor="pointer",
                role="button",
                aria_label="Abrir menu de navegação",
                _hover={"bg": Color.PRIMARY_LIGHT},
            ),
        ),
        rx.menu.content(
            *[
                rx.menu.item(
                    rx.hstack(
                        rx.icon(tag=item["icon"], size=18),
                        rx.text(item["label"], font_size="0.9rem"),
                        spacing="3",
                    ),
                    on_select=lambda i=item: State.set_page(i["id"]),
                    padding="12px",
                )
                for item in NAV_ITEMS
            ],
            rx.menu.separator(),
            rx.menu.item(
                rx.hstack(
                    rx.icon(tag="log-out", size=18),
                    rx.text("Sair", font_size="0.9rem"),
                    spacing="3",
                ),
                color="red",
                on_select=State.logout,
                padding="12px",
            ),
            width="260px",
        ),
    )


def navbar() -> rx.Component:
    """
    Sistema de navegação completo:
    - Desktop: Sidebar lateral fixa + Top bar
    - Mobile: Top bar com menu hambúrguer
    """
    return rx.fragment(
        sidebar(),
        top_bar(),
    )


def mobile_nav() -> rx.Component:
    """Compatibilidade - não usado mais"""
    return rx.fragment()
