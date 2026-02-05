# 🚀 Plano de Implementação - Fase 1: Funcionalidades Core

**Projeto:** LabBridge  
**Data:** 2026-02-03  
**Estimativa Total:** 10-15 horas  
**Status:** 🔴 Não Iniciado

---

## 📋 Sumário Executivo

A Fase 1 foca em transformar o LabBridge de um protótipo com dados mock para uma aplicação funcional com persistência real no Supabase. O objetivo é entregar:

1. **Autenticação Real** via Supabase Auth
2. **Persistência de Análises** no banco de dados
3. **IA Detective Funcional** com Gemini API
4. **Dashboard com Dados Reais**

---

## 📊 Arquitetura Atual

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  Reflex (Python → React)                                    │
│  ├── pages/ (dashboard, analise, conversor, ...)            │
│  ├── states/ (auth_state, analysis_state, ai_state, ...)    │
│  └── components/ (ui, navbar, widgets)                      │
├─────────────────────────────────────────────────────────────┤
│                        SERVICES                             │
│  ├── supabase_client.py ✅ Configurado                      │
│  ├── saved_analysis_service.py ✅ Lógica pronta            │
│  ├── ai_service.py ⚠️ Precisa API Key                      │
│  └── subscription_service.py ❌ Mock apenas                 │
├─────────────────────────────────────────────────────────────┤
│                       REPOSITORIES                          │
│  └── saved_analysis_repository.py ✅ CRUD Supabase pronto   │
├─────────────────────────────────────────────────────────────┤
│                        SUPABASE                             │
│  ├── Auth ❌ Não integrado (usando mock)                    │
│  ├── Database ⚠️ cliente conectado, tabelas não testadas   │
│  └── RLS ❌ Políticas não aplicadas                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Task 1.1: Autenticação Supabase Real

**Objetivo:** Substituir login mock por Supabase Auth  
**Estimativa:** 3-4h  
**Prioridade:** 🔴 CRÍTICA

### 1.1.1 Verificar Configuração Supabase Auth

- [ ] Acessar [Supabase Dashboard](https://supabase.com/dashboard)
- [ ] Verificar se "Email Auth" está habilitado
- [ ] Criar usuário de teste no painel Auth
- [ ] Confirmar `SUPABASE_URL` e `SUPABASE_KEY` no `.env`

### 1.1.2 Modificar `auth_state.py`

**Arquivo:** `labbridge/states/auth_state.py`

**Mudanças:**

```python
# ANTES (Mock)
def attempt_login(self):
    if self.login_email == Config.AUTH_EMAIL and self.login_password == Config.AUTH_PASSWORD:
        self.is_authenticated = True

# DEPOIS (Supabase Auth)
async def attempt_login(self):
    from ..services.supabase_client import supabase
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": self.login_email,
            "password": self.login_password
        })
        
        if response.user:
            self.is_authenticated = True
            self.login_error = ""
            
            # Carregar perfil do usuário do banco
            profile = supabase.table("profiles").select("*")\
                .eq("user_id", response.user.id).single().execute()
            
            if profile.data:
                self.current_user = User(
                    id=response.user.id,
                    email=response.user.email,
                    tenant_id=profile.data["tenant_id"],
                    role=profile.data["role"]
                )
                
                # Carregar tenant
                tenant = supabase.table("tenants").select("*")\
                    .eq("id", profile.data["tenant_id"]).single().execute()
                
                if tenant.data:
                    self.current_tenant = Tenant(**tenant.data)
            
            return rx.redirect("/dashboard")
        else:
            self.login_error = "Credenciais inválidas."
            
    except Exception as e:
        self.login_error = f"Erro: {str(e)}"
```

### 1.1.3 Implementar Logout Real

```python
async def logout(self):
    from ..services.supabase_client import supabase
    
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    self.is_authenticated = False
    self.current_user = None
    self.current_tenant = None
    return rx.redirect("/login")
```

### 1.1.4 Criar Tabelas no Supabase

**SQL para executar no Supabase SQL Editor:**

```sql
-- Tabela de Tenants (Laboratórios)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    cnpj TEXT,
    email TEXT,
    phone TEXT,
    plan_type TEXT DEFAULT 'starter',
    subscription_status TEXT DEFAULT 'active',
    stripe_customer_id TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de Profiles (vincula User do Auth com Tenant)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member', -- owner, admin, member
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Trigger para criar profile automaticamente após signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (user_id, tenant_id, role)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'tenant_id', COALESCE(NEW.raw_user_meta_data->>'role', 'member'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Ativar trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### 1.1.5 Verificação

- [ ] Login funciona com email/senha real
- [ ] Logout limpa sessão
- [ ] `current_tenant` é carregado do banco
- [ ] Redirecionamento para dashboard após login

---

## 🎯 Task 1.2: Persistência de Análises

**Objetivo:** Conectar salvamento de análises ao Supabase  
**Estimativa:** 4-5h  
**Prioridade:** 🟠 ALTA

### 1.2.1 Criar Tabelas de Análises

**SQL para executar no Supabase:**

```sql
-- Tabela de Análises Salvas
CREATE TABLE IF NOT EXISTS saved_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    analysis_name TEXT NOT NULL,
    analysis_date DATE NOT NULL,
    description TEXT,
    
    -- URLs de arquivos
    compulab_file_url TEXT,
    compulab_file_name TEXT,
    simus_file_url TEXT,
    simus_file_name TEXT,
    converted_compulab_url TEXT,
    converted_simus_url TEXT,
    analysis_report_url TEXT,
    
    -- Totais
    compulab_total DECIMAL(12,2) DEFAULT 0,
    simus_total DECIMAL(12,2) DEFAULT 0,
    difference DECIMAL(12,2) DEFAULT 0,
    
    -- Contadores
    missing_patients_count INT DEFAULT 0,
    missing_patients_total DECIMAL(12,2) DEFAULT 0,
    missing_exams_count INT DEFAULT 0,
    missing_exams_total DECIMAL(12,2) DEFAULT 0,
    divergences_count INT DEFAULT 0,
    divergences_total DECIMAL(12,2) DEFAULT 0,
    extra_simus_count INT DEFAULT 0,
    
    -- Metadata
    ai_summary TEXT,
    tags TEXT[],
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de Itens de Análise
CREATE TABLE IF NOT EXISTS analysis_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES saved_analyses(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL, -- 'missing_patient', 'missing_exam', 'divergence', 'extra_simus'
    patient_name TEXT,
    exam_name TEXT,
    compulab_value DECIMAL(12,2),
    simus_value DECIMAL(12,2),
    difference DECIMAL(12,2),
    exams_count INT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_saved_analyses_tenant ON saved_analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_date ON saved_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_items_analysis ON analysis_items(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_items_type ON analysis_items(item_type);

-- RLS: Habilitar Row Level Security
ALTER TABLE saved_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_items ENABLE ROW LEVEL SECURITY;

-- Política: Usuários só veem análises do seu tenant
CREATE POLICY "tenant_isolation_saved_analyses" ON saved_analyses
    FOR ALL USING (
        tenant_id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "tenant_isolation_analysis_items" ON analysis_items
    FOR ALL USING (
        analysis_id IN (
            SELECT id FROM saved_analyses WHERE tenant_id IN (
                SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
            )
        )
    );
```

### 1.2.2 Verificar Repository Existente

**Arquivo:** `labbridge/repositories/saved_analysis_repository.py`

O repository já está implementado! ✅ Verificar:
- [ ] Método `create()` funciona
- [ ] Método `get_all()` retorna dados
- [ ] Método `add_items()` insere itens

### 1.2.3 Conectar Analysis State ao Service

**Arquivo:** `labbridge/states/analysis_state.py`

**Mudança Principal:**

```python
# Adicionar no final do método run_analysis()
async def _save_to_database(self):
    """Salva análise atual no banco"""
    from ..services.saved_analysis_service import saved_analysis_service
    from datetime import date
    
    result = await saved_analysis_service.save_complete_analysis(
        name=f"Análise {date.today().strftime('%d/%m/%Y')}",
        analysis_date=date.today(),
        compulab_total=self.compulab_total,
        simus_total=self.simus_total,
        missing_patients_count=len(self.missing_patients),
        missing_patients_total=self.missing_patients_total,
        missing_exams_count=len(self.missing_exams),
        missing_exams_total=self.missing_exams_total,
        divergences_count=len(self.value_divergences),
        divergences_total=self.value_divergences_total,
        extra_simus_count=len(self.extra_simus_exams),
        missing_patients=self.missing_patients,
        missing_exams=self.missing_exams,
        value_divergences=self.value_divergences,
        extra_simus_exams=self.extra_simus_exams,
        tenant_id=self.current_tenant.id if self.current_tenant else ""
    )
    
    if result["success"]:
        print(f"✅ Análise salva: {result['analysis_id']}")
    else:
        print(f"❌ Erro ao salvar: {result['message']}")
```

### 1.2.4 Verificação

- [ ] Análise é salva automaticamente após processamento
- [ ] Histórico exibe análises do banco
- [ ] Filtro por tenant funciona

---

## 🎯 Task 1.3: IA Detective (Gemini)

**Objetivo:** Ativar chat inteligente para análise de divergências  
**Estimativa:** 2-3h  
**Prioridade:** 🟡 MÉDIA

### 1.3.1 Obter API Key do Gemini

1. Acessar [Google AI Studio](https://aistudio.google.com/)
2. Criar nova API Key
3. Adicionar ao `.env`:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   ```

### 1.3.2 Verificar AI Service

**Arquivo:** `labbridge/services/ai_service.py`

- [ ] Verificar se está usando `google-generativeai` corretamente
- [ ] Testar geração de resposta simples
- [ ] Ajustar prompts para contexto de laboratório

### 1.3.3 Testar Detective State

**Arquivo:** `labbridge/states/detective_state.py`

- [ ] Verificar método `send_message()`
- [ ] Testar com perguntas sobre divergências
- [ ] Ajustar contexto com dados reais da análise

### 1.3.4 Verificação

- [ ] Chat responde perguntas
- [ ] Contexto de divergências é incluído
- [ ] Mensagens são exibidas corretamente

---

## 🎯 Task 1.4: Dashboard com Dados Reais

**Objetivo:** Substituir mock data por consultas Supabase  
**Estimativa:** 3-4h  
**Prioridade:** 🟡 MÉDIA

### 1.4.1 Criar Computed Vars Conectadas ao Banco

**Arquivo:** `labbridge/state.py`

```python
@rx.var
def dashboard_total_analyses(self) -> int:
    """Total de análises do mês atual"""
    from .services.saved_analysis_service import saved_analysis_service
    from datetime import datetime
    
    now = datetime.now()
    report = saved_analysis_service.get_monthly_report(
        tenant_id=self.current_tenant.id if self.current_tenant else "",
        year=now.year,
        month=now.month
    )
    return report.get("count", 0) if report else 0

@rx.var
def dashboard_total_revenue(self) -> str:
    """Receita total do mês"""
    from .services.saved_analysis_service import saved_analysis_service
    from datetime import datetime
    
    now = datetime.now()
    report = saved_analysis_service.get_monthly_report(
        tenant_id=self.current_tenant.id if self.current_tenant else "",
        year=now.year,
        month=now.month
    )
    total = report.get("total_compulab", 0) if report else 0
    return f"R$ {total:,.2f}"
```

### 1.4.2 Atualizar Dashboard Page

**Arquivo:** `labbridge/pages/dashboard.py`

- [ ] Substituir `State.analyses_today` por `State.dashboard_total_analyses`
- [ ] Substituir `State.total_revenue_month` por `State.dashboard_total_revenue`
- [ ] Carregar gráficos com dados reais

### 1.4.3 Verificação

- [ ] Dashboard mostra dados do banco
- [ ] Gráficos refletem análises reais
- [ ] Métricas atualizam após nova análise

---

## 📋 Checklist de Conclusão Fase 1

### Entregáveis

| Item | Critério de Aceite | Status |
|------|-------------------|--------|
| Login Real | Usuário faz login com email/senha no Supabase Auth | ⬜ |
| Logout Funcional | Sessão é destruída ao clicar "Sair" | ⬜ |
| Salvar Análise | Análise é persistida no Supabase após processamento | ⬜ |
| Histórico Real | Lista de análises vem do banco de dados | ⬜ |
| IA Detective | Chat responde perguntas sobre divergências | ⬜ |
| Dashboard Real | Métricas refletem dados salvos | ⬜ |
| Multi-tenant | Dados são isolados por tenant_id | ⬜ |

### Testes Manuais

- [ ] Criar novo usuário no Supabase Auth
- [ ] Logar com novo usuário
- [ ] Fazer upload de PDFs e executar análise
- [ ] Verificar se análise foi salva no banco
- [ ] Fazer logout e logar novamente
- [ ] Verificar se análises persistiram
- [ ] Testar chat Detective com pergunta
- [ ] Verificar dashboard atualizado

---

## 🔧 Dependências

### Pacotes Python Necessários

```bash
pip install google-generativeai  # Para Gemini AI
pip install supabase             # Cliente Supabase (já instalado)
```

### Variáveis de Ambiente Necessárias

```env
# .env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# Gemini AI
GEMINI_API_KEY=AIzaSyXXX...

# Opcional (remover após migração)
AUTH_EMAIL=admin@labbridge.com
AUTH_PASSWORD=senha_segura
```

---

## 📅 Cronograma Sugerido

| Dia | Task | Horas |
|-----|------|-------|
| 1 | 1.1 Autenticação Supabase | 3-4h |
| 2 | 1.2 Persistência de Análises | 4-5h |
| 3 | 1.3 IA Detective + 1.4 Dashboard | 3-4h |

**Total Estimado:** 10-13 horas

---

## 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Tabelas não existem no Supabase | Alta | Alto | Executar SQL antes de começar |
| API Key Gemini inválida | Baixa | Médio | Testar isoladamente primeiro |
| RLS bloqueia queries | Média | Alto | Testar com service_role key primeiro |
| Conflito de sessão Reflex | Baixa | Médio | Limpar cache `.web` se necessário |

---

**Próximo Passo:** Executar SQL de criação de tabelas no Supabase.

Deseja que eu comece pela **Task 1.1 (Autenticação)** ou pela **criação das tabelas no Supabase**?
