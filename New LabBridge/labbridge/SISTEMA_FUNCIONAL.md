# Sistema Funcional Simulado - LabBridge

## Visão Geral

Este documento descreve a implementação do **Sistema Funcional Simulado** para as funcionalidades de **Usuários & Permissões** e **Integrações** do LabBridge.

O sistema foi implementado com:
- ✅ Persistência local via SQLite
- ✅ CRUD completo de usuários e integrações
- ✅ Fallback automático quando Supabase não está configurado
- ✅ Notificações toast de feedback
- ✅ Dados de demonstração pré-carregados

## Arquitetura

```
labbridge/
├── services/
│   ├── local_storage.py      # 🆕 Persistência SQLite local
│   ├── team_service.py       # ✏️ Atualizado com fallback local
│   ├── integration_service.py # ✏️ Atualizado com fallback local
│   └── supabase_client.py    # Cliente Supabase (opcional)
│
├── states/
│   ├── team_state.py         # Estado para gestão de equipe
│   └── integration_state.py  # Estado para gestão de integrações
│
├── pages/
│   ├── team.py               # Página de Usuários & Permissões
│   └── integrations.py       # ✏️ Página de Integrações (dinâmica)
│
├── data/
│   └── labbridge_local.db    # 🆕 Banco SQLite (criado automaticamente)
│
└── models.py                 # Modelos de dados (TeamMember, Integration, etc.)
```

## Funcionalidades Implementadas

### 1. Usuários & Permissões (`/team`)

| Funcionalidade | Status | Descrição |
|----------------|--------|-----------|
| Listar membros | ✅ | Lista todos os membros da equipe |
| Adicionar membro | ✅ | Convite via modal com email e role |
| Editar membro | ✅ | Alterar nome e papel |
| Alterar status | ✅ | Ativar/desativar usuários |
| Remover membro | ✅ | Exclusão com confirmação |
| Reenviar convite | ✅ | Para membros pendentes |
| Busca/filtro | ✅ | Buscar por nome ou email |
| Estatísticas | ✅ | Total, ativos, pendentes, admins |

**Papéis disponíveis:**
- `admin_global` - Controle total do sistema
- `admin_lab` - Gerência do laboratório
- `analyst` - Operações do dia a dia
- `viewer` - Apenas leitura

### 2. Integrações (`/integrations`)

| Funcionalidade | Status | Descrição |
|----------------|--------|-----------|
| Listar integrações | ✅ | Lista todas as integrações |
| Ativar/desativar | ✅ | Toggle de status |
| Sincronizar | ✅ | Sync individual ou todas |
| Configurar | ✅ | Modal de configuração |
| Testar conexão | ✅ | Teste de conectividade |
| Estatísticas | ✅ | Total, ativas, inativas, erros |

**Integrações pré-configuradas:**
- 🔬 Shift LIS (Sistema de Gestão Laboratorial)
- 🧬 Matrix (API HL7/FHIR)
- 💰 Concent (Faturamento TISS)
- 📋 Portal TISS (Envio de guias)
- 📁 Google Drive (Backup)
- 💬 WhatsApp Business (Comunicação)

## Banco de Dados Local

O sistema utiliza SQLite para persistência local, criando automaticamente o banco na primeira execução.

### Tabelas

```sql
-- Membros da equipe
CREATE TABLE team_members (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'viewer',
    status TEXT DEFAULT 'pending',
    tenant_id TEXT DEFAULT 'local',
    invited_by TEXT,
    last_active TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(email, tenant_id)
);

-- Convites
CREATE TABLE team_invites (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT DEFAULT 'viewer',
    tenant_id TEXT DEFAULT 'local',
    invited_by TEXT,
    token TEXT,
    message TEXT,
    status TEXT DEFAULT 'pending',
    expires_at TEXT,
    created_at TEXT NOT NULL
);

-- Integrações
CREATE TABLE integrations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    icon TEXT DEFAULT '🔌',
    status TEXT DEFAULT 'inactive',
    tenant_id TEXT DEFAULT 'local',
    config TEXT DEFAULT '{}',
    credentials TEXT DEFAULT '{}',
    last_sync TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Logs de integração
CREATE TABLE integration_logs (
    id TEXT PRIMARY KEY,
    integration_id TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    details TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);
```

### Localização do Banco

O arquivo SQLite é criado em:
```
labbridge/data/labbridge_local.db
```

## Como Funciona o Fallback

```python
# No TeamService e IntegrationService:
def __init__(self):
    self.client = supabase           # Cliente Supabase
    self.local = local_storage       # Storage local SQLite
    self._use_local = self.client is None  # Fallback automático

def get_team_members(self, tenant_id: str):
    if self._use_local:
        # Usa SQLite local
        return self.local.get_team_members(tenant_id)
    else:
        # Usa Supabase
        return self.client.table("team_members")...
```

## Migração para Produção

Quando estiver pronto para usar Supabase em produção:

1. **Configure as variáveis de ambiente:**
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key
```

2. **Crie as tabelas no Supabase** usando os mesmos schemas SQL

3. **Migre os dados locais** (opcional):
```python
from labbridge.services.local_storage import local_storage
from labbridge.services.supabase_client import supabase

# Exportar dados locais
members = local_storage.get_team_members("local")
integrations = local_storage.get_integrations("local")

# Importar no Supabase
for member in members:
    supabase.table("team_members").insert(member).execute()
```

## Dados de Demonstração

O sistema vem com dados pré-carregados:

### Usuários
| Nome | Email | Papel | Status |
|------|-------|-------|--------|
| Admin Principal | admin@labbridge.com | Admin Global | Ativo |
| Dr. João Silva | joao@laboratorio.com | Admin Lab | Ativo |
| Ana Costa | ana@laboratorio.com | Analista | Ativo |
| Carlos Souza | carlos@laboratorio.com | Analista | Ativo |
| Maria Santos | maria@laboratorio.com | Visualizador | Ativo |
| Pedro Lima | pedro@laboratorio.com | Visualizador | Ativo |
| Julia Oliveira | julia@laboratorio.com | Analista | Pendente |
| Lucas Mendes | lucas@laboratorio.com | Visualizador | Pendente |

### Integrações
| Nome | Categoria | Status |
|------|-----------|--------|
| Shift LIS | LIS | Ativo |
| Matrix | LIS | Inativo |
| Concent | Faturamento | Erro |
| Portal TISS | Faturamento | Inativo |
| Google Drive | Storage | Ativo |
| WhatsApp Business | Comunicação | Ativo |

## Uso

### Iniciar o Sistema

```bash
cd labbridge
reflex run
```

### Acessar as Páginas

- **Usuários & Permissões:** http://localhost:3000/team
- **Integrações:** http://localhost:3000/integrations

### Reset do Banco Local

Para limpar todos os dados e recomeçar:

```bash
# Remover o arquivo de banco
rm labbridge/data/labbridge_local.db

# Reiniciar o sistema (dados serão recriados)
reflex run
```

## Vantagens desta Abordagem

1. **Funciona Offline** - Não depende de serviços externos
2. **Zero Custo** - Sem necessidade de plano pago de banco de dados
3. **Demonstração Completa** - Todas as funcionalidades funcionam
4. **Fácil Migração** - Mesma interface, basta configurar Supabase
5. **Desenvolvimento Ágil** - Sem setup complexo de infraestrutura

## Próximos Passos (Opcional)

Para implementar o **Sistema Funcional Completo**:

1. [ ] Configurar Supabase com as tabelas
2. [ ] Implementar autenticação com JWT
3. [ ] Configurar serviço de email (SendGrid/Resend) para convites
4. [ ] Implementar OAuth para Google Drive
5. [ ] Configurar WhatsApp Business API
6. [ ] Adicionar Row Level Security no Supabase
