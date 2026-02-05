# 🔐 Plano de Implementação - Fase 2: Multi-Tenancy & Segurança

**Projeto:** LabBridge  
**Data:** 2026-02-03  
**Estimativa Total:** 6-8 horas  
**Pré-requisito:** Fase 1 Completa  
**Status:** 🔴 Não Iniciado

---

## 📋 Sumário Executivo

A Fase 2 foca em garantir **isolamento de dados** entre laboratórios (tenants) e implementar **segurança robusta** no banco de dados. Isso é crítico para um SaaS multi-tenant onde múltiplos clientes compartilham a mesma infraestrutura.

### Objetivos

1. **Row Level Security (RLS)** → Políticas no Supabase para isolamento automático
2. **Contexto de Tenant** → Propagar `tenant_id` em todas as operações
3. **Auditoria de Acessos** → Log de ações sensíveis
4. **Proteção de Rotas** → Middleware de autenticação no frontend

---

## 🏗️ Arquitetura Multi-Tenant

```
┌─────────────────────────────────────────────────────────────┐
│                    TENANT A (Lab Alpha)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ User Admin   │  │ User Analyst │  │ User Viewer  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                │                │               │
│           └────────────────┼────────────────┘               │
│                            ▼                                │
│              ┌─────────────────────────┐                    │
│              │   tenant_id = "A"       │                    │
│              │   saved_analyses        │                    │
│              │   exam_mappings         │                    │
│              │   audit_logs            │                    │
│              └─────────────────────────┘                    │
├─────────────────────────────────────────────────────────────┤
│                    TENANT B (Lab Beta)                      │
│              ┌─────────────────────────┐                    │
│              │   tenant_id = "B"       │                    │
│              │   saved_analyses        │                    │
│              │   exam_mappings         │                    │
│              │   audit_logs            │                    │
│              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │     SUPABASE DATABASE         │
            │  ┌─────────────────────────┐  │
            │  │   RLS POLICIES          │  │
            │  │   Filtro por tenant_id  │  │
            │  │   automático            │  │
            │  └─────────────────────────┘  │
            └───────────────────────────────┘
```

---

## 🎯 Task 2.1: Row Level Security (RLS) Completo

**Objetivo:** Aplicar políticas RLS em todas as tabelas sensíveis  
**Estimativa:** 2-3h  
**Prioridade:** 🔴 CRÍTICA

### 2.1.1 Listar Tabelas que Precisam de RLS

| Tabela | tenant_id | RLS Necessário |
|--------|-----------|----------------|
| `tenants` | É a própria PK | Usuário só vê seu tenant |
| `profiles` | FK para tenants | Usuário só vê seu perfil |
| `saved_analyses` | ✅ Existe | Filtrar por tenant |
| `analysis_items` | Via FK | Herdar de saved_analyses |
| `exam_mappings` | ✅ Existe | Filtrar por tenant |
| `audit_logs` | ✅ Existe | Filtrar por tenant |

### 2.1.2 SQL: Políticas RLS Completas

```sql
-- ============================================
-- RLS POLICIES - MULTI-TENANT ISOLATION
-- ============================================

-- 1. TENANTS TABLE
-- ============================================
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

-- Usuário só vê o tenant ao qual pertence
CREATE POLICY "Users can view own tenant" ON tenants
    FOR SELECT USING (
        id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    );

-- Apenas admins podem atualizar o tenant
CREATE POLICY "Admins can update own tenant" ON tenants
    FOR UPDATE USING (
        id IN (
            SELECT tenant_id FROM profiles 
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- 2. PROFILES TABLE
-- ============================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Usuário vê todos os profiles do seu tenant (para gestão de equipe)
CREATE POLICY "Users can view team profiles" ON profiles
    FOR SELECT USING (
        tenant_id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    );

-- Usuário só pode atualizar seu próprio perfil
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (user_id = auth.uid());

-- Apenas owners podem inserir novos membros
CREATE POLICY "Owners can insert team members" ON profiles
    FOR INSERT WITH CHECK (
        tenant_id IN (
            SELECT tenant_id FROM profiles 
            WHERE user_id = auth.uid() AND role = 'owner'
        )
    );

-- 3. SAVED_ANALYSES TABLE
-- ============================================
ALTER TABLE saved_analyses ENABLE ROW LEVEL SECURITY;

-- Política unificada: ALL operations filtradas por tenant
CREATE POLICY "Tenant isolation for saved_analyses" ON saved_analyses
    FOR ALL USING (
        tenant_id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    )
    WITH CHECK (
        tenant_id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    );

-- 4. ANALYSIS_ITEMS TABLE
-- ============================================
ALTER TABLE analysis_items ENABLE ROW LEVEL SECURITY;

-- Herda isolamento via FK para saved_analyses
CREATE POLICY "Tenant isolation for analysis_items" ON analysis_items
    FOR ALL USING (
        analysis_id IN (
            SELECT id FROM saved_analyses WHERE tenant_id IN (
                SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
            )
        )
    );

-- 5. EXAM_MAPPINGS TABLE (se existir)
-- ============================================
CREATE TABLE IF NOT EXISTS exam_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    original_name TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    source TEXT DEFAULT 'manual', -- 'manual', 'ai_suggested', 'imported'
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, original_name)
);

ALTER TABLE exam_mappings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant isolation for exam_mappings" ON exam_mappings
    FOR ALL USING (
        tenant_id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    );

-- 6. AUDIT_LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    action TEXT NOT NULL, -- 'login', 'analysis_created', 'mapping_added', etc.
    resource_type TEXT, -- 'analysis', 'mapping', 'user'
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Usuários podem ver logs do seu tenant
CREATE POLICY "Tenant isolation for audit_logs" ON audit_logs
    FOR SELECT USING (
        tenant_id IN (
            SELECT tenant_id FROM profiles WHERE user_id = auth.uid()
        )
    );

-- Inserção via service_role apenas (backend)
CREATE POLICY "Service can insert audit_logs" ON audit_logs
    FOR INSERT WITH CHECK (true); -- Controlado via service_role key
```

### 2.1.3 Verificação de RLS

```sql
-- Testar se políticas estão ativas
SELECT tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;

-- Verificar se RLS está habilitado
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
```

### 2.1.4 Checklist

- [ ] Executar SQL de políticas no Supabase
- [ ] Testar com 2 usuários de tenants diferentes
- [ ] Confirmar que Tenant A não vê dados de Tenant B
- [ ] Verificar que INSERT/UPDATE respeitam RLS

---

## 🎯 Task 2.2: Contexto de Tenant no Estado

**Objetivo:** Garantir que todas as operações usem o `tenant_id` correto  
**Estimativa:** 2h  
**Prioridade:** 🟠 ALTA

### 2.2.1 Criar Helper para Obter Tenant ID

**Arquivo:** `labbridge/utils/tenant_context.py`

```python
"""
Tenant Context Helper
Centraliza acesso ao tenant_id do usuário logado
"""
from typing import Optional

def get_current_tenant_id(state) -> Optional[str]:
    """
    Retorna o tenant_id do usuário atual.
    Usado em todas as operações de banco de dados.
    """
    if hasattr(state, 'current_tenant') and state.current_tenant:
        return state.current_tenant.id
    return None

def require_tenant_id(state) -> str:
    """
    Retorna tenant_id ou levanta exceção.
    Usa em operações que EXIGEM tenant.
    """
    tenant_id = get_current_tenant_id(state)
    if not tenant_id:
        raise ValueError("Operação requer tenant autenticado")
    return tenant_id
```

### 2.2.2 Modificar Services para Usar Tenant Context

**Arquivo:** `labbridge/services/saved_analysis_service.py`

```python
# ANTES
def get_saved_analyses(self, tenant_id: str, limit: int = 50):
    # tenant_id passado manualmente

# DEPOIS
def get_saved_analyses(self, tenant_id: str, limit: int = 50):
    """
    Retorna análises do tenant.
    RLS no Supabase garante isolamento adicional.
    """
    if not tenant_id:
        print("⚠️ Aviso: tenant_id vazio, retornando lista vazia")
        return []
    
    return self.repository.get_all(tenant_id, limit=limit)
```

### 2.2.3 Modificar States para Propagar Tenant

**Arquivo:** `labbridge/states/analysis_state.py`

```python
class AnalysisState(AuthState):
    
    async def run_analysis(self):
        # ... processamento ...
        
        # Salvar com tenant_id do usuário logado
        await self._save_to_database()
    
    async def _save_to_database(self):
        from ..services.saved_analysis_service import saved_analysis_service
        
        # Garantir tenant_id
        tenant_id = self.current_tenant.id if self.current_tenant else ""
        if not tenant_id:
            print("❌ Erro: Não é possível salvar sem tenant autenticado")
            return
        
        result = await saved_analysis_service.save_complete_analysis(
            # ... outros parâmetros ...
            tenant_id=tenant_id  # <-- SEMPRE incluir
        )
```

### 2.2.4 Criar Audit Logger

**Arquivo:** `labbridge/services/audit_service.py`

```python
"""
Audit Service - Log de Ações Sensíveis
"""
from typing import Optional, Dict, Any
from .supabase_client import supabase

class AuditService:
    """Serviço para registrar ações de auditoria"""
    
    @staticmethod
    def log(
        tenant_id: str,
        user_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Registra uma ação no log de auditoria.
        
        Actions:
        - login, logout
        - analysis_created, analysis_deleted
        - mapping_created, mapping_imported
        - user_invited, user_removed
        - settings_changed
        """
        if not supabase:
            return
        
        try:
            supabase.table("audit_logs").insert({
                "tenant_id": tenant_id,
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {}
            }).execute()
        except Exception as e:
            print(f"⚠️ Erro ao registrar auditoria: {e}")

audit_service = AuditService()
```

### 2.2.5 Checklist

- [ ] Criar `tenant_context.py`
- [ ] Atualizar services para usar tenant_id
- [ ] Atualizar states para propagar tenant
- [ ] Implementar audit_service
- [ ] Testar log de login/logout

---

## 🎯 Task 2.3: Proteção de Rotas (Frontend)

**Objetivo:** Impedir acesso a páginas protegidas sem autenticação  
**Estimativa:** 1-2h  
**Prioridade:** 🟠 ALTA

### 2.3.1 Criar Componente de Proteção

**Arquivo:** `labbridge/components/auth_guard.py`

```python
"""
Auth Guard - Proteção de Rotas
"""
import reflex as rx
from ..states.auth_state import AuthState

def require_auth(component: rx.Component) -> rx.Component:
    """
    HOC que protege um componente, redirecionando se não autenticado.
    """
    return rx.cond(
        AuthState.is_authenticated,
        component,
        rx.box(
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Redirecionando para login...", color="gray"),
                    spacing="4"
                ),
                height="100vh"
            ),
            on_mount=AuthState.check_auth  # Redireciona para /login
        )
    )

def require_role(component: rx.Component, roles: list[str]) -> rx.Component:
    """
    Protege componente por role específica.
    """
    return rx.cond(
        AuthState.is_authenticated & AuthState.current_user.role.is_in(roles),
        component,
        rx.box(
            rx.center(
                rx.vstack(
                    rx.icon("shield-x", size=48, color="red"),
                    rx.heading("Acesso Negado", size="6"),
                    rx.text("Você não tem permissão para acessar esta página."),
                    rx.button("Voltar ao Dashboard", on_click=rx.redirect("/dashboard")),
                    spacing="4"
                ),
                height="100vh"
            )
        )
    )
```

### 2.3.2 Aplicar Proteção nas Páginas

**Arquivo:** `labbridge/labbridge.py`

```python
from .components.auth_guard import require_auth

# Páginas públicas (sem proteção)
app.add_page(login_page, route="/login", title="Login - LabBridge")

# Páginas protegidas (requer autenticação)
app.add_page(
    require_auth(dashboard_page()), 
    route="/dashboard", 
    title="Dashboard - LabBridge"
)

app.add_page(
    require_auth(analysis_page()), 
    route="/analise", 
    title="Análise - LabBridge"
)

# Páginas com role específica
from .components.auth_guard import require_role

app.add_page(
    require_role(team_page(), ["owner", "admin"]),
    route="/team",
    title="Equipe - LabBridge"
)

app.add_page(
    require_role(settings_page(), ["owner", "admin"]),
    route="/settings",
    title="Configurações - LabBridge"
)
```

### 2.3.3 Checklist

- [ ] Criar `auth_guard.py`
- [ ] Aplicar `require_auth` em todas as páginas protegidas
- [ ] Aplicar `require_role` em páginas administrativas
- [ ] Testar acesso direto via URL sem login
- [ ] Verificar redirecionamento funciona

---

## 🎯 Task 2.4: Validação e Testes de Segurança

**Objetivo:** Garantir que o sistema é seguro contra ataques comuns  
**Estimativa:** 1-2h  
**Prioridade:** 🟡 MÉDIA

### 2.4.1 Checklist de Segurança

| Verificação | Como Testar | Esperado |
|-------------|-------------|----------|
| Tenant A não vê dados de B | Login como A, verificar banco | Lista vazia |
| SQL Injection | Input malicioso em campos | Query escapa strings |
| XSS | Script em campos de texto | HTML é escapado |
| CSRF | Request sem token | Rejeitado |
| Sessão expira | Aguardar timeout | Logout automático |

### 2.4.2 Script de Teste de Isolamento

**Arquivo:** `tests/test_tenant_isolation.py`

```python
"""
Testes de Isolamento Multi-Tenant
"""
import pytest
from supabase import create_client

# Configurar com 2 usuários de tenants diferentes
TENANT_A_EMAIL = "user_a@test.com"
TENANT_A_PASSWORD = "senha123"
TENANT_B_EMAIL = "user_b@test.com"
TENANT_B_PASSWORD = "senha456"

@pytest.fixture
def supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def test_tenant_a_cannot_see_tenant_b_data(supabase_client):
    """Tenant A não deve ver análises de Tenant B"""
    
    # Login como Tenant A
    supabase_client.auth.sign_in_with_password({
        "email": TENANT_A_EMAIL,
        "password": TENANT_A_PASSWORD
    })
    
    # Buscar todas as análises
    result = supabase_client.table("saved_analyses").select("*").execute()
    
    # Verificar que nenhuma pertence a Tenant B
    for analysis in result.data:
        assert analysis["tenant_id"] != TENANT_B_ID, \
            f"Tenant A conseguiu ver análise de Tenant B: {analysis['id']}"

def test_tenant_cannot_insert_in_other_tenant(supabase_client):
    """Tenant A não deve conseguir inserir dados em Tenant B"""
    
    # Login como Tenant A
    supabase_client.auth.sign_in_with_password({
        "email": TENANT_A_EMAIL,
        "password": TENANT_A_PASSWORD
    })
    
    # Tentar inserir com tenant_id de B
    with pytest.raises(Exception):  # Deve falhar
        supabase_client.table("saved_analyses").insert({
            "tenant_id": TENANT_B_ID,  # ID do outro tenant
            "analysis_name": "Hacked!",
            "analysis_date": "2026-01-01"
        }).execute()
```

### 2.4.3 Monitoramento de Logs

```sql
-- Query para verificar tentativas suspeitas
SELECT 
    user_id,
    action,
    details,
    created_at
FROM audit_logs
WHERE action IN ('unauthorized_access', 'rate_limit_exceeded', 'invalid_token')
ORDER BY created_at DESC
LIMIT 100;
```

### 2.4.4 Checklist

- [ ] Executar testes de isolamento
- [ ] Verificar logs de auditoria
- [ ] Testar inputs maliciosos
- [ ] Confirmar sessão expira corretamente

---

## 📋 Checklist de Conclusão Fase 2

### Entregáveis

| Item | Critério de Aceite | Status |
|------|-------------------|--------|
| RLS em todas as tabelas | Políticas aplicadas e funcionando | ⬜ |
| Tenant Context | tenant_id propagado em todas operações | ⬜ |
| Audit Logs | Ações sensíveis são registradas | ⬜ |
| Route Protection | Páginas protegidas redirecionam sem auth | ⬜ |
| Role-based Access | Apenas admins acessam team/settings | ⬜ |
| Testes de Isolamento | Tenant A não vê dados de B | ⬜ |

### Testes Manuais

- [ ] Criar 2 tenants e 2 usuários diferentes
- [ ] Login com Usuário A, criar análise
- [ ] Login com Usuário B, verificar que não vê análise de A
- [ ] Tentar acessar /dashboard sem login (deve redirecionar)
- [ ] Verificar que member não acessa /team
- [ ] Verificar logs de audit no banco

---

## 🔧 Dependências

### Nenhuma Nova Dependência

Todos os recursos utilizam:
- Supabase RLS (nativo)
- Reflex State (já existe)

### Variáveis de Ambiente

Nenhuma nova variável necessária.

---

## 📅 Cronograma Sugerido

| Dia | Task | Horas |
|-----|------|-------|
| 1 | 2.1 RLS Policies | 2-3h |
| 1 | 2.2 Tenant Context | 2h |
| 2 | 2.3 Route Protection | 1-2h |
| 2 | 2.4 Testes de Segurança | 1-2h |

**Total Estimado:** 6-8 horas

---

## 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| RLS bloqueia queries legítimas | Média | Alto | Testar com service_role primeiro |
| Performance degradada com RLS | Baixa | Médio | Adicionar índices nas FKs |
| Usuário perde acesso | Baixa | Alto | Backup de policies antes de aplicar |
| Audit logs crescem muito | Alta | Baixo | Implementar retention policy |

---

## 🔗 Dependência com Fase 1

Esta fase **REQUER** que a Fase 1 esteja completa:
- ✅ Tabelas `tenants` e `profiles` existem
- ✅ Autenticação Supabase funciona
- ✅ `current_tenant` está disponível no state

---

**Próximo Passo:** Completar Fase 1, depois executar SQL de RLS policies.
