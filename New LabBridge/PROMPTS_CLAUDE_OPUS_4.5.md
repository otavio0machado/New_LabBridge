# 🤖 PROMPTS PARA CLAUDE OPUS 4.5 - LABBRIDGE

**Objetivo:** Guiar o Claude Opus 4.5 para implementar as features do LabBridge
**Sprint:** 1-3 (completo)
**Data:** 05 de Fevereiro de 2026

---

## 📋 COMO USAR ESTE DOCUMENTO

1. **Copie o prompt inteiro** (entre `---`)
2. **Cole no Claude Opus 4.5** (ou Claude Code)
3. **Execute as tarefas** conforme pedido
4. **Valide os resultados**

---

## 🔴 SPRINT 1: FEATURES CRÍTICAS

---

# PROMPT 1: LOGIN SUPABASE AUTH

```
---INICIO PROMPT---

Você é um desenvolvedor senior especialista em Python/Reflex e Supabase.

CONTEXTO:
- Projeto: LabBridge (aplicação SaaS de auditoria financeira)
- Framework: Reflex (Python para frontend + backend)
- Banco de Dados: Supabase PostgreSQL
- Objetivo: Implementar autenticação Supabase completa

TAREFA: Migrar autenticação de hardcoded (.env) para Supabase Auth

ESTRUTURA DO PROJETO:
```
labbridge/
├─ .env (tem SUPABASE_URL e SUPABASE_KEY)
├─ labbridge/
│  ├─ services/
│  │  └─ auth_service.py (PRECISA MODIFICAR)
│  ├─ states/
│  │  └─ auth_state.py (PRECISA MODIFICAR)
│  └─ pages/
│     ├─ login.py (PRECISA MODIFICAR)
│     └─ auth_callback.py (VERIFICAR)
```

REQUISITOS:
1. ✅ Usar Supabase Auth SDK (supabase-py)
2. ✅ Implementar signup (registro de novo usuário)
3. ✅ Implementar signin (login)
4. ✅ Implementar logout
5. ✅ Implementar verificação de sessão
6. ✅ Criar tabela user_profiles vinculada
7. ✅ Implementar recuperação de senha (email)
8. ✅ Testes básicos

CODIGO EXISTENTE:

File: auth_service.py (ATUAL - QUEBRADO)
```python
# Código atual com hardcoded - SUBSTITUIR
AUTH_EMAIL = os.getenv("AUTH_EMAIL", "admin@labbridge.com")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "senha_segura")

def login(email: str, password: str) -> bool:
    return email == AUTH_EMAIL and password == AUTH_PASSWORD
```

ESTRUTURA ESPERADA:

File: auth_service.py (NOVO)
```python
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

class AuthService:
    def __init__(self, url: str, key: str):
        # Inicializar cliente Supabase
        # url: https://uqoykrznpomtftzaenbl.supabase.co
        # key: SERVICE_ROLE_KEY do .env

    async def signup(self, email: str, password: str, full_name: str) -> dict:
        # Criar novo usuário em auth.users
        # Criar registro em user_profiles com tenant_id padrão
        # Retornar {'success': True, 'user': {...}} ou {'success': False, 'error': '...'}

    async def signin(self, email: str, password: str) -> dict:
        # Autenticar usuário
        # Retornar session e user_id

    async def logout(self) -> dict:
        # Logout do usuário

    async def get_current_user(self, access_token: str):
        # Buscar dados do usuário autenticado
        # Validar token

    async def reset_password(self, email: str) -> dict:
        # Enviar email de recuperação de senha

    async def confirm_password_reset(self, token: str, new_password: str) -> dict:
        # Confirmar reset de senha
```

File: auth_state.py (REFLEX STATE - NOVO)
```python
class AuthState(rx.State):
    # User data
    user_id: str = ""
    email: str = ""
    full_name: str = ""
    tenant_id: str = ""
    role: str = "analyst"  # admin, analyst, viewer
    is_authenticated: bool = False
    is_loading: bool = False

    # Errors
    error_message: str = ""

    # Methods
    async def handle_signup(self, email: str, password: str, full_name: str):
        # Chamar auth_service.signup()
        # Atualizar estado

    async def handle_signin(self, email: str, password: str):
        # Chamar auth_service.signin()
        # Armazenar session
        # Redirecionar para /dashboard

    async def handle_logout(self):
        # Chamar auth_service.logout()
        # Limpar estado
        # Redirecionar para /login

    async def check_session(self):
        # Verificar se usuário está autenticado
        # Restaurar sessão se necessário

    async def handle_reset_password(self, email: str):
        # Chamar auth_service.reset_password()
```

DEPENDÊNCIAS NECESSÁRIAS:
- supabase>=2.1.0 (já instalado)
- python-dotenv (já instalado)

BANCO DE DADOS - TABELAS EXISTENTES:
- auth.users (gerenciado por Supabase)
- user_profiles (tabela criada, com colunas: id, email, full_name, tenant_id, role)

CONSIDERAÇÕES DE SEGURANÇA:
1. ✅ Nunca enviar Service Role Key ao frontend
2. ✅ Validar tokens em cada requisição
3. ✅ Usar RLS (Row Level Security) do Supabase
4. ✅ Hash de senhas (Supabase faz automaticamente)
5. ✅ Proteção contra CSRF

FLUXO ESPERADO:
1. Usuário entra em /login
2. Preenche email e senha
3. Clica em "Entrar" ou "Cadastrar"
4. Sistema chama AuthState.handle_signin() ou handle_signup()
5. Se sucesso, redireciona para /dashboard
6. Se erro, mostra mensagem

TESTES:
- [ ] Signup com email válido
- [ ] Signup com email duplicado (deve falhar)
- [ ] Signin com credenciais corretas
- [ ] Signin com credenciais erradas
- [ ] Logout e logout realizado
- [ ] Reset de senha envia email
- [ ] Session persiste após refresh da página

ENTREGA:
1. Arquivo auth_service.py (completo)
2. Arquivo auth_state.py (modificado)
3. Arquivo login.py (modificado para usar novo estado)
4. Arquivo requirements.txt (verificar dependências)
5. Script de testes (test_auth.py)
6. Documentação de como usar

CONTEXTO ADICIONAL:
- Projeto usa Reflex (React backend em Python)
- Estado é reativo (rx.State)
- Componentes seguem padrão Reflex
- Multi-tenant com tenant_id

Faça a implementação completa agora, incluindo:
1. ✅ Código funcional
2. ✅ Tratamento de erros robusto
3. ✅ Comentários explicativos
4. ✅ Type hints em Python
5. ✅ Validação de entrada
6. ✅ Logs para debug

---FIM PROMPT---
```

---

# PROMPT 2: LISTAR ANÁLISES SALVAS

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Histórico de análises salvas (listar, buscar, filtrar)
- Banco: Supabase (tabela saved_analyses)
- Usuário: Autenticado (com tenant_id validado)

TAREFA: Implementar listagem de análises salvas com filtros e paginação

ESTRUTURA:
```
labbridge/
├─ states/
│  └─ history_state.py (CRIAR/MODIFICAR)
├─ pages/
│  └─ history.py (MODIFICAR para usar dados reais)
├─ components/
│  └─ results.py (REUTILIZAR)
└─ services/
   └─ saved_analysis_service.py (USAR EXISTENTE)
```

TABELA DO BANCO:
```sql
saved_analyses (
    id: UUID,
    tenant_id: UUID,
    created_by: UUID,
    created_at: TIMESTAMP,
    name: VARCHAR,
    description: TEXT,
    analysis_date: DATE,
    status: VARCHAR (completed, draft, error),
    compulab_file_url: TEXT,
    simus_file_url: TEXT,
    analysis_report_url: TEXT,
    compulab_total: DECIMAL,
    simus_total: DECIMAL,
    difference: DECIMAL
)
```

REQUISITOS:
1. ✅ Buscar análises do usuário (filtrar por tenant_id)
2. ✅ Paginação (10-20 itens por página)
3. ✅ Ordenação (mais recentes primeiro)
4. ✅ Filtros: por data, status, nome
5. ✅ Busca por texto (nome/description)
6. ✅ Contador total de análises
7. ✅ Loading state
8. ✅ Tratamento de erro

ESTRUTURA DO STATE (history_state.py):
```python
class HistoryState(rx.State):
    # Data
    analyses: list[dict] = []
    total_count: int = 0
    current_page: int = 1
    per_page: int = 10

    # Filters
    search_query: str = ""
    status_filter: str = ""  # all, completed, draft, error
    date_from: str = ""
    date_to: str = ""

    # UI
    is_loading: bool = False
    error_message: str = ""

    # Methods
    async def load_analyses(self, page: int = 1):
        # Buscar análises do Supabase
        # Aplicar filtros
        # Retornar página específica

    async def search_analyses(self, query: str):
        # Busca de texto
        # Resetar página para 1

    async def filter_by_status(self, status: str):
        # Filtrar por status
        # Recarregar

    async def filter_by_date_range(self, date_from: str, date_to: str):
        # Filtrar por período
        # Recarregar

    async def delete_analysis(self, analysis_id: str):
        # Deletar análise (soft delete ou hard delete)
        # Recarregar lista

    async def get_analysis_detail(self, analysis_id: str) -> dict:
        # Buscar análise específica com todos os details
        # Retornar para poder reabrir
```

INTERFACE ESPERADA (history.py):
```
┌─────────────────────────────────────┐
│ Histórico de Análises               │
├─────────────────────────────────────┤
│ [🔍 Buscar] [📅 Filtro Data] [⚙️ Status] │
│                                     │
│ Total: 42 análises                  │
├─────────────────────────────────────┤
│ Análise 1  | 10/01/2026 | ✅ Pronto │
│ Análise 2  | 09/01/2026 | ⏳ Rascunho│
│ ...                                 │
├─────────────────────────────────────┤
│ < Anterior  [1] [2] [3] ...  Próximo> │
└─────────────────────────────────────┘
```

CÓDIGO DO SERVIÇO:
```python
class SavedAnalysisService:
    def __init__(self, supabase_client):
        self.client = supabase_client

    async def get_user_analyses(self, tenant_id: str, page: int = 1, per_page: int = 10):
        # SELECT * FROM saved_analyses
        # WHERE tenant_id = tenant_id
        # ORDER BY created_at DESC
        # LIMIT per_page OFFSET (page-1)*per_page

    async def search_analyses(self, tenant_id: str, query: str):
        # Busca por nome ou description (ILIKE)

    async def filter_analyses(self, tenant_id: str, filters: dict):
        # Aplicar múltiplos filtros

    async def get_analysis_by_id(self, analysis_id: str, tenant_id: str):
        # Buscar uma análise específica com todos os dados

    async def count_analyses(self, tenant_id: str, filters: dict = None):
        # Contar total de análises (para paginação)

    async def delete_analysis(self, analysis_id: str, tenant_id: str):
        # Deletar análise (validar tenant_id)
```

COMPONENTES A CRIAR:
1. AnalysisList - componente que lista as análises
2. AnalysisFilters - componente com filtros
3. AnalysisPagination - componente de paginação

FLUXO:
1. Página carrega → call load_analyses()
2. Usuário digita na busca → call search_analyses()
3. Usuário seleciona filtro → call filter_by_*()
4. Usuário muda página → call load_analyses(page=n)
5. Usuário clica em análise → call get_analysis_detail() + redireciona

VALIDAÇÕES:
- ✅ Validar tenant_id (segurança)
- ✅ Validar permissões do usuário
- ✅ Validar índices no banco (performance)
- ✅ Implementar cache se necessário

TESTES:
- [ ] Listar 50+ análises
- [ ] Paginação funciona
- [ ] Busca por nome funciona
- [ ] Filtro por status funciona
- [ ] Filtro por data funciona
- [ ] Deletar análise funciona
- [ ] Performance aceitável (<2s)

ENTREGA:
1. history_state.py (novo estado completo)
2. history.py (página modificada)
3. saved_analysis_service.py (método novo/atualizado)
4. Componentes reutilizáveis
5. Tests

---FIM PROMPT---
```

---

# PROMPT 3: REABRIR ANÁLISE SALVA

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Reabrir análise salva (carregar estado completo)
- Banco: Supabase (saved_analyses + analysis_items)
- Fluxo: Usuário clica em "Reabrir" → carrega análise original

TAREFA: Implementar carregamento completo de análise salva

ESTRUTURA:
```
labbridge/
├─ states/
│  ├─ analysis_state.py (MODIFICAR)
│  └─ history_state.py (JÁ TEM método get_analysis_detail)
├─ pages/
│  └─ analise.py (MODIFICAR)
└─ services/
   └─ saved_analysis_service.py (MÉTODOS NOVOS)
```

TABELAS:
```sql
saved_analyses {
    id, tenant_id, created_by, name, description,
    analysis_date, status,
    compulab_file_url, simus_file_url, analysis_report_url,
    compulab_total, simus_total, difference
}

analysis_items {
    id, analysis_id, item_type (missing_patient, missing_exam, divergence, extra_simus),
    patient_name, exam_name,
    compulab_value, simus_value, difference
}
```

REQUISITOS:
1. ✅ Carregar análise completa (saved_analyses)
2. ✅ Carregar todos os items (analysis_items)
3. ✅ Restaurar estado da aplicação
4. ✅ Mostrar resultados originais
5. ✅ Permitir re-export de PDF/CSV
6. ✅ Mostrar "Reanálise" se necessário
7. ✅ Auditoria de acesso (logs)

ESTRUTURA DO STATE (analysis_state.py - ADICIONAR):
```python
class AnalysisState(rx.State):
    # ... estado existente ...

    # Loaded Analysis
    loaded_analysis_id: str = ""
    loaded_from_history: bool = False
    original_analysis_date: str = ""

    async def load_analysis_from_history(self, analysis_id: str):
        # 1. Buscar saved_analyses no Supabase
        # 2. Buscar analysis_items no Supabase
        # 3. Restaurar estado:
        #    - compulab_data
        #    - simus_data
        #    - divergences
        #    - missing_exams
        #    - missing_patients
        # 4. Marcar loaded_from_history = True
        # 5. Atualizar UI

    def can_user_access_analysis(self, analysis_id: str, user_id: str) -> bool:
        # Validar se usuário pode acessar essa análise
        # Verificar tenant_id
```

DADOS A RESTAURAR:
```python
{
    "analysis_id": "uuid",
    "name": "Análise XYZ",
    "created_date": "2026-01-15",
    "created_by": "user@email.com",

    # Dados processados
    "compulab_total": 50000.00,
    "simus_total": 48500.00,
    "difference": 1500.00,

    # Items por tipo
    "divergences": [
        {
            "patient_name": "João Silva",
            "exam_name": "Hemograma",
            "compulab_value": 100.00,
            "simus_value": 95.00,
            "difference": 5.00
        },
        ...
    ],
    "missing_exams": [...],
    "missing_patients": [...],
    "extra_simus": [...]
}
```

COMPONENTES A MODIFICAR:
1. results.py - mostrar que é histórico (badge "Histórico")
2. analise.py - adicionar botão "Reanalisar"

INTERFACE ESPERADA:
```
┌────────────────────────────────┐
│ 📋 Histórico - Análise XYZ      │ ← badge
│ Criada em: 15/01/2026          │
│ Por: João (admin@lab.com)       │
├────────────────────────────────┤
│ [🔄 Reanalisar] [📥 Baixar PDF] │
│ [📊 Exportar CSV] [🗑️ Deletar]  │
├────────────────────────────────┤
│ Divergências: 15                │
│ Exames Faltando: 3              │
│ ... (tabelas originais)         │
└────────────────────────────────┘
```

FLUXO:
1. Usuário em /history clica em análise
2. Chama: analysis_state.load_analysis_from_history(analysis_id)
3. State carrega dados do Supabase
4. Redireciona para /analise (mesma página de upload)
5. Mostra resultados com badge "Histórico"
6. Usuário pode exportar, deletar ou reanalisar

REANÁLISE:
- Botão "Reanalisar" limpa loaded_from_history
- Permite novo upload dos mesmos arquivos
- Depois compara com análise anterior

AUDITORIA:
```python
# Log de acesso
audit_log = {
    "user_id": current_user_id,
    "action": "opened_historical_analysis",
    "analysis_id": analysis_id,
    "timestamp": now(),
    "ip_address": request.ip
}
# Salvar em audit_summaries ou nova tabela audit_logs
```

VALIDAÇÕES:
- ✅ Verificar se análise existe
- ✅ Validar tenant_id
- ✅ Verificar permissões do usuário
- ✅ Validar integridade dos dados

TESTES:
- [ ] Carregar análise completa
- [ ] Todos os items carregaram
- [ ] Estado restaurado corretamente
- [ ] UI mostra dados corretos
- [ ] Botão reanalisar funciona
- [ ] Log de auditoria criado
- [ ] Permissões validadas

ENTREGA:
1. analysis_state.py (modificado com novo método)
2. analise.py (modificado)
3. results.py (modificado)
4. saved_analysis_service.py (método get_with_items)
5. Tests

---FIM PROMPT---
```

---

# PROMPT 4: EXPORTAÇÃO CSV

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Exportar análise para CSV/Excel
- Banco: Dados em memory (analysis_state)
- Usuário: Clica em botão "Exportar CSV"

TAREFA: Implementar exportação de análise para CSV com múltiplos formatos

REQUISITOS:
1. ✅ Exportar divergências em CSV
2. ✅ Exportar exames faltando
3. ✅ Exportar pacientes faltando
4. ✅ Exportar exames extras (SIMUS)
5. ✅ Resumo executivo
6. ✅ Formatação profissional
7. ✅ Download automático
8. ✅ Suportar múltiplas abas (como Excel)

ESTRUTURA:
```
labbridge/
├─ utils/
│  └─ export_utils.py (CRIAR/MODIFICAR)
├─ states/
│  └─ analysis_state.py (ADICIONAR método)
└─ pages/
   └─ analise.py (ADICIONAR botão)
```

FORMATOS ESPERADOS:

Arquivo 1: resumo.csv
```
Campo,Valor
Data da Análise,2026-01-15
Laboratório,LabXYZ
Total COMPULAB,50000.00
Total SIMUS,48500.00
Diferença,1500.00
Taxa de Acurácia,97.0%
```

Arquivo 2: divergencias.csv
```
Paciente,Exame,Valor COMPULAB,Valor SIMUS,Diferença,Porcentagem
João Silva,Hemograma,100.00,95.00,5.00,5.0%
Maria Santos,Glicose,120.00,118.00,2.00,1.7%
...
```

Arquivo 3: exames_faltando.csv
```
Paciente,Exame,Valor COMPULAB,Status
João Silva,Tomografia,5000.00,Não encontrado em SIMUS
...
```

Arquivo 4: pacientes_faltando.csv
```
Paciente,Quantidade Exames,Total
José Costa,5,2500.00
...
```

CÓDIGO DO SERVIÇO (export_utils.py):
```python
class CSVExporter:
    @staticmethod
    def export_analysis(analysis_data: dict) -> bytes:
        # Criar arquivo ZIP com múltiplos CSVs
        # Retornar bytes para download

    @staticmethod
    def export_divergences(items: list) -> str:
        # Exportar divergências em CSV

    @staticmethod
    def export_missing_exams(items: list) -> str:
        # Exportar exames faltando

    @staticmethod
    def export_missing_patients(items: list) -> str:
        # Exportar pacientes faltando

    @staticmethod
    def export_summary(totals: dict) -> str:
        # Exportar resumo executivo

class ExcelExporter:
    # Versão em .xlsx se necessário
    @staticmethod
    def export_to_excel(analysis_data: dict) -> bytes:
        # Criar arquivo Excel com múltiplas abas
        # Aba 1: Resumo
        # Aba 2: Divergências
        # Aba 3: Exames Faltando
        # Aba 4: Pacientes Faltando
```

INTERFACE:
```
Botões na página de resultados:
[📥 Baixar CSV] [📊 Baixar Excel] [🖨️ Imprimir] [💾 Salvar]
```

FLUXO:
1. Usuário clica em "Baixar CSV"
2. Estado chama: export_utils.export_analysis(self.analysis_data)
3. Gera arquivo(s)
4. Dispara download automático
5. Mostra mensagem de sucesso

FORMATO:
- CSV com UTF-8 encoding
- Delimitador: vírgula (,)
- Decimais: ponto (.)
- Data: YYYY-MM-DD
- Moeda: R$ X,XX.00

VALIDAÇÕES:
- ✅ Dados não vazios
- ✅ Formatação correta
- ✅ Nomes de coluna consistentes
- ✅ Sem caracteres especiais problemáticos

TESTES:
- [ ] CSV exporta corretamente
- [ ] Arquivo é válido (abrir em Excel)
- [ ] Todos os dados estão presentes
- [ ] Formatação está correta
- [ ] Download dispara
- [ ] ZIP com múltiplos arquivos funciona
- [ ] Excel com múltiplas abas funciona

ENTREGA:
1. export_utils.py (completo)
2. analysis_state.py (método export_csv)
3. analise.py (botão + handler)
4. Tests

---FIM PROMPT---
```

---

# PROMPT 5: GERAÇÃO DE PDF

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Gerar PDF profissional de análise
- Biblioteca: ReportLab (ou pypdf2)
- Banco: Dados em memory (analysis_state)

TAREFA: Implementar geração de PDF com layout profissional

REQUISITOS:
1. ✅ Header com logo e informações do laboratório
2. ✅ Resumo executivo
3. ✅ Tabelas de dados (divergências, exames faltando, etc)
4. ✅ Gráficos (pizza, barras)
5. ✅ Rodapé com data/hora
6. ✅ Múltiplas páginas se necessário
7. ✅ Watermark (se rascunho)
8. ✅ Assinatura/QR code

ESTRUTURA:
```
labbridge/
├─ utils/
│  ├─ pdf_report.py (CRIAR/MODIFICAR)
│  └─ analysis_pdf_report.py (VERIFICAR)
├─ assets/
│  ├─ logo.png (USE EXISTENTE)
│  └─ watermark.png (CRIAR)
└─ pages/
   └─ analise.py (ADICIONAR botão)
```

LAYOUT DO PDF:

┌─────────────────────────────────────┐
│ [LOGO] LABBRIDGE                    │
│        Auditoria Financeira         │
├─────────────────────────────────────┤
│ ANÁLISE #00123                      │
│ Data: 15/01/2026 às 14:30          │
│ Laboratório: LabXYZ                │
│ Responsável: João Silva            │
├─────────────────────────────────────┤
│ RESUMO EXECUTIVO                   │
│                                     │
│ Total COMPULAB:      R$ 50.000,00  │
│ Total SIMUS:         R$ 48.500,00  │
│ Diferença:           R$ 1.500,00   │
│ Variação:            3.0%           │
├─────────────────────────────────────┤
│ GRÁFICO: Distribuição de valores   │
│                                     │
│ [GRÁFICO PIE]                      │
│                                     │
├─────────────────────────────────────┤
│ DIVERGÊNCIAS ENCONTRADAS           │
│                                     │
│ Paciente  │ Exame   │ COMPULAB │...│
│ João Silva│Hemograma│100,00   │...│
│ ...                                 │
│                                     │
│ Total Divergências: 15             │
├─────────────────────────────────────┤
│ [PÁGINA 2]                         │
│ EXAMES FALTANDO                    │
│ ...                                 │
└─────────────────────────────────────┘

CÓDIGO (pdf_report.py):
```python
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

class PDFReportGenerator:
    def __init__(self, analysis_data: dict):
        self.analysis_data = analysis_data
        self.story = []

    def generate(self) -> bytes:
        # 1. Header (logo + info)
        # 2. Resumo executivo
        # 3. Gráficos
        # 4. Tabelas de divergências
        # 5. Tabelas de itens faltando
        # 6. Assinatura
        # 7. Gerar PDF e retornar bytes

    def _add_header(self):
        # Logo + Título + Data
        pass

    def _add_summary(self):
        # Resumo com totais
        pass

    def _add_graphics(self):
        # Gráficos (Recharts export SVG?)
        pass

    def _add_divergences_table(self):
        # Tabela de divergências
        pass

    def _add_missing_exams_table(self):
        # Tabela de exames faltando
        pass

    def _add_signature_section(self):
        # Rodapé com data/hora/assinatura
        pass

    @staticmethod
    def format_currency(value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
```

FLUXO:
1. Usuário clica em "Baixar PDF"
2. Chama: pdf_report.generate(analysis_data)
3. Gera PDF com todas as seções
4. Dispara download
5. Mostra mensagem de sucesso

CONSIDERAÇÕES:
- ✅ Formatação profissional
- ✅ Paginação automática
- ✅ Tabelas formatadas com cores alternadas
- ✅ Fontes legíveis (mínimo 10pt)
- ✅ Margens adequadas (2cm)
- ✅ Quebras de página automáticas
- ✅ Compressão de imagem (logo)

TESTES:
- [ ] PDF gera sem erros
- [ ] Todos os dados estão presentes
- [ ] Formatação está correta
- [ ] Paginação funciona
- [ ] Gráficos renderizam
- [ ] Tabelas são legíveis
- [ ] Download dispara
- [ ] Arquivo abre em leitor PDF

ENTREGA:
1. pdf_report.py (completo)
2. analysis_state.py (método export_pdf)
3. analise.py (botão + handler)
4. Assets (logo, watermark)
5. Tests

---FIM PROMPT---
```

---

## 🟡 SPRINT 2: PRIORIDADE MÉDIA

---

# PROMPT 6: DASHBOARD COM KPIS DINÂMICOS

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Dashboard com KPIs dinâmicos (não MOCK)
- Banco: Supabase (saved_analyses, audit_summaries)
- Usuário: Acessa /dashboard e vê métricas reais

TAREFA: Implementar dashboard com dados em tempo real do Supabase

REQUISITOS:
1. ✅ KPI: Total de análises (count)
2. ✅ KPI: Economia encontrada (sum de differences)
3. ✅ KPI: Taxa de acurácia (average)
4. ✅ KPI: Análises este mês
5. ✅ Gráfico: Tendência de análises (últimos 30 dias)
6. ✅ Gráfico: Distribuição por status
7. ✅ Lista: Últimas 5 análises
8. ✅ Filtros: Por período, laboratório

ESTRUTURA:
```
labbridge/
├─ states/
│  └─ dashboard_state.py (MODIFICAR)
└─ pages/
   └─ dashboard.py (MODIFICAR)
```

TABELAS:
```sql
saved_analyses {
    id, tenant_id, created_at, status,
    compulab_total, simus_total, difference
}

audit_summaries {
    id, tenant_id, created_at, analysis_id,
    missing_exams_count, divergences_count,
    missing_patients_count
}
```

QUERIES NECESSÁRIAS:
```python
# KPI 1: Total de análises
SELECT COUNT(*) FROM saved_analyses
WHERE tenant_id = ? AND status = 'completed'

# KPI 2: Economia encontrada
SELECT SUM(difference) FROM saved_analyses
WHERE tenant_id = ? AND status = 'completed'

# KPI 3: Taxa de acurácia média
SELECT AVG((compulab_total - ABS(difference)) / compulab_total * 100)
FROM saved_analyses
WHERE tenant_id = ? AND status = 'completed'

# KPI 4: Análises este mês
SELECT COUNT(*) FROM saved_analyses
WHERE tenant_id = ? AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW())

# Gráfico: Últimos 30 dias
SELECT DATE(created_at) as date, COUNT(*) as count
FROM saved_analyses
WHERE tenant_id = ? AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date

# Últimas análises
SELECT id, name, created_at, status, difference
FROM saved_analyses
WHERE tenant_id = ?
ORDER BY created_at DESC
LIMIT 5
```

ESTADO (dashboard_state.py):
```python
class DashboardState(rx.State):
    # KPIs
    total_analyses: int = 0
    total_savings: float = 0.0
    avg_accuracy: float = 0.0
    analyses_this_month: int = 0

    # Dados para gráficos
    trend_data: list[dict] = []  # data + count
    status_distribution: dict = {}  # {completed: 10, draft: 2}
    recent_analyses: list[dict] = []

    # Filters
    period_days: int = 30
    is_loading: bool = False

    async def load_dashboard_data(self):
        # Chamar Supabase e popular todos os dados
        # Mostrar loading durante fetch
        pass

    async def change_period(self, days: int):
        # Mudar período (7, 30, 90 dias)
        # Recarregar gráficos
        pass
```

INTERFACE:
```
┌─────────────────────────────────────────────┐
│ Dashboard                [Período: 30 dias] │
├─────────────────────────────────────────────┤
│                                             │
│ ┌──────┬──────┬──────┬──────┐              │
│ │Total │Econ. │Taxa  │Mês   │              │
│ │ 42   │R$ 1M │97.3% │ 8    │              │
│ └──────┴──────┴──────┴──────┘              │
│                                             │
├─────────────────────────────────────────────┤
│ Tendência (últimos 30 dias)                │
│                                             │
│ [GRÁFICO: Linha/Barras]                    │
│                                             │
├─────────────────────────────────────────────┤
│ Distribuição por Status                    │
│                                             │
│ ✅ Completo:  40 (95%)                     │
│ ⏳ Rascunho:  2  (5%)                      │
│                                             │
├─────────────────────────────────────────────┤
│ Últimas Análises                           │
│                                             │
│ Análise XYZ  | 15/01 | ✅ | +R$ 5.000     │
│ ...                                        │
└─────────────────────────────────────────────┘
```

TESTES:
- [ ] KPIs carregam corretamente
- [ ] Gráficos renderizam com dados
- [ ] Filtro de período funciona
- [ ] Performance aceitável (<3s)
- [ ] Dados atualizam ao criar nova análise
- [ ] Formatação de moeda correta

ENTREGA:
1. dashboard_state.py (completo)
2. dashboard.py (modificado)
3. Serviço de dashboard (criar)
4. Tests

---FIM PROMPT---
```

---

# PROMPT 7: SALVAR CONFIGURAÇÕES DE PERFIL

```
---INTRO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Salvar configurações de perfil (nome, email, laboratório)
- Banco: Supabase (user_profiles, organizations)
- Usuário: Clica em Settings > Profile > Salvar

TAREFA: Implementar salvar e carregar configurações de usuário

REQUISITOS:
1. ✅ Carregar dados do usuário na inicialização
2. ✅ Editar nome completo
3. ✅ Editar email
4. ✅ Editar dados do laboratório (CNPJ, nome)
5. ✅ Editar preferências de notificação
6. ✅ Validação de entrada
7. ✅ Mensagem de sucesso/erro
8. ✅ Botão "Salvar" com loading state

ESTRUTURA:
```
labbridge/
├─ states/
│  └─ settings_state.py (MODIFICAR)
├─ pages/
│  └─ settings.py (MODIFICAR)
└─ services/
   └─ user_service.py (CRIAR)
```

TABELAS:
```sql
user_profiles {
    id, full_name, email, tenant_id, role,
    settings (JSONB), notification_preferences (JSONB)
}

organizations {
    id, name, cnpj, subscription_plan
}
```

ESTADO (settings_state.py):
```python
class SettingsState(rx.State):
    # User Profile
    full_name: str = ""
    email: str = ""
    phone: str = ""

    # Organization (lab)
    lab_name: str = ""
    lab_cnpj: str = ""

    # Preferences
    notifications_email: bool = True
    notifications_dashboard: bool = True

    # UI
    is_loading: bool = False
    is_saving: bool = False
    success_message: str = ""
    error_message: str = ""

    async def load_user_settings(self):
        # Carregar do Supabase
        pass

    async def save_profile(self):
        # Validar dados
        # Salvar em user_profiles
        # Mostrar mensagem
        pass

    async def save_organization(self):
        # Validar CNPJ
        # Salvar em organizations
        # Mostrar mensagem
        pass

    async def save_preferences(self):
        # Salvar notification_preferences em JSONB
        pass
```

VALIDAÇÕES:
- ✅ Email válido (regex)
- ✅ Nome não vazio
- ✅ CNPJ válido (se preenchido)
- ✅ Telefone válido (se preenchido)

INTERFACE:
```
┌─────────────────────────────────┐
│ Configurações                   │
├─────────────────────────────────┤
│ Perfil                          │
│                                 │
│ Nome Completo:                  │
│ [________________] (editável)   │
│                                 │
│ Email:                          │
│ [email@lab.com] (editável)      │
│                                 │
│ Telefone:                       │
│ [(11) 9****-****] (editável)   │
│                                 │
├─────────────────────────────────┤
│ Laboratório                     │
│                                 │
│ Nome:                           │
│ [Lab XYZ] (editável)           │
│                                 │
│ CNPJ:                           │
│ [00.000.000/0000-00] (edit.)   │
│                                 │
├─────────────────────────────────┤
│ Notificações                    │
│                                 │
│ ☑ Email                        │
│ ☑ Dashboard                    │
│                                 │
├─────────────────────────────────┤
│ [💾 Salvar Alterações]         │
│                                 │
│ ✅ Salvo com sucesso!          │
└─────────────────────────────────┘
```

FLUXO:
1. Página Settings carrega → load_user_settings()
2. Preenche campos com dados
3. Usuário edita
4. Clica "Salvar"
5. Valida dados
6. Salva no Supabase
7. Mostra sucesso ou erro

TESTES:
- [ ] Carregar dados do usuário
- [ ] Editar nome funciona
- [ ] Editar email com validação
- [ ] Editar CNPJ com validação
- [ ] Salvar funciona
- [ ] Mensagem de sucesso aparece
- [ ] Dados persistem após refresh

ENTREGA:
1. settings_state.py (modificado)
2. settings.py (modificado)
3. user_service.py (novo)
4. Tests

---FIM PROMPT---
```

---

# PROMPT 8: CONVITAR MEMBROS PARA EQUIPE

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Convidar membros para a equipe (via email)
- Banco: Supabase (team_invitations, user_profiles)
- Email: Resend API
- Usuário: Admin clica em "Convidar Membro"

TAREFA: Implementar convite de membros com email + link de aceitar

REQUISITOS:
1. ✅ Formulário com email e role (admin, analyst, viewer)
2. ✅ Validação de email único por tenant
3. ✅ Gerar token de convite
4. ✅ Enviar email com link
5. ✅ Listar convites pendentes
6. ✅ Listar membros ativos
7. ✅ Remover membro
8. ✅ Alterar role do membro

ESTRUTURA:
```
labbridge/
├─ states/
│  └─ team_state.py (MODIFICAR)
├─ pages/
│  └─ team.py (MODIFICAR)
├─ services/
│  ├─ team_service.py (MODIFICAR)
│  └─ email_service.py (USAR)
└─ utils/
   └─ token_utils.py (CRIAR)
```

TABELAS:
```sql
team_invitations {
    id, tenant_id, invited_by, email, role,
    token (UNIQUE), expires_at, accepted_at, created_at
}

user_profiles {
    id, email, tenant_id, role, full_name, created_at
}
```

ESTADO (team_state.py):
```python
class TeamState(rx.State):
    # Members
    team_members: list[dict] = []
    pending_invitations: list[dict] = []

    # Form
    invite_email: str = ""
    invite_role: str = "analyst"

    # UI
    is_loading: bool = False
    is_inviting: bool = False
    success_message: str = ""
    error_message: str = ""

    async def load_team_members(self):
        # Buscar user_profiles onde tenant_id = atual
        pass

    async def load_pending_invitations(self):
        # Buscar team_invitations onde accepted_at IS NULL
        pass

    async def send_invitation(self, email: str, role: str):
        # 1. Validar email
        # 2. Gerar token aleatório
        # 3. Criar record em team_invitations
        # 4. Enviar email com link
        # 5. Mostrar mensagem
        pass

    async def remove_member(self, user_id: str):
        # Remover do user_profiles
        pass

    async def change_member_role(self, user_id: str, new_role: str):
        # Alterar role do membro
        pass

    async def resend_invitation(self, invitation_id: str):
        # Reenviar email de convite
        pass

    async def cancel_invitation(self, invitation_id: str):
        # Cancelar convite pendente
        pass
```

EMAIL TEMPLATE:
```
Assunto: Você foi convidado para LabBridge!

Olá [email],

[admin_name] o(a) convidou para fazer parte da equipe [lab_name] no LabBridge.

Clique no link abaixo para aceitar o convite:
[APP_URL]/auth/accept-invitation?token=[TOKEN]

Este link expires em 7 dias.

Se você não espera este convite, ignore este email.

Obrigado,
LabBridge
```

FLUXO COMPLETO:
1. Admin vai em /team
2. Clica em "Convidar Membro"
3. Preenche email e seleciona role
4. Clica "Enviar Convite"
5. Sistema gera token
6. Envia email
7. Mostra "Convite enviado"
8. Email aparece em "Convites Pendentes"
9. Membro clica no link do email
10. Sistema valida token
11. Redireciona para signup/login
12. Após autenticar, membro entra na equipe
13. Admin vê em "Membros Ativos"

INTERFACE:
```
┌──────────────────────────────────────┐
│ Equipe                               │
├──────────────────────────────────────┤
│ [+ Convidar Membro]                 │
│                                      │
│ Membros Ativos (3)                   │
│ ├─ João Silva (Admin)    [👤 Alterar]│
│ ├─ Maria Santos (Analyst)[👤 Alterar]│
│ └─ Pedro Costa (Viewer)  [👤 Alterar]│
│                                      │
│ Convites Pendentes (1)               │
│ ├─ novo@email.com (Analyst) [✉️ Re]  │
│                                      │
│ [🗑️ Remover] para cada membro       │
└──────────────────────────────────────┘
```

ROLES E PERMISSÕES:
- **Admin**: Tudo (convidar, remover, alterar roles)
- **Analyst**: Criar/editar análises, ver dados do time
- **Viewer**: Apenas visualizar relatórios

VALIDAÇÕES:
- ✅ Email válido
- ✅ Email não duplicado no tenant
- ✅ Permissão do usuário (só admin pode convidar)
- ✅ Token valido ao aceitar
- ✅ Não expirado

TESTES:
- [ ] Enviar convite funciona
- [ ] Email enviado corretamente
- [ ] Token gerado e válido
- [ ] Link no email funciona
- [ ] Membro aceita convite
- [ ] Membro aparece em "Ativos"
- [ ] Admin remove membro
- [ ] Admin altera role
- [ ] Permissões validadas

ENTREGA:
1. team_state.py (modificado)
2. team.py (modificado)
3. team_service.py (modificado)
4. token_utils.py (novo)
5. Email template
6. Auth callback para aceitar invites
7. Tests

---FIM PROMPT---
```

---

## 🟢 SPRINT 3: PRIORIDADE BAIXA

---

# PROMPT 9: RBAC (ROLE-BASED ACCESS CONTROL) COMPLETO

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: RBAC completo com middleware de segurança
- Banco: Supabase RLS + user_profiles.role
- Usuário: Cada requisição é validada por role

TAREFA: Implementar middleware de RBAC em toda a aplicação

REQUISITOS:
1. ✅ 3 roles: admin, analyst, viewer
2. ✅ Middleware Reflex que valida role
3. ✅ Supabase RLS policies por role
4. ✅ Ocultar UI baseado em role
5. ✅ Proteger routes (sem role, redirect login)
6. ✅ Logs de acesso
7. ✅ Auditoria de ações críticas

ESTRUTURA:
```
labbridge/
├─ middleware/
│  └─ rbac_middleware.py (CRIAR)
├─ utils/
│  └─ rbac_utils.py (CRIAR)
├─ states/
│  └─ auth_state.py (JÁ TEM role)
└─ pages/ (TODAS PRECISAM VALIDAR)
```

ROLES E PERMISSÕES:

| Ação | Admin | Analyst | Viewer |
|------|-------|---------|--------|
| Criar análise | ✓ | ✓ | ✗ |
| Ver resultados | ✓ | ✓ | ✓ |
| Exportar dados | ✓ | ✓ | ✗ |
| Deletar análise | ✓ | ✗ | ✗ |
| Convidar membros | ✓ | ✗ | ✗ |
| Alterar permissões | ✓ | ✗ | ✗ |
| Configurar integrações | ✓ | ✗ | ✗ |

MIDDLEWARE (rbac_middleware.py):
```python
class RBACMiddleware:
    PROTECTED_ROUTES = {
        '/analise': ['admin', 'analyst'],
        '/dashboard': ['admin', 'analyst', 'viewer'],
        '/history': ['admin', 'analyst', 'viewer'],
        '/reports': ['admin', 'analyst'],
        '/team': ['admin'],
        '/settings': ['admin'],
        '/integrations': ['admin'],
    }

    @staticmethod
    def check_access(route: str, user_role: str) -> bool:
        # Validar se role tem acesso à route
        pass

    @staticmethod
    def require_role(*roles: str):
        # Decorator para funções que precisam role específico
        pass

    @staticmethod
    def log_access(user_id: str, action: str, resource: str, granted: bool):
        # Log de auditoria
        pass
```

SUPABASE RLS POLICIES:
```sql
-- Para cada tabela, criar policies por role

-- saved_analyses
CREATE POLICY "analysts_can_create"
    ON saved_analyses FOR INSERT
    WITH CHECK (
        (SELECT role FROM user_profiles WHERE id = auth.uid())
        IN ('admin', 'analyst')
    );

CREATE POLICY "analysts_can_update_own"
    ON saved_analyses FOR UPDATE
    USING (
        created_by = auth.uid() AND
        (SELECT role FROM user_profiles WHERE id = auth.uid())
        IN ('admin', 'analyst')
    );

-- etc para cada tabela e operação
```

FLUXO:
1. Usuário faz requisição
2. Middleware valida session
3. Middleware obtém role
4. Middleware valida route + role
5. Se OK, executa ação
6. Se não, redireciona login ou mostra erro 403
7. Log de acesso

TESTES:
- [ ] Admin tem acesso a tudo
- [ ] Analyst tem acesso correto
- [ ] Viewer tem acesso limitado
- [ ] RLS policies funcionam no Supabase
- [ ] Logs de auditoria são criados
- [ ] Tentativa de acesso negado redireciona

ENTREGA:
1. rbac_middleware.py (completo)
2. rbac_utils.py (decorators)
3. Supabase RLS policies (SQL)
4. auth_state.py (validar role)
5. Proteção em todas as pages
6. Tests

---FIM PROMPT---
```

---

# PROMPT 10: OAUTH (LOGIN GOOGLE + MICROSOFT)

```
---INICIO PROMPT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Login social (Google + Microsoft)
- Serviço: Supabase Auth com OAuth
- Usuário: Clica em "Entrar com Google"

TAREFA: Implementar OAuth2 com Google e Microsoft

REQUISITOS:
1. ✅ Configurar OAuth apps (Google Cloud, Azure)
2. ✅ Integrar Supabase OAuth providers
3. ✅ Botões de login social na página
4. ✅ Criar user_profiles automaticamente após OAuth
5. ✅ Redirecionar para dashboard após sucesso
6. ✅ Tratamento de erro

SETUP NECESSÁRIO:

### Google OAuth:
1. Ir para: https://console.cloud.google.com/
2. Criar novo projeto
3. Ativar Google+ API
4. Criar credentials (OAuth 2.0 Client)
5. Adicionar redirect URI: https://seu-dominio.com/auth/callback
6. Copiar Client ID e Secret

### Microsoft OAuth:
1. Ir para: https://portal.azure.com/
2. Criar novo app registration
3. Configurar permissões (delegated)
4. Criar client secret
5. Adicionar redirect URI
6. Copiar Application ID e Secret

### Supabase:
1. Dashboard → Authentication → Providers
2. Ativar Google (colar Client ID/Secret)
3. Ativar Microsoft (colar Application ID/Secret)

CÓDIGO (auth_service.py - ADICIONAR):
```python
async def signin_with_oauth(self, provider: str) -> dict:
    # 'google' ou 'microsoft'
    # Retornar URL de login
    pass

async def handle_oauth_callback(self, code: str, provider: str) -> dict:
    # Validar callback
    # Criar user_profiles se novo
    # Retornar sessão
    pass
```

PÁGINA:
```
┌─────────────────────────────────┐
│ Entrar no LabBridge            │
├─────────────────────────────────┤
│                                 │
│ [📧 Email] [Senha] [Entrar]   │
│                                 │
│ OU                              │
│                                 │
│ [🔵 Entrar com Google]         │
│ [🔷 Entrar com Microsoft]      │
│                                 │
└─────────────────────────────────┘
```

FLUXO:
1. Usuário clica "Entrar com Google"
2. Redireciona para Google OAuth
3. Usuário faz login no Google
4. Google redireciona para callback
5. Sistema valida token
6. Cria user_profiles se novo
7. Redireciona para dashboard

TESTES:
- [ ] Login Google funciona
- [ ] Login Microsoft funciona
- [ ] user_profiles criado após OAuth
- [ ] Session validada
- [ ] Callback trata erros

ENTREGA:
1. auth_service.py (adicionar métodos OAuth)
2. auth_callback.py (novo)
3. login.py (adicionar botões)
4. Configuração Supabase (documentada)

---FIM PROMPT---
```

---

# PROMPT 11: STRIPE CHECKOUT (PAGAMENTOS)

```
---INIT---

CONTEXTO:
- Projeto: LabBridge
- Feature: Integração Stripe para upgrade de planos
- Planos: Free, Pro, Enterprise
- Usuário: Clica em "Upgrade" e pagaFLUXO completo de checkout

TAREFA: Implementar Stripe checkout integrado

REQUISITOS:
1. ✅ Planos com preços
2. ✅ Botão "Upgrade" na página
3. ✅ Stripe Checkout Session
4. ✅ Webhook para confirmar pagamento
5. ✅ Atualizar subscription no banco
6. ✅ Redirecionar pós-pagamento
7. ✅ Suportar cancelamento

SETUP:
1. Ir para: https://dashboard.stripe.com
2. Criar conta (ou usar existente)
3. Gerar API keys (test mode)
4. Adicionar em .env: STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
5. Criar produtos e preços no Stripe
6. Configurar webhook

CÓDIGO (stripe_service.py):
```python
class StripeService:
    def __init__(self, secret_key: str):
        self.stripe = stripe
        self.stripe.api_key = secret_key

    async def create_checkout_session(
        self, user_id: str, plan: str
    ) -> str:
        # Criar session
        # plan: 'pro', 'enterprise'
        # Retornar URL de checkout
        pass

    async def handle_webhook(self, event: dict):
        # Processar eventos Stripe
        # Se payment_intent.succeeded → atualizar subscription
        pass

    async def cancel_subscription(self, subscription_id: str):
        # Cancelar assinatura
        pass
```

FLUXO:
1. Usuário em /subscription clica "Upgrade para Pro"
2. Sistema cria Checkout Session no Stripe
3. Redireciona para checkout.stripe.com
4. Usuário preenche dados do cartão
5. Stripe processa pagamento
6. Webhook notifica sistema
7. Sistema atualiza subscription_plan no banco
8. Redireciona para dashboard com sucesso

TESTES:
- [ ] Checkout session criada
- [ ] Redirecionamento funciona
- [ ] Pagamento processado
- [ ] Webhook executado
- [ ] Subscription atualizada

ENTREGA:
1. stripe_service.py
2. subscription_state.py (modificado)
3. Webhook endpoint
4. Tests

---FIM PROMPT---
```

---

## 📊 RESUMO EXECUTIVO

| Sprint | Features | Prompts | Dias | Prioridade |
|--------|----------|---------|------|-----------|
| 1 | Auth, History, Reopen, CSV, PDF | 5 | 10 | 🔴 ALTA |
| 2 | Dashboard, Settings, Team, ... | 3 | 10 | 🟡 MÉDIA |
| 3 | RBAC, OAuth, Stripe | 3 | 10 | 🟢 BAIXA |

**Total: 11 Prompts Prontos para Claude Opus 4.5**

---

## 🎯 COMO USAR

### Processo Recomendado:

1. **Copie um prompt**
2. **Cole no Claude Opus 4.5**
3. **Execute as tarefas**
4. **Teste os resultados**
5. **Valide com MCP Supabase**
6. **Merge no git**
7. **Próximo prompt**

### Velocidade Esperada:

- **Prompt 1 (Auth):** 2-3 horas
- **Prompt 2 (History):** 1-2 horas
- **Prompt 3 (Reopen):** 1-2 horas
- **Prompt 4 (CSV):** 1 hora
- **Prompt 5 (PDF):** 2-3 horas

**Sprint 1 completo: ~8-10 horas de trabalho do Claude Opus 4.5**

---

**Sucesso! Bora implementar LabBridge! 🚀**
