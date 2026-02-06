"""
LabBridge - Dashboard
Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Secao 5. Dashboard

Objetivo: Visao rapida do estado financeiro e operacional.
Componentes:
- Cards de KPIs (Receita total, Divergencias, Auditorias concluidas)
- Grafico principal (tendencia)
- Lista de auditorias recentes
- Acoes rapidas (Nova auditoria, Upload de arquivo)
"""
import reflex as rx
from ..state import State
from ..states.analysis_state import AnalysisState
from ..styles import Color, Design, Typography, Spacing
from ..components import ui


def kpi_card(
    label: str,
    value: str,
    icon: str,
    trend: str = None,
    trend_value: str = None,
    color: str = "primary",
) -> rx.Component:
    """Card de KPI com tendencia"""
    color_map = {
        "primary": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "success": (Color.SUCCESS, Color.SUCCESS_BG),
        "warning": (Color.WARNING, Color.WARNING_BG),
        "error": (Color.ERROR, Color.ERROR_BG),
    }
    main_color, bg_color = color_map.get(color, color_map["primary"])

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=24, color=main_color),
                    padding="12px",
                    border_radius=Design.RADIUS_MD,
                    bg=bg_color,
                ),
                rx.spacer(),
                rx.cond(
                    trend is not None,
                    rx.hstack(
                        rx.icon(
                            tag=rx.cond(trend == "up", "trending-up", "trending-down"),
                            size=14,
                            color=rx.cond(trend == "up", Color.SUCCESS, Color.ERROR),
                        ),
                        rx.text(
                            trend_value,
                            font_size="0.75rem",
                            font_weight="600",
                            color=rx.cond(trend == "up", Color.SUCCESS, Color.ERROR),
                        ),
                        spacing="1",
                        align="center",
                        padding="4px 8px",
                        bg=rx.cond(trend == "up", Color.SUCCESS_BG, Color.ERROR_BG),
                        border_radius="full",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(
                    value,
                    font_size=["1.5rem", "1.75rem", "2rem"],
                    font_weight="700",
                    color=Color.DEEP,
                    line_height="1",
                ),
                rx.text(
                    label,
                    font_size="0.875rem",
                    color=Color.TEXT_SECONDARY,
                ),
                spacing="1",
                align_items="start",
            ),
            spacing="4",
            width="100%",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.LG,
        transition="all 0.2s ease",
        _hover={
            "border_color": main_color,
            "box_shadow": Design.SHADOW_MD,
        },
    )


def quick_action_card(
    title: str,
    description: str,
    icon: str,
    page: str,
    color: str = "primary",
) -> rx.Component:
    """Card de acao rapida"""
    color_map = {
        "primary": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "success": (Color.SUCCESS, Color.SUCCESS_BG),
        "warning": (Color.WARNING, Color.WARNING_BG),
    }
    main_color, bg_color = color_map.get(color, color_map["primary"])

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(tag=icon, size=28, color=main_color),
                padding=Spacing.MD,
                border_radius=Design.RADIUS_MD,
                bg=bg_color,
                transition="transform 0.2s ease",
                _group_hover={"transform": "scale(1.1)"},
            ),
            rx.vstack(
                rx.text(title, font_weight="600", color=Color.TEXT_PRIMARY),
                rx.text(description, font_size="0.875rem", color=Color.TEXT_SECONDARY),
                spacing="1",
                align_items="start",
            ),
            spacing="4",
            align="center",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_LG,
        padding=Spacing.LG,
        cursor="pointer",
        transition="all 0.2s ease",
        _hover={
            "border_color": main_color,
            "transform": "translateY(-2px)",
            "box_shadow": Design.SHADOW_MD,
        },
        on_click=State.navigate_to(page),
        class_name="group",
    )


def render_recent_audit_item(analysis: dict) -> rx.Component:
    """Renderiza item de auditoria recente usando dados reais"""
    # Determina status e configuracao visual
    status_raw = analysis["status"]
    status_label = rx.cond(
        status_raw == "completed",
        "Concluida",
        rx.cond(
            status_raw == "processing",
            "Em Analise",
            "Pendente",
        ),
    )

    # Determina cores baseado no status
    status_color = rx.cond(
        status_raw == "completed",
        Color.SUCCESS,
        rx.cond(
            status_raw == "processing",
            Color.WARNING,
            Color.TEXT_SECONDARY,
        ),
    )

    status_bg = rx.cond(
        status_raw == "completed",
        Color.SUCCESS_BG,
        rx.cond(
            status_raw == "processing",
            Color.WARNING_BG,
            Color.BACKGROUND,
        ),
    )

    status_icon = rx.cond(
        status_raw == "completed",
        "circle-check",
        rx.cond(
            status_raw == "processing",
            "clock",
            "circle",
        ),
    )

    analysis_id = analysis["id"]
    name = rx.cond(analysis["analysis_name"] != "", analysis["analysis_name"], "Analise")
    date_label = rx.cond(analysis["formatted_date"] != "", analysis["formatted_date"], analysis["analysis_date"])
    value = "R$ " + analysis["compulab_total"].to(str)

    return rx.hstack(
        rx.hstack(
            rx.box(
                rx.icon(tag=status_icon, size=16, color=status_color),
                padding="8px",
                bg=status_bg,
                border_radius="full",
            ),
            rx.vstack(
                rx.text(name, font_weight="500", color=Color.TEXT_PRIMARY),
                rx.text("#ANL-", analysis_id, " - ", date_label, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        rx.vstack(
            rx.text(value, font_weight="600", color=Color.DEEP),
            rx.badge(
                status_label,
                color_scheme=rx.cond(
                    status_raw == "completed",
                    "green",
                    rx.cond(status_raw == "processing", "yellow", "gray")
                ),
                size="1"
            ),
            spacing="1",
            align_items="end",
        ),
        width="100%",
        padding=Spacing.MD,
        border_radius=Design.RADIUS_MD,
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={"bg": Color.PRIMARY_LIGHT},
        on_click=AnalysisState.open_saved_analysis(analysis_id),
    )


def dashboard_page() -> rx.Component:
    """Dashboard - Visao rapida do estado financeiro e operacional"""

    return rx.box(
        rx.vstack(
            # Page Header
            ui.page_header(
                title="Dashboard",
                description="Visao geral do estado financeiro e operacional",
                actions=rx.hstack(
                    ui.button("Nova Auditoria", icon="plus", on_click=State.navigate_to("analise")),
                    ui.button("Upload", icon="upload", variant="secondary", on_click=State.navigate_to("conversor")),
                    spacing="2",
                ),
            ),

            # === ONBOARDING BANNER (shown when no analyses exist) ===
            rx.cond(
                AnalysisState.saved_analyses_list.length() == 0,
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="rocket", size=32, color="white"),
                            padding="16px",
                            bg=Color.GRADIENT_PRIMARY,
                            border_radius=Design.RADIUS_LG,
                        ),
                        rx.vstack(
                            rx.text("Bem-vindo ao LabBridge!", font_weight="700", font_size="1.15rem", color=Color.DEEP),
                            rx.text(
                                "Comece sua primeira auditoria em 3 passos simples:",
                                color=Color.TEXT_SECONDARY,
                                font_size="0.95rem",
                            ),
                            rx.hstack(
                                rx.hstack(
                                    rx.badge("1", color_scheme="green", variant="solid", size="1"),
                                    rx.text("Importe seus PDFs", font_size="0.875rem", color=Color.TEXT_PRIMARY),
                                    spacing="2", align="center",
                                ),
                                rx.icon(tag="arrow-right", size=14, color=Color.TEXT_MUTED),
                                rx.hstack(
                                    rx.badge("2", color_scheme="green", variant="solid", size="1"),
                                    rx.text("Execute a auditoria cruzada", font_size="0.875rem", color=Color.TEXT_PRIMARY),
                                    spacing="2", align="center",
                                ),
                                rx.icon(tag="arrow-right", size=14, color=Color.TEXT_MUTED),
                                rx.hstack(
                                    rx.badge("3", color_scheme="green", variant="solid", size="1"),
                                    rx.text("Visualize divergencias e exporte", font_size="0.875rem", color=Color.TEXT_PRIMARY),
                                    spacing="2", align="center",
                                ),
                                spacing="3",
                                flex_wrap="wrap",
                                margin_top=Spacing.SM,
                            ),
                            spacing="2",
                            align_items="start",
                            flex="1",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.hstack(
                                rx.icon(tag="play", size=16),
                                rx.text("Iniciar Primeira Auditoria"),
                                spacing="2",
                            ),
                            bg=Color.PRIMARY,
                            color="white",
                            border_radius=Design.RADIUS_MD,
                            size="3",
                            cursor="pointer",
                            _hover={"bg": Color.PRIMARY_HOVER},
                            on_click=State.navigate_to("analise"),
                        ),
                        width="100%",
                        align="center",
                        spacing="4",
                        flex_wrap="wrap",
                    ),
                    bg=Color.SURFACE,
                    border=f"2px solid {Color.PRIMARY}30",
                    border_radius=Design.RADIUS_XL,
                    padding=Spacing.LG,
                    margin_bottom=Spacing.LG,
                    width="100%",
                ),
            ),

            # KPI Cards Grid
            rx.grid(
                kpi_card(
                    label="Receita Total",
                    value=State.formatted_compulab_total,
                    icon="banknote",
                    trend=rx.cond(State.financial_growth_day >= 0, "up", "down"),
                    trend_value=State.financial_growth_day.to(str) + "%",
                    color="primary",
                ),
                kpi_card(
                    label="Divergencias Encontradas",
                    value=State.divergences_count.to(str),
                    icon="triangle-alert",
                    color="warning",
                ),
                kpi_card(
                    label="Auditorias Concluidas",
                    value=State.dashboard_approval_rate.to(str) + "%",
                    icon="circle-check",
                    color="success",
                ),
                kpi_card(
                    label="Pacientes Processados",
                    value=State.total_patients_count.to(str),
                    icon="users",
                    color="primary",
                ),
                columns=rx.breakpoints(initial="1", sm="2", md="2", lg="4"),
                spacing="4",
                width="100%",
            ),

            # Main Content Grid
            rx.grid(
                # Left Column - Chart + Offenders
                rx.vstack(
                    # Revenue Chart Card
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Tendencia de Faturamento", font_weight="600", color=Color.TEXT_PRIMARY),
                                    rx.text("Ultimos 6 meses", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                                    spacing="0",
                                    align_items="start",
                                ),
                                rx.spacer(),
                                rx.hstack(
                                    rx.box(
                                        rx.icon(tag="chart-line", size=20, color=Color.PRIMARY),
                                        padding="8px",
                                        bg=Color.PRIMARY_LIGHT,
                                        border_radius=Design.RADIUS_MD,
                                    ),
                                    spacing="2",
                                ),
                                width="100%",
                                align="center",
                            ),
                            # Revenue Chart - Functional
                            rx.recharts.bar_chart(
                                rx.recharts.bar(
                                    data_key="analises",
                                    fill=Color.PRIMARY,
                                    radius=[4, 4, 0, 0],
                                ),
                                rx.recharts.x_axis(data_key="name"),
                                rx.recharts.y_axis(),
                                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                                rx.recharts.graphing_tooltip(),
                                data=State.monthly_analyses_chart,
                                width="100%",
                                height=200,
                                margin={"top": 10, "right": 10, "left": -10, "bottom": 0},
                            ),
                            # Forecast
                            rx.hstack(
                                rx.hstack(
                                    rx.icon(tag="sparkles", size=16, color=Color.PRIMARY),
                                    rx.text("Previsao proximo mes:", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                                    spacing="2",
                                ),
                                rx.text(State.formatted_revenue_forecast, font_weight="700", color=Color.DEEP),
                                width="100%",
                                justify="between",
                                margin_top=Spacing.MD,
                                padding=Spacing.MD,
                                bg=Color.PRIMARY_LIGHT,
                                border_radius=Design.RADIUS_MD,
                            ),
                            spacing="0",
                            width="100%",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                    ),

                    # Goal Progress
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.hstack(
                                    rx.icon(tag="target", size=18, color=Color.PRIMARY),
                                    rx.text("Meta Mensal", font_weight="600", color=Color.TEXT_PRIMARY),
                                    spacing="2",
                                ),
                                rx.spacer(),
                                rx.text(State.goal_progress.to(str) + "%", font_weight="700", color=Color.PRIMARY),
                                width="100%",
                                align="center",
                            ),
                            # Progress bar
                            rx.box(
                                rx.box(
                                    width=State.goal_progress.to(str) + "%",
                                    height="100%",
                                    bg=Color.GRADIENT_PRIMARY,
                                    border_radius="full",
                                    transition="width 1s ease",
                                ),
                                width="100%",
                                height="12px",
                                bg=Color.BACKGROUND,
                                border_radius="full",
                                overflow="hidden",
                            ),
                            rx.hstack(
                                rx.text(State.formatted_compulab_total, font_size="0.875rem", color=Color.TEXT_SECONDARY),
                                rx.spacer(),
                                rx.text("Meta: " + State.formatted_monthly_goal, font_size="0.875rem", color=Color.TEXT_SECONDARY),
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                    ),

                    spacing="4",
                    width="100%",
                ),

                # Right Column - Recent Audits + Quick Actions
                rx.vstack(
                    # Recent Audits - Now using real data
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Auditorias Recentes", font_weight="600", color=Color.TEXT_PRIMARY),
                                rx.spacer(),
                                rx.link(
                                    rx.text("Ver todas", font_size="0.875rem", color=Color.PRIMARY),
                                    href="/history",
                                ),
                                width="100%",
                                align="center",
                            ),
                            rx.divider(color=Color.BORDER, margin_y=Spacing.SM),
                            rx.cond(
                                AnalysisState.saved_analyses_list.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        AnalysisState.saved_analyses_list[:3],  # Limita a 3 itens
                                        render_recent_audit_item,
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.icon(tag="inbox", size=32, color=Color.TEXT_MUTED),
                                        rx.text("Nenhuma auditoria recente", color=Color.TEXT_SECONDARY),
                                        rx.text("Execute uma analise para ver aqui", font_size="0.8rem", color=Color.TEXT_MUTED),
                                        spacing="2",
                                        align="center",
                                    ),
                                    padding=Spacing.XL,
                                ),
                            ),
                            spacing="0",
                            width="100%",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                    ),

                    # Quick Actions
                    rx.box(
                        rx.vstack(
                            rx.text("Acoes Rapidas", font_weight="600", color=Color.TEXT_PRIMARY, margin_bottom=Spacing.SM),
                            quick_action_card(
                                "Nova Auditoria",
                                "Iniciar analise cruzada de dados",
                                "file-search",
                                "analise",
                                "primary",
                            ),
                            quick_action_card(
                                "Upload de Arquivo",
                                "Importar relatorios PDF",
                                "upload",
                                "conversor",
                                "success",
                            ),
                            quick_action_card(
                                "Ver Relatorios",
                                "Exportar e visualizar dados",
                                "file-bar-chart",
                                "reports",
                                "warning",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                    ),

                    spacing="4",
                    width="100%",
                ),

                columns=rx.breakpoints(initial="1", md="2"),
                spacing="4",
                width="100%",
                margin_top=Spacing.LG,
            ),

            width="100%",
            spacing="0",
        ),
        width="100%",
        on_mount=AnalysisState.load_saved_analyses,
    )
