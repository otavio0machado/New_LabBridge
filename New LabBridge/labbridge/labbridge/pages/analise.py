"""
Análise COMPULAB x SIMUS page
Design moderno com upload aprimorado e visualização de dados premium
"""
import reflex as rx
from typing import Any
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator
from ..components.save_analysis_modal import save_analysis_modal, saved_analyses_list
from ..components.analysis.widgets import metric_card_premium, insight_card, patient_history_modal, action_table
from ..components.analysis.deep_analysis import (
    executive_summary_card,
    difference_breakdown_panel,
    repeated_exams_alert,
    extra_patients_badge,
    analysis_status_banner
)
from ..components.analysis.exam_link_modal import exam_link_modal
from ..components import ui
from ..styles import Color, Design, Spacing

def analise_page() -> rx.Component:
    """Página de Análise Premium"""

    # SVG compacto do Erlenmeyer (Purificado)
    erlenmeyer_small = f"""
        <svg viewBox="0 0 50 60" width="36" height="44">
            <path d="M18 8 L32 8 L32 22 L42 50 Q43 54 39 56 L11 56 Q7 54 8 50 L18 22 Z" 
                  fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <circle cx="25" cy="42" r="6" fill="{Color.SUCCESS}" opacity="0.3"/>
        </svg>
    """

    # SVG compacto dos Tubos (Purificado)
    tubes_small = f"""
        <svg viewBox="0 0 60 60" width="36" height="44">
            <rect x="12" y="10" width="10" height="40" rx="5" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="25" y="10" width="10" height="40" rx="5" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="38" y="10" width="10" height="40" rx="5" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="12" y="28" width="10" height="22" rx="5" fill="{Color.SUCCESS}" opacity="0.3"/>
            <rect x="25" y="24" width="10" height="26" rx="5" fill="{Color.SUCCESS}" opacity="0.3"/>
            <rect x="38" y="32" width="10" height="18" rx="5" fill="{Color.SUCCESS}" opacity="0.3"/>
        </svg>
    """

    return rx.box(
        rx.vstack(
            ui.page_header(
                title="Auditoria Financeira",
                description="Sincronização em tempo real entre COMPULAB e SIMUS. Detecte divergências com precisão cirúrgica.",
            ),

            # === HISTORICO DE ARQUIVOS ===
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("Histórico de Arquivos", font_weight="600", color=Color.TEXT_PRIMARY),
                        rx.spacer(),
                        rx.text("Acesso rápido", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                        width="100%",
                        align="center",
                    ),
                    rx.accordion.root(
                        rx.accordion.item(
                            header=rx.text("Arquivos Salvos", font_weight="600", color=Color.DEEP),
                            content=saved_analyses_list(),
                        ),
                        collapsible=True,
                        variant="ghost",
                    ),
                    spacing="3",
                    width="100%",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.LG,
                margin_bottom=Spacing.LG,
            ),

            # === UPLOAD AREA ===
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("cloud-upload", color=Color.PRIMARY, size=24),
                        rx.text("Upload de Relatórios", weight="bold", color=Color.DEEP, size="4"),
                        spacing="3",
                        align_items="center",
                        width="100%",
                        justify_content="center",
                        margin_bottom=Spacing.MD,
                    ),
                    rx.grid(
                        compact_upload_card("COMPULAB", erlenmeyer_small, "compulab_anl", State.compulab_file_name, State.compulab_file_size, State.handle_compulab_upload, State.clear_compulab_file, "COMPLETO"),
                        compact_upload_card("SIMUS", tubes_small, "simus_anl", State.simus_file_name, State.simus_file_size, State.handle_simus_upload, State.clear_simus_file, "COMPLETO"),
                        columns="2",
                        spacing="6",
                        width="100%",
                    ),
                    upload_progress_indicator(State.is_uploading),
                    rx.cond(
                        State.is_analyzing,
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.spinner(size="2", color=Color.PRIMARY),
                                    rx.text(State.analysis_stage, font_weight="600", color=Color.DEEP),
                                    rx.spacer(),
                                    rx.text(f"{State.analysis_progress_percentage}%", font_weight="700", color=Color.PRIMARY),
                                    width="100%",
                                    align_items="center",
                                ),
                                rx.box(
                                    rx.box(
                                        bg=Color.GRADIENT_PRIMARY,
                                        border_radius="full",
                                        transition="width 0.3s ease",
                                        width=rx.cond(State.analysis_progress_percentage > 0, f"{State.analysis_progress_percentage}%", "0%"),
                                        height="100%",
                                        position="relative",
                                        overflow="hidden",
                                        _after={
                                            "content": '""',
                                            "position": "absolute",
                                            "top": "0",
                                            "left": "0",
                                            "right": "0",
                                            "bottom": "0",
                                            "background": "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
                                            "animation": "shimmer 1.5s infinite",
                                        },
                                    ),
                                    width="100%",
                                    height="8px",
                                    bg=Color.BACKGROUND,
                                    border_radius="full",
                                    overflow="hidden",
                                ),
                                spacing="2",
                                width="100%",
                                align_items="center",
                            ),
                            bg=Color.PRIMARY_LIGHT,
                            border=f"1px solid {Color.PRIMARY}30",
                            border_radius=Design.RADIUS_LG,
                            padding=Spacing.MD,
                            margin_top=Spacing.LG,
                            width="100%",
                            max_width="600px",
                            margin_x="auto",
                        ),
                    ),

                    rx.cond(
                        ~State.is_analyzing,
                        ui.button("Iniciar Auditoria Cruzada", icon="zap", on_click=State.run_analysis, disabled=~State.has_files, width="100%", variant="primary", size="4", margin_top=Spacing.LG, padding="24px"),
                        ui.button("Processando Inteligência de Dados...", icon="loader-circle", is_loading=True, width="100%", variant="primary", margin_top=Spacing.LG, padding="24px"),
                    ),

                    padding=Spacing.LG,
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                width="100%",
                margin_bottom=Spacing.LG,
            ),

            # === EXAM LINKING CTA ===
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.text("Vincular Exames", weight="bold", color=Color.DEEP, size="4"),
                        rx.text(
                            "Cadastre equivalências SIMUS -> COMPULAB para reduzir pendências.",
                            color=Color.TEXT_SECONDARY,
                            font_size="0.95rem",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    exam_link_modal(),
                    align_items="center",
                    width="100%",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                padding=Spacing.LG,
                border_radius=Design.RADIUS_XL,
                width="100%",
                margin_bottom=Spacing.LG,
            ),

            # === RESULTS SECTION ===
            rx.cond(
                State.has_analysis,
                rx.vstack(
                    # === ACTION BAR (sempre visível quando há análise) ===
                    rx.box(
                        rx.hstack(
                            rx.hstack(
                                rx.icon("circle-check", color=Color.SUCCESS, size=20),
                                rx.text("Auditoria concluída", weight="bold", color=Color.SUCCESS),
                                # Badge de Histórico quando é análise reaberta
                                rx.cond(
                                    State.is_from_history,
                                    rx.badge(
                                        rx.hstack(
                                            rx.icon("history", size=12),
                                            rx.text("Historico"),
                                            spacing="1",
                                            align="center",
                                        ),
                                        color_scheme="blue",
                                        size="1",
                                        variant="soft",
                                    ),
                                    rx.fragment(),
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.hstack(
                                # Botao Nova Analise (quando reaberta do historico)
                                rx.cond(
                                    State.is_from_history,
                                    ui.button(
                                        "Nova Analise",
                                        icon="plus",
                                        variant="outline",
                                        on_click=State.clear_analysis_for_new,
                                    ),
                                    rx.fragment(),
                                ),
                                save_analysis_modal(),
                                ui.button(
                                    "Exportar CSV",
                                    icon="table",
                                    variant="secondary",
                                    on_click=State.export_analysis_csv,
                                ),
                                ui.button(
                                    "Gerar PDF",
                                    icon="file-text",
                                    variant="secondary",
                                    on_click=State.generate_pdf_report,
                                ),
                                spacing="3",
                            ),
                            width="100%",
                            align="center",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_LG,
                        padding=Spacing.MD,
                        margin_bottom=Spacing.LG,
                        width="100%",
                    ),

                    rx.flex(
                        # === LEFT PANEL ===
                        rx.vstack(
                            # Status Banner
                            analysis_status_banner(State.analysis_status, State.executive_summary),

                        # KPI Grid
                        rx.grid(
                            metric_card_premium("Faturamento Compulab", State.formatted_compulab_total, "building-2", color_scheme="blue", delay="0.1s"),
                            metric_card_premium("Faturamento Simus", State.formatted_simus_total, "database", color_scheme="green", delay="0.2s"),
                            metric_card_premium("Diferença Total", State.formatted_difference, "git-compare", "Alerta", "orange", delay="0.3s"),
                            metric_card_premium("Itens Pendentes", State.pending_items_count, "list-x", "Ação Necessária", "red", delay="0.4s"),
                            columns={"initial": "1", "md": "2", "xl": "2"},
                            spacing="5",
                            width="100%",
                            margin_bottom="32px",
                        ),

                        # Deep Analysis Alerts Row
                        rx.grid(
                            extra_patients_badge(State.extra_patients_count, State.extra_patients_value),
                            repeated_exams_alert(State.repeated_exams_count, State.repeated_exams_value),
                            columns={"initial": "1", "md": "2"},
                            spacing="4",
                            width="100%",
                            margin_bottom="32px",
                        ),

                        # Executive Summary Card
                        executive_summary_card(State.executive_summary),

                        # Difference Breakdown Panel
                        difference_breakdown_panel(
                            State.difference_breakdown,
                            State.extra_patients_formatted,
                            State.repeated_exams_formatted,
                            State.residual_formatted,
                        ),

                        # Charts & Insights
                        rx.grid(
                            # Chart Card
                            rx.vstack(
                                rx.text("Distribuição de Perdas", weight="bold", color=Color.DEEP, margin_bottom="12px"),
                                rx.recharts.pie_chart(
                                    rx.recharts.pie(
                                        data=State.revenue_distribution_data,
                                        data_key="value",
                                        name_key="name",
                                        cx="50%",
                                        cy="50%",
                                        inner_radius=70,
                                        outer_radius=90,
                                        padding_angle=2,
                                        stroke="none",
                                        label=True,
                                    ),
                                    rx.recharts.legend(),
                                    height=300,
                                    width="100%",
                                ),
                                bg="rgba(255,255,255,0.7)",
                                p="8",
                                border_radius=Design.RADIUS_XL,
                                border=f"1px solid {Color.BORDER}",
                                width="100%",
                            ),
                            # Insights List
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("lightbulb", color=Color.WARNING, size=20),
                                    rx.text("Insights & Ações", weight="bold", color=Color.DEEP),
                                    align_items="center",
                                    spacing="3",
                                    margin_bottom="16px",
                                ),
                                rx.vstack(
                                    rx.foreach(
                                        State.action_center_insights,
                                        lambda x: insight_card(x["icon"], x["title"], x["description"], "warning"),
                                    ),
                                    spacing="4",
                                    width="100%",
                                ),
                                bg="rgba(255,255,255,0.7)",
                                p="8",
                                border_radius=Design.RADIUS_XL,
                                border=f"1px solid {Color.BORDER}",
                                width="100%",
                            ),
                            columns={"initial": "1", "xl": "2"},
                            spacing="6",
                            width="100%",
                            margin_bottom="48px",
                        ),

                        # Data Controls
                        rx.box(
                            ui.segmented_control(
                                [
                                    {"label": "Pacientes somente COMPULAB", "value": "patients_only_compulab"},
                                    {"label": "Pacientes somente SIMUS", "value": "patients_only_simus"},
                                    {"label": "Exames somente COMPULAB", "value": "exams_only_compulab"},
                                    {"label": "Exames somente SIMUS", "value": "exams_only_simus"},
                                    {"label": "Diferença de Valores", "value": "value_diffs"},
                                ],
                                State.analysis_active_tab,
                                State.set_analysis_active_tab,
                            ),
                            margin_bottom="32px",
                            width="100%",
                        ),

                        # Tab Content
                        rx.box(
                            rx.cond(
                                State.analysis_active_tab == "patients_only_compulab",
                                action_table(["Paciente", "Qtd Exames", "Valor Total"], State.patients_only_compulab, ["patient", "exams_count", "total_value"], patient_key="patient", error_options=State.ERROR_TYPES_PATIENTS_COMPULAB),
                            ),
                            rx.cond(
                                State.analysis_active_tab == "patients_only_simus",
                                action_table(["Paciente", "Qtd Exames", "Valor Total"], State.patients_only_simus, ["patient", "exams_count", "total_value"], patient_key="patient", error_options=State.ERROR_TYPES_PATIENTS_SIMUS),
                            ),
                            rx.cond(
                                State.analysis_active_tab == "exams_only_compulab",
                                action_table(["Paciente", "Exame", "Valor Compulab"], State.exams_only_compulab, ["patient", "exam_name", "compulab_value"], error_options=State.ERROR_TYPES_EXAMS_COMPULAB),
                            ),
                            rx.cond(
                                State.analysis_active_tab == "exams_only_simus",
                                action_table(["Paciente", "Exame", "Valor Simus"], State.exams_only_simus, ["patient", "exam_name", "simus_value"], error_options=State.ERROR_TYPES_EXAMS_SIMUS),
                            ),
                            rx.cond(
                                State.analysis_active_tab == "value_diffs",
                                action_table(["Paciente", "Exame", "Compulab", "Simus", "Diferença"], State.value_divergences, ["patient", "exam_name", "compulab_value", "simus_value", "difference"], is_divergence=True, error_options=State.ERROR_TYPES_VALUE_DIFFS),
                            ),
                            width="100%",
                        ),

                        flex="1",
                        min_width="0",
                        animation="fadeInUp 0.8s ease-out 0.2s both",
                        padding_right={"initial": "0", "lg": Spacing.LG},
                        margin_bottom={"initial": "32px", "lg": "0"},
                    ),

                    # === RIGHT PANEL (Export Actions) ===
                    rx.cond(
                        State.has_analysis,
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("file-check", color=Color.PRIMARY, size=24),
                                    rx.text("Exportar Relatório", weight="bold", color=Color.DEEP, size="4"),
                                    width="100%",
                                    align_items="center",
                                    padding_bottom="16px",
                                    border_bottom=f"1px solid {Color.BORDER}",
                                ),
                                rx.vstack(
                                    # Status do PDF
                                    rx.cond(
                                        State.pdf_url != "",
                                        rx.hstack(
                                            rx.icon("circle-check", size=16, color=Color.SUCCESS),
                                            rx.text("PDF gerado com sucesso!", font_size="0.875rem", color=Color.SUCCESS),
                                            spacing="2",
                                        ),
                                        rx.hstack(
                                            rx.icon("loader", size=16, color=Color.TEXT_MUTED),
                                            rx.text("Gerando PDF...", font_size="0.875rem", color=Color.TEXT_MUTED),
                                            spacing="2",
                                        ),
                                    ),
                                    rx.divider(color=Color.BORDER, margin_y="12px"),
                                    # Botões de ação
                                    rx.vstack(
                                        rx.cond(
                                            State.pdf_url != "",
                                            rx.link(
                                                ui.button(
                                                    "Abrir PDF",
                                                    icon="external-link",
                                                    variant="primary",
                                                    width="100%",
                                                ),
                                                href=State.pdf_url,
                                                is_external=True,
                                                width="100%",
                                            ),
                                            ui.button(
                                                "Abrir PDF",
                                                icon="external-link",
                                                variant="primary",
                                                width="100%",
                                                on_click=State.download_analysis_pdf,
                                            ),
                                        ),
                                        ui.button(
                                            "Baixar PDF",
                                            icon="download",
                                            variant="secondary",
                                            width="100%",
                                            on_click=State.download_analysis_pdf,
                                        ),
                                        ui.button(
                                            "Exportar CSV",
                                            icon="table",
                                            variant="secondary",
                                            width="100%",
                                            on_click=State.export_analysis_csv,
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                    padding_top="12px",
                                ),
                                height="100%",
                                width="100%",
                                spacing="4",
                            ),
                            width={"initial": "100%", "lg": "280px"},
                            min_width={"initial": "100%", "lg": "250px"},
                            flex_shrink="0",
                            bg=Color.SURFACE,
                            border=f"1px solid {Color.BORDER}",
                            border_radius=Design.RADIUS_XL,
                            padding=Spacing.LG,
                            height="fit-content",
                            position={"initial": "relative", "lg": "sticky"},
                            top="40px",
                            box_shadow=Design.SHADOW_LG,
                        ),
                        rx.box(),
                    ),

                    width="100%",
                    justify_content="start",
                    direction={"initial": "column", "lg": "row"},
                    align_items="start",
                    gap="32px",
                ),
                width="100%",
                spacing="0",
            ),
        ),

            patient_history_modal(),
            width="100%",
            spacing="0",
        ),
        width="100%",
    )
