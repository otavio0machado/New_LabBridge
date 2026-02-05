"""
Chart components for Biodiagnóstico App
"""
import reflex as rx
from ..state import State
from ..styles import Color, Design, Spacing, TextSize


def divergences_chart() -> rx.Component:
    """Gráfico de divergências (placeholder - usar plotly ou recharts)"""
    return rx.cond(
        State.divergences_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("📊", font_size=TextSize.H3),
                    rx.text(
                        "Visualização de Divergências",
                        color=Color.DEEP,
                        font_weight="700",
                        font_size=TextSize.BODY_LARGE
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.text(
                    "Gráfico interativo das principais divergências",
                    color=Color.TEXT_SECONDARY
                ),
                # Placeholder para gráfico - pode usar rx.recharts ou plotly
                rx.box(
                    rx.center(
                        rx.vstack(
                            rx.text("📈", font_size="3rem", color=Color.BORDER),
                            rx.text(
                                "Gráfico de barras das divergências",
                                color=Color.TEXT_MUTED
                            ),
                            spacing="2",
                        ),
                        height="16rem"
                    ),
                    bg=Color.BACKGROUND,
                    border_radius=Design.RADIUS_LG,
                    border=f"2px dashed {Color.BORDER}"
                ),
                spacing="4",
                width="100%",
            ),
            bg=Color.SURFACE,
            padding=Spacing.LG,
            border_radius=Design.RADIUS_XL,
            box_shadow=Design.SHADOW_LG,
            border=f"1px solid {Color.SUCCESS_BG}",
            margin_top=Spacing.LG
        ),
    )


def summary_pie_chart() -> rx.Component:
    """Gráfico de pizza do breakdown"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("🥧", font_size=TextSize.H3),
                    rx.text(
                        "Composição da Diferença",
                        color=Color.DEEP,
                        font_weight="700",
                        font_size=TextSize.BODY_LARGE
                    ),
                    spacing="3",
                    align="center",
                ),
                # Barras horizontais simples como alternativa
                rx.vstack(
                    # Pacientes faltantes
                    rx.box(
                        rx.hstack(
                            rx.text(
                                "Pacientes somente COMPULAB",
                                font_size=TextSize.SMALL,
                                color=Color.TEXT_SECONDARY,
                                width="10rem"
                            ),
                            rx.box(
                                height="1.5rem",
                                bg=Color.SUCCESS,
                                border_radius="0 9999px 9999px 0",
                                transition="all 0.3s ease",
                                width="33%",
                            ),
                            rx.text(
                                State.formatted_patients_only_compulab_total,
                                font_size=TextSize.SMALL,
                                color=Color.TEXT_PRIMARY,
                                margin_left=Spacing.SM,
                                width="8rem"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    # Exames faltantes
                    rx.box(
                        rx.hstack(
                            rx.text(
                                "Exames somente COMPULAB",
                                font_size=TextSize.SMALL,
                                color=Color.TEXT_SECONDARY,
                                width="10rem"
                            ),
                            rx.box(
                                height="1.5rem",
                                bg=Color.WARNING,
                                border_radius="0 9999px 9999px 0",
                                transition="all 0.3s ease",
                                width="33%",
                            ),
                            rx.text(
                                State.formatted_exams_only_compulab_total,
                                font_size=TextSize.SMALL,
                                color=Color.TEXT_PRIMARY,
                                margin_left=Spacing.SM,
                                width="8rem"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    # Divergências
                    rx.box(
                        rx.hstack(
                            rx.text(
                                "Divergências",
                                font_size=TextSize.SMALL,
                                color=Color.TEXT_SECONDARY,
                                width="10rem"
                            ),
                            rx.box(
                                height="1.5rem",
                                bg=Color.WARNING_HOVER,
                                border_radius="0 9999px 9999px 0",
                                transition="all 0.3s ease",
                                width="33%",
                            ),
                            rx.text(
                                State.formatted_divergences_total,
                                font_size=TextSize.SMALL,
                                color=Color.TEXT_PRIMARY,
                                margin_left=Spacing.SM,
                                width="8rem"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                    bg=Color.BACKGROUND,
                    padding=Spacing.MD,
                    border_radius=Design.RADIUS_LG
                ),
                spacing="4",
                width="100%",
            ),
            bg=Color.SURFACE,
            padding=Spacing.LG,
            border_radius=Design.RADIUS_XL,
            box_shadow=Design.SHADOW_LG,
            border=f"1px solid {Color.SUCCESS_BG}",
            margin_top=Spacing.LG
        ),
    )
