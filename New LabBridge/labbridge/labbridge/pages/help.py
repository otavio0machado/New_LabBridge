"""
LabBridge - Central de Ajuda / Help Center
Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md - Secao 13. Suporte / Help Center

Conteudo:
- Busca central
- Categorias
- FAQs
- Tutoriais rapidos
- Contato humano
"""
import reflex as rx
from ..state import State
from ..states.help_state import HelpState
from ..styles import Color, Design, Spacing, TextSize
from ..components import ui


def search_hero() -> rx.Component:
    """Secao de busca principal"""
    return rx.box(
        rx.vstack(
            rx.icon(tag="circle-help", size=48, color=Color.PRIMARY),
            rx.text(
                "Como podemos ajudar?",
                font_size="1.75rem",
                font_weight="700",
                color=Color.DEEP,
                text_align="center",
            ),
            rx.text(
                "Busque por artigos, tutoriais e respostas as duvidas mais comuns",
                font_size="1rem",
                color=Color.TEXT_SECONDARY,
                text_align="center",
            ),
            rx.box(
                rx.hstack(
                    rx.icon(tag="search", size=20, color=Color.TEXT_SECONDARY),
                    rx.input(
                        placeholder="Buscar na Central de Ajuda...",
                        value=HelpState.search_query,
                        on_change=HelpState.set_search_query,
                        width="100%",
                        border="none",
                        bg="transparent",
                        _focus={"outline": "none"},
                    ),
                    bg=Color.SURFACE,
                    padding=Spacing.MD,
                    border_radius=Design.RADIUS_LG,
                    border=f"1px solid {Color.BORDER}",
                    width=["100%", "100%", "500px"],
                    _focus_within={
                        "border_color": Color.PRIMARY,
                        "box_shadow": f"0 0 0 3px {Color.PRIMARY_LIGHT}",
                    },
                ),
                # Resultados da busca
                rx.cond(
                    HelpState.search_query != "",
                    rx.box(
                        rx.cond(
                            HelpState.search_results.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    HelpState.search_results,
                                    lambda result: rx.hstack(
                                        rx.icon(
                                            tag=rx.cond(
                                                result["type"] == "category",
                                                "folder",
                                                rx.cond(
                                                    result["type"] == "tutorial",
                                                    "play-circle",
                                                    "help-circle"
                                                )
                                            ),
                                            size=16,
                                            color=Color.PRIMARY,
                                        ),
                                        rx.text(result["title"], font_size="0.875rem", color=Color.TEXT_PRIMARY),
                                        spacing="2",
                                        padding=Spacing.SM,
                                        width="100%",
                                        cursor="pointer",
                                        border_radius=Design.RADIUS_MD,
                                        _hover={"bg": Color.PRIMARY_LIGHT},
                                        on_click=lambda r=result: HelpState.select_category(r["id"]),
                                    ),
                                ),
                                spacing="1",
                                width="100%",
                            ),
                            rx.text(
                                "Nenhum resultado encontrado",
                                font_size="0.875rem",
                                color=Color.TEXT_SECONDARY,
                                padding=Spacing.MD,
                            ),
                        ),
                        position="absolute",
                        top="100%",
                        left="0",
                        right="0",
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius=Design.RADIUS_MD,
                        box_shadow=Design.SHADOW_LG,
                        margin_top="4px",
                        max_height="300px",
                        overflow_y="auto",
                        z_index="100",
                    ),
                    rx.fragment(),
                ),
                position="relative",
                width=["100%", "100%", "500px"],
            ),
            spacing="4",
            align="center",
            padding_y=Spacing.XXL,
        ),
        width="100%",
        bg=f"linear-gradient(180deg, {Color.PRIMARY_LIGHT} 0%, {Color.BACKGROUND} 100%)",
        margin_bottom=Spacing.XL,
    )


def category_card(title: str, description: str, icon: str, article_count: int, category_id: str) -> rx.Component:
    """Card de categoria de ajuda"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(tag=icon, size=24, color=Color.PRIMARY),
                padding=Spacing.MD,
                bg=Color.PRIMARY_LIGHT,
                border_radius=Design.RADIUS_MD,
            ),
            rx.text(title, font_weight="600", color=Color.TEXT_PRIMARY),
            rx.text(description, font_size="0.875rem", color=Color.TEXT_SECONDARY, text_align="center"),
            rx.text(f"{article_count} artigos", font_size="0.75rem", color=Color.TEXT_MUTED),
            spacing="2",
            align="center",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.LG,
        cursor="pointer",
        transition="all 0.2s ease",
        _hover={
            "border_color": Color.PRIMARY,
            "transform": "translateY(-4px)",
            "box_shadow": Design.SHADOW_MD,
        },
        on_click=HelpState.select_category(category_id),
    )


def faq_item(question: str, answer: str) -> rx.Component:
    """Item de FAQ com accordion"""
    return rx.accordion.item(
        header=rx.text(question, font_weight="500", color=Color.TEXT_PRIMARY),
        content=rx.text(answer, font_size="0.875rem", color=Color.TEXT_SECONDARY, line_height="1.6"),
        value=question,
    )


def tutorial_card(title: str, duration: str, difficulty: str, icon: str, tutorial_id: str) -> rx.Component:
    """Card de tutorial rapido"""
    difficulty_config = {
        "Basico": (Color.SUCCESS, Color.SUCCESS_BG),
        "Intermediario": (Color.WARNING, Color.WARNING_BG),
        "Avancado": (Color.ERROR, Color.ERROR_BG),
    }
    color, bg = difficulty_config.get(difficulty, difficulty_config["Basico"])

    return rx.hstack(
        rx.box(
            rx.icon(tag=icon, size=20, color=Color.PRIMARY),
            padding="10px",
            bg=Color.PRIMARY_LIGHT,
            border_radius=Design.RADIUS_MD,
        ),
        rx.vstack(
            rx.text(title, font_weight="500", color=Color.TEXT_PRIMARY),
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="clock", size=12, color=Color.TEXT_MUTED),
                    rx.text(duration, font_size="0.75rem", color=Color.TEXT_MUTED),
                    spacing="1",
                ),
                rx.badge(difficulty, color_scheme="green" if difficulty == "Basico" else "yellow" if difficulty == "Intermediario" else "red", size="1"),
                spacing="2",
            ),
            spacing="0",
            align_items="start",
        ),
        rx.spacer(),
        rx.icon(tag="circle-play", size=20, color=Color.PRIMARY),
        width="100%",
        padding=Spacing.MD,
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_LG,
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={
            "border_color": Color.PRIMARY,
            "bg": Color.PRIMARY_LIGHT,
        },
        on_click=HelpState.open_tutorial(tutorial_id),
    )


def contact_card(title: str, description: str, icon: str, action_label: str, action_icon: str, contact_type: str) -> rx.Component:
    """Card de contato/suporte"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(tag=icon, size=24, color=Color.PRIMARY),
                padding=Spacing.MD,
                bg=Color.PRIMARY_LIGHT,
                border_radius="full",
            ),
            rx.text(title, font_weight="600", color=Color.TEXT_PRIMARY),
            rx.text(description, font_size="0.875rem", color=Color.TEXT_SECONDARY, text_align="center"),
            rx.button(
                rx.icon(tag=action_icon, size=16),
                rx.text(action_label),
                variant="outline",
                size="2",
                cursor="pointer",
                margin_top=Spacing.SM,
                on_click=rx.cond(
                    contact_type == "chat",
                    HelpState.start_chat,
                    rx.cond(
                        contact_type == "email",
                        HelpState.send_email_direct,
                        HelpState.schedule_call,
                    ),
                ),
            ),
            spacing="2",
            align="center",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.LG,
    )


def contact_modal() -> rx.Component:
    """Modal de contato"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="message-circle", size=20, color=Color.PRIMARY),
                    rx.text("Entrar em Contato"),
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                rx.vstack(
                    rx.cond(
                        HelpState.contact_success,
                        rx.vstack(
                            rx.icon(tag="circle-check", size=48, color=Color.SUCCESS),
                            rx.text("Mensagem enviada com sucesso!", font_weight="600", color=Color.SUCCESS),
                            rx.text("Responderemos em ate 24 horas.", font_size="0.875rem", color=Color.TEXT_SECONDARY),
                            spacing="2",
                            align="center",
                            padding_y=Spacing.LG,
                        ),
                        rx.vstack(
                            rx.text("Nome", font_size="0.875rem", font_weight="500"),
                            rx.input(
                                placeholder="Seu nome completo",
                                value=HelpState.contact_name,
                                on_change=HelpState.set_contact_name,
                                width="100%",
                            ),
                            rx.text("Email", font_size="0.875rem", font_weight="500", margin_top=Spacing.SM),
                            rx.input(
                                placeholder="seu@email.com",
                                value=HelpState.contact_email,
                                on_change=HelpState.set_contact_email,
                                width="100%",
                            ),
                            rx.text("Mensagem", font_size="0.875rem", font_weight="500", margin_top=Spacing.SM),
                            rx.text_area(
                                placeholder="Descreva sua duvida ou problema...",
                                value=HelpState.contact_message,
                                on_change=HelpState.set_contact_message,
                                width="100%",
                                min_height="100px",
                            ),
                            rx.cond(
                                HelpState.contact_error != "",
                                rx.text(HelpState.contact_error, font_size="0.875rem", color=Color.ERROR),
                                rx.fragment(),
                            ),
                            spacing="1",
                            width="100%",
                            align_items="start",
                        ),
                    ),
                    width="100%",
                ),
            ),
            rx.hstack(
                rx.button(
                    "Cancelar",
                    variant="ghost",
                    on_click=HelpState.close_contact_modal,
                ),
                rx.cond(
                    ~HelpState.contact_success,
                    rx.button(
                        rx.cond(
                            HelpState.is_sending_contact,
                            rx.hstack(rx.spinner(size="1"), rx.text("Enviando..."), spacing="2"),
                            rx.text("Enviar"),
                        ),
                        variant="solid",
                        bg=Color.PRIMARY,
                        color="white",
                        on_click=HelpState.send_contact,
                        disabled=HelpState.is_sending_contact,
                    ),
                    rx.fragment(),
                ),
                spacing="2",
                justify="end",
                width="100%",
                margin_top=Spacing.MD,
            ),
            max_width="450px",
        ),
        open=HelpState.show_contact_modal,
        on_open_change=HelpState.close_contact_modal,
    )


def help_page() -> rx.Component:
    """Pagina da Central de Ajuda"""
    return rx.box(
        rx.vstack(
            # Search Hero
            search_hero(),

            # Categories Section
            rx.vstack(
                rx.text("Categorias", font_weight="600", font_size="1.25rem", color=Color.DEEP, margin_bottom=Spacing.MD),
                rx.grid(
                    category_card("Primeiros Passos", "Configuracao inicial e tour pela plataforma", "rocket", 8, "primeiros-passos"),
                    category_card("Auditorias", "Como criar, gerenciar e exportar auditorias", "file-search", 12, "auditorias"),
                    category_card("Importacao de Dados", "Upload de arquivos e processamento", "upload", 6, "importacao"),
                    category_card("Relatorios", "Geracao e exportacao de relatorios", "file-bar-chart", 9, "relatorios"),
                    category_card("Integracoes", "Conectar sistemas externos", "plug", 5, "integracoes"),
                    category_card("Conta e Faturamento", "Planos, pagamentos e configuracoes", "credit-card", 7, "conta"),
                    columns=rx.breakpoints(initial="1", sm="2", md="2", lg="3"),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                margin_bottom=Spacing.XXL,
            ),

            # FAQ Section
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="message-circle-question", size=24, color=Color.PRIMARY),
                        rx.text("Perguntas Frequentes", font_weight="600", font_size="1.25rem", color=Color.DEEP),
                        spacing="2",
                    ),
                    rx.accordion.root(
                        faq_item(
                            "Como faco para criar minha primeira auditoria?",
                            "Acesse o menu 'Auditorias' na barra lateral, clique em 'Nova Auditoria' e siga o passo a passo. Voce precisara fazer upload dos arquivos do Compulab e Simus para iniciar a analise cruzada.",
                        ),
                        faq_item(
                            "Quais formatos de arquivo sao aceitos?",
                            "O LabBridge aceita arquivos PDF dos sistemas Compulab e Simus. Os arquivos devem estar no formato padrao gerado por esses sistemas para garantir a extracao correta dos dados.",
                        ),
                        faq_item(
                            "Como exportar relatorios em diferentes formatos?",
                            "Na pagina de Relatorios, selecione o relatorio desejado e clique no botao de download. Voce pode escolher entre PDF, CSV e Excel. Para exportar multiplos relatorios, use a opcao 'Exportar Todos'.",
                        ),
                        faq_item(
                            "E possivel adicionar mais usuarios a minha conta?",
                            "Sim! Acesse 'Usuarios & Permissoes' no menu. Clique em 'Convidar Membro' e insira o e-mail do novo usuario. Voce pode definir diferentes niveis de acesso: Admin, Analista ou Visualizador.",
                        ),
                        faq_item(
                            "Como entrar em contato com o suporte tecnico?",
                            "Voce pode abrir um ticket de suporte diretamente pelo chat (canto inferior direito), enviar e-mail para suporte@labbridge.com.br ou agendar uma chamada com nossa equipe tecnica.",
                        ),
                        type="single",
                        collapsible=True,
                        width="100%",
                    ),
                    width="100%",
                    spacing="4",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.LG,
                margin_bottom=Spacing.XXL,
            ),

            # Tutorials Section
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="play", size=24, color=Color.PRIMARY),
                    rx.text("Tutoriais Rapidos", font_weight="600", font_size="1.25rem", color=Color.DEEP),
                    rx.spacer(),
                    rx.link(
                        rx.text("Ver todos", font_size="0.875rem", color=Color.PRIMARY),
                        href="#",
                        on_click=lambda: rx.toast.info("Mais tutoriais em breve!"),
                    ),
                    width="100%",
                ),
                rx.grid(
                    tutorial_card("Criando sua primeira auditoria", "5 min", "Basico", "file-plus", "primeira-auditoria"),
                    tutorial_card("Importando dados do Compulab", "3 min", "Basico", "upload", "importar-compulab"),
                    tutorial_card("Analisando divergencias", "8 min", "Intermediario", "search", "analisar-divergencias"),
                    tutorial_card("Configurando integracoes", "10 min", "Avancado", "plug", "configurar-integracoes"),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                margin_bottom=Spacing.XXL,
            ),

            # Contact Section
            rx.vstack(
                rx.text("Precisa de mais ajuda?", font_weight="600", font_size="1.25rem", color=Color.DEEP, margin_bottom=Spacing.MD),
                rx.grid(
                    contact_card(
                        "Chat ao Vivo",
                        "Converse com nossa equipe em tempo real",
                        "message-circle",
                        "Iniciar Chat",
                        "message-square",
                        "chat",
                    ),
                    contact_card(
                        "E-mail",
                        "Envie sua duvida e responderemos em ate 24h",
                        "mail",
                        "Enviar E-mail",
                        "send",
                        "email",
                    ),
                    contact_card(
                        "Agendar Chamada",
                        "Fale diretamente com um especialista",
                        "phone",
                        "Agendar",
                        "calendar",
                        "call",
                    ),
                    columns=rx.breakpoints(initial="1", md="3"),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            ),

            # Contact Modal
            contact_modal(),

            width="100%",
            spacing="0",
            padding_x=[Spacing.MD, Spacing.LG],
        ),
        width="100%",
    )
