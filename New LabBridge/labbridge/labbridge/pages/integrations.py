"""
LabBridge - Integrações
Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Seção 12. Integrações

Estrutura:
- Lista de integrações disponíveis
- Status (Ativa / Inativa / Erro)
- Configuração simples
- Teste de conexão visível
"""
import reflex as rx
from ..states.integration_state import IntegrationState
from ..styles import Color, Design, Spacing, TextSize
from ..components import ui


def integration_card_dynamic(integration: dict) -> rx.Component:
    """Card de integração dinâmico com status e ações"""
    integration_id = integration["id"]
    name = integration["name"]
    description = integration["description"]
    icon = integration["icon"]
    status = integration["status"]
    category = integration["category"]
    last_sync = integration["last_sync"]
    last_error = integration["last_error"]

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text(icon, font_size="1.5rem"),
                    width="48px",
                    height="48px",
                    bg=Color.BACKGROUND,
                    border_radius=Design.RADIUS_MD,
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.vstack(
                    rx.text(name, font_weight="600", color=Color.TEXT_PRIMARY),
                    rx.text(description, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                # Status badge dinâmico
                rx.hstack(
                    rx.icon(
                        tag=rx.cond(
                            status == "active", "circle-check",
                            rx.cond(status == "error", "circle-alert", 
                                rx.cond(status == "syncing", "refresh-cw", "circle"))
                        ),
                        size=14,
                        color=rx.cond(
                            status == "active", Color.SUCCESS,
                            rx.cond(status == "error", Color.ERROR,
                                rx.cond(status == "syncing", Color.PRIMARY, Color.TEXT_SECONDARY))
                        ),
                    ),
                    rx.text(
                        rx.cond(
                            status == "active", "Conectado",
                            rx.cond(status == "error", "Erro",
                                rx.cond(status == "syncing", "Sincronizando", "Desconectado"))
                        ),
                        font_size="0.75rem",
                        font_weight="500",
                        color=rx.cond(
                            status == "active", Color.SUCCESS,
                            rx.cond(status == "error", Color.ERROR,
                                rx.cond(status == "syncing", Color.PRIMARY, Color.TEXT_SECONDARY))
                        ),
                    ),
                    spacing="1",
                    padding="4px 10px",
                    bg=rx.cond(
                        status == "active", Color.SUCCESS_BG,
                        rx.cond(status == "error", Color.ERROR_BG,
                            rx.cond(status == "syncing", Color.PRIMARY_LIGHT, Color.BACKGROUND))
                    ),
                    border_radius="full",
                ),
                width="100%",
                align="center",
            ),
            rx.divider(color=Color.BORDER, margin_y=Spacing.MD),
            rx.hstack(
                rx.hstack(
                    rx.badge(
                        category,
                        variant="soft",
                        size="1"
                    ),
                    rx.cond(
                        last_sync != "",
                        rx.text(
                            last_sync,
                            font_size="0.75rem",
                            color=Color.TEXT_MUTED
                        ),
                        rx.cond(
                            last_error != "",
                            rx.text(
                                last_error,
                                font_size="0.75rem",
                                color=Color.ERROR
                            ),
                            rx.fragment(),
                        ),
                    ),
                    spacing="2",
                ),
                rx.spacer(),
                rx.hstack(
                    # Botão sincronizar (apenas se ativo)
                    rx.cond(
                        status == "active",
                        rx.button(
                            rx.icon(tag="refresh-cw", size=14),
                            rx.text("Sincronizar"),
                            variant="ghost",
                            size="1",
                            cursor="pointer",
                            on_click=lambda: IntegrationState.sync_integration(integration_id),
                            loading=IntegrationState.is_syncing,
                        ),
                        rx.fragment(),
                    ),
                    # Botão configurar
                    rx.button(
                        rx.icon(tag="settings", size=14),
                        rx.text("Configurar"),
                        variant="ghost",
                        size="1",
                        cursor="pointer",
                        on_click=lambda: IntegrationState.open_config_modal(integration_id),
                    ),
                    # Switch ativo/inativo
                    rx.switch(
                        checked=status == "active",
                        size="1",
                        on_change=lambda checked: IntegrationState.toggle_integration(integration_id, checked),
                    ),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="center",
            ),
            width="100%",
            spacing="0",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_LG,
        padding=Spacing.LG,
        transition="all 0.15s ease",
        _hover={
            "border_color": rx.cond(status == "active", Color.SUCCESS, Color.BORDER_DARK),
            "box_shadow": Design.SHADOW_SM,
        },
    )


def category_section_dynamic(title: str, integrations: list) -> rx.Component:
    """Seção de categoria de integrações"""
    return rx.cond(
        integrations.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.text(title, font_weight="600", color=Color.TEXT_PRIMARY),
                rx.badge(integrations.length(), variant="soft", size="1"),
                spacing="2",
                margin_bottom=Spacing.MD,
            ),
            rx.foreach(
                integrations,
                integration_card_dynamic,
            ),
            spacing="3",
            width="100%",
            margin_bottom=Spacing.XL,
        ),
        rx.fragment(),
    )


def config_modal() -> rx.Component:
    """Modal de configuração de integração"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="settings", size=20),
                    rx.text(f"Configurar {IntegrationState.current_integration_name}"),
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                "Configure as credenciais e parâmetros desta integração.",
                margin_bottom=Spacing.LG,
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("URL da API", font_weight="500", font_size=TextSize.SMALL),
                    ui.input(
                        placeholder="https://api.exemplo.com",
                        width="100%",
                        value=IntegrationState.config_fields.get("api_url", ""),
                        on_change=lambda v: IntegrationState.update_config_field("api_url", v),
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Chave de API", font_weight="500", font_size=TextSize.SMALL),
                    ui.input(
                        placeholder="Sua chave de API",
                        width="100%",
                        type="password",
                        value=IntegrationState.config_fields.get("api_key", ""),
                        on_change=lambda v: IntegrationState.update_config_field("api_key", v),
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    IntegrationState.error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-alert", size=16, color=Color.ERROR),
                            rx.text(IntegrationState.error_message, color=Color.ERROR, font_size="0.875rem"),
                            spacing="2",
                        ),
                        bg=Color.ERROR_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    ui.button("Cancelar", variant="ghost", on_click=IntegrationState.close_config_modal),
                ),
                rx.dialog.close(
                    ui.button(
                        "Salvar",
                        variant="primary",
                        icon="save",
                        on_click=IntegrationState.save_config,
                        loading=IntegrationState.is_loading,
                    ),
                ),
                spacing="2",
                justify="end",
                margin_top=Spacing.LG,
            ),
            max_width="450px",
        ),
        open=IntegrationState.show_config_modal,
    )


def integrations_page() -> rx.Component:
    """Página de Integrações - Dinâmica com dados do banco"""
    return rx.box(
        rx.vstack(
            # Page Header
            ui.page_header(
                title="Integrações",
                description="Conecte o LabBridge aos seus sistemas",
                actions=rx.hstack(
                    rx.button(
                        rx.icon(tag="refresh-cw", size=16),
                        rx.text("Sincronizar Todas"),
                        variant="outline",
                        size="2",
                        on_click=IntegrationState.sync_all_integrations,
                        loading=IntegrationState.is_syncing,
                    ),
                    ui.button(
                        "Adicionar Integração",
                        icon="plus",
                        on_click=IntegrationState.open_add_modal,
                    ),
                    spacing="2",
                ),
            ),

            # Success/Error Toast Messages
            rx.cond(
                IntegrationState.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon(tag="circle-check", size=20, color=Color.SUCCESS),
                        rx.text(IntegrationState.success_message, color=Color.SUCCESS),
                        rx.spacer(),
                        rx.button(
                            rx.icon(tag="x", size=14),
                            variant="ghost",
                            size="1",
                            on_click=IntegrationState.clear_messages,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    bg=Color.SUCCESS_BG,
                    border=f"1px solid {Color.SUCCESS}40",
                    padding=Spacing.MD,
                    border_radius=Design.RADIUS_LG,
                    margin_bottom=Spacing.MD,
                ),
            ),
            rx.cond(
                IntegrationState.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon(tag="circle-alert", size=20, color=Color.ERROR),
                        rx.text(IntegrationState.error_message, color=Color.ERROR),
                        rx.spacer(),
                        rx.button(
                            rx.icon(tag="x", size=14),
                            variant="ghost",
                            size="1",
                            on_click=IntegrationState.clear_messages,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    bg=Color.ERROR_BG,
                    border=f"1px solid {Color.ERROR}40",
                    padding=Spacing.MD,
                    border_radius=Design.RADIUS_LG,
                    margin_bottom=Spacing.MD,
                ),
            ),

            # Status Summary - Dynamic
            rx.grid(
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="plug", size=20, color=Color.PRIMARY),
                            padding="10px",
                            bg=Color.PRIMARY_LIGHT,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(IntegrationState.total_integrations, font_size="1.5rem", font_weight="700", color=Color.DEEP),
                            rx.text("Total", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="circle-check", size=20, color=Color.SUCCESS),
                            padding="10px",
                            bg=Color.SUCCESS_BG,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(IntegrationState.active_count, font_size="1.5rem", font_weight="700", color=Color.SUCCESS),
                            rx.text("Ativas", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="circle", size=20, color=Color.TEXT_SECONDARY),
                            padding="10px",
                            bg=Color.BACKGROUND,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(IntegrationState.inactive_count, font_size="1.5rem", font_weight="700", color=Color.TEXT_SECONDARY),
                            rx.text("Inativas", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="circle-alert", size=20, color=Color.ERROR),
                            padding="10px",
                            bg=Color.ERROR_BG,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(IntegrationState.error_count, font_size="1.5rem", font_weight="700", color=Color.ERROR),
                            rx.text("Com Erro", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                columns=rx.breakpoints(initial="2", md="4"),
                spacing="4",
                width="100%",
                margin_bottom=Spacing.LG,
            ),

            # Loading State
            rx.cond(
                IntegrationState.is_loading,
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3", color=Color.PRIMARY),
                        rx.text("Carregando integrações...", color=Color.TEXT_SECONDARY),
                        spacing="3",
                    ),
                    padding=Spacing.XXL,
                ),
                rx.fragment(
                    # Integration Categories - Dynamic
                    category_section_dynamic(
                        "Sistemas de Gestão Laboratorial",
                        IntegrationState.lis_integrations,
                    ),
                    category_section_dynamic(
                        "Faturamento e Convênios",
                        IntegrationState.billing_integrations,
                    ),
                    category_section_dynamic(
                        "Armazenamento e Comunicação",
                        IntegrationState.other_integrations,
                    ),
                ),
            ),

            # Connection Test Section - Dynamic
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="activity", size=20, color=Color.PRIMARY),
                        rx.text("Teste de Conexão", font_weight="600", color=Color.TEXT_PRIMARY),
                        spacing="2",
                    ),
                    rx.text(
                        "Verifique a conectividade de todas as integrações ativas.",
                        font_size="0.875rem",
                        color=Color.TEXT_SECONDARY,
                        margin_bottom=Spacing.MD,
                    ),
                    rx.hstack(
                        rx.select(
                            IntegrationState.active_integration_names,
                            value=IntegrationState.test_selected,
                            on_change=IntegrationState.set_test_selected,
                            size="2",
                        ),
                        rx.button(
                            rx.icon(tag="zap", size=16),
                            rx.text("Executar Teste"),
                            variant="solid",
                            size="2",
                            bg=Color.PRIMARY,
                            color="white",
                            _hover={"bg": Color.PRIMARY_HOVER},
                            on_click=IntegrationState.run_connection_test,
                            loading=IntegrationState.is_testing,
                        ),
                        spacing="2",
                    ),
                    # Test Result
                    rx.cond(
                        IntegrationState.test_result != "",
                        rx.box(
                            rx.text(
                                IntegrationState.test_result,
                                font_size="0.875rem",
                                color=rx.cond(
                                    IntegrationState.test_success,
                                    Color.SUCCESS,
                                    Color.ERROR
                                ),
                                white_space="pre-line",
                            ),
                            bg=rx.cond(
                                IntegrationState.test_success,
                                Color.SUCCESS_BG,
                                Color.ERROR_BG
                            ),
                            padding=Spacing.MD,
                            border_radius=Design.RADIUS_MD,
                            margin_top=Spacing.MD,
                            width="100%",
                        ),
                    ),
                    width="100%",
                    spacing="2",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.LG,
            ),

            # Config Modal
            config_modal(),

            width="100%",
            spacing="0",
        ),
        width="100%",
        on_mount=IntegrationState.load_integrations,
    )
