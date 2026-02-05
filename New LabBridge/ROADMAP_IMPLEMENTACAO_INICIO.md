# 🚀 ROADMAP DE IMPLEMENTAÇÃO - LabBridge

**Data:** 05 de Fevereiro de 2026
**Status:** 🟢 PRONTO PARA INICIAR
**Etapa:** Sprint 1 - Features Críticas

---

## ✅ PRÉ-REQUISITOS COMPLETOS

- ✅ Supabase conectado e validado
- ✅ 9/9 tabelas criadas
- ✅ SDK Python funcionando
- ✅ MCP configurada (em progresso)
- ✅ Ambiente configurado

---

## 🎯 SPRINT 1: FEATURES CRÍTICAS (2 semanas)

### 1️⃣ **Login Supabase Auth** (2-3 dias)
**Bloqueador:** Sim - necessário para múltiplas features
**Impacto:** CRÍTICO

**O que fazer:**
- [ ] Migrar `auth_service.py` para usar Supabase Auth SDK
- [ ] Implementar formulário de registro
- [ ] Implementar recuperação de senha
- [ ] Testar fluxo completo de autenticação

**Arquivo:** `labbridge/labbridge/services/auth_service.py`
**Dependência:** Nenhuma

---

### 2️⃣ **Listar Análises Salvas** (1 dia)
**Bloqueador:** Sim - necessário para histórico e reabertura
**Impacto:** CRÍTICO

**O que fazer:**
- [ ] Conectar `HistoryState` com tabela `saved_analyses`
- [ ] Implementar busca com paginação
- [ ] Adicionar filtros (data, nome, status)
- [ ] Testar com dados reais

**Arquivo:** `labbridge/labbridge/states/history_state.py`
**Dependência:** #1 (Login)

---

### 3️⃣ **Reabrir Análise Salva** (2 dias)
**Bloqueador:** Sim - core da aplicação
**Impacto:** CRÍTICO

**O que fazer:**
- [ ] Carregar análise completa do `saved_analyses`
- [ ] Recuperar `analysis_items` associados
- [ ] Restaurar estado da aplicação
- [ ] Mostrar resultados originais

**Arquivo:** `labbridge/labbridge/states/analysis_state.py`
**Dependência:** #2 (Listar Análises)

---

### 4️⃣ **Exportação CSV** (1 dia)
**Bloqueador:** Não
**Impacto:** ALTO - Pedido por usuários

**O que fazer:**
- [ ] Criar função de export para CSV
- [ ] Adicionar botão na página de análise
- [ ] Testar com análises complexas
- [ ] Validar formatação

**Arquivo:** `labbridge/labbridge/utils/export_utils.py`
**Dependência:** #2 (Listar Análises)

---

### 5️⃣ **Geração de PDF** (3 dias)
**Bloqueador:** Não
**Impacto:** ALTO - Pedido por usuários

**O que fazer:**
- [ ] Implementar gerador com ReportLab
- [ ] Criar template de relatório
- [ ] Adicionar gráficos e tabelas
- [ ] Testar com diferentes tipos de análise

**Arquivo:** `labbridge/labbridge/utils/pdf_report.py`
**Dependência:** #2 (Listar Análises)

---

## 📊 PROGRESSO ESPERADO

```
Semana 1:
├─ Login Supabase Auth .......................... 60%
├─ Listar Análises ............................. 80%
└─ Reabrir Análise ............................. 40%

Semana 2:
├─ Reabrir Análise ............................. 100%
├─ Exportação CSV .............................. 100%
├─ Geração de PDF .............................. 70%
└─ Testes e Ajustes ............................ 30%

Fim de Sprint 1: ~75% das features core funcionando
```

---

## 🔄 FLUXO DE DESENVOLVIMENTO

### Arquitetura Atual

```
┌─────────────────────────────────────────┐
│        Frontend (Reflex/React)          │
│                                         │
├─────────────────────────────────────────┤
│        Estados (States)                 │
│  - auth_state      ← Começar aqui       │
│  - analysis_state                       │
│  - history_state   ← Depois             │
│  - reports_state                        │
└─────────────────────────────────────────┤
│        Serviços (Services)              │
│  - auth_service                         │
│  - saved_analysis_service               │
│  - pdf_service (criar)                  │
└─────────────────────────────────────────┤
│        Supabase (Banco)                 │
│  - saved_analyses (existente)           │
│  - analysis_items (existente)           │
│  - profiles (existente)                 │
│  - tenants (existente)                  │
└─────────────────────────────────────────┘
```

### Padrão de Desenvolvimento

1. **State** - Define o estado local da feature
2. **Service** - Comunica com Supabase
3. **Component** - Renderiza a UI
4. **Page** - Integra tudo junto

---

## 📝 PRÓXIMAS AÇÕES

### Imediato (Hoje)

1. **Confirmar MCP funcionando**
   - Reabra Claude Code
   - Me envie: "teste a conexão com Supabase"
   - Se funcionar, começamos

2. **Criar branch de desenvolvimento**
   ```bash
   git checkout -b feature/supabase-integration
   ```

### Amanhã

1. **Começar Login Supabase Auth**
2. **Criar estrutura de arquivos necessários**
3. **Implementar primeiro estado (AuthState)**

---

## 💾 CÓDIGO BASE

### Estrutura Esperada

**auth_service.py** (novo padrão):
```python
from supabase import create_client, Client

class AuthService:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    async def signup(self, email: str, password: str):
        # Implementar com Supabase Auth
        pass

    async def signin(self, email: str, password: str):
        # Implementar com Supabase Auth
        pass

    async def get_current_user(self):
        # Recuperar usuário atual
        pass
```

**history_state.py** (novo padrão):
```python
class HistoryState(rx.State):
    analyses: list[SavedAnalysis] = []
    is_loading: bool = False

    async def load_analyses(self):
        # Buscar de saved_analyses
        pass

    async def delete_analysis(self, analysis_id: str):
        # Deletar análise
        pass
```

---

## 🧪 TESTES

### Para Cada Feature

```python
# test_auth_service.py
def test_signup():
    assert signup("user@test.com", "senha")

def test_signin():
    assert signin("user@test.com", "senha")

# test_history_state.py
def test_load_analyses():
    analyses = load_analyses()
    assert len(analyses) > 0
```

---

## 🔐 SEGURANÇA

**Cuidados ao Implementar:**

1. ✅ Usar RLS (Row Level Security) do Supabase
2. ✅ Nunca enviar credenciais ao frontend
3. ✅ Validar tenant_id em todo acesso
4. ✅ Usar Service Role Key apenas no backend
5. ✅ Implementar rate limiting em APIs

---

## 📦 DEPENDÊNCIAS NECESSÁRIAS

```python
# requirements.txt - Adicionar se não estiver

supabase>=2.1.0
python-dotenv>=1.0.0
```

Verifique:
```bash
pip list | grep supabase
```

---

## 🚨 POSSÍVEIS BLOCKERS

| Problema | Solução |
|----------|---------|
| MCP não conecta | Verificar mcp-config.json |
| Erro 401 em Supabase | Regenerar Service Role Key |
| Tabela não existe | Executar SQL de criação |
| Tipo de dado incompat. | Converter antes de enviar |
| Performance lenta | Adicionar índices no Supabase |

---

## 📈 MÉTRICAS DE SUCESSO

### Semana 1:
- [ ] Auth funcionando
- [ ] 50%+ histórico implementado
- [ ] Zero erros críticos

### Semana 2:
- [ ] Todas features Sprint 1 funcionando
- [ ] Testes cobrindo 80%+ do código
- [ ] Documentação atualizada

---

## 📞 PRÓXIMO PASSO

**Quando você estiver pronto:**

1. Me envie: `"Confirma que estou pronto para começar Sprint 1"`
2. Vou criar a estrutura de diretórios
3. Começamos com Login Supabase Auth
4. Você implementa, eu review

---

**Status:** 🟢 PRONTO PARA COMEÇAR
**Tempo até primeiro resultado:** ~5 horas
**Complexidade:** Média

Bora começar? 🚀
