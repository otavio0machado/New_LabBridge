import reflex as rx
from ..styles import Color, Design, Typography, Animation, Spacing, CARD_STYLE, BUTTON_PRIMARY_STYLE, BUTTON_SECONDARY_STYLE, BUTTON_XL_STYLE, INPUT_STYLE, INPUT_XL_STYLE

# =============================================================================
# BIODIAGNÓSTICO VIBE UI
# Centralized Component Library - Protocol K.I.S.S
# =============================================================================

# --- Typography Helpers ---

def heading(text: str, level: int = 1, color: str = None, **props) -> rx.Component:
    """Standardized Heading (H1-H5)"""
    map_level = {
        1: Typography.H1, 2: Typography.H2, 3: Typography.H3, 
        4: Typography.H4, 5: Typography.H5
    }
    style = map_level.get(level, Typography.H1).copy()
    if color: style["color"] = color
    style.update(props)
    return rx.text(text, **style)

def animated_heading(text: str, level: int = 1, animation: str = "fade-in-up", **props) -> rx.Component:
    """Heading with entrance animation"""
    map_anim = {
        "fade-in": "animate-fade-in",
        "fade-in-up": "animate-fade-in-up",
        "slide-up": "animate-slide-up"
    }
    return heading(text, level=level, class_name=map_anim.get(animation, "animate-fade-in-up"), **props)

def text(content: str, size: str = "body", **props) -> rx.Component:
    """Standardized Text Component"""
    map_size = {
        "body": Typography.BODY,
        "body_large": Typography.BODY_LARGE,
        "body_secondary": Typography.BODY_SECONDARY,
        "small": Typography.SMALL,
        "caption": Typography.CAPTION,
        "label": Typography.LABEL,
        "label_large": Typography.LABEL_LARGE,
    }
    style = map_size.get(size, Typography.BODY).copy()
    style.update(props)
    return rx.text(content, **style)

# --- Containers & Cards ---

def card(*children, **props) -> rx.Component:
    """Premium Glass/Surface Card"""
    style = CARD_STYLE.copy()
    style.update(props)
    return rx.box(*children, **style)

def empty_state(icon: str, title: str, description: str, action_label: str = "", on_action=None) -> rx.Component:
    """Clean Empty State Placeholder"""
    return card(
        rx.vstack(
            rx.icon(tag=icon, size=48, color=Color.TEXT_SECONDARY),
            heading(title, level=3, color=Color.DEEP),
            text(description, size="body_secondary", text_align="center", max_width="400px"),
            rx.cond(action_label != "", button(action_label, on_click=on_action)),
            padding=Spacing.XXL, align_items="center", gap=Spacing.LG
        ),
        text_align="center"
    )

# --- Actions & Inputs ---

def button(label: str, icon: str = None, variant: str = "primary", size: str = "default", is_loading: bool = False, **props) -> rx.Component:
    """Unified Vibe Button"""
    # Variants configuration
    variants = {
        "primary": BUTTON_PRIMARY_STYLE,
        "secondary": BUTTON_SECONDARY_STYLE,
        "ghost": {
            "bg": "transparent", "color": Color.TEXT_SECONDARY, "padding_x": "0.75rem",
            "_hover": {"bg": Color.PRIMARY_LIGHT, "color": Color.DEEP}
        },
        "danger": {
            "bg": Color.ERROR_BG, "color": Color.ERROR, "border": f"1px solid {Color.ERROR}40",
            "_hover": {"bg": Color.ERROR, "color": "white", "border_color": Color.ERROR}
        }
    }
    
    # Select Base Style
    base_style = variants.get(variant, BUTTON_PRIMARY_STYLE).copy()
    
    # Apply Size Overrides
    if size == "large" and variant == "primary":
        base_style.update(BUTTON_XL_STYLE)
    
    style = base_style
    user_disabled = props.pop("disabled", False)
    style.update(props)
    
    # Build content based on icon presence
    # Check if icon is a Reflex Var (dynamic) or a Python value
    if is_loading:
        content = rx.hstack(rx.spinner(size="1"), rx.text("Carregando..."), align="center", gap="8px")
    elif icon is not None:
        # icon can be a string or a rx.Var - both work with rx.icon
        if label:
            content = rx.hstack(rx.icon(tag=icon, size=18), rx.text(label), align="center", gap="8px")
        else:
            content = rx.icon(tag=icon, size=18)
    else:
        content = rx.text(label)
    
    return rx.button(content, disabled=user_disabled, **style)

def input(placeholder: str = "", size: str = "default", **props) -> rx.Component:
    """Standard Input"""
    style = INPUT_STYLE.copy()
    if size == "large":
        style = INPUT_XL_STYLE.copy()
        
    style["placeholder"] = placeholder
    style.update(props)
    return rx.input(**style)

def select(items: list, placeholder: str = "Selecione...", **props) -> rx.Component:
    """Standard Select"""
    style = INPUT_STYLE.copy() # Reuse Input style base
    style.update(props)
    return rx.select(items, placeholder=placeholder, **style)

def form_field(label: str, control: rx.Component, required: bool = False, error: str = "") -> rx.Component:
    """Label + Control + Error Message Wrapper"""
    return rx.vstack(
        rx.hstack(
            rx.text(label, **Typography.LABEL),
            rx.cond(required, rx.text("*", color=Color.ERROR, font_size="0.875rem")),
            gap="4px"
        ),
        control,
        rx.cond(error != "", rx.text(error, color=Color.ERROR, font_size="0.75rem")),
        width="100%", gap="4px", align_items="start"
    )

# --- Data Display ---

def status_badge(text: str, status: str = "default") -> rx.Component:
    """Semantic Status Badge"""
    config = {
        "success": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "warning": (Color.WARNING, Color.WARNING_BG, "triangle-alert"),
        "error": (Color.ERROR, Color.ERROR_BG, "circle-x"),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT, "info"),
        "neutral": (Color.TEXT_SECONDARY, Color.BACKGROUND, "circle-help"),
    }
    color, bg, icon = config.get(status, config["neutral"])
    
    return rx.badge(
        rx.hstack(rx.icon(tag=icon, size=14), rx.text(text), gap="4px", align_items="center"),
        bg=bg, color=color, variant="soft", radius="full", padding_x=Spacing.MD, padding_y="2px"
    )

def stat_card(title: str, value: str, icon: str, trend: str = "neutral", subtext: str = "") -> rx.Component:
    """Dashboard Statistic Card"""
    return card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=24, color=Color.PRIMARY),
                    padding="12px", border_radius="12px", bg=Color.PRIMARY_LIGHT,
                ),
                rx.spacer(),
                rx.cond(subtext != "", status_badge(subtext, status=trend)),
                width="100%", align_items="center"
            ),
            rx.vstack(
                rx.text(value, font_size="2rem", font_weight="800", color=Color.DEEP, line_height="1.1"),
                rx.text(title, style=Typography.SMALL, color=Color.TEXT_SECONDARY, text_transform="uppercase"),
                gap="2px", align_items="start"
            ),
            gap=Spacing.LG
        )
    )

def toast(message: str, status: str = "info") -> rx.Component:
    """Floating Toast Notification"""
    colors = {
        "success": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "error": (Color.ERROR, Color.ERROR_BG, "circle-x"),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT, "info"),
    }
    color, bg, icon = colors.get(status, colors["info"])
    
    return rx.box(
        rx.hstack(
            rx.icon(tag=icon, size=20, color=color),
            rx.text(message, style=Typography.LABEL, color=Color.DEEP),
            align_items="center", gap=Spacing.MD
        ),
        bg=bg, border=f"1px solid {color}40", border_radius=Design.RADIUS_LG,
        padding=Spacing.MD, box_shadow=Design.SHADOW_MD,
        position="fixed", bottom="2rem", right="2rem", z_index="9999"
    )

def loading_spinner(text: str = "Carregando...") -> rx.Component:
    """Full width loading state"""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color=Color.PRIMARY),
            rx.text(text, color=Color.TEXT_SECONDARY),
            gap="12px", align_items="center"
        ),
        width="100%", padding=Spacing.XL
    )

def text_area(placeholder: str = "", **props) -> rx.Component:
    """Standard TextArea"""
    style = INPUT_STYLE.copy()
    style.update({
        "min_height": "100px",
        "resize": "vertical",
        "padding": Spacing.MD
    })
    style["placeholder"] = placeholder
    style.update(props)
    return rx.text_area(**style)

def segmented_control(items: list[dict], value: str, on_change) -> rx.Component:
    """Standard Segmented Control"""
    return rx.segmented_control.root(
        *[rx.segmented_control.item(item["label"], value=item["value"]) for item in items],
        value=value,
        on_change=on_change,
        variant="surface",
        size="2",
        radius="large",
        width="100%",
    )


# =============================================================================
# PAGE STRUCTURE COMPONENTS
# Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Seção 4.1 Padrão de Página
# =============================================================================

def page_header(
    title: str,
    description: str = "",
    actions: rx.Component = None,
    breadcrumbs: list = None,
) -> rx.Component:
    """
    Cabeçalho padrão de página
    1. Título principal
    2. Descrição curta (1 linha)
    3. Área de ações primárias
    """
    return rx.box(
        rx.vstack(
            # Breadcrumbs (opcional)
            rx.cond(
                breadcrumbs is not None,
                rx.hstack(
                    *[
                        rx.fragment(
                            rx.link(
                                rx.text(b["label"], font_size="0.875rem", color=Color.TEXT_SECONDARY),
                                href=b.get("href", "#"),
                                _hover={"color": Color.PRIMARY},
                            ),
                            rx.text("/", font_size="0.875rem", color=Color.TEXT_MUTED, padding_x="8px"),
                        ) if i < len(breadcrumbs) - 1 else
                        rx.text(b["label"], font_size="0.875rem", color=Color.TEXT_PRIMARY, font_weight="500")
                        for i, b in enumerate(breadcrumbs or [])
                    ],
                    margin_bottom=Spacing.SM,
                ),
                rx.fragment(),
            ),

            # Title + Actions Row
            rx.hstack(
                rx.vstack(
                    heading(title, level=1),
                    rx.cond(
                        description != "",
                        text(description, size="body_secondary"),
                        rx.fragment(),
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.cond(
                    actions is not None,
                    actions,
                    rx.fragment(),
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
                gap=Spacing.MD,
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        padding_bottom=Spacing.LG,
        margin_bottom=Spacing.LG,
        border_bottom=f"1px solid {Color.BORDER}",
    )


def page_section(
    title: str = "",
    description: str = "",
    children: rx.Component = None,
    actions: rx.Component = None,
) -> rx.Component:
    """Seção de página com título opcional"""
    return rx.box(
        rx.vstack(
            rx.cond(
                title != "",
                rx.hstack(
                    rx.vstack(
                        heading(title, level=3),
                        rx.cond(
                            description != "",
                            text(description, size="small"),
                            rx.fragment(),
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.cond(actions is not None, actions, rx.fragment()),
                    width="100%",
                    align="center",
                    margin_bottom=Spacing.MD,
                ),
                rx.fragment(),
            ),
            children,
            width="100%",
            spacing="0",
        ),
        width="100%",
        margin_bottom=Spacing.XL,
    )


# =============================================================================
# INTERFACE STATES
# Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Seção 15. Estados de Interface
# =============================================================================

def loading_state(
    message: str = "Carregando dados...",
    description: str = "",
) -> rx.Component:
    """
    Estado de carregamento
    - Explica o que está acontecendo
    """
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color=Color.PRIMARY),
            rx.text(message, font_weight="500", color=Color.TEXT_PRIMARY),
            rx.cond(
                description != "",
                rx.text(description, font_size="0.875rem", color=Color.TEXT_SECONDARY),
                rx.fragment(),
            ),
            spacing="3",
            align="center",
            padding=Spacing.XXL,
        ),
        width="100%",
        min_height="300px",
    )


def error_state(
    title: str = "Algo deu errado",
    message: str = "Não foi possível carregar os dados.",
    action_label: str = "Tentar novamente",
    on_action=None,
) -> rx.Component:
    """
    Estado de erro
    - Explica o que está acontecendo
    - Diz o que o usuário pode fazer
    """
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon(tag="circle-alert", size=48, color=Color.ERROR),
                padding=Spacing.MD,
                bg=Color.ERROR_BG,
                border_radius="full",
            ),
            heading(title, level=3, color=Color.ERROR),
            text(message, size="body_secondary", text_align="center", max_width="400px"),
            rx.cond(
                action_label != "" and on_action is not None,
                button(action_label, icon="refresh-cw", variant="primary", on_click=on_action),
                rx.fragment(),
            ),
            spacing="4",
            align="center",
            padding=Spacing.XXL,
        ),
        width="100%",
        min_height="300px",
    )


def success_state(
    title: str = "Sucesso!",
    message: str = "Operação realizada com sucesso.",
    action_label: str = "",
    on_action=None,
) -> rx.Component:
    """
    Estado de sucesso
    - Confirma a ação realizada
    - Oferece próximo passo
    """
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon(tag="circle-check", size=48, color=Color.SUCCESS),
                padding=Spacing.MD,
                bg=Color.SUCCESS_BG,
                border_radius="full",
            ),
            heading(title, level=3, color=Color.SUCCESS),
            text(message, size="body_secondary", text_align="center", max_width="400px"),
            rx.cond(
                action_label != "" and on_action is not None,
                button(action_label, variant="primary", on_click=on_action),
                rx.fragment(),
            ),
            spacing="4",
            align="center",
            padding=Spacing.XXL,
        ),
        width="100%",
        min_height="300px",
    )


def warning_state(
    title: str = "Atenção",
    message: str = "Esta ação requer sua atenção.",
    action_label: str = "",
    on_action=None,
) -> rx.Component:
    """
    Estado de alerta/atenção
    - Chama atenção para algo importante
    """
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon(tag="triangle-alert", size=48, color=Color.WARNING),
                padding=Spacing.MD,
                bg=Color.WARNING_BG,
                border_radius="full",
            ),
            heading(title, level=3, color=Color.WARNING_HOVER),
            text(message, size="body_secondary", text_align="center", max_width="400px"),
            rx.cond(
                action_label != "" and on_action is not None,
                button(action_label, variant="secondary", on_click=on_action),
                rx.fragment(),
            ),
            spacing="4",
            align="center",
            padding=Spacing.XXL,
        ),
        width="100%",
        min_height="300px",
    )


# =============================================================================
# DATA DISPLAY COMPONENTS
# =============================================================================

def data_table_header(*columns: str) -> rx.Component:
    """Cabeçalho de tabela padronizado"""
    return rx.table.header(
        rx.table.row(
            *[
                rx.table.column_header_cell(
                    rx.text(col, font_weight="600", font_size="0.75rem", text_transform="uppercase", letter_spacing="0.05em"),
                )
                for col in columns
            ],
        ),
    )


def kpi_card(
    label: str,
    value: str,
    icon: str,
    trend: str = None,
    trend_value: str = None,
    color: str = "primary",
) -> rx.Component:
    """
    Card de KPI para Dashboard
    - Receita total, Divergências, Auditorias concluídas
    """
    color_map = {
        "primary": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "success": (Color.SUCCESS, Color.SUCCESS_BG),
        "warning": (Color.WARNING, Color.WARNING_BG),
        "error": (Color.ERROR, Color.ERROR_BG),
    }
    main_color, bg_color = color_map.get(color, color_map["primary"])

    return card(
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
                    trend is not None and trend_value is not None,
                    rx.hstack(
                        rx.icon(
                            tag="trending-up" if trend == "up" else "trending-down",
                            size=14,
                            color=Color.SUCCESS if trend == "up" else Color.ERROR,
                        ),
                        rx.text(
                            trend_value,
                            font_size="0.75rem",
                            font_weight="600",
                            color=Color.SUCCESS if trend == "up" else Color.ERROR,
                        ),
                        spacing="1",
                        align="center",
                        padding="4px 8px",
                        bg=Color.SUCCESS_BG if trend == "up" else Color.ERROR_BG,
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
                    font_size="2rem",
                    font_weight="700",
                    color=Color.DEEP,
                    line_height="1",
                ),
                rx.text(
                    label,
                    font_size="0.875rem",
                    color=Color.TEXT_SECONDARY,
                    text_transform="uppercase",
                    letter_spacing="0.03em",
                ),
                spacing="1",
                align_items="start",
            ),
            spacing="4",
            width="100%",
        ),
    )


def action_card(
    title: str,
    description: str,
    icon: str,
    on_click=None,
    color: str = "primary",
) -> rx.Component:
    """Card de ação rápida para Dashboard"""
    color_map = {
        "primary": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "success": (Color.SUCCESS, Color.SUCCESS_BG),
        "warning": (Color.WARNING, Color.WARNING_BG),
    }
    main_color, bg_color = color_map.get(color, color_map["primary"])

    return rx.box(
        card(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=28, color=main_color),
                    padding=Spacing.MD,
                    border_radius=Design.RADIUS_MD,
                    bg=bg_color,
                ),
                rx.vstack(
                    heading(title, level=4),
                    text(description, size="small"),
                    spacing="1",
                    align_items="start",
                ),
                spacing="4",
                align="center",
            ),
            cursor="pointer" if on_click else "default",
            on_click=on_click,
            _hover={
                "border_color": main_color,
                "transform": "translateY(-2px)",
                "box_shadow": Design.SHADOW_MD,
            } if on_click else {},
            transition="all 0.2s ease",
        ),
    )


def filter_bar(*children, on_clear=None) -> rx.Component:
    """Barra de filtros padronizada"""
    return rx.box(
        rx.hstack(
            *children,
            rx.spacer(),
            rx.cond(
                on_clear is not None,
                button("Limpar filtros", icon="x", variant="ghost", on_click=on_clear),
                rx.fragment(),
            ),
            spacing="3",
            align="center",
            flex_wrap="wrap",
        ),
        width="100%",
        padding=Spacing.MD,
        bg=Color.BACKGROUND,
        border_radius=Design.RADIUS_LG,
        border=f"1px solid {Color.BORDER}",
        margin_bottom=Spacing.LG,
    )


def progress_bar(value: int, max_value: int = 100, color: str = "primary") -> rx.Component:
    """Barra de progresso"""
    color_map = {
        "primary": Color.PRIMARY,
        "success": Color.SUCCESS,
        "warning": Color.WARNING,
        "error": Color.ERROR,
    }
    bar_color = color_map.get(color, Color.PRIMARY)
    percentage = min(100, max(0, (value / max_value) * 100))

    return rx.box(
        rx.box(
            width=f"{percentage}%",
            height="100%",
            bg=bar_color,
            border_radius="full",
            transition="width 0.5s ease",
        ),
        width="100%",
        height="8px",
        bg=Color.BACKGROUND,
        border_radius="full",
        overflow="hidden",
    )


def timeline_item(
    title: str,
    description: str = "",
    date: str = "",
    status: str = "default",
    is_last: bool = False,
) -> rx.Component:
    """Item de linha do tempo para histórico"""
    status_colors = {
        "success": Color.SUCCESS,
        "error": Color.ERROR,
        "warning": Color.WARNING,
        "default": Color.PRIMARY,
    }
    dot_color = status_colors.get(status, Color.PRIMARY)

    return rx.hstack(
        # Timeline dot and line
        rx.vstack(
            rx.box(
                width="12px",
                height="12px",
                bg=dot_color,
                border_radius="full",
                border=f"3px solid {Color.SURFACE}",
                box_shadow=f"0 0 0 2px {dot_color}40",
            ),
            rx.cond(
                not is_last,
                rx.box(
                    width="2px",
                    flex="1",
                    min_height="40px",
                    bg=Color.BORDER,
                ),
                rx.fragment(),
            ),
            spacing="0",
            align="center",
        ),
        # Content
        rx.vstack(
            rx.hstack(
                rx.text(title, font_weight="500", color=Color.TEXT_PRIMARY),
                rx.spacer(),
                rx.text(date, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                width="100%",
            ),
            rx.cond(
                description != "",
                rx.text(description, font_size="0.875rem", color=Color.TEXT_SECONDARY),
                rx.fragment(),
            ),
            spacing="1",
            align_items="start",
            flex="1",
            padding_bottom=Spacing.LG,
        ),
        spacing="3",
        align_items="start",
        width="100%",
    )


def status_banner(
    status: str,
    title: str,
    description: str = "",
) -> rx.Component:
    """
    Banner de status semântico padronizado

    Args:
        status: "critical" | "warning" | "success" | "info"
        title: Título do banner
        description: Descrição opcional
    """
    config = {
        "critical": (Color.ERROR, Color.ERROR_BG, Color.ERROR_LIGHT, "circle-alert"),
        "warning": (Color.WARNING_HOVER, Color.WARNING_BG, Color.WARNING_LIGHT, "triangle-alert"),
        "success": (Color.SUCCESS, Color.SUCCESS_BG, Color.SUCCESS_LIGHT, "circle-check"),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT, Color.PRIMARY_BORDER, "info"),
    }
    text_color, bg_color, border_color, icon = config.get(status, config["info"])

    return rx.box(
        rx.hstack(
            rx.icon(tag=icon, color=text_color, size=24),
            rx.vstack(
                rx.text(title, font_weight="700", color=text_color),
                rx.cond(
                    description != "",
                    rx.text(description, font_size="0.875rem", color=text_color),
                    rx.fragment(),
                ),
                spacing="1",
                align_items="start",
            ),
            spacing="4",
            align_items="center",
        ),
        bg=bg_color,
        border=f"1px solid {border_color}",
        border_radius=Design.RADIUS_LG,
        padding=Spacing.MD,
        width="100%",
    )
