"""
Biodiagnóstico Lab - Sistema de Administração
Design oficial baseado na identidade visual do laboratório
"""
import logging
import reflex as rx
from .config import Config
from .state import State

logger = logging.getLogger(__name__)

# Validar configuracoes obrigatorias na inicializacao
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuracao invalida: {e}")
    raise
from .components.navbar import navbar, mobile_nav
from .components.floating_chat import floating_chat
from .pages.login import login_page
from .pages.conversor import conversor_page
from .pages.analise import analise_page
from .pages.subscription import subscription_page
from .pages.settings import settings_page
from .pages.help import help_page
from .pages.reports import reports_page
from .pages.history import history_page
from .pages.team import team_page
from .pages.integrations import integrations_page
from .pages.auth_callback import auth_callback

from .pages.dashboard import dashboard_page
from .styles import Color


from .pages.insight_chat import insight_chat_page

def main_content() -> rx.Component:
    """Conteúdo principal baseado na página atual"""
    return rx.match(
        State.current_page,
        ("dashboard", dashboard_page()),
        ("conversor", conversor_page()),
        ("analise", analise_page()),
        ("subscription", subscription_page()),
        ("settings", settings_page()),
        ("help", help_page()),
        ("reports", reports_page()),
        ("history", history_page()),
        ("team", team_page()),
        ("integrations", integrations_page()),

        ("detetive", insight_chat_page()), # New page match
        dashboard_page(),  # default
    )


def authenticated_layout(content: rx.Component = None) -> rx.Component:
    """
    Layout principal com Sidebar lateral fixa (desktop) + Top bar
    Seguindo: UI_UX_STRUCTURE_LABBRIDGE.md
    """
    return rx.box(
        # Navbar (Sidebar + Top bar)
        navbar(),

        # Área de conteúdo principal
        rx.box(
            rx.box(
                content if content else main_content(),
                width="100%",
                max_width="1200px",
                margin_x="auto",
                padding_x=["1rem", "1.5rem", "2rem"],
                padding_y=["1rem", "1.5rem", "2rem"],
            ),
            # Margin-left para compensar a sidebar em desktop
            margin_left=["0", "0", "240px", "260px"],
            width=["100%", "100%", "calc(100% - 240px)", "calc(100% - 260px)"],
            min_height="100vh",
            bg=Color.BACKGROUND,
            transition="margin-left 0.3s ease",
        ),

        # Floating AI Chat (Bio IA)
        floating_chat(),

        class_name="font-sans",
    )


def index() -> rx.Component:
    """Página principal - Login obrigatório para acesso interno"""
    return rx.cond(
        State.is_authenticated,
        authenticated_layout(),
        login_page()
    )


def index_dashboard() -> rx.Component:
    """Rota Dashboard"""
    return authenticated_layout(dashboard_page())

def route_conversor() -> rx.Component:
    """Rota Conversor"""
    return authenticated_layout(conversor_page())

def route_analise() -> rx.Component:
    """Rota Análise"""
    return authenticated_layout(analise_page())



def route_insights() -> rx.Component:
    """Rota Detetive de Dados"""
    return authenticated_layout(insight_chat_page())

def route_subscription() -> rx.Component:
    """Rota Assinatura"""
    return authenticated_layout(subscription_page())

def route_settings() -> rx.Component:
    """Rota Configurações"""
    return authenticated_layout(settings_page())

def route_help() -> rx.Component:
    """Rota Central de Ajuda"""
    return authenticated_layout(help_page())

def route_reports() -> rx.Component:
    return authenticated_layout(reports_page())

def route_history() -> rx.Component:
    return authenticated_layout(history_page())

def route_team() -> rx.Component:
    return authenticated_layout(team_page())

def route_integrations() -> rx.Component:
    return authenticated_layout(integrations_page())

# Configurar aplicação - LabBridge Design System
# Cores: Azul (ações principais), Verde (sucesso), Amarelo-esverdeado (atenção)
app = rx.App(
    theme=rx.theme(
        accent_color="blue",
        gray_color="slate",
        radius="large",
        appearance="light",
    ),
    head_components=[
        # Favicon
        rx.el.link(rel="icon", href="/favicon.ico", sizes="any"),
        rx.el.link(rel="icon", href="/favicon.png", type="image/png"),
        rx.el.link(rel="apple-touch-icon", href="/apple-touch-icon.png"),
        # PWA
        rx.el.link(rel="manifest", href="/manifest.json"),
        rx.el.meta(name="theme-color", content="#2563EB"),
        rx.el.meta(name="apple-mobile-web-app-capable", content="yes"),
        rx.el.meta(name="mobile-web-app-capable", content="yes"),
        rx.el.meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
        # SEO
        rx.el.meta(name="description", content="LabBridge - Sistema de Auditoria & Inteligencia Laboratorial. Seguranca e precisao em cada analise."),
        rx.el.meta(name="author", content="LabBridge"),
        # Open Graph
        rx.el.meta(property="og:title", content="LabBridge"),
        rx.el.meta(property="og:description", content="Sistema de Auditoria & Inteligencia Laboratorial"),
        rx.el.meta(property="og:type", content="website"),
        rx.el.meta(property="og:image", content="/labbridge_logo.png"),
    ],
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
        "/custom.css",
    ],
)

# Adicionar rotas explícitas - Isso resolve os erros 404 e permite refresh
app.add_page(index, route="/", title="LabBridge - Login")
app.add_page(index_dashboard, route="/dashboard", title="LabBridge - Dashboard")
app.add_page(route_conversor, route="/conversor", title="LabBridge - Importador de Dados")
app.add_page(route_analise, route="/analise", title="LabBridge - Auditoria Financeira", on_load=State.load_saved_analyses)
app.add_page(route_subscription, route="/subscription", title="LabBridge - Planos e Preços")
app.add_page(route_settings, route="/settings", title="LabBridge - Configurações")
app.add_page(route_help, route="/help", title="LabBridge - Central de Ajuda")
app.add_page(route_insights, route="/detetive", title="LabBridge - Assistente IA")
app.add_page(route_reports, route="/reports", title="LabBridge - Relatórios Detalhados")
app.add_page(route_history, route="/history", title="LabBridge - Histórico de Auditorias")
app.add_page(route_team, route="/team", title="LabBridge - Gestão de Usuários")
app.add_page(route_integrations, route="/integrations", title="LabBridge - Integrações")
app.add_page(auth_callback, route="/auth/callback", title="LabBridge - Autenticação")
