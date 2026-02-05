# 📡 GUIA: Instalação de MCP Supabase + Claude Code

**Objetivo:** Conectar Claude Code diretamente ao seu banco Supabase para ajudar na integração LabBridge

---

## 🎯 POR QUE UMA MCP?

Com a MCP do Supabase, eu poderei:
- ✅ **Ler dados** direto do seu banco (sem código intermediário)
- ✅ **Executar queries SQL** para validar estrutura
- ✅ **Verificar RLS policies** e segurança
- ✅ **Atualizar schemas** conforme necessário
- ✅ **Testar dados** em tempo real
- ✅ **Gerar migrations** automaticamente

---

## 📋 PRÉ-REQUISITOS

Antes de começar, verifique se você tem:

```bash
# 1. Node.js instalado (versão 18+)
node --version
# Esperado: v18.0.0 ou superior

# 2. npm disponível
npm --version
# Esperado: 9.0.0 ou superior

# 3. Git (opcional, mas recomendado)
git --version
```

Se não tiver, instale em:
- **Node.js:** https://nodejs.org/ (baixe versão LTS)

---

## 🚀 PASSO 1: OBTER CREDENCIAIS SUPABASE

### A. Acesse o Dashboard Supabase

```
1. Vá para: https://supabase.com/dashboard
2. Faça login com sua conta
3. Selecione seu projeto LabBridge
```

### B. Copie as Credenciais

Na aba **"Settings"** → **"API"**:

```
📋 Copie EXATAMENTE:
├─ Project URL:         https://xxx.supabase.co
├─ Anon Public Key:     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
└─ Service Role Key:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                        (⚠️ MANTENHA SEGURO - Não compartilhe)
```

**Dica:** O Service Role Key tem mais permissões (necessário para a MCP funcionar).

---

## ⚙️ PASSO 2: INSTALAR A MCP GLOBALMENTE

### Abra PowerShell (Windows) ou Terminal (Mac/Linux):

```powershell
# Windows PowerShell
npm install -g @supabase-community/supabase-mcp
```

```bash
# Mac/Linux
sudo npm install -g @supabase-community/supabase-mcp
```

**Verificar instalação:**
```bash
supabase-mcp --version
```

---

## 📝 PASSO 3: CONFIGURAR CLAUDE CODE

### A. Atualizar arquivo de configuração MCP

Edite o arquivo que criei para você:
```
C:\Users\otavi\.claude\mcp-config.json
```

Substitua pelos seus dados:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["@supabase-community/supabase-mcp"],
      "env": {
        "SUPABASE_URL": "https://seu-projeto.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "SUPABASE_PROJECT_ID": "seu-projeto-id"
      }
    }
  }
}
```

**Exemplo completo:**
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["@supabase-community/supabase-mcp"],
      "env": {
        "SUPABASE_URL": "https://labbridge-abc123.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhYmJyaWRnZSIsInJvbGUiOiJzZXJ2aWNlX3JvbGUifQ...",
        "SUPABASE_PROJECT_ID": "labbridge-abc123"
      }
    }
  }
}
```

---

## ✅ PASSO 4: VALIDAR A CONFIGURAÇÃO

### A. Testar a Conexão (Claude Code)

Quando reiniciar o Claude Code, a MCP deve estar disponível. Você verá uma mensagem como:

```
🔌 MCP Server "supabase" inicializado com sucesso
```

### B. Teste um Comando Simples

Me envie uma mensagem assim:
```
"Teste a conexão Supabase - liste as tabelas do meu banco"
```

Se funcionou, você verá:
```
✅ Conectado ao Supabase
📊 Tabelas encontradas:
  - saved_analyses
  - analysis_items
  - user_profiles
  - ... (suas outras tabelas)
```

---

## 🔐 PASSO 5: SEGURANÇA (IMPORTANTE!)

### ⚠️ Nunca Faça Isso:

```
❌ NÃO COMPARTILHE o Service Role Key
❌ NÃO COLOQUE em arquivos públicos
❌ NÃO COMMITE no git
```

### ✅ Faça Isso:

```
✅ Guarde em local seguro (.env local)
✅ Revogue se vazar (Settings → API → Regenerate)
✅ Use em desenvolvimento apenas
```

**Para Produção:**
- Use variáveis de ambiente do sistema
- Não hardcode credenciais

---

## 🛠️ PASSO 6: USAR A MCP

Após configurar, você pode me pedir:

### Exemplos de Comandos:

```
"Crie a tabela saved_analyses com as colunas..."
"Execute esta query SQL e me mostre os resultados"
"Valide as RLS policies da tabela user_profiles"
"Verifique se a coluna tenant_id existe em todas as tabelas"
"Gere uma migration para adicionar a coluna..."
"Mostre os dados atuais da tabela audit_summaries"
```

### O Que Eu Posso Fazer:

| Ação | Exemplo |
|------|---------|
| 📖 Ler dados | "Quantas análises foram salvas?" |
| 📝 Executar SQL | "Run: SELECT * FROM saved_analyses LIMIT 5" |
| 🔧 Criar tabelas | "Crie a tabela exam_synonyms" |
| 🔒 Gerenciar RLS | "Mostre as policies de saved_analyses" |
| 🚀 Migrations | "Crie uma migration para adicionar coluna x" |
| ✅ Validar | "Verifique se o schema está correto" |

---

## 🐛 TROUBLESHOOTING

### Problema: "MCP não conecta"

```
❌ Erro: SUPABASE_URL não configurado
✅ Solução: Verifique se as variáveis estão corretas em mcp-config.json
```

**Checklist:**
```
□ Node.js 18+ instalado
□ npm install -g @supabase-community/supabase-mcp funcionou
□ mcp-config.json tem SUPABASE_URL correto
□ Service Role Key é válido (não expirou)
□ Nenhuma mudança manual nas permissões Supabase
```

### Problema: "Permissão negada"

```
❌ Erro: 401 Unauthorized
✅ Solução: Service Role Key pode ter expirado
```

**Como Regenerar:**
1. Supabase Dashboard → Settings → API
2. Clique em "Regenerate" no Service Role Key
3. Atualize o mcp-config.json

### Problema: "Porta em uso"

```
❌ Erro: Port 3000 already in use
✅ Solução: Feche outros processos na porta 3000
```

```powershell
# Windows
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Mac/Linux
lsof -i :3000
kill -9 [PID]
```

---

## 📊 FLUXO DE TRABALHO PROPOSTO

Com a MCP funcionando, aqui está como vamos trabalhar:

```
┌─────────────────────────────────────────────┐
│ 1. Você: "Crie as tabelas no Supabase"      │
│    ↓                                         │
│ 2. Claude (MCP): Conecta e executa SQL      │
│    ↓                                         │
│ 3. Validação: Verifica se criou com sucesso │
│    ↓                                         │
│ 4. Resultado: "✅ Tabelas criadas!"         │
│    ↓                                         │
│ 5. Próximo Passo: Implementação de features │
└─────────────────────────────────────────────┘
```

---

## 🎯 PRÓXIMAS ETAPAS

### Imediatamente Após Configurar:

1. **Envie uma mensagem simples:**
   ```
   "Teste a conexão com Supabase"
   ```

2. **Se funcionar, vou poder:**
   - ✅ Ver quais tabelas existem
   - ✅ Validar o schema
   - ✅ Executar queries
   - ✅ Ajudar com migrations

3. **Depois, podemos:**
   - 📋 Criar as tabelas do RELATORIO_FUNCIONALIDADES_PENDENTES.md
   - 🔐 Configurar RLS policies
   - 🧪 Testar com dados de exemplo
   - 🚀 Começar a integração das features

---

## 📞 SUPORTE

Se tiver problemas:

1. **Erro ao instalar?**
   - Verifique Node.js: `node --version`
   - Limpe cache npm: `npm cache clean --force`

2. **Erro ao conectar?**
   - Teste credenciais no Supabase Dashboard
   - Regenere o Service Role Key

3. **Dúvidas sobre MCP?**
   - Docs oficiais: [supabase.com/docs/guides/getting-started/mcp](https://supabase.com/docs/guides/getting-started/mcp)

---

## ✨ BENEFÍCIOS IMEDIATOS

Com essa configuração, você ganha:

```
🚀 Integração mais rápida
🔍 Visibilidade completa do banco
✅ Validação automática de schema
📊 Testes de dados em tempo real
🔧 Migrations gerenciadas automáticamente
🛡️ Segurança implementada junto
⏱️ Menos comunicação, mais ação
```

---

**Status:** Pronto para começar!

Depois de seguir os passos, me envie uma mensagem simples e vou confirmar se a conexão está funcionando. 🎉

