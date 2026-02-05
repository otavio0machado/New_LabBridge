# LabBridge

**Sistema de Inteligência e Auditoria para Laboratórios**

O LabBridge é uma plataforma SaaS moderna desenvolvida para laboratórios de análises clínicas, focada em auditoria financeira, inteligência de dados (IA) e gestão operacional.

## 🚀 Funcionalidades Principais

*   **Auditoria Financeira**: Importe faturas e compare automaticamente com os valores de convênios. Evite glosas e recupere receita.
*   **Importador Universal**: Suporte a diversos formatos (PDF, CSV, Excel) parar ingestão de dados.
*   **Assistente IA ("Detetive")**: Um agente inteligente que analisa tendências, anomalias e responde perguntas sobre seus dados operacionais.
*   **Gestão Multi-laboratório**: Arquitetura multi-tenant permitindo que múltiplos laboratórios usem a plataforma com isolamento total de dados.
*   **Central de Relatórios**: Dashboards e extratos detalhados para tomada de decisão.

## 🛠️ Stack Tecnológica

*   **Frontend/Backend**: [Reflex](https://reflex.dev) (Python puro)
*   **Banco de Dados**: Supabase (PostgreSQL)
*   **AI Engine**: Google Gemini 1.5 Flash (via API)
*   **Estilo**: Tailwind CSS v4 (via Reflex)

## 📦 Instalação e Execução

### Pré-requisitos
*   Python 3.9+
*   Conta no Supabase (para banco de dados)
*   Chave de API Gemini (para funcionalidades de IA)

### Passos

1.  **Clone o repositório** (se aplicável)
2.  **Crie um ambiente virtual**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .venv\Scripts\activate     # Windows
    ```
3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure as Variáveis de Ambiente**:
    Crie um arquivo `.env` na raiz baseado no exemplo e preencha suas chaves:
    ```env
    SUPABASE_URL=...
    SUPABASE_KEY=...
    GEMINI_API_KEY=...
    AUTH_EMAIL=admin@labbridge.com
    AUTH_PASSWORD=senha_segura
    ```
5.  **Execute as Migrações de Banco**:
    Rode os scripts SQL contidos na pasta `migrations/` no seu painel Supabase.
6.  **Inicie o Servidor**:
    ```bash
    rx run
    ```
    Acesse em: [http://localhost:3000](http://localhost:3000)

## 📂 Estrutura do Projeto

*   `labbridge/`: Código fonte da aplicação
    *   `pages/`: Rotas e páginas (Dashboard, Análise, Configurações, etc.)
    *   `components/`: Componentes reutilizáveis (Navbar, Cards)
    *   `states/`: Lógica de estado e conexão com backend
    *   `services/`: Lógica de negócios (Assinaturas, IA)
    *   `models.py`: Modelos de dados Pydantic
    *   `styles.py`: Design tokens e definições de tema

## 🛡️ Segurança

*   Isolamento de dados via `tenant_id` e RLS (Row Level Security).
*   Autenticação robusta.

---
**LabBridge** © 2026 - Todos os direitos reservados.
