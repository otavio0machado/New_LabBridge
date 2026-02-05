"""
Componentes de UI para Análise Profunda (Deep Analysis)
"""
import reflex as rx
from ...styles import Color, Design, Spacing


def analysis_status_banner(status: rx.Var, executive_summary: rx.Var) -> rx.Component:
    """Banner de status da análise"""
    
    return rx.cond(
        status == "critical",
        rx.box(
            rx.hstack(
                rx.icon("circle-alert", color=Color.ERROR, size=24),
                rx.text(
                    "Atenção: Diferenças Significativas Detectadas",
                    font_weight="700",
                    color=Color.ERROR_DARK,
                    font_size="1rem"
                ),
                spacing="4",
                align_items="center",
                width="100%"
            ),
            bg=Color.ERROR_BG,
            border=f"1px solid {Color.ERROR_LIGHT}",
            border_radius=Design.RADIUS_LG,
            padding=Spacing.MD,
            margin_bottom=Spacing.LG,
            width="100%"
        ),
        rx.cond(
            status == "warning",
            rx.box(
                rx.hstack(
                    rx.icon("triangle-alert", color=Color.WARNING_HOVER, size=24),
                    rx.text(
                        "Alerta: Revisão Recomendada",
                        font_weight="700",
                        color=Color.WARNING_DARK,
                        font_size="1rem"
                    ),
                    spacing="4",
                    align_items="center",
                    width="100%"
                ),
                bg=Color.WARNING_BG,
                border=f"1px solid {Color.WARNING_LIGHT}",
                border_radius=Design.RADIUS_LG,
                padding=Spacing.MD,
                margin_bottom=Spacing.LG,
                width="100%"
            ),
            rx.cond(
                status == "ok",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-check", color=Color.SUCCESS, size=24),
                        rx.text(
                            "Análise Concluída: Diferenças Explicadas",
                            font_weight="700",
                            color=Color.SUCCESS_DARK,
                            font_size="1rem"
                        ),
                        spacing="4",
                        align_items="center",
                        width="100%"
                    ),
                    bg=Color.SUCCESS_BG,
                    border=f"1px solid {Color.SUCCESS_LIGHT}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                    margin_bottom=Spacing.LG,
                    width="100%"
                ),
                rx.box()
            )
        )
    )


def extra_patients_badge(count: rx.Var, value: rx.Var) -> rx.Component:
    """Badge indicando pacientes extras encontrados no COMPULAB"""
    
    return rx.cond(
        count > 0,
        rx.box(
            rx.hstack(
                rx.icon("users", color=Color.PRIMARY, size=20),
                rx.vstack(
                    rx.hstack(
                        rx.text(count, font_weight="700", color=Color.PRIMARY_DARK, font_size="1rem"),
                        rx.text("Paciente(s) Extras no COMPULAB", font_weight="600", color=Color.PRIMARY_DARK, font_size="0.95rem"),
                        spacing="2",
                        align_items="center"
                    ),
                    rx.hstack(
                        rx.text("Valor total:", font_size="0.875rem", color=Color.SECONDARY),
                        rx.text(value, font_size="0.875rem", color=Color.SECONDARY, font_weight="600"),
                        spacing="1",
                        align_items="center"
                    ),
                    spacing="0",
                    align_items="start"
                ),
                spacing="3",
                align_items="center"
            ),
            bg=Color.PRIMARY_LIGHT,
            border=f"1px solid {Color.PRIMARY_BORDER}",
            border_radius=Design.RADIUS_LG,
            padding=Spacing.MD,
            width="100%"
        ),
        rx.box()
    )


def repeated_exams_alert(count: rx.Var, value: rx.Var) -> rx.Component:
    """Alerta destacando exames repetidos encontrados"""
    
    return rx.cond(
        count > 0,
        rx.box(
            rx.hstack(
                rx.icon("copy-x", color=Color.ERROR, size=20),
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.text(count, font_weight="700", color=Color.ERROR_DARK, font_size="1rem"),
                            rx.text("Exame(s) Repetido(s)", font_weight="600", color=Color.ERROR_DARK, font_size="0.95rem"),
                            spacing="2",
                            align_items="center"
                        ),
                        rx.badge("REVISAR", color_scheme="red", size="1", variant="soft"),
                        spacing="2",
                        align_items="center"
                    ),
                    rx.hstack(
                        rx.text("Possível duplicidade:", font_size="0.875rem", color=Color.ERROR),
                        rx.text(value, font_size="0.875rem", color=Color.ERROR, font_weight="600"),
                        spacing="1",
                        align_items="center"
                    ),
                    spacing="0",
                    align_items="start"
                ),
                spacing="3",
                align_items="center"
            ),
            bg=Color.ERROR_BG,
            border=f"1px solid {Color.ERROR_LIGHT}",
            border_radius=Design.RADIUS_LG,
            padding=Spacing.MD,
            width="100%"
        ),
        rx.box(
            rx.hstack(
                rx.icon("circle-check", color=Color.SUCCESS, size=20),
                rx.text("Nenhum exame repetido detectado", font_weight="500", color=Color.SUCCESS_DARK, font_size="0.95rem"),
                spacing="3",
                align_items="center"
            ),
            bg=Color.SUCCESS_BG,
            border=f"1px solid {Color.SUCCESS_LIGHT}",
            border_radius=Design.RADIUS_LG,
            padding=Spacing.MD,
            width="100%"
        )
    )


def executive_summary_card(summary: rx.Var) -> rx.Component:
    """Card de resumo executivo com métricas principais"""
    
    return rx.cond(
        summary != None,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("file-text", color=Color.SUCCESS, size=22),
                    rx.text("Resumo Executivo", font_weight="700", color=Color.SUCCESS_DARK, font_size="1.1rem"),
                    rx.spacer(),
                    rx.badge("Análise Completa", color_scheme="green", size="2"),
                    width="100%",
                    spacing="3",
                    align_items="center",
                    padding_bottom=Spacing.SM,
                    border_bottom=f"1px solid {Color.BORDER}"
                ),
                rx.text(
                    "Análise comparativa entre COMPULAB e SIMUS concluída. "
                    "Verifique os detalhes abaixo para identificar divergências.",
                    font_size="0.9rem",
                    color=Color.TEXT_SECONDARY
                ),
                spacing="4",
                width="100%",
                align_items="start"
            ),
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_XL,
            padding=Spacing.LG,
            margin_bottom=Spacing.XL,
            width="100%",
            box_shadow=Design.SHADOW_DEFAULT
        ),
        rx.box()
    )


def difference_breakdown_panel(
    breakdown: rx.Var,
    extra_patients_formatted: rx.Var,
    repeated_exams_formatted: rx.Var,
    residual_formatted: rx.Var
) -> rx.Component:
    """Painel mostrando a explicação passo a passo da diferença"""
    
    return rx.cond(
        breakdown != None,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("calculator", color=Color.SUCCESS, size=22),
                    rx.text("Explicação da Diferença", font_weight="700", color=Color.SUCCESS_DARK, font_size="1.1rem"),
                    rx.spacer(),
                    rx.badge("Detalhado", color_scheme="blue", size="2"),
                    width="100%",
                    spacing="3",
                    align_items="center",
                    padding_bottom=Spacing.SM,
                    border_bottom=f"1px solid {Color.BORDER}"
                ),

                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Pacientes Extras", font_size="0.8rem", color=Color.TEXT_SECONDARY),
                            rx.text(extra_patients_formatted, font_size="1rem", font_weight="600", color=Color.PRIMARY_DARK),
                            spacing="1",
                            align_items="start"
                        ),
                        padding=Spacing.MD,
                        bg=Color.PRIMARY_LIGHT,
                        border=f"1px solid {Color.PRIMARY_BORDER}",
                        border_radius=Design.RADIUS_LG,
                        width="100%"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Exames Repetidos", font_size="0.8rem", color=Color.TEXT_SECONDARY),
                            rx.text(repeated_exams_formatted, font_size="1rem", font_weight="600", color=Color.ERROR_DARK),
                            spacing="1",
                            align_items="start"
                        ),
                        padding=Spacing.MD,
                        bg=Color.ERROR_BG,
                        border=f"1px solid {Color.ERROR_LIGHT}",
                        border_radius=Design.RADIUS_LG,
                        width="100%"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Diferença Não Explicada", font_size="0.8rem", color=Color.TEXT_SECONDARY),
                            rx.text(residual_formatted, font_size="1rem", font_weight="600", color=Color.WARNING_HOVER),
                            spacing="1",
                            align_items="start"
                        ),
                        padding=Spacing.MD,
                        bg=Color.WARNING_BG,
                        border=f"1px solid {Color.WARNING_LIGHT}",
                        border_radius=Design.RADIUS_LG,
                        width="100%"
                    ),
                    columns={"initial": "1", "md": "3"},
                    spacing="4",
                    width="100%"
                ),

                rx.box(
                    rx.hstack(
                        rx.icon("info", color=Color.SUCCESS, size=16),
                        rx.text(
                            "A análise considera pacientes extras no COMPULAB, "
                            "exames repetidos e divergências de valores.",
                            font_size="0.85rem",
                            color=Color.TEXT_PRIMARY,
                            font_style="italic"
                        ),
                        spacing="2",
                        align_items="start"
                    ),
                    padding=Spacing.SM,
                    bg=Color.PRIMARY_LIGHT,
                    border_radius=Design.RADIUS_LG,
                    border=f"1px solid {Color.PRIMARY_BORDER}",
                    width="100%"
                ),

                spacing="4",
                width="100%",
                align_items="start"
            ),
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_XL,
            padding=Spacing.LG,
            margin_bottom=Spacing.XL,
            width="100%",
            box_shadow=Design.SHADOW_DEFAULT
        ),
        rx.box()
    )
