# 🚀 Guia Completo: Adicionar Todos os MCPs ao LabBridge

**Data**: 05/02/2026
**Status**: Pronto para implementação
**Tempo Estimado**: ~30-45 minutos para setup inicial

---

## 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [MCPs por Prioridade](#mcps-por-prioridade)
3. [Instalação Passo a Passo](#instalação-passo-a-passo)
4. [Verificação e Testes](#verificação-e-testes)
5. [Troubleshooting](#troubleshooting)

---

## ✅ Pré-requisitos

Antes de começar, você precisa:

- [ ] Node.js 18.0.0 ou superior instalado
- [ ] NPX disponível no terminal
- [ ] Acesso a contas/APIs de serviços externos
- [ ] Git configurado (para credenciais)
- [ ] Uma pasta `.claude` ou criar em `~/.claude/` (Linux/Mac) ou `C:\Users\{user}\.claude\` (Windows)

**Verificar instalação:**
```bash
node --version
npm --version
npx --version
```

---

## 🎯 MCPs por Prioridade

### TIER 1: CRÍTICO ⚠️ (Fazer Primeira)
- [x] Supabase
- [x] PostgreSQL
- [ ] Stripe

### TIER 2: IMPORTANTE (Depois do Tier 1)
- [ ] Slack
- [ ] Resend
- [ ] Filesystem
- [ ] AWS S3

### TIER 3: COMPLEMENTAR (Opcional)
- [ ] GitHub
- [ ] Memory
- [ ] n8n (já implementado)
- [ ] OpenAI (fallback)

---

## 🔧 Instalação Passo a Passo

### 1️⃣ SUPABASE MCP (CRÍTICO)

#### O que faz:
- Acesso total ao banco de dados PostgreSQL do Supabase
- Criar/modificar tabelas
- Executar queries com RLS (Row Level Security)
- Gerenciar migrations

#### Passo 1: Configuração inicial
```bash
# Terminal em qualquer lugar
claude mcp add
```

Ao executar, ele perguntará:
- **MCP Server Name**: `supabase`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y @supabase-community/supabase-mcp@latest`

#### Passo 2: Autenticação Supabase
Quando você usar o MCP pela primeira vez:
1. O terminal abrirá uma janela do navegador automaticamente
2. Faça login na sua conta Supabase (https://supabase.com)
3. Autorize o MCP a acessar sua organização
4. Copie o **Project ID** do seu projeto LabBridge

#### Passo 3: Confirmar sucesso
```bash
claude mcp list
# Deve mostrar "supabase" na lista
```

#### Exemplo de uso no prompt:
```
Leia todas as análises na tabela 'saved_analyses' e mostre quantas há por laboratório
```

---

### 2️⃣ POSTGRESQL MCP (CRÍTICO)

#### O que faz:
- Conexão direta ao PostgreSQL (backend do Supabase)
- Queries SQL complexas
- Transações
- Performance analysis

#### Passo 1: Configuração
```bash
claude mcp add
```

Responda:
- **Name**: `postgresql`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y @modelcontextprotocol/server-postgres postgresql://user:password@localhost:5432/labbridge_db`

#### ⚠️ IMPORTANTE: Credenciais do Banco

Se você usa **Supabase**, precisa das credenciais do banco:

1. Vá para: [Supabase Dashboard](https://supabase.com) → Seu Projeto → Connection Strings
2. Copie a string do PostgreSQL (formato `postgresql://...`)
3. Substitua na configuração acima

**Ou, se usar banco local:**
```
postgresql://postgres:sua_senha@localhost:5432/labbridge_db
```

#### Passo 2: Testar conexão
```bash
# No terminal, testar conexão
psql postgresql://usuario:senha@host:5432/labbridge_db -c "SELECT version();"
```

Se der erro, ajuste as credenciais.

#### Exemplo de uso:
```
Ache todos os exames no SIMUS que têm COMPULAB_EXAME_ID null e exporte como lista
```

---

### 3️⃣ STRIPE MCP (IMPORTANTE)

#### O que faz:
- Gerenciar clientes e assinaturas
- Criar/atualizar produtos e preços
- Gerar invoices
- Webhooks de pagamento

#### Passo 1: Obter Stripe API Key

1. Vá para: [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copie a **Secret Key** (começa com `sk_test_` ou `sk_live_`)
3. ⚠️ NUNCA compartilhe essa chave!

#### Passo 2: Adicionar MCP
```bash
claude mcp add
```

Responda:
- **Name**: `stripe`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y @stripe/mcp --tools=all`
- **Environment Variables**:
  ```
  STRIPE_SECRET_KEY=sk_test_SEU_SECRET_KEY_AQUI
  ```

#### Passo 3: Testar
No prompt, peça:
```
Liste todos os meus produtos e preços no Stripe
```

---

### 4️⃣ SLACK MCP (IMPORTANTE)

#### O que faz:
- Postar mensagens em canais
- Notificações de análises completadas
- Alertas de divergências críticas

#### Passo 1: Criar Bot Slack

1. Vá para: [Slack Apps](https://api.slack.com/apps)
2. Clique em "Create New App" → "From scratch"
3. Nome: `LabBridge Bot`
4. Workspace: selecione seu workspace

#### Passo 2: Configurar permissões

No painel do app:
1. Na esquerda, clique em **OAuth & Permissions**
2. Scroll para **Scopes** > **Bot Token Scopes**
3. Adicione essas permissões:
   - `chat:write`
   - `channels:read`
   - `users:read`
   - `chat:write.public`

#### Passo 3: Instalar no workspace

1. Volte para **OAuth & Permissions**
2. Click em **Install to Workspace**
3. Autorize
4. Copie o **Bot User OAuth Token** (começa com `xoxb-`)

#### Passo 4: Adicionar ao Claude
```bash
claude mcp add
```

Responda:
- **Name**: `slack`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y @korotovsky/slack-mcp-server`
- **Environment Variables**:
  ```
  SLACK_BOT_TOKEN=xoxb-SEU_TOKEN_AQUI
  ```

---

### 5️⃣ RESEND MCP (IMPORTANTE)

#### O que faz:
- Enviar emails de notificação
- Relatórios automáticos
- Confirmações de análise

#### Passo 1: Criar conta Resend

1. Vá para: [Resend](https://resend.com)
2. Crie conta grátis
3. Vá para: [API Keys](https://resend.com/api-keys)
4. Copie sua chave (começa com `re_`)

#### Passo 2: Adicionar MCP
```bash
claude mcp add
```

Responda:
- **Name**: `resend`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y mcp-send-email`
- **Environment Variables**:
  ```
  RESEND_API_KEY=re_SEU_API_KEY_AQUI
  ```

#### ⚠️ Importante: Domínio verificado
Para enviar emails para outros endereços além de teste:
1. Vá para [Resend Domains](https://resend.com/domains)
2. Adicione seu domínio (ex: `labbridge.com.br`)
3. Siga as instruções de verificação DNS

---

### 6️⃣ FILESYSTEM MCP (IMPORTANTE)

#### O que faz:
- Ler/escrever arquivos locais
- Processar PDFs e CSVs
- Criar relatórios

#### Passo 1: Adicionar MCP
```bash
claude mcp add
```

Responda:
- **Name**: `filesystem`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y @modelcontextprotocol/server-filesystem C:\Users\otavi\Desktop\New_LabBridge`

#### Passo 2: Definir diretórios permitidos

Edite `~/.claude/mcp-config.json` e adicione:
```json
"filesystem": {
  "allowed_directories": [
    "C:\\Users\\otavi\\Desktop\\New_LabBridge\\uploads",
    "C:\\Users\\otavi\\Desktop\\New_LabBridge\\exports",
    "C:\\Users\\otavi\\Desktop\\New_LabBridge\\labbridge"
  ]
}
```

---

### 7️⃣ AWS S3 MCP (IMPORTANTE)

#### O que faz:
- Alternativa ao Cloudinary
- Upload/download de arquivos
- Listar e gerenciar buckets

#### Passo 1: Criar credenciais AWS

1. Vá para: [AWS IAM](https://console.aws.amazon.com/iam/)
2. Crie um novo usuário (ex: `labbridge-claude`)
3. Nas permissões, adicione apenas:
   - `AmazonS3FullAccess` (ou más específico)
4. Crie uma Access Key
5. Copie: **Access Key ID** e **Secret Access Key**

#### Passo 2: Adicionar MCP
```bash
claude mcp add
```

Responda:
- **Name**: `s3`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y aws-s3-mcp --allow-write`
- **Environment Variables**:
  ```
  AWS_REGION=us-east-1
  AWS_ACCESS_KEY_ID=AKIA_SEU_ACCESS_KEY
  AWS_SECRET_ACCESS_KEY=SUA_SECRET_KEY
  S3_BUCKETS=labbridge-uploads,labbridge-exports
  ```

#### Passo 3: Criar buckets (se necessário)
```bash
# No AWS Console, crie os buckets:
# - labbridge-uploads
# - labbridge-exports
```

---

### 8️⃣ GITHUB MCP (ÚTIL)

#### O que faz:
- Versionamento de relatórios
- Criar issues de divergências críticas
- Commits automáticos

#### Passo 1: Gerar GitHub Token

1. Vá para: [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Clique em "Generate new token (classic)"
3. Escopo necessário:
   - ✅ `repo` (acesso completo)
   - ✅ `read:user` (ler dados públicos do usuário)
4. Copie o token

#### Passo 2: Adicionar MCP
```bash
claude mcp add
```

Responda:
- **Name**: `github`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y github-mcp-server`
- **Environment Variables**:
  ```
  GITHUB_TOKEN=ghp_SEU_TOKEN
  GITHUB_OWNER=seu-usuario-ou-org
  GITHUB_REPO=labbridge
  ```

---

### 9️⃣ MEMORY MCP (ÚTIL - SEM CONFIG)

#### O que faz:
- Salva conhecimento entre conversas
- Grafo de memória persistente

#### Passo 1: Adicionar MCP
```bash
claude mcp add
```

Responda:
- **Name**: `memory`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y @modelcontextprotocol/server-memory`

**Não requer credenciais!**

---

### 🔟 N8N MCP (OPCIONAL - JÁ IMPLEMENTADO)

Seu projeto já tem n8n configurado em `services/n8n_service.py`.

Se quiser usar MCP também:
```bash
claude mcp add
```

- **Name**: `n8n`
- **Type**: `command`
- **Command**: `npx`
- **Arguments**: `-y n8n-mcp`
- **Environment Variables**:
  ```
  N8N_BASE_URL=http://localhost:5678
  N8N_API_KEY=seu_api_key
  ```

---

## ✔️ Verificação e Testes

### Listar todos os MCPs instalados:
```bash
claude mcp list
```

Deve mostrar:
```
✓ supabase
✓ postgresql
✓ stripe
✓ slack
✓ resend
✓ filesystem
✓ s3
✓ github
✓ memory
```

### Testar cada MCP:

#### Supabase
```
List all tables in my Supabase project
```

#### PostgreSQL
```
Show me the schema of the saved_analyses table
```

#### Stripe
```
Get my Stripe account balance
```

#### Slack
```
Post a test message to #general saying "LabBridge MCP test"
```

#### Resend
```
Send a test email to my@email.com saying "MCP is working"
```

#### Filesystem
```
List all files in the uploads directory
```

#### GitHub
```
Show my recent commits in the labbridge repository
```

---

## 🐛 Troubleshooting

### Erro: "command not found: npx"
```bash
# Instale Node.js de novo
# ou reinstale npm
npm install -g npm@latest
```

### Erro: "Permission denied" no PostgreSQL
- Verifique credenciais de acesso
- Se usar Supabase, obtenha a connection string correta
- No terminal, teste manualmente:
  ```bash
  psql postgresql://usuario:senha@host/database
  ```

### Erro: "Invalid token" (Slack, Stripe, etc)
- Copie a chave exatamente como está (sem espaços extras)
- Certifique-se de que não expirou
- Gere uma nova chave se necessário

### MCP não aparece no `claude mcp list`
1. Feche e reabra o terminal
2. Execute `claude mcp add` novamente
3. Verifique o arquivo `~/.claude/mcp-config.json`

### Credenciais não são passadas ao MCP
1. Verifique que as variáveis estão no `mcp-config.json`
2. Tente definir como variáveis de ambiente do sistema:
   ```bash
   # Linux/Mac
   export STRIPE_SECRET_KEY=sk_test_...

   # Windows PowerShell
   $env:STRIPE_SECRET_KEY="sk_test_..."
   ```

---

## 📝 Próximos Passos

Depois de instalar todos os MCPs:

1. **Testar integração** com o código do LabBridge
2. **Criar prompts específicos** para cada feature (veja PROMPTS_CLAUDE_OPUS_4.5.md)
3. **Adicionar tratamento de erros** nas integrações
4. **Documentar** como usar cada MCP no projeto

---

## 📚 Referências Oficiais

- [Supabase MCP Docs](https://supabase.com/docs/guides/getting-started/mcp)
- [Stripe MCP Docs](https://docs.stripe.com/mcp)
- [Slack MCP Docs](https://docs.slack.dev/ai/mcp-server/)
- [Resend MCP GitHub](https://github.com/resend/mcp-send-email)
- [AWS S3 MCP Docs](https://awslabs.github.io/mcp/servers/s3-tables-mcp-server)
- [GitHub MCP Docs](https://docs.github.com/en/rest)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/specification/2025-11-25)

---

**Status**: ✅ Pronto para implementação
**Última atualização**: 05/02/2026
