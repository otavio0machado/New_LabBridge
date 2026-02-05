"""
Configuracoes centralizadas da aplicacao
"""
import os
import logging
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)

# Carregar variaveis de ambiente procurando em diretorios pais
load_dotenv(find_dotenv())


class Config:
    """Configuracoes da aplicacao"""

    # Ambiente: development | production
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    IS_PRODUCTION = ENVIRONMENT == "production"

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

    # Auth local (somente desenvolvimento)
    AUTH_EMAIL = os.getenv("AUTH_EMAIL", "")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")

    # App
    APP_URL = os.getenv("APP_URL", "http://localhost:3000")

    @classmethod
    def validate(cls):
        """Valida configuracoes obrigatorias para producao"""
        missing = []

        if cls.IS_PRODUCTION:
            if not cls.SUPABASE_URL:
                missing.append("SUPABASE_URL")
            if not cls.SUPABASE_KEY:
                missing.append("SUPABASE_KEY")
            if cls.AUTH_EMAIL or cls.AUTH_PASSWORD:
                logger.warning("AUTH_EMAIL/AUTH_PASSWORD definidos em producao. "
                               "Login local deve ser desabilitado.")

        if missing:
            raise ValueError(
                f"Variaveis de ambiente obrigatorias faltando: {', '.join(missing)}\n"
                f"Consulte .env.example para ver todas as variaveis."
            )

    @classmethod
    def is_supabase_configured(cls) -> bool:
        """Verifica se Supabase esta configurado"""
        return bool(cls.SUPABASE_URL and cls.SUPABASE_KEY)
