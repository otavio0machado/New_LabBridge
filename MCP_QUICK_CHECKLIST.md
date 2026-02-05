# ⚡ MCP Quick Checklist - O que Fazer Manualmente

**Versão Rápida (5-10 minutos de leitura)**

---

## 📋 Ordem de Implementação

### FASE 1: Credenciais (20 minutos)
Você precisa obter chaves de APIs de 7 serviços. **Faça AGORA:**

#### 1. Supabase
- [ ] Já tem conta? Se não: [supabase.com/sign-up](https://supabase.com)
- [ ] Vá para: **Seu Projeto** → **Settings** → **Database** → **Connection Pooling**
- [ ] Copie: `SUPABASE_URL` e `SUPABASE_ANON_KEY`
- [ ] **Adicione ao arquivo**: `.env` do projeto

#### 2. Stripe
- [ ] Vá para: [dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)
- [ ] Copie: **Secret Key** (começa com `sk_test_`)
- [ ] 🔑 **Guarde com segurança!**

#### 3. Slack
- [ ] Vá para: [api.slack.com/apps](https://api.slack.com/apps)
- [ ] **Create New App** → **From scratch**
- [ ] Nome: `LabBridge Bot`
- [ ] Workspace: seu workspace
- [ ] **OAuth & Permissions** → Adicione scopes: `chat:write`, `channels:read`, `users:read`
- [ ] **Install to Workspace**
- [ ] Copie: **Bot User OAuth Token** (começa com `xoxb-`)

#### 4. Resend
- [ ] Vá para: [resend.com/sign-up](https://resend.com/sign-up)
- [ ] Crie conta (grátis)
- [ ] Vá para: [resend.com/api-keys](https://resend.com/api-keys)
- [ ] Copie: sua **API Key** (começa com `re_`)

#### 5. AWS S3
- [ ] Vá para: [console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/)
- [ ] **Users** → **Create user** → Nome: `labbridge-claude`
- [ ] **Attach policies** → `AmazonS3FullAccess`
- [ ] **Create access key**
- [ ] Copie: **Access Key ID** e **Secret Access Key**

#### 6. GitHub
- [ ] Vá para: [github.com/settings/tokens](https://github.com/settings/tokens)
- [ ] **Generate new token (classic)**
- [ ] Escopo: `repo` + `read:user`
- [ ] Copie: o token (começa com `ghp_`)

#### 7. PostgreSQL (do Supabase)
- [ ] Vá para seu projeto Supabase
- [ ] **Settings** → **Database** → **Connection string**
- [ ] Copie a string PostgreSQL (formato: `postgresql://user:pass@host/db`)

---

### FASE 2: Instalação no Claude Code (15 minutos)

Abra o terminal e execute:

```bash
# 1. Supabase
claude mcp add
# Quando pedir:
# - Name: supabase
# - Type: command
# - Command: npx
# - Args: -y @supabase-community/supabase-mcp@latest

# 2. PostgreSQL
claude mcp add
# - Name: postgresql
# - Type: command
# - Command: npx
# - Args: -y @modelcontextprotocol/server-postgres postgresql://user:pass@host/db

# 3. Stripe
claude mcp add
# - Name: stripe
# - Type: command
# - Command: npx
# - Args: -y @stripe/mcp --tools=all
# - Env: STRIPE_SECRET_KEY=sk_test_...

# 4. Slack
claude mcp add
# - Name: slack
# - Type: command
# - Command: npx
# - Args: -y @korotovsky/slack-mcp-server
# - Env: SLACK_BOT_TOKEN=xoxb-...

# 5. Resend
claude mcp add
# - Name: resend
# - Type: command
# - Command: npx
# - Args: -y mcp-send-email
# - Env: RESEND_API_KEY=re_...

# 6. Filesystem
claude mcp add
# - Name: filesystem
# - Type: command
# - Command: npx
# - Args: -y @modelcontextprotocol/server-filesystem C:\Users\otavi\Desktop\New_LabBridge

# 7. AWS S3
claude mcp add
# - Name: s3
# - Type: command
# - Command: npx
# - Args: -y aws-s3-mcp --allow-write
# - Env: AWS_REGION=us-east-1 | AWS_ACCESS_KEY_ID=... | AWS_SECRET_ACCESS_KEY=...

# 8. GitHub
claude mcp add
# - Name: github
# - Type: command
# - Command: npx
# - Args: -y github-mcp-server
# - Env: GITHUB_TOKEN=ghp_... | GITHUB_OWNER=seu-user | GITHUB_REPO=labbridge

# 9. Memory
claude mcp add
# - Name: memory
# - Type: command
# - Command: npx
# - Args: -y @modelcontextprotocol/server-memory
# (sem credenciais)

# Verificar
claude mcp list
```

---

### FASE 3: Validação (5 minutos)

No prompt do Claude, teste cada um:

```
# Supabase
"List all tables in my Supabase project"

# PostgreSQL
"Show me the schema of the saved_analyses table"

# Stripe
"Get my Stripe account balance"

# Slack
"Post a message to #general saying 'LabBridge MCP is working'"

# Resend
"Send a test email to test@example.com with subject 'MCP Test'"

# S3
"List all files in my labbridge-uploads bucket"

# GitHub
"Show my recent commits"
```

Se todos retornarem sem erro → ✅ **Pronto!**

---

## 🚨 Coisas Importantes

### Segurança
- ❌ **NUNCA** commit suas chaves no Git
- ✅ Use `.env` files
- ✅ Coloque `.env` no `.gitignore`
- ✅ Regenere chaves regularmente

### Erros Comuns
| Erro | Solução |
|------|---------|
| `command not found: npx` | Reinstale Node.js |
| `Invalid token` | Copie a chave novamente, sem espaços |
| MCP não aparece | Feche/reabra terminal e execute `claude mcp list` |
| `Permission denied` no PostgreSQL | Verifique credenciais do banco |

---

## ✅ Depois de Tudo Instalado

1. Feche e reabra o Claude Code
2. Teste cada MCP 1x
3. Leia: `PROMPTS_CLAUDE_OPUS_4.5.md` para ver como usar
4. Comece com o Sprint 1 das funcionalidades

---

**Tempo Total**: ~30-45 minutos
**Dificuldade**: ⭐⭐ (Fácil-Médio)
**Próximo**: Abra `SETUP_MCP_MANUAL_STEPS.md` para instruções detalhadas
