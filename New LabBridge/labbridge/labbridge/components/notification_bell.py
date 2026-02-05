"""
NotificationBell - Componente de UI para Centro de Notificações
Ícone de sino com badge e dropdown de notificações
"""
import reflex as rx
from ..states.notification_state import NotificationState


def notification_item(notification: dict) -> rx.Component:
    """Renderiza um item de notificação"""
    
    return rx.box(
        rx.hstack(
            rx.icon(
                "bell",
                size=18,
                color=rx.color("blue", 10)
            ),
            rx.vstack(
                rx.text(
                    notification["title"],
                    font_weight="500",
                    font_size="14px",
                    color=rx.color("gray", 12)
                ),
                rx.text(
                    notification["message"],
                    font_size="12px",
                    color=rx.color("gray", 10),
                    max_width="250px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap"
                ),
                align_items="start",
                spacing="0",
                flex="1"
            ),
            width="100%",
            spacing="3",
            align="start"
        ),
        padding="12px",
        cursor="pointer",
        _hover={"background": rx.color("gray", 3)},
        border_bottom=f"1px solid {rx.color('gray', 4)}",
        on_click=NotificationState.mark_as_read(notification["id"])
    )


def notification_bell() -> rx.Component:
    """Componente do sino de notificações"""
    
    return rx.box(
        # Botão do sino
        rx.button(
            rx.box(
                rx.icon("bell", size=20, color=rx.color("gray", 11)),
                # Badge de contagem
                rx.cond(
                    NotificationState.has_unread,
                    rx.box(
                        rx.text(
                            NotificationState.unread_count,
                            font_size="10px",
                            font_weight="bold",
                            color="white"
                        ),
                        position="absolute",
                        top="-4px",
                        right="-4px",
                        min_width="18px",
                        height="18px",
                        border_radius="9px",
                        bg=rx.color("red", 9),
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        padding="0 4px"
                    ),
                    rx.box()
                ),
                position="relative"
            ),
            variant="ghost",
            size="2",
            on_click=NotificationState.toggle_notifications,
            cursor="pointer"
        ),
        
        # Dropdown de notificações
        rx.cond(
            NotificationState.show_notifications,
            rx.box(
                # Header
                rx.hstack(
                    rx.text(
                        "Notificações",
                        font_weight="600",
                        font_size="14px"
                    ),
                    rx.spacer(),
                    rx.cond(
                        NotificationState.has_unread,
                        rx.button(
                            "Marcar todas como lidas",
                            size="1",
                            variant="ghost",
                            color_scheme="blue",
                            on_click=NotificationState.mark_all_read,
                            cursor="pointer"
                        ),
                        rx.box()
                    ),
                    width="100%",
                    padding="12px",
                    border_bottom=f"1px solid {rx.color('gray', 5)}"
                ),
                
                # Lista de notificações
                rx.cond(
                    NotificationState.notifications.length() > 0,
                    rx.box(
                        rx.foreach(
                            NotificationState.recent_notifications,
                            notification_item
                        ),
                        max_height="300px",
                        overflow_y="auto"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("bell-off", size=32, color=rx.color("gray", 8)),
                            rx.text(
                                "Nenhuma notificação",
                                color=rx.color("gray", 9),
                                font_size="14px"
                            ),
                            spacing="2",
                            align="center",
                            padding="24px"
                        )
                    )
                ),
                
                # Footer
                rx.hstack(
                    rx.button(
                        rx.icon("trash-2", size=14),
                        "Limpar todas",
                        size="1",
                        variant="ghost",
                        color_scheme="gray",
                        on_click=NotificationState.clear_notifications,
                        cursor="pointer"
                    ),
                    justify="center",
                    width="100%",
                    padding="8px",
                    border_top=f"1px solid {rx.color('gray', 5)}"
                ),
                
                position="absolute",
                top="100%",
                right="0",
                width="340px",
                bg=rx.color("gray", 1),
                border=f"1px solid {rx.color('gray', 5)}",
                border_radius="8px",
                box_shadow="0 4px 12px rgba(0,0,0,0.15)",
                z_index="1000",
                margin_top="8px"
            ),
            rx.box()
        ),
        
        position="relative",
        on_mount=NotificationState.load_notifications
    )


def notification_center() -> rx.Component:
    """Componente completo do centro de notificações para sidebar/header"""
    return notification_bell()
