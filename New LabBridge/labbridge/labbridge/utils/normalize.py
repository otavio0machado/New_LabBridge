"""
Funcoes de normalizacao compartilhadas - fonte unica de verdade.
Usadas por comparison.py, ai_analysis.py, analysis_module.py, pdf_processor.py
"""
import re
import unicodedata
from decimal import Decimal
from typing import Any


def normalize_patient_name(name: str) -> str:
    """
    Normaliza nome do paciente para matching robusto.
    - Remove acentos
    - Converte para maiusculas
    - Remove espacos extras
    - Remove caracteres especiais
    """
    if not name:
        return ""
    name = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('ASCII')
    name = name.upper()
    name = re.sub(r'[^A-Z0-9\s]', '', name)
    name = ' '.join(name.split())
    return name.strip()


def normalize_exam_name(name: str) -> str:
    """
    Normaliza nome do exame para matching.
    - Remove acentos
    - Converte para maiusculas
    - Remove caracteres especiais
    """
    if not name:
        return ""
    name = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('ASCII')
    name = name.upper()
    name = re.sub(r'[^A-Z0-9\s]', '', name)
    name = ' '.join(name.split())
    return name.strip()


def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """Converte valor para Decimal de forma segura."""
    if value is None:
        return default
    try:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, str):
            value = value.replace('.', '').replace(',', '.')
        return Decimal(str(value))
    except (ValueError, TypeError, ArithmeticError):
        return default


def format_currency_br(value) -> str:
    """Formata valor como moeda brasileira (R$ X.XXX,XX)."""
    try:
        val = float(value)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"
