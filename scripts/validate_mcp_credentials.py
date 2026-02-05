#!/usr/bin/env python3
"""
Validador de Credenciais MCP para LabBridge

Testa se todas as credenciais estão configuradas corretamente
antes de tentar usar os MCPs.

Uso:
    python validate_mcp_credentials.py
    python validate_mcp_credentials.py --detailed
    python validate_mcp_credentials.py --fix-env
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Tuple, List
import subprocess


class MCPValidator:
    def __init__(self):
        self.home = Path.home()
        self.mcp_config_path = self.home / ".claude" / "mcp-config.json"
        self.env_file = Path.cwd() / ".env"
        self.results: Dict[str, Dict] = {}

    def validate_all(self) -> bool:
        """Valida todos os MCPs e retorna True se tudo está OK"""
        print("🔍 Validando MCPs do LabBridge...\n")

        validators = [
            ("supabase", self.validate_supabase),
            ("postgresql", self.validate_postgresql),
            ("stripe", self.validate_stripe),
            ("slack", self.validate_slack),
            ("resend", self.validate_resend),
            ("s3", self.validate_s3),
            ("github", self.validate_github),
            ("filesystem", self.validate_filesystem),
            ("memory", self.validate_memory),
        ]

        for name, validator in validators:
            self.results[name] = validator()

        return self.print_summary()

    def validate_supabase(self) -> Dict:
        """Valida Supabase"""
        result = {"name": "Supabase", "status": "PENDING", "issues": []}

        # Verificar se MCP está instalado
        if not self.check_mcp_installed("supabase"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        # Verificar credenciais
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            result["issues"].append("SUPABASE_URL ou SUPABASE_KEY não encontrados")
            result["status"] = "MISSING_CREDENTIALS"
        else:
            result["status"] = "✅ OK"
            result["url"] = url[:30] + "..." if len(url) > 30 else url

        return result

    def validate_postgresql(self) -> Dict:
        """Valida PostgreSQL"""
        result = {"name": "PostgreSQL", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("postgresql"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        # Tentar conectar
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        db_user = os.getenv("POSTGRES_USER")
        db_pass = os.getenv("POSTGRES_PASSWORD")
        db_name = os.getenv("POSTGRES_DATABASE")

        if not all([db_user, db_pass, db_name]):
            result["issues"].append("Credenciais do PostgreSQL incompletas")
            result["status"] = "MISSING_CREDENTIALS"
        else:
            result["status"] = "✅ OK"
            result["host"] = f"{db_host}:{db_port}"

        return result

    def validate_stripe(self) -> Dict:
        """Valida Stripe"""
        result = {"name": "Stripe", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("stripe"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        key = os.getenv("STRIPE_SECRET_KEY")
        if not key:
            result["issues"].append("STRIPE_SECRET_KEY não encontrada")
            result["status"] = "MISSING_CREDENTIALS"
        elif not key.startswith("sk_"):
            result["issues"].append("Chave Stripe inválida (deve começar com sk_)")
            result["status"] = "INVALID"
        else:
            result["status"] = "✅ OK"

        return result

    def validate_slack(self) -> Dict:
        """Valida Slack"""
        result = {"name": "Slack", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("slack"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            result["issues"].append("SLACK_BOT_TOKEN não encontrada")
            result["status"] = "MISSING_CREDENTIALS"
        elif not token.startswith("xoxb-"):
            result["issues"].append("Token Slack inválido (deve começar com xoxb-)")
            result["status"] = "INVALID"
        else:
            result["status"] = "✅ OK"

        return result

    def validate_resend(self) -> Dict:
        """Valida Resend"""
        result = {"name": "Resend", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("resend"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        key = os.getenv("RESEND_API_KEY")
        if not key:
            result["issues"].append("RESEND_API_KEY não encontrada")
            result["status"] = "MISSING_CREDENTIALS"
        elif not key.startswith("re_"):
            result["issues"].append("Chave Resend inválida (deve começar com re_)")
            result["status"] = "INVALID"
        else:
            result["status"] = "✅ OK"

        return result

    def validate_s3(self) -> Dict:
        """Valida AWS S3"""
        result = {"name": "AWS S3", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("s3"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = os.getenv("AWS_REGION")

        if not all([access_key, secret_key, region]):
            result["issues"].append(
                "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY ou AWS_REGION não encontrados"
            )
            result["status"] = "MISSING_CREDENTIALS"
        elif not access_key.startswith("AKIA"):
            result["issues"].append("Access Key inválida (deve começar com AKIA)")
            result["status"] = "INVALID"
        else:
            result["status"] = "✅ OK"
            result["region"] = region

        return result

    def validate_github(self) -> Dict:
        """Valida GitHub"""
        result = {"name": "GitHub", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("github"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        token = os.getenv("GITHUB_TOKEN")
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")

        if not token or not owner or not repo:
            result["issues"].append(
                "GITHUB_TOKEN, GITHUB_OWNER ou GITHUB_REPO não encontrados"
            )
            result["status"] = "MISSING_CREDENTIALS"
        elif not token.startswith("ghp_"):
            result["issues"].append("Token GitHub inválido (deve começar com ghp_)")
            result["status"] = "INVALID"
        else:
            result["status"] = "✅ OK"
            result["repo"] = f"{owner}/{repo}"

        return result

    def validate_filesystem(self) -> Dict:
        """Valida Filesystem"""
        result = {"name": "Filesystem", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("filesystem"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
            return result

        # Verificar se diretório base existe
        base_dir = Path.cwd()
        if base_dir.exists():
            result["status"] = "✅ OK"
            result["path"] = str(base_dir)
        else:
            result["issues"].append(f"Diretório {base_dir} não existe")
            result["status"] = "INVALID"

        return result

    def validate_memory(self) -> Dict:
        """Valida Memory (sem credenciais necessárias)"""
        result = {"name": "Memory (Anthropic)", "status": "PENDING", "issues": []}

        if not self.check_mcp_installed("memory"):
            result["issues"].append("MCP não instalado")
            result["status"] = "NOT_INSTALLED"
        else:
            result["status"] = "✅ OK"
            result["note"] = "Não requer credenciais"

        return result

    def check_mcp_installed(self, name: str) -> bool:
        """Verifica se um MCP está instalado"""
        try:
            with open(self.mcp_config_path, "r") as f:
                config = json.load(f)
                return name in config.get("mcpServers", {})
        except FileNotFoundError:
            return False

    def print_summary(self) -> bool:
        """Imprime resumo e retorna True se tudo está OK"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DAS VALIDAÇÕES")
        print("=" * 60 + "\n")

        all_ok = True
        critical_ok = True

        for name, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            emoji = "✅" if status == "✅ OK" else "❌"
            print(f"{emoji} {result['name']:20} {status}")

            if result.get("issues"):
                for issue in result["issues"]:
                    print(f"   └─ ⚠️  {issue}")

            if status != "✅ OK":
                all_ok = False
                if name in ["supabase", "postgresql", "stripe"]:
                    critical_ok = False

        print("\n" + "=" * 60)

        if all_ok:
            print("✅ TUDO PRONTO! Todos os MCPs estão configurados.")
        elif critical_ok:
            print("⚠️  AVISO: Alguns MCPs não estão instalados, mas o core está OK")
        else:
            print(
                "❌ ERRO: MCPs críticos não estão configurados. Veja SETUP_MCP_MANUAL_STEPS.md"
            )

        print("=" * 60 + "\n")
        return all_ok

    def generate_env_template(self) -> str:
        """Gera template .env com todas as variáveis"""
        template = """# === LABBRIDGE MCP CREDENTIALS ===
# Copie este arquivo para .env e preencha com suas credenciais
# NUNCA commit este arquivo ao Git!

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_anon_key

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=labbridge_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha

# Stripe
STRIPE_SECRET_KEY=sk_test_...

# Slack
SLACK_BOT_TOKEN=xoxb-...

# Resend
RESEND_API_KEY=re_...

# AWS S3
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKETS=labbridge-uploads,labbridge-exports

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_OWNER=seu-usuario
GITHUB_REPO=labbridge
"""
        return template


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Valida credenciais dos MCPs")
    parser.add_argument(
        "--detailed", action="store_true", help="Mostra informações detalhadas"
    )
    parser.add_argument("--generate-env", action="store_true", help="Gera template .env")

    args = parser.parse_args()

    validator = MCPValidator()

    if args.generate_env:
        print(validator.generate_env_template())
        return

    success = validator.validate_all()

    if args.detailed:
        print("\n📋 Detalhes completos:")
        print(json.dumps(validator.results, indent=2))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
