"""
LabBridge - Relatorios
Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Secao 8. Relatorios

Objetivo: Transformar dados em decisao.
Componentes:
- Filtros avancados
- Visualizacao tabular e grafica
- Exportacao (PDF, CSV)
- Resumo executivo no topo
"""
import reflex as rx
from ..state import State
from ..states.analysis_state import AnalysisState
from ..states.reports_state import ReportsState
from ..styles import Color, Design, Spacing, TextSize
from ..components import ui


def executive_summary() -> rx.Component:
    """Resumo executivo no topo da pagina - dados dinamicos"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="file-text", size=24, color=Color.PRIMARY),
                    rx.text("Resumo Executivo", font_weight="600", font_size="1.125rem", color=Color.DEEP),
                    spacing="3",
                ),
                rx.spacer(),
                rx.text("Analises Salvas", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                width="100%",
                align="center",
            ),
            rx.divider(color=Color.BORDER, margin_y=Spacing.MD),
            rx.grid(
                # Total COMPULAB (soma de todas analises)
                rx.hstack(
                    rx.box(
                        rx.icon(tag="banknote", size=20, color=Color.SUCCESS),
                        padding="8px",
                        bg=Color.SUCCESS_BG,
                        border_radius=Design.RADIUS_MD,
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(
                                AnalysisState.saved_analyses_list.length() > 0,
                                "R$ " + AnalysisState.compulab_total.to(str),
                                "R$ 0,00"
                            ),
                            font_weight="700", font_size="1.25rem", color=Color.DEEP
                        ),
                        rx.text("COMPULAB (Atual)", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="3",
                ),
                # Total SIMUS
                rx.hstack(
                    rx.box(
                        rx.icon(tag="credit-card", size=20, color=Color.PRIMARY),
                        padding="8px",
                        bg=Color.PRIMARY_LIGHT,
                        border_radius=Design.RADIUS_MD,
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(
                                AnalysisState.saved_analyses_list.length() > 0,
                                "R$ " + AnalysisState.simus_total.to(str),
                                "R$ 0,00"
                            ),
                            font_weight="700", font_size="1.25rem", color=Color.DEEP
                        ),
                        rx.text("SIMUS (Atual)", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="3",
                ),
                # Analises salvas
                rx.hstack(
                    rx.box(
                        rx.icon(tag="file-check", size=20, color=Color.PRIMARY),
                        padding="8px",
                        bg=Color.PRIMARY_LIGHT,
                        border_radius=Design.RADIUS_MD,
                    ),
                    rx.vstack(
                        rx.text(
                            AnalysisState.saved_analyses_list.length().to_string(),
                            font_weight="700", font_size="1.25rem", color=Color.DEEP
                        ),
                        rx.text("Analises Salvas", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="3",
                ),
                # Divergencias
                rx.hstack(
                    rx.box(
                        rx.icon(tag="triangle-alert", size=20, color=Color.WARNING),
                        padding="8px",
                        bg=Color.WARNING_BG,
                        border_radius=Design.RADIUS_MD,
                    ),
                    rx.vstack(
                        rx.text(
                            AnalysisState.divergences_count.to(str),
                            font_weight="700", font_size="1.25rem", color=Color.WARNING_HOVER
                        ),
                        rx.text("Divergencias (Atual)", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="3",
                ),
                columns=rx.breakpoints(initial="2", md="4"),
                spacing="4",
                width="100%",
            ),
            width="100%",
            spacing="0",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.LG,
        margin_bottom=Spacing.LG,
    )


def saved_analysis_card(analysis: dict) -> rx.Component:
    """Card de analise salva do banco de dados"""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag="file-search", size=20, color=Color.PRIMARY),
                    padding="10px",
                    bg=Color.PRIMARY_LIGHT,
                    border_radius=Design.RADIUS_MD,
                ),
                rx.vstack(
                    rx.text(analysis["analysis_name"], font_weight="500", color=Color.TEXT_PRIMARY),
                    rx.hstack(
                        rx.text("Data: ", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        rx.text(analysis["analysis_date"], font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        rx.text(" - COMPULAB: R$ ", font_size="0.75rem", color=Color.TEXT_MUTED),
                        rx.text(analysis["compulab_total"], font_size="0.75rem", color=Color.SUCCESS),
                        rx.text(" - SIMUS: R$ ", font_size="0.75rem", color=Color.TEXT_MUTED),
                        rx.text(analysis["simus_total"], font_size="0.75rem", color=Color.PRIMARY),
                        spacing="1",
                    ),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.badge(
                    rx.text(analysis["divergences_count"], " divergencias"),
                    color_scheme="yellow",
                    variant="soft",
                ),
                # Botao para abrir PDF (se disponivel)
                rx.cond(
                    analysis["analysis_report_url"] != None,
                    rx.link(
                        rx.button(
                            rx.icon(tag="file-text", size=16),
                            variant="ghost",
                            size="1",
                            cursor="pointer",
                            title="Abrir PDF",
                        ),
                        href=analysis["analysis_report_url"],
                        is_external=True,
                    ),
                    rx.button(
                        rx.icon(tag="file-x", size=16),
                        variant="ghost",
                        size="1",
                        cursor="not-allowed",
                        title="PDF nao disponivel",
                        disabled=True,
                        color=Color.TEXT_MUTED,
                    ),
                ),
                # Botao para ver detalhes da analise
                rx.button(
                    rx.icon(tag="eye", size=16),
                    variant="ghost",
                    size="1",
                    cursor="pointer",
                    title="Ver detalhes",
                    on_click=AnalysisState.open_saved_analysis(analysis["id"]),
                ),
                rx.button(
                    rx.icon(tag="trash-2", size=16),
                    variant="ghost",
                    size="1",
                    cursor="pointer",
                    color=Color.ERROR,
                    title="Excluir",
                    on_click=AnalysisState.delete_saved_analysis(analysis["id"]),
                ),
                spacing="1",
            ),
            width="100%",
            align="center",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_LG,
        padding=Spacing.MD,
        transition="all 0.15s ease",
        _hover={
            "border_color": Color.PRIMARY,
            "box_shadow": Design.SHADOW_SM,
        },
    )


def filters_section() -> rx.Component:
    """Secao de filtros avancados"""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.select(
                    ["Todos os Tipos", "Financeiro", "Operacional", "Auditoria"],
                    value=ReportsState.type_filter,
                    on_change=ReportsState.set_type_filter,
                    size="2",
                ),
                rx.select(
                    ["Ultimo Mes", "Ultimos 3 Meses", "Ultimo Ano", "Personalizado"],
                    value=ReportsState.date_filter,
                    on_change=ReportsState.set_date_filter,
                    size="2",
                ),
                rx.input(
                    placeholder="Buscar relatorio...",
                    value=ReportsState.search_query,
                    on_change=ReportsState.set_search_query,
                    width="200px",
                ),
                spacing="2",
                flex_wrap="wrap",
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    rx.icon(tag="filter-x", size=16),
                    rx.text("Limpar", display=["none", "inline"]),
                    variant="ghost",
                    size="2",
                    on_click=ReportsState.clear_filters,
                ),
                rx.button(
                    rx.icon(tag="plus", size=16),
                    rx.text("Novo Relatorio"),
                    variant="solid",
                    size="2",
                    bg=Color.PRIMARY,
                    color="white",
                    _hover={"bg": Color.PRIMARY_HOVER},
                    on_click=State.navigate_to("analise"),
                ),
                spacing="2",
            ),
            width="100%",
            align="center",
            flex_wrap="wrap",
            gap="3",
        ),
        width="100%",
        padding=Spacing.MD,
        bg=Color.BACKGROUND,
        border_radius=Design.RADIUS_LG,
        border=f"1px solid {Color.BORDER}",
        margin_bottom=Spacing.LG,
    )


def reports_page() -> rx.Component:
    """Pagina de Relatorios"""
    return rx.box(
        rx.vstack(
            # Page Header
            ui.page_header(
                title="Relatorios",
                description="Visualize e exporte analises salvas",
                actions=rx.hstack(
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.button(
                                rx.cond(
                                    ReportsState.is_exporting,
                                    rx.hstack(rx.spinner(size="1"), rx.text("Exportando..."), spacing="2"),
                                    rx.hstack(rx.icon(tag="download", size=16), rx.text("Exportar Todos"), spacing="2"),
                                ),
                                variant="outline",
                                size="2",
                                disabled=ReportsState.is_exporting,
                            ),
                        ),
                        rx.menu.content(
                            rx.menu.item(
                                rx.hstack(rx.icon(tag="file-text", size=14), rx.text("Exportar como PDF"), spacing="2"),
                                on_click=ReportsState.export_all_pdf,
                            ),
                            rx.menu.item(
                                rx.hstack(rx.icon(tag="table", size=14), rx.text("Exportar como CSV"), spacing="2"),
                                on_click=ReportsState.export_all_csv,
                            ),
                            rx.menu.item(
                                rx.hstack(rx.icon(tag="file-spreadsheet", size=14), rx.text("Exportar como Excel"), spacing="2"),
                                on_click=ReportsState.export_all_excel,
                            ),
                        ),
                    ),
                    ui.button("Gerar Relatorio", icon="plus", on_click=State.navigate_to("analise")),
                    spacing="2",
                ),
            ),

            # Executive Summary
            executive_summary(),

            # Filters
            filters_section(),

            # Reports List
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("Analises Salvas", font_weight="600", color=Color.TEXT_PRIMARY),
                        rx.spacer(),
                        rx.hstack(
                            rx.text(
                                AnalysisState.saved_analyses_list.length().to_string() + " analises",
                                font_size="0.875rem",
                                color=Color.TEXT_SECONDARY,
                            ),
                            rx.button(
                                rx.icon(tag="refresh-cw", size=14),
                                rx.text("Atualizar"),
                                variant="ghost",
                                size="1",
                                on_click=AnalysisState.load_saved_analyses,
                            ),
                            spacing="3",
                        ),
                        width="100%",
                        align="center",
                        margin_bottom=Spacing.MD,
                    ),
                    # Lista dinamica de analises salvas
                    rx.cond(
                        AnalysisState.saved_analyses_list.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                AnalysisState.saved_analyses_list,
                                saved_analysis_card,
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.box(
                            rx.vstack(
                                rx.icon(tag="file-x", size=48, color=Color.TEXT_MUTED),
                                rx.text("Nenhuma analise salva", font_weight="500", color=Color.TEXT_SECONDARY),
                                rx.text(
                                    "Execute uma analise e clique em 'Salvar' para ver aqui.",
                                    font_size="0.875rem",
                                    color=Color.TEXT_MUTED,
                                    text_align="center",
                                ),
                                rx.button(
                                    rx.icon(tag="plus", size=16),
                                    rx.text("Nova Analise"),
                                    variant="solid",
                                    bg=Color.PRIMARY,
                                    color="white",
                                    on_click=State.navigate_to("analise"),
                                ),
                                spacing="3",
                                align="center",
                                padding_y=Spacing.XL,
                            ),
                            width="100%",
                        ),
                    ),
                    width="100%",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.LG,
            ),

            # Pagination - Now functional
            rx.cond(
                AnalysisState.saved_analyses_list.length() > 0,
                rx.hstack(
                    rx.text(
                        "Mostrando ",
                        AnalysisState.saved_analyses_list.length().to_string(),
                        " analises",
                        font_size="0.875rem",
                        color=Color.TEXT_SECONDARY
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            rx.icon(tag="chevron-left", size=16),
                            variant="ghost",
                            size="1",
                            disabled=~ReportsState.can_go_prev,
                            on_click=ReportsState.prev_page,
                        ),
                        rx.text(
                            ReportsState.current_page.to_string(),
                            font_size="0.875rem",
                            color=Color.TEXT_PRIMARY
                        ),
                        rx.button(
                            rx.icon(tag="chevron-right", size=16),
                            variant="ghost",
                            size="1",
                            on_click=ReportsState.next_page,
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    margin_top=Spacing.MD,
                ),
                rx.fragment(),
            ),

            width="100%",
            spacing="0",
        ),
        width="100%",
        on_mount=AnalysisState.load_saved_analyses,
    )
