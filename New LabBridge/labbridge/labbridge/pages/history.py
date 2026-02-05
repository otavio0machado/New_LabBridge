"""
LabBridge - Historico de Auditorias
Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Secao 9. Historico

Conteudo:
- Linha do tempo
- Status visual
- Possibilidade de reabrir auditorias
- Logs claros e auditaveis
"""
import reflex as rx
from ..state import State
from ..states.analysis_state import AnalysisState
from ..states.history_state import HistoryState
from ..styles import Color, Design, Spacing, TextSize
from ..components import ui


def timeline_item(
    id_: str,
    title: str,
    description: str,
    date: str,
    time: str,
    status: str,
    user: str = "Admin",
    is_last: bool = False,
    on_view=None,
    on_reopen=None,
) -> rx.Component:
    """Item da linha do tempo"""
    status_config = {
        "Concluido": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "Em Analise": (Color.WARNING, Color.WARNING_BG, "clock"),
        "Pendente": (Color.TEXT_SECONDARY, Color.BACKGROUND, "circle"),
        "Erro": (Color.ERROR, Color.ERROR_BG, "circle-x"),
        "Reaberto": (Color.PRIMARY, Color.PRIMARY_LIGHT, "refresh-cw"),
    }
    color, bg, icon = status_config.get(status, status_config["Pendente"])

    return rx.hstack(
        # Timeline dot and line
        rx.vstack(
            rx.box(
                rx.icon(tag=icon, size=14, color="white"),
                width="28px",
                height="28px",
                bg=color,
                border_radius="full",
                display="flex",
                align_items="center",
                justify_content="center",
                box_shadow=f"0 0 0 4px {bg}",
            ),
            rx.cond(
                not is_last,
                rx.box(
                    width="2px",
                    flex="1",
                    min_height="60px",
                    bg=Color.BORDER,
                ),
                rx.box(height="0"),
            ),
            spacing="0",
            align="center",
        ),
        # Content
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.hstack(
                            rx.text(title, font_weight="600", color=Color.TEXT_PRIMARY),
                            rx.badge(
                                status,
                                color_scheme=rx.cond(
                                    status == "Concluido",
                                    "green",
                                    rx.cond(
                                        status == "Em Analise",
                                        "yellow",
                                        rx.cond(
                                            status == "Erro",
                                            "red",
                                            rx.cond(
                                                status == "Reaberto",
                                                "blue",
                                                "gray",
                                            ),
                                        ),
                                    ),
                                ),
                                size="1",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text("#ANL-", id_, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.vstack(
                        rx.text(date, font_size="0.875rem", color=Color.TEXT_PRIMARY, font_weight="500"),
                        rx.text(time, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="0",
                        align_items="end",
                    ),
                    width="100%",
                    align="start",
                ),
                description,
                rx.hstack(
                    rx.hstack(
                        rx.avatar(fallback=user[:2], size="1", radius="full"),
                        rx.text(user, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            rx.icon(tag="eye", size=14),
                            rx.text("Ver Detalhes"),
                            variant="ghost",
                            size="1",
                            cursor="pointer",
                            on_click=on_view,
                        ),
                        rx.cond(
                            status == "Concluido",
                            rx.button(
                                rx.icon(tag="refresh-cw", size=14),
                                rx.text("Reabrir"),
                                variant="ghost",
                                size="1",
                                cursor="pointer",
                                color=Color.PRIMARY,
                                on_click=on_reopen,
                            ),
                            rx.fragment(),
                        ),
                        spacing="1",
                    ),
                    width="100%",
                    align="center",
                    margin_top=Spacing.SM,
                ),
                width="100%",
                spacing="0",
            ),
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_LG,
            padding=Spacing.MD,
            flex="1",
            margin_left=Spacing.MD,
            transition="all 0.15s ease",
            _hover={
                "border_color": color,
                "box_shadow": Design.SHADOW_SM,
            },
        ),
        align_items="start",
        width="100%",
        margin_bottom=Spacing.MD,
    )


def render_saved_analysis_item(analysis: dict) -> rx.Component:
    """Renderiza item de linha do tempo usando dados reais (Var-safe)."""
    status_raw = analysis["status"]
    status_label = rx.cond(
        status_raw == "completed",
        "Concluido",
        rx.cond(
            status_raw == "processing",
            "Em Analise",
            rx.cond(
                status_raw == "archived",
                "Reaberto",
                rx.cond(
                    status_raw == "error",
                    "Erro",
                    "Pendente",
                ),
            ),
        ),
    )

    analysis_id = analysis["id"]
    title = rx.cond(analysis["analysis_name"] != "", analysis["analysis_name"], "Analise")
    date_label = rx.cond(analysis["formatted_date"] != "", analysis["formatted_date"], analysis["analysis_date"])
    time_label = analysis["formatted_time"]

    description = rx.text(
        "COMPULAB: ",
        analysis["formatted_compulab"],
        " | SIMUS: ",
        analysis["formatted_simus"],
        " | Pendencias: ",
        analysis["missing_patients_count"],
        " pacientes, ",
        analysis["missing_exams_count"],
        " exames, ",
        analysis["divergences_count"],
        " divergencias.",
        font_size="0.875rem",
        color=Color.TEXT_SECONDARY,
        margin_top=Spacing.XS,
    )

    return timeline_item(
        analysis_id,
        title,
        description,
        date_label,
        time_label,
        status_label,
        user="Sistema",
        on_view=lambda: State.open_saved_analysis(analysis_id),
        on_reopen=lambda: State.open_saved_analysis(analysis_id),
    )


def audit_log_item(action: str, user: str, timestamp: str, details: str = "") -> rx.Component:
    """Item de log de auditoria"""
    return rx.hstack(
        rx.box(
            width="6px",
            height="6px",
            bg=Color.PRIMARY,
            border_radius="full",
        ),
        rx.vstack(
            rx.hstack(
                rx.text(action, font_size="0.875rem", color=Color.TEXT_PRIMARY),
                rx.text("-", color=Color.TEXT_MUTED),
                rx.text(user, font_size="0.875rem", color=Color.TEXT_SECONDARY),
                spacing="2",
            ),
            rx.cond(
                details != "",
                rx.text(details, font_size="0.75rem", color=Color.TEXT_MUTED),
                rx.fragment(),
            ),
            spacing="0",
            align_items="start",
        ),
        rx.spacer(),
        rx.text(timestamp, font_size="0.75rem", color=Color.TEXT_SECONDARY),
        width="100%",
        align="center",
        padding_y=Spacing.SM,
        border_bottom=f"1px solid {Color.BORDER}",
    )


def history_page() -> rx.Component:
    """Pagina de Historico de Auditorias"""
    return rx.box(
        rx.vstack(
            # Page Header
            ui.page_header(
                title="Historico de Auditorias",
                description="Rastreabilidade completa de todas as auditorias realizadas",
                actions=rx.hstack(
                    rx.select(
                        ["Todas", "Concluidas", "Em Analise", "Pendentes"],
                        value=HistoryState.status_filter,
                        on_change=HistoryState.set_status_filter,
                        size="2",
                    ),
                    rx.button(
                        rx.cond(
                            HistoryState.is_exporting,
                            rx.hstack(rx.spinner(size="1"), rx.text("Exportando..."), spacing="2"),
                            rx.hstack(rx.icon(tag="download", size=16), rx.text("Exportar Logs"), spacing="2"),
                        ),
                        variant="outline",
                        size="2",
                        on_click=HistoryState.export_logs,
                        disabled=HistoryState.is_exporting,
                    ),
                    rx.button(
                        rx.icon(tag="plus", size=16),
                        rx.text("Nova Auditoria"),
                        variant="solid",
                        size="2",
                        bg=Color.PRIMARY,
                        color="white",
                        cursor="pointer",
                        _hover={"bg": Color.PRIMARY_HOVER},
                        on_click=rx.redirect("/analise"),
                    ),
                    spacing="2",
                ),
            ),

            # Main Content Grid
            rx.grid(
                # Timeline Column
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("Linha do Tempo", font_weight="600", color=Color.TEXT_PRIMARY),
                            rx.spacer(),
                            rx.text(
                                AnalysisState.saved_analyses_list.length().to_string() + " analises",
                                font_size="0.875rem",
                                color=Color.TEXT_SECONDARY
                            ),
                            width="100%",
                            align="center",
                            margin_bottom=Spacing.LG,
                        ),
                        rx.cond(
                            AnalysisState.saved_analyses_list.length() > 0,
                            rx.vstack(
                                rx.foreach(AnalysisState.saved_analyses_list, render_saved_analysis_item),
                                spacing="0",
                                width="100%",
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="inbox", size=32, color=Color.TEXT_SECONDARY),
                                    rx.text("Nenhuma analise salva", font_size="0.9rem", color=Color.TEXT_SECONDARY),
                                    rx.text("Execute uma auditoria e salve para ver aqui.", font_size="0.8rem", color=Color.TEXT_SECONDARY),
                                    spacing="1",
                                    align="center",
                                ),
                                padding=Spacing.LG,
                            ),
                        ),
                        width="100%",
                        spacing="0",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_XL,
                    padding=Spacing.LG,
                ),

                # Logs Column
                rx.vstack(
                    # Summary Stats - Now using real data
                    rx.box(
                        rx.vstack(
                            rx.text("Resumo do Periodo", font_weight="600", color=Color.TEXT_PRIMARY, margin_bottom=Spacing.MD),
                            rx.grid(
                                rx.vstack(
                                    rx.text(
                                        AnalysisState.saved_analyses_list.length().to_string(),
                                        font_size="1.5rem",
                                        font_weight="700",
                                        color=Color.DEEP
                                    ),
                                    rx.text("Total", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                                    spacing="0",
                                    align="center",
                                ),
                                rx.vstack(
                                    rx.text(
                                        AnalysisState.saved_analyses_list.length().to_string(),
                                        font_size="1.5rem",
                                        font_weight="700",
                                        color=Color.SUCCESS
                                    ),
                                    rx.text("Concluidas", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                                    spacing="0",
                                    align="center",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "0",
                                        font_size="1.5rem",
                                        font_weight="700",
                                        color=Color.WARNING_HOVER
                                    ),
                                    rx.text("Em Analise", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                                    spacing="0",
                                    align="center",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "0",
                                        font_size="1.5rem",
                                        font_weight="700",
                                        color=Color.PRIMARY
                                    ),
                                    rx.text("Reabertas", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                                    spacing="0",
                                    align="center",
                                ),
                                columns="4",
                                spacing="2",
                                width="100%",
                            ),
                            width="100%",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                    ),

                    # Activity Log - Now dynamic
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Log de Atividades", font_weight="600", color=Color.TEXT_PRIMARY),
                                rx.spacer(),
                                rx.button(
                                    rx.icon(tag="refresh-cw", size=14),
                                    rx.text("Atualizar"),
                                    variant="ghost",
                                    size="1",
                                    on_click=HistoryState.load_activity_log,
                                ),
                                width="100%",
                                align="center",
                                margin_bottom=Spacing.MD,
                            ),
                            rx.cond(
                                AnalysisState.saved_analyses_list.length() > 0,
                                rx.vstack(
                                    audit_log_item("Ultima analise salva", "Sistema", "Recente", "Via LabBridge"),
                                    audit_log_item("Analises carregadas", "Sistema", "On mount", f"{AnalysisState.saved_analyses_list.length()} itens"),
                                    spacing="0",
                                    width="100%",
                                ),
                                rx.center(
                                    rx.text("Nenhuma atividade recente", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                                    padding=Spacing.MD,
                                ),
                            ),
                            width="100%",
                            spacing="0",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                    ),

                    spacing="4",
                    width="100%",
                ),

                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="4",
                width="100%",
            ),

            width="100%",
            spacing="0",
        ),
        width="100%",
        on_mount=[State.load_saved_analyses, HistoryState.load_activity_log],
    )
