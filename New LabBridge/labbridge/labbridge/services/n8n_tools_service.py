"""
Serviço de Tools para integração com n8n AI Agent.

Este módulo fornece funções que podem ser chamadas pelo n8n
através de HTTP requests, permitindo que o AI Agent execute
operações complexas no backend.

Seguindo SKILL "O Oráculo" - Integração AI e Prompts
"""

from typing import Optional
from dataclasses import dataclass
import math


@dataclass
# WestgardResult removido.


class N8NToolsService:
    """
    Serviço que implementa as ferramentas (tools) utilizadas pelo AI Agent do n8n.
    
    Cada método corresponde a uma ferramenta que o agente pode invocar.
    """
    
    # Westgard interpreter has been removed.
    
    @staticmethod
    def gerar_contestacao(
        convenio: str = "[Nome do Convênio]",
        exame: str = "[Nome do Exame]",
        valor_cobrado: float = 0,
        valor_pago: float = 0,
        motivo: str = "divergência de valores",
        paciente: str = "[Nome do Paciente]"
    ) -> dict:
        """
        Gera uma carta profissional para contestar uma glosa de convênio.
        
        Args:
            convenio: Nome do convênio
            exame: Nome do exame
            valor_cobrado: Valor que foi cobrado
            valor_pago: Valor que foi pago pelo convênio
            motivo: Motivo alegado pela glosa
            paciente: Nome do paciente
            
        Returns:
            Dicionário com a carta formatada e próximos passos
        """
        from datetime import datetime
        
        diferenca = valor_cobrado - valor_pago
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        
        def format_brl(v: float) -> str:
            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        carta = f"""
╔══════════════════════════════════════════════════════════════╗
║           CARTA DE CONTESTAÇÃO DE GLOSA                       ║
╚══════════════════════════════════════════════════════════════╝

À {convenio}
Setor de Auditoria e Faturamento

Ref.: Contestação de Glosa - Procedimento {exame}
Data: {data_hoje}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prezados Senhores,

Vimos, por meio desta, CONTESTAR FORMALMENTE a glosa aplicada ao procedimento abaixo:

┌─────────────────────────────────────────────────────────────┐
│ 📋 DADOS DO PROCEDIMENTO                                     │
├─────────────────────────────────────────────────────────────┤
│ Paciente:        {paciente[:40]:<40}│
│ Procedimento:    {exame[:40]:<40}│
│ Valor Cobrado:   R$ {format_brl(valor_cobrado):<37}│
│ Valor Pago:      R$ {format_brl(valor_pago):<37}│
│ Diferença:       R$ {format_brl(diferenca):<37}│
│ Motivo Alegado:  {motivo[:40]:<40}│
└─────────────────────────────────────────────────────────────┘

📌 FUNDAMENTAÇÃO:

1. O procedimento foi realizado em conformidade com as normas técnicas
   vigentes e o contrato estabelecido entre as partes.

2. A cobrança está de acordo com a tabela de preços pactuada,
   conforme anexo contratual de [inserir data do contrato].

3. Toda documentação comprobatória encontra-se disponível para
   verificação (requisição médica, resultado do exame, nota fiscal).

4. Não houve duplicidade de cobrança ou erro de digitação.

📎 DOCUMENTOS ANEXOS:
   ☐ Cópia da requisição médica
   ☐ Laudo do exame
   ☐ Tabela de preços contratada
   ☐ Nota fiscal correspondente

🎯 SOLICITAÇÃO:
Solicitamos a REVISÃO da glosa e o PAGAMENTO da diferença de
R$ {format_brl(diferenca)} no prazo legal de 30 dias.

Aguardamos manifestação.

Atenciosamente,

_________________________________
Laboratório Biodiagnóstico
Setor de Faturamento
Telefone: (XX) XXXX-XXXX
Email: faturamento@biodiagnostico.com.br

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return {
            "sucesso": True,
            "carta_contestacao": carta,
            "resumo": {
                "convenio": convenio,
                "exame": exame,
                "diferenca": f"R$ {format_brl(diferenca)}"
            },
            "proximos_passos": [
                "1. Revise e personalize os campos entre colchetes [ ]",
                "2. Anexe os documentos listados",
                "3. Protocole junto ao convênio (guarde o número de protocolo!)",
                "4. Acompanhe a resposta em até 30 dias",
                "5. Se necessário, escale para recurso de 2ª instância"
            ]
        }
    
    @staticmethod
    def comparar_tabelas(exame: str = "HEMOGRAMA") -> dict:
        """
        Compara valores entre a tabela do laboratório e as tabelas dos convênios.
        
        Args:
            exame: Nome do exame a comparar
            
        Returns:
            Dicionário com comparativo de preços
        """
        exame_consultado = exame.upper()
        
        # Tabelas simuladas (em produção viriam do Supabase)
        tabela_lab = {
            "HEMOGRAMA": 35.00,
            "GLICOSE": 12.50,
            "COLESTEROL TOTAL": 18.00,
            "TSH": 45.00,
            "T4 LIVRE": 42.00,
            "CREATININA": 15.00,
            "UREIA": 12.00,
            "ACIDO URICO": 14.00
        }
        
        tabelas_convenios = {
            "UNIMED": {
                "HEMOGRAMA": 32.00, "GLICOSE": 10.00, "COLESTEROL TOTAL": 15.00,
                "TSH": 40.00, "T4 LIVRE": 38.00, "CREATININA": 13.00
            },
            "BRADESCO": {
                "HEMOGRAMA": 30.00, "GLICOSE": 11.00, "COLESTEROL TOTAL": 16.50,
                "TSH": 42.00, "T4 LIVRE": 40.00, "CREATININA": 14.00
            },
            "AMIL": {
                "HEMOGRAMA": 28.00, "GLICOSE": 9.50, "COLESTEROL TOTAL": 14.00,
                "TSH": 38.00, "T4 LIVRE": 36.00, "CREATININA": 12.00
            },
            "SULAMERICA": {
                "HEMOGRAMA": 33.00, "GLICOSE": 11.50, "COLESTEROL TOTAL": 17.00,
                "TSH": 43.00, "T4 LIVRE": 41.00, "CREATININA": 14.50
            }
        }
        
        valor_lab = tabela_lab.get(exame_consultado, 0)
        comparativo = []
        
        for convenio, tabela in tabelas_convenios.items():
            valor_conv = tabela.get(exame_consultado, 0)
            if valor_conv > 0:
                diferenca = valor_lab - valor_conv
                percentual = ((diferenca / valor_lab) * 100) if valor_lab > 0 else 0
                
                if diferenca > 5:
                    status = "⚠️ DEFASADO"
                elif diferenca > 2:
                    status = "🟡 ATENÇÃO"
                else:
                    status = "✅ OK"
                
                comparativo.append({
                    "convenio": convenio,
                    "valor_lab": f"R$ {valor_lab:.2f}",
                    "valor_convenio": f"R$ {valor_conv:.2f}",
                    "diferenca": f"R$ {diferenca:.2f}",
                    "percentual": f"{percentual:.1f}%",
                    "status": status
                })
        
        # Ordenar do mais defasado para o menos
        comparativo.sort(key=lambda x: float(x["diferenca"].replace("R$ ", "")), reverse=True)
        
        convenio_mais_defasado = comparativo[0] if comparativo else None
        diferenca_maior = float(convenio_mais_defasado["diferenca"].replace("R$ ", "")) if convenio_mais_defasado else 0
        
        if convenio_mais_defasado and diferenca_maior > 5:
            recomendacao = f"📞 Priorizar renegociação de tabela com {convenio_mais_defasado['convenio']}"
        else:
            recomendacao = "✅ Tabelas dentro do esperado"
        
        return {
            "sucesso": True,
            "exame_consultado": exame_consultado,
            "valor_tabela_laboratorio": f"R$ {valor_lab:.2f}",
            "comparativo_convenios": comparativo,
            "convenio_mais_defasado": convenio_mais_defasado,
            "recomendacao": recomendacao,
            "metafora": (
                "💰 Tabelas defasadas são como cupons de desconto que você dá sem querer: "
                "o cliente (convênio) paga menos do que deveria."
            )
        }


# Instância global do serviço
n8n_tools_service = N8NToolsService()
