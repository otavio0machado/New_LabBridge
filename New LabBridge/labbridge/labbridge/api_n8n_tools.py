"""
API Endpoints para integração com n8n AI Agent Tools.

Estes endpoints são chamados pelo n8n quando o AI Agent precisa
executar ferramentas que requerem processamento no backend.

Seguindo SKILL "O Oráculo" - Integração AI e Prompts
"""

import reflex as rx
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.n8n_tools_service import n8n_tools_service


# ============================================================
# Modelos Pydantic para validação de entrada
# ============================================================

# Westgard endpoint removed.


@n8n_tools_router.post("/contestacao")
async def tool_contestacao(data: ContestacaoInput):
    """
    Endpoint para a ferramenta gerar_contestacao.
    
    Gera uma carta profissional para contestar uma glosa de convênio.
    
    Chamado pelo n8n via toolHttpRequest.
    """
    try:
        result = n8n_tools_service.gerar_contestacao(
            convenio=data.convenio,
            exame=data.exame,
            valor_cobrado=data.valor_cobrado,
            valor_pago=data.valor_pago,
            motivo=data.motivo,
            paciente=data.paciente
        )
        return result
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@n8n_tools_router.post("/comparar-tabelas")
async def tool_comparar_tabelas(data: CompararTabelasInput):
    """
    Endpoint para a ferramenta comparar_tabelas.
    
    Compara valores entre a tabela do laboratório e as tabelas dos convênios.
    
    Chamado pelo n8n via toolHttpRequest.
    """
    try:
        result = n8n_tools_service.comparar_tabelas(exame=data.exame)
        return result
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@n8n_tools_router.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    return {"status": "ok", "service": "n8n-tools"}


# ============================================================
# Função para registrar o router no app Reflex
# ============================================================

def register_n8n_tools_api(app: rx.App):
    """
    Registra os endpoints de tools do n8n no app Reflex/FastAPI.
    
    Deve ser chamado após a criação do app.
    
    Exemplo:
        app = rx.App(...)
        register_n8n_tools_api(app)
    """
    # Reflex expõe uma instância FastAPI que podemos estender
    # Isso será feito no arquivo principal ou em um hook de inicialização
    pass
