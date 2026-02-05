import reflex as rx
import os

def _get_api_url() -> str:
    """Determina a API URL baseado no ambiente.

    Em producao (Railway), a API_URL deve apontar para o dominio publico.
    O Reflex usa isso para o frontend saber onde conectar o WebSocket.
    """
    # Se API_URL foi definida explicitamente, usar ela
    api_url = os.getenv("API_URL", "")
    if api_url:
        return api_url

    # Se APP_URL foi definida (dominio do Railway), derivar API_URL dela
    app_url = os.getenv("APP_URL", "")
    if app_url and app_url != "http://localhost:3000":
        # Em producao, backend e frontend estao no mesmo dominio (via nginx)
        return app_url

    # Fallback para desenvolvimento local
    return "http://localhost:8000"


def _parse_cors_origins(raw: str) -> list[str]:
    if not raw:
        # Em producao, adicionar o dominio do Railway
        app_url = os.getenv("APP_URL", "")
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ]
        if app_url and app_url not in origins:
            origins.insert(0, app_url)
            # Adicionar versao https se nao tiver
            if app_url.startswith("http://"):
                https_url = app_url.replace("http://", "https://", 1)
                origins.insert(0, https_url)
            elif app_url.startswith("https://"):
                http_url = app_url.replace("https://", "http://", 1)
                origins.append(http_url)
        return origins
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:3000", "http://127.0.0.1:3000"]

config = rx.Config(
    app_name="labbridge",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    # Configuracoes do servidor
    frontend_port=int(os.getenv("FRONTEND_PORT", "3000")),
    backend_port=int(os.getenv("BACKEND_PORT", "8000")),
    api_url=_get_api_url(),
    cors_allowed_origins=_parse_cors_origins(os.getenv("CORS_ALLOWED_ORIGINS", "")),
)
