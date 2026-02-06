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

    # Stripe
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Email (Resend ou SMTP)
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

    # Auth local (somente desenvolvimento)
    AUTH_EMAIL = os.getenv("AUTH_EMAIL", "")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")

    # App
    APP_URL = os.getenv("APP_URL", "http://localhost:3000")

    @classmethod
    def validate(cls):
        """Valida configuracoes obrigatorias para producao"""
        missing = []
        warnings = []

        if cls.IS_PRODUCTION:
            if not cls.SUPABASE_URL:
                missing.append("SUPABASE_URL")
            if not cls.SUPABASE_KEY:
                missing.append("SUPABASE_KEY")
            if cls.AUTH_EMAIL or cls.AUTH_PASSWORD:
                logger.warning("AUTH_EMAIL/AUTH_PASSWORD definidos em producao - "
                               "login local sera ignorado.")
            if not cls.GEMINI_API_KEY and not cls.OPENAI_API_KEY:
                warnings.append("Nenhuma chave de IA configurada (GEMINI_API_KEY ou OPENAI_API_KEY)")
            if not cls.STRIPE_SECRET_KEY:
                warnings.append("STRIPE_SECRET_KEY nao configurada - pagamentos em modo simulado")
            if not cls.RESEND_API_KEY:
                warnings.append("RESEND_API_KEY nao configurada - emails em modo simulado")
            if not cls.CLOUDINARY_CLOUD_NAME:
                warnings.append("CLOUDINARY nao configurado - uploads desabilitados")
        else:
            # Desenvolvimento - avisos leves
            if not cls.SUPABASE_URL:
                logger.info("SUPABASE_URL nao configurada - usando armazenamento local")

        for w in warnings:
            logger.warning(w)

        if missing:
            raise ValueError(
                f"Variaveis de ambiente obrigatorias faltando: {', '.join(missing)}\n"
                f"Consulte .env.example para ver todas as variaveis."
            )

        logger.info(f"Config validada (env={cls.ENVIRONMENT}, supabase={'OK' if cls.is_supabase_configured() else 'OFF'})")

    @classmethod
    def is_supabase_configured(cls) -> bool:
        """Verifica se Supabase esta configurado"""
        return bool(cls.SUPABASE_URL and cls.SUPABASE_KEY)
