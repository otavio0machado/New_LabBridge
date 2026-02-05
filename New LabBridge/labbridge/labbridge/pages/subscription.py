"""
LabBridge - Planos e Assinaturas
Gerencia os planos de assinatura do usuario.
"""
import reflex as rx
from ..states.auth_state import AuthState
from ..states.subscription_state import SubscriptionState
from ..components import ui
from ..styles import Color, Spacing, Design


def plan_card(title: str, price: str, features: list[str], plan_id: str, recommended: bool = False) -> rx.Component:
    """Card de plano de assinatura"""
    is_current = rx.cond(
        SubscriptionState.current_plan == plan_id,
        True,
        False
    )

    return rx.vstack(
        # Badge recomendado
        rx.cond(
            recommended,
            rx.badge(
                "Mais Popular",
                color_scheme="green",
                size="1",
                position="absolute",
                top="-10px",
                right="50%",
                transform="translateX(50%)",
            ),
            rx.fragment(),
        ),

        rx.text(title, size="5", weight="bold", color=Color.DEEP if not recommended else "white"),
        rx.heading(price, size="8", weight="bold", color=Color.PRIMARY if not recommended else "white"),
        rx.text("por mes", size="2", color=Color.TEXT_SECONDARY if not recommended else "rgba(255,255,255,0.8)"),

        rx.divider(margin_y=Spacing.SM, opacity="0.2"),

        rx.vstack(
            *[
                rx.hstack(
                    rx.icon("check", size=16, color=Color.SUCCESS if not recommended else "white"),
                    rx.text(feature, size="3", color=Color.TEXT_PRIMARY if not recommended else "white"),
                    spacing="2",
                ) for feature in features
            ],
            spacing="3",
            align_items="start",
            width="100%",
        ),

        rx.spacer(),

        rx.button(
            rx.cond(
                is_current,
                rx.text("Plano Atual"),
                rx.text("Escolher Plano"),
            ),
            width="100%",
            variant="outline" if not recommended else "solid",
            color_scheme="gray" if not recommended else "indigo",
            disabled=is_current,
            cursor=rx.cond(is_current, "default", "pointer"),
            bg="white" if not recommended else "rgba(255,255,255,0.2)",
            color=Color.PRIMARY if not recommended else "white",
            _hover=rx.cond(
                is_current,
                {},
                {"bg": Color.BACKGROUND} if not recommended else {"bg": "rgba(255,255,255,0.3)"}
            ),
            on_click=SubscriptionState.select_plan(plan_id),
        ),

        bg=Color.PRIMARY if recommended else "white",
        border=f"1px solid {Color.BORDER}" if not recommended else "none",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.XL,
        width=["100%", "300px"],
        height="480px",
        align_items="center",
        box_shadow=Design.SHADOW_LG if recommended else Design.SHADOW_MD,
        transform="scale(1.05)" if recommended else "scale(1)",
        z_index="1" if recommended else "0",
        position="relative",
    )


def upgrade_modal() -> rx.Component:
    """Modal de confirmacao de upgrade"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="credit-card", size=20, color=Color.PRIMARY),
                    rx.text("Confirmar Mudanca de Plano"),
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                rx.vstack(
                    rx.cond(
                        SubscriptionState.payment_success,
                        rx.vstack(
                            rx.icon(tag="circle-check", size=48, color=Color.SUCCESS),
                            rx.text("Plano alterado com sucesso!", font_weight="600", color=Color.SUCCESS),
                            rx.text("Seu novo plano ja esta ativo.", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                            spacing="2",
                            align="center",
                            padding_y=Spacing.LG,
                        ),
                        rx.vstack(
                            rx.text(
                                "Voce esta prestes a mudar para o plano ",
                                rx.text(
                                    rx.cond(
                                        SubscriptionState.selected_plan == "starter",
                                        "Starter (R$ 0/mes)",
                                        "Pro (R$ 299/mes)"
                                    ),
                                    font_weight="600",
                                    color=Color.PRIMARY,
                                    as_="span",
                                ),
                                ".",
                                font_size="0.9rem",
                                color=Color.TEXT_SECONDARY,
                            ),
                            rx.cond(
                                SubscriptionState.selected_plan == "starter",
                                rx.box(
                                    rx.hstack(
                                        rx.icon(tag="triangle-alert", size=16, color=Color.WARNING),
                                        rx.text(
                                            "Ao fazer downgrade, voce perdera acesso aos recursos Premium.",
                                            font_size="0.875rem",
                                            color=Color.WARNING_HOVER,
                                        ),
                                        spacing="2",
                                    ),
                                    padding=Spacing.MD,
                                    bg=Color.WARNING_BG,
                                    border_radius=Design.RADIUS_MD,
                                    margin_top=Spacing.SM,
                                ),
                                rx.fragment(),
                            ),
                            rx.cond(
                                SubscriptionState.payment_error != "",
                                rx.text(SubscriptionState.payment_error, font_size="0.875rem", color=Color.ERROR),
                                rx.fragment(),
                            ),
                            spacing="2",
                            width="100%",
                            align_items="start",
                        ),
                    ),
                    width="100%",
                ),
            ),
            rx.dialog.close(
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        variant="ghost",
                        on_click=SubscriptionState.close_upgrade_modal,
                    ),
                    rx.cond(
                        ~SubscriptionState.payment_success,
                        rx.button(
                            rx.cond(
                                SubscriptionState.is_processing,
                                rx.hstack(rx.spinner(size="1"), rx.text("Processando..."), spacing="2"),
                                rx.text("Confirmar"),
                            ),
                            variant="solid",
                            bg=Color.PRIMARY,
                            color="white",
                            on_click=SubscriptionState.confirm_plan_change,
                            disabled=SubscriptionState.is_processing,
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    margin_top=Spacing.MD,
                ),
            ),
            max_width="450px",
        ),
        open=SubscriptionState.show_upgrade_modal,
        on_open_change=SubscriptionState.close_upgrade_modal,
    )


def enterprise_modal() -> rx.Component:
    """Modal de contato Enterprise"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="building-2", size=20, color=Color.PRIMARY),
                    rx.text("Plano Enterprise"),
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "Preencha seus dados e nossa equipe entrara em contato para criar uma proposta personalizada.",
                        font_size="0.875rem",
                        color=Color.TEXT_SECONDARY,
                        margin_bottom=Spacing.MD,
                    ),
                    rx.text("Nome *", font_size="0.875rem", font_weight="500"),
                    rx.input(
                        placeholder="Seu nome completo",
                        value=SubscriptionState.enterprise_name,
                        on_change=SubscriptionState.set_enterprise_name,
                        width="100%",
                    ),
                    rx.text("Email *", font_size="0.875rem", font_weight="500", margin_top=Spacing.SM),
                    rx.input(
                        placeholder="seu@email.com",
                        value=SubscriptionState.enterprise_email,
                        on_change=SubscriptionState.set_enterprise_email,
                        width="100%",
                    ),
                    rx.text("Empresa *", font_size="0.875rem", font_weight="500", margin_top=Spacing.SM),
                    rx.input(
                        placeholder="Nome da empresa",
                        value=SubscriptionState.enterprise_company,
                        on_change=SubscriptionState.set_enterprise_company,
                        width="100%",
                    ),
                    rx.text("Mensagem (opcional)", font_size="0.875rem", font_weight="500", margin_top=Spacing.SM),
                    rx.text_area(
                        placeholder="Conte-nos sobre suas necessidades...",
                        value=SubscriptionState.enterprise_message,
                        on_change=SubscriptionState.set_enterprise_message,
                        width="100%",
                        min_height="80px",
                    ),
                    spacing="1",
                    width="100%",
                    align_items="start",
                ),
            ),
            rx.dialog.close(
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        variant="ghost",
                        on_click=SubscriptionState.close_enterprise_modal,
                    ),
                    rx.button(
                        rx.cond(
                            SubscriptionState.is_processing,
                            rx.hstack(rx.spinner(size="1"), rx.text("Enviando..."), spacing="2"),
                            rx.text("Enviar Solicitacao"),
                        ),
                        variant="solid",
                        bg=Color.PRIMARY,
                        color="white",
                        on_click=SubscriptionState.submit_enterprise_contact,
                        disabled=SubscriptionState.is_processing,
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    margin_top=Spacing.MD,
                ),
            ),
            max_width="450px",
        ),
        open=SubscriptionState.show_enterprise_modal,
        on_open_change=SubscriptionState.close_enterprise_modal,
    )


def subscription_page() -> rx.Component:
    """Pagina de Assinatura e Planos"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.vstack(
                    ui.page_header(
                        title="Planos e Assinaturas",
                        description="Escolha o plano ideal para o seu laboratorio",
                    ),

                    # Plano atual badge
                    rx.center(
                        rx.hstack(
                            rx.icon(tag="crown", size=16, color=Color.PRIMARY),
                            rx.text("Seu plano atual: ", font_size="0.9rem", color=Color.TEXT_SECONDARY),
                            rx.badge(
                                SubscriptionState.plan_display_name,
                                color_scheme="blue",
                                size="2",
                            ),
                            spacing="2",
                        ),
                        width="100%",
                        margin_bottom=Spacing.LG,
                    ),

                    rx.flex(
                        plan_card(
                            title="Starter",
                            price="R$ 0",
                            features=[
                                "Ate 50 analises/mes",
                                "1 Usuario",
                                "Suporte por Email",
                                "Retencao de 30 dias"
                            ],
                            plan_id="starter",
                        ),
                        plan_card(
                            title="Pro",
                            price="R$ 299",
                            features=[
                                "Analises Ilimitadas",
                                "5 Usuarios",
                                "Suporte Prioritario",
                                "Retencao de 1 ano",
                                "IA Detective Avancado"
                            ],
                            plan_id="pro",
                            recommended=True,
                        ),
                        plan_card(
                            title="Enterprise",
                            price="Sob Consulta",
                            features=[
                                "Usuarios Ilimitados",
                                "API Dedicada",
                                "Gerente de Contas",
                                "SLA de 99.9%",
                                "Onboarding Personalizado"
                            ],
                            plan_id="enterprise",
                        ),
                        spacing="6",
                        flex_wrap="wrap",
                        justify_content="center",
                        align_items="center",
                        margin_top=Spacing.XL,
                        width="100%",
                    ),

                    # Features comparison
                    rx.box(
                        rx.vstack(
                            rx.text("Recursos por Plano", font_weight="600", font_size="1.1rem", color=Color.DEEP),
                            rx.divider(margin_y=Spacing.SM),
                            rx.hstack(
                                rx.text("Analises mensais", flex="1", color=Color.TEXT_SECONDARY),
                                rx.text("50", width="80px", text_align="center"),
                                rx.text("Ilimitado", width="80px", text_align="center", color=Color.PRIMARY, font_weight="600"),
                                rx.text("Ilimitado", width="80px", text_align="center"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("Usuarios", flex="1", color=Color.TEXT_SECONDARY),
                                rx.text("1", width="80px", text_align="center"),
                                rx.text("5", width="80px", text_align="center", color=Color.PRIMARY, font_weight="600"),
                                rx.text("Ilimitado", width="80px", text_align="center"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("IA Detective", flex="1", color=Color.TEXT_SECONDARY),
                                rx.icon(tag="x", size=16, color=Color.ERROR, width="80px"),
                                rx.icon(tag="check", size=16, color=Color.SUCCESS, width="80px"),
                                rx.icon(tag="check", size=16, color=Color.SUCCESS, width="80px"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("API Access", flex="1", color=Color.TEXT_SECONDARY),
                                rx.icon(tag="x", size=16, color=Color.ERROR, width="80px"),
                                rx.icon(tag="x", size=16, color=Color.ERROR, width="80px"),
                                rx.icon(tag="check", size=16, color=Color.SUCCESS, width="80px"),
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_XL,
                        padding=Spacing.LG,
                        margin_top=Spacing.XXL,
                        max_width="600px",
                        width="100%",
                    ),

                    max_width="1200px",
                    width="100%",
                    margin_x="auto",
                    padding=Spacing.XL,
                    align_items="center",
                ),
                width="100%",
                min_height="calc(100vh - 80px)",
                bg=Color.BACKGROUND,
            ),

            # Modals
            upgrade_modal(),
            enterprise_modal(),

            width="100%",
        ),
        width="100%",
    )
