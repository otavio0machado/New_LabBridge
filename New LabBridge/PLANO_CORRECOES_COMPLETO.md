# PLANO DE CORRECOES COMPLETO - LabBridge

**Data:** 2026-02-05
**Total de issues:** 70+
**Fases:** 6 (P0 a P5)
**Estimativa de prompts:** 28

> **Como usar:** Cada prompt abaixo e auto-contido. Copie e cole no Claude Code
> em sequencia. Aguarde a conclusao de cada prompt antes de enviar o proximo.
> Prompts da mesma fase podem ser executados em paralelo quando indicado.

---

## FASE 0 - CRASHES CRITICOS (4 bugs que impedem a app de funcionar)

### Prompt 0.1 - Fix asyncio import em detective_state.py

```
No arquivo labbridge/labbridge/states/detective_state.py:

1. Adicione `import asyncio` no bloco de imports do topo do arquivo
2. Verifique se existem outros imports faltando
3. NAO altere nenhuma outra logica do arquivo

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\states\detective_state.py
```

### Prompt 0.2 - Fix metodo inexistente em history_state.py

```
No arquivo labbridge/labbridge/states/history_state.py:

1. Na funcao `load_history_data`, ha uma chamada `self._load_activity_log()` (com underscore)
   mas o metodo real se chama `load_activity_log()` (sem underscore).
   Corrija a chamada para usar o nome correto do metodo.
2. Como `load_activity_log` e um event handler async com yield, a chamada correta
   deve ser: `async for _ in self.load_activity_log(): yield` ao inves de `await`.

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\states\history_state.py
```

### Prompt 0.3 - Fix imports top-level que crasham em ai_analysis.py

```
No arquivo labbridge/labbridge/utils/ai_analysis.py:

1. Os imports `import openai` (linha ~7) e `import google.genai as genai` (linha ~14-15)
   estao no top-level e causam ImportError se os pacotes nao estiverem instalados.
2. Mova esses imports para dentro das funcoes que os utilizam (lazy imports),
   usando try/except ImportError para dar mensagem clara.
3. Exemplo do padrao a seguir:
   ```python
   def process_batch_openai(...):
       try:
           import openai
       except ImportError:
           raise ImportError("Pacote 'openai' nao instalado. Execute: pip install openai")
       ...
   ```
4. Faca o mesmo para google.genai nas funcoes que usam Gemini.
5. Remova tambem: a funcao `format_ai_report()` (linhas ~796-798) que e um no-op,
   a funcao `chunk_data()` (~linha 215) que nunca e chamada,
   e a funcao `calculate_local_totals()` (~linha 32) que nunca e chamada.
6. Remova o yield duplicado (mesmo texto, mesmo progresso) que ocorre em linhas ~496-498.

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\utils\ai_analysis.py
```

### Prompt 0.4 - Fix @dataclass dangling em n8n_tools_service.py

```
No arquivo labbridge/labbridge/services/n8n_tools_service.py:

1. Ha um decorator `@dataclass` orfao (linha ~16) que sobrou da remocao de
   `WestgardResult` e esta sendo aplicado incorretamente na classe `N8NToolsService`.
2. Remova esse `@dataclass` decorator.
3. Se o import de `dataclass` ficou sem uso, remova-o tambem.

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\services\n8n_tools_service.py
```

---

## FASE 1 - SEGURANCA (8 vulnerabilidades)

### Prompt 1.1 - Proteger API keys e senhas nos states

```
Corrija as seguintes vulnerabilidades de exposicao de dados sensiveis no frontend:

1. Em labbridge/states/ai_state.py:
   - Mude `openai_api_key: str = ""` para `_openai_api_key: str = ""`
     (prefixo _ faz o Reflex tratar como backend-only var, nao serializada pro frontend)
   - Atualize TODAS as referencias a `openai_api_key` neste arquivo e em qualquer
     outro arquivo que o referencie (busque por "openai_api_key" no projeto)
   - Na UI (se houver input para o usuario digitar a key), use um event handler
     `set_api_key(self, key: str)` que seta `self._openai_api_key = key`

2. Em labbridge/states/settings_state.py:
   - Mude `current_password: str = ""` para `_current_password: str = ""`
   - Mude `new_password: str = ""` para `_new_password: str = ""`
   - Mude `confirm_password: str = ""` para `_confirm_password: str = ""`
   - Crie event handlers para setar essas vars:
     ```python
     def set_current_password(self, val: str):
         self._current_password = val
     def set_new_password(self, val: str):
         self._new_password = val
     def set_confirm_password(self, val: str):
         self._confirm_password = val
     ```
   - Atualize `change_password()` para usar os nomes com prefixo _
   - Atualize a pagina settings.py para usar os novos event handlers nos on_change

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 1.2 - Fix tenant_id isolation no base_repository e audit_service

```
Corrija o vazamento de dados multi-tenant:

1. Em labbridge/repositories/base_repository.py:
   - Modifique `get_all()` para EXIGIR `tenant_id` como parametro obrigatorio:
     ```python
     def get_all(self, tenant_id: str, limit: int = 100) -> list:
         try:
             response = self.client.table(self.table_name)\
                 .select("*")\
                 .eq("tenant_id", tenant_id)\
                 .limit(limit)\
                 .execute()
             return response.data if response.data else []
         except Exception as e:
             print(f"Erro get_all: {e}")
             return []
     ```
   - Modifique `get_by_id()` para tambem filtrar por tenant_id
   - Modifique `delete()` para tambem filtrar por tenant_id

2. Em labbridge/services/audit_service.py:
   - Adicione `tenant_id: str` como parametro obrigatorio em TODOS os metodos:
     `get_audit_history`, `get_latest_audit_summary`, `get_patient_history`,
     `get_resolutions`, `save_audit_summary`, `save_divergence_resolution`
   - Adicione `.eq("tenant_id", tenant_id)` em todas as queries

3. Em labbridge/repositories/audit_repository.py:
   - Atualize as chamadas para passar tenant_id

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 1.3 - Remover tenant_id="local" do auth_service

```
No arquivo labbridge/services/auth_service.py:

1. Busque TODAS as ocorrencias de `tenant_id = "local"` ou `"tenant_id": "local"`
2. Na funcao `_try_local_login()`: em vez de retornar tenant_id "local",
   busque o tenant real do usuario no Supabase, ou se for modo dev,
   use o tenant_id do .env (adicione TENANT_ID no .env se necessario)
3. Na funcao `get_or_create_profile()`: os fallbacks que retornam "local"
   devem retornar o tenant_id real do usuario logado
4. Remova tambem o metodo `get_current_user()` DUPLICADO (ha 2 definicoes,
   a primeira ~linha 167 e silenciosamente sobrescrita pela segunda ~linha 385).
   Mantenha APENAS a segunda versao (que inclui created_at e tem error logging).
5. Corrija a inconsistencia de senha minima: `update_password()` exige 6 chars
   mas `verify_and_change_password()` exige 8 chars. Padronize para 8.

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\services\auth_service.py
```

### Prompt 1.4 - Fix OAuth callback e default tenant

```
No arquivo labbridge/states/auth_state.py:

1. Na funcao `handle_oauth_callback()`: apos setar `self.current_user`,
   TAMBEM busque e sete `self.current_tenant` (usando o tenant_id do user).
   Exemplo:
   ```python
   # Apos setar current_user
   if self.current_user and self.current_user.tenant_id:
       from ..services.supabase_client import supabase
       if supabase:
           result = supabase.table("tenants").select("*").eq("id", self.current_user.tenant_id).single().execute()
           if result.data:
               self.current_tenant = Tenant(**result.data)
   ```

2. Remova o fallback de tenant com `id="default"` (~linhas 169-174).
   Se nao ha tenant, o usuario NAO deve estar autenticado. Sete
   `self.is_authenticated = False` e mostre erro em vez de criar tenant fake.

3. Corrija `is_viewer` que retorna True para qualquer usuario logado
   (porque `bool(self.user_role)` e sempre True). A logica correta seria:
   ```python
   @rx.var
   def is_viewer(self) -> bool:
       return self.user_role in ["viewer", "member", "analyst", "admin_lab", "admin_global", "admin", "owner"]
   ```
   Ou simplesmente: `return self.is_authenticated`

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\states\auth_state.py
```

### Prompt 1.5 - Fix checkout trust e subscription defaults

```
No arquivo labbridge/states/subscription_state.py:

1. Mude o default de `current_plan` de `"pro"` para `"starter"`:
   ```python
   current_plan: str = "starter"
   ```

2. Em `handle_checkout_success()`: NAO confie no parametro `plan` vindo do cliente.
   Em vez disso, verifique com o Stripe:
   ```python
   async def handle_checkout_success(self, session_id: str):
       from ..services.stripe_service import stripe_service
       # Verificar a sessao no Stripe
       if stripe_service.is_configured:
           import stripe
           session = stripe.checkout.Session.retrieve(session_id)
           # Extrair o plano real da sessao
           plan = session.metadata.get("plan", "starter")
           self.current_plan = plan
       self.payment_success = True
   ```
   Se o Stripe nao estiver configurado (modo dev), aceite o parametro mas logue um warning.

3. Adicione um `on_mount` handler ou um metodo `load_subscription()` que busque
   o plano real do tenant no Supabase ao carregar a pagina.

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\states\subscription_state.py
```

---

## FASE 2 - BUGS FUNCIONAIS (10 issues que fazem features nao funcionar)

### Prompt 2.1 - Fix f-strings nao reativas em dashboard, analise, conversor

```
CONTEXTO: Em Reflex, `f"{State.some_var}%"` avalia no build-time (Python), nao
reativamente. O correto e usar `State.some_var.to(str) + "%"` ou `rx.text(State.some_var, "%")`.

Corrija TODOS os f-strings com rx.Vars nos seguintes arquivos:

1. Em labbridge/pages/dashboard.py (~7 instancias):
   - `f"{State.financial_growth_day}%"` -> `State.financial_growth_day.to(str) + "%"`
   - `f"{State.divergences_count}"` -> `State.divergences_count.to(str)`
   - `f"{State.dashboard_approval_rate}%"` -> `State.dashboard_approval_rate.to(str) + "%"`
   - `f"{State.total_patients_count}"` -> `State.total_patients_count.to(str)`
   - `f"{State.goal_progress}%"` -> `State.goal_progress.to(str) + "%"`
   - `f"Meta: {State.formatted_monthly_goal}"` -> `"Meta: " + State.formatted_monthly_goal`
   - Para o width do progress bar: use `State.goal_progress.to(str) + "%"` como valor de width

2. Em labbridge/pages/analise.py (~1 instancia):
   - `f"{State.analysis_progress_percentage}%"` -> `State.analysis_progress_percentage.to(str) + "%"`

3. Em labbridge/pages/conversor.py (~2 instancias):
   - `f"{State.csv_progress_percentage}%"` -> `State.csv_progress_percentage.to(str) + "%"`
   - Qualquer outro f-string com State vars

Busque por `f"` seguido de `State.` em todos os arquivos de pages/ para garantir
que nao perdemos nenhum.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 2.2 - Fix Python dict.get() com rx.Var em team.py e history.py

```
CONTEXTO: Em Reflex, quando `role` vem de `rx.foreach`, e um rx.Var, nao um string
Python. Chamar `python_dict.get(rx_var)` sempre retorna o default. A solucao e usar
`rx.match()` ou encadear `rx.cond()`.

1. Em labbridge/pages/team.py, funcao `role_badge(role)`:
   Substitua o padrao dict.get() por rx.match:
   ```python
   def role_badge(role):
       return rx.match(
           role,
           ("admin_global", rx.badge("Admin Global", color_scheme="red", variant="solid", ...)),
           ("admin_lab", rx.badge("Admin Lab", color_scheme="purple", variant="solid", ...)),
           ("admin", rx.badge("Admin", color_scheme="purple", variant="solid", ...)),
           ("owner", rx.badge("Proprietario", color_scheme="red", variant="solid", ...)),
           ("analyst", rx.badge("Analista", color_scheme="blue", variant="solid", ...)),
           ("member", rx.badge("Membro", color_scheme="blue", variant="soft", ...)),
           # default
           rx.badge("Visualizador", color_scheme="gray", variant="soft", ...),
       )
   ```

2. Em labbridge/pages/history.py, funcao `timeline_item(...)`:
   Substitua o dict.get() para `status` por rx.match da mesma forma:
   ```python
   # Para o icone
   icon = rx.match(
       status,
       ("concluida", rx.icon("check-circle", color=Color.SUCCESS, size=20)),
       ("erro", rx.icon("x-circle", color=Color.ERROR, size=20)),
       ("em_analise", rx.icon("clock", color=Color.WARNING, size=20)),
       rx.icon("circle", color=Color.TEXT_MUTED, size=20),  # default
   )
   # Para a cor do dot/connector
   dot_color = rx.match(
       status,
       ("concluida", Color.SUCCESS),
       ("erro", Color.ERROR),
       ("em_analise", Color.WARNING),
       Color.TEXT_MUTED,
   )
   ```

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 2.3 - Fix lambda closures em rx.foreach

```
CONTEXTO: Em Reflex, lambdas dentro de rx.foreach capturam a referencia da variavel
do loop, nao o valor. Todas apontam para o ultimo item. A solucao e usar
o event handler diretamente com o argumento, sem lambda wrapper.

1. Em labbridge/pages/team.py:
   Onde houver patterns como:
   ```python
   on_click=lambda: TeamState.open_edit_modal(member["id"])
   ```
   Substitua por:
   ```python
   on_click=TeamState.open_edit_modal(member["id"])
   ```
   (Em Reflex, `State.handler(arg)` dentro de rx.foreach ja faz o bind correto)

   Faca isso para TODAS as lambdas dentro de rx.foreach no arquivo:
   - open_edit_modal
   - remove_member
   - toggle_member_status
   - resend_member_invite
   - Qualquer outra

2. Em labbridge/pages/integrations.py:
   Mesmo fix para todas as lambdas dentro de rx.foreach:
   - sync_integration
   - open_config_modal
   - toggle_integration

3. Em labbridge/components/save_analysis_modal.py:
   Mesmo fix para:
   - load_saved_analysis
   - delete_saved_analysis

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 2.4 - Implementar filtros e paginacao funcionais em reports e history

```
Os filtros e paginacao existem na UI mas nao fazem nada. Implemente-os:

1. Em labbridge/states/reports_state.py:
   Crie uma computed var `filtered_analyses` que aplique os filtros:
   ```python
   @rx.var(auto_deps=False, deps=["type_filter", "date_filter", "search_query", "current_page", "items_per_page"])
   def filtered_analyses(self) -> list[dict]:
       # Pegar analyses do AnalysisState via getattr
       from .analysis_state import AnalysisState
       all_analyses = getattr(self, 'saved_analyses_list', [])

       filtered = all_analyses

       # Filtro por tipo
       if self.type_filter and self.type_filter != "all":
           filtered = [a for a in filtered if a.get("type", "") == self.type_filter]

       # Filtro por busca
       if self.search_query:
           q = self.search_query.lower()
           filtered = [a for a in filtered if q in a.get("name", "").lower() or q in a.get("description", "").lower()]

       return filtered

   @rx.var(auto_deps=False, deps=["filtered_analyses", "current_page", "items_per_page"])
   def paginated_analyses(self) -> list[dict]:
       start = self.current_page * self.items_per_page
       end = start + self.items_per_page
       return self.filtered_analyses[start:end]

   @rx.var(auto_deps=False, deps=["filtered_analyses", "items_per_page"])
   def total_pages(self) -> int:
       import math
       return max(1, math.ceil(len(self.filtered_analyses) / self.items_per_page))
   ```

   NOTA: ReportsState herda de AuthState, NAO de AnalysisState. Para acessar
   saved_analyses_list, voce precisara de uma abordagem diferente. Considere:
   - Adicionar um state var `_analyses: list[dict] = []` e um handler `load_analyses`
     que busca do Supabase diretamente
   - OU mudar a heranca para incluir AnalysisState (cuidado com diamond inheritance)

2. Em labbridge/pages/reports.py:
   - Substitua `AnalysisState.saved_analyses_list` por `ReportsState.paginated_analyses`
   - Atualize os controles de paginacao para usar `ReportsState.total_pages`
   - Adicione `on_mount=ReportsState.load_analyses` (ou equivalente)

3. Em labbridge/states/history_state.py:
   Faca o mesmo: crie computed vars para filtrar por status_filter e search_query.

4. Em labbridge/pages/history.py:
   Use a lista filtrada ao inves de `AnalysisState.saved_analyses_list` direto.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 2.5 - Fix DashboardState orfao e computed var shadowing

```
O DashboardState herda de AuthState e nunca consegue acessar dados de analise.
As computed vars de State tambem fazem shadow de vars de AnalysisState.

1. REMOVA o arquivo labbridge/states/dashboard_state.py inteiro.
   Ele e dead code - todas as computed vars retornam valores default.

2. Remova a referencia a DashboardState em labbridge/states/__init__.py

3. Em labbridge/state.py, resolva os shadowing de computed vars:
   - REMOVA `formatted_compulab_total` (ja existe em AnalysisState, e State herda dele)
   - REMOVA `top_offenders` (ja existe em AnalysisState)
   - Para `divergences_count`: AnalysisState tem como state var (int = 0) e State
     tem como computed var. REMOVA a computed var de State e use a state var
     de AnalysisState que e setada durante run_analysis.
   - Verifique que nenhuma pagina referencia `DashboardState` diretamente

4. `financial_growth_day` em state.py retorna hardcoded 2.5.
   Mude para calcular de verdade ou retorne 0.0 com um TODO claro:
   ```python
   @rx.var
   def financial_growth_day(self) -> float:
       # TODO: implementar calculo real de crescimento diario
       # Comparar receita de hoje vs media dos ultimos 7 dias
       return 0.0
   ```

5. `dashboard_pending_maintenances` retorna hardcoded 0. Mesmo tratamento.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 2.6 - Fix navbar com dados hardcoded e dual routing

```
1. Em labbridge/components/navbar.py:
   A secao do usuario no sidebar mostra "Admin"/"Administrador"/"AD" hardcoded.
   Corrija para usar dados reais:
   ```python
   # Onde esta o avatar e nome hardcoded, substitua por:
   rx.avatar(
       fallback=State.current_user.full_name.to(str)[:2].upper(),
       size="2",
   ),
   rx.box(
       rx.text(State.current_user.full_name, size="2", weight="medium"),
       rx.text(State.user_role, size="1", color=Color.TEXT_MUTED),
   ),
   ```

   NOTA: Voce vai precisar importar State no arquivo.

2. Remova a funcao `mobile_nav()` que retorna fragmento vazio.

3. Remova a duplicata "Meu Perfil" / "Configuracoes" que vao para a mesma rota.
   Mantenha apenas "Configuracoes".

4. Na barra de busca decorativa: por agora, remova-a completamente ou adicione
   um placeholder desabilitado com tooltip "Em breve". NAO deixe um input
   funcional que nao faz nada.

5. Para o dual routing (href vs State.set_page):
   - No mobile menu, substitua `on_select=State.set_page(...)` por
     `on_select=rx.redirect(href)` para usar o mesmo sistema de navegacao
     do sidebar (URL-based).
   - Ou melhor: use `rx.link` com `href` consistentemente em ambos.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

---

## FASE 3 - REMOVER MOCK DATA E DEAD CODE

### Prompt 3.1 - Remover arquivos de componentes mortos

```
Remova os seguintes arquivos que sao 100% dead code (nunca importados/usados):

1. DELETE labbridge/components/audit_alert.py
2. DELETE labbridge/components/charts.py
3. DELETE labbridge/components/results.py

Em labbridge/state.py, remova as state vars que so eram usadas por audit_alert:
- `audit_alert_message: str = ""`
- `is_audit_alert_visible: bool = False`
- `audit_warning_level: str = "warning"`

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 3.2 - Limpar funcoes mortas em ui.py

```
Em labbridge/components/ui.py, remova as 17 funcoes que nunca sao chamadas:

REMOVER: animated_heading, toast, stat_card, loading_spinner, kpi_card,
action_card, filter_bar, progress_bar, timeline_item, status_banner,
data_table_header, loading_state, error_state, success_state, warning_state,
empty_state, page_section

MANTER (estas sao usadas): heading, text, card, button, input, select,
form_field, page_header, segmented_control, text_area, status_badge

Apos remover, verifique se algum import no topo do arquivo ficou sem uso e remova-o.

Caminho: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\components\ui.py
```

### Prompt 3.3 - Limpar state vars e funcoes mortas

```
Remova as seguintes state vars nao utilizadas:

1. Em labbridge/states/analysis_state.py:
   - `resolution_notes: Dict[str, str] = {}` (nunca lido ou escrito)
   - `audit_history: list = []` (nunca populado)
   - `analysis_pdf: str = ""` (nunca escrito, usa pdf_preview_b64/pdf_url)
   - `processing_progress: int = 0` (superseded por analysis_progress_percentage)
   - `processing_total: int = 0` (idem)
   - `is_large_file_processing: bool = False` (idem)
   - `processing_progress_text: str = ""` (idem)
   - `ai_loading_progress: int = 0` (idem)
   - `compulab_file_bytes: bytes = b""` (sempre vazio apos upload)
   - `simus_file_bytes: bytes = b""` (sempre vazio apos upload)

2. Em labbridge/states/ai_state.py:
   - `ai_analysis_data: List[Dict] = []` (nunca populado)
   - `ai_analysis_csv: str = ""` (nunca escrito)

3. Em labbridge/states/reports_state.py:
   - `download_data: str = ""` (nunca usado, downloads usam rx.call_script)
   - `download_filename: str = ""` (idem)

4. Em labbridge/states/subscription_state.py:
   - `stripe_subscription_id: str = ""` (nunca setado)
   - `next_billing_date: str = ""` (nunca setado)

5. Em labbridge/states/settings_state.py:
   - `settings_email: str = ""` (nunca usado, sem setter, nao salvo)

6. Remova tambem:
   - `save_analysis_button()` em components/save_analysis_modal.py
   - `notification_center()` em components/notification_bell.py
   - `file_upload_section()` e `large_file_progress_indicator()` em components/file_upload.py

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 3.4 - Substituir mock data por dados reais ou TODOs claros

```
Substitua mock data por implementacoes reais ou TODOs explicitos:

1. Em labbridge/states/analysis_state.py, funcao `view_patient_history()`:
   - Remova os 3 PatientHistoryEntry hardcoded
   - Implemente busca real no Supabase:
   ```python
   async def view_patient_history(self, patient_name: str):
       self.selected_patient_name = patient_name
       self.is_showing_patient_history = True
       self.patient_history_data = []
       try:
           from ..services.audit_service import audit_service
           history = await audit_service.get_patient_history(
               patient_name=patient_name,
               tenant_id=self.current_user.tenant_id
           )
           self.patient_history_data = history
       except Exception as e:
           print(f"Erro ao carregar historico: {e}")
   ```

2. Em labbridge/states/detective_state.py, funcao `load_context()`:
   - Remova o fallback para `get_mock_divergency_data()`
   - Quando nao ha dados de analise, sete um contexto vazio com mensagem:
   ```python
   if not context_parts:
       self.data_context = "Nenhuma analise carregada. Faca upload e analise de arquivos primeiro."
       return
   ```

3. Em labbridge/services/subscription_service.py:
   - Adicione um TODO claro no topo: `# TODO: SUBSTITUIR POR SUPABASE - Este servico e 100% mock`
   - Por agora mantenha o mock mas adicione logging de warning:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.warning("subscription_service usando dados MOCK - implementar Supabase")
   ```

4. Em labbridge/services/local_storage.py:
   - Remova `_seed_team_members()` e `_seed_integrations()` inteiramente
   - Remova as chamadas a eles em `_seed_initial_data()`
   - Mantenha apenas a criacao das tabelas SQL

5. Em labbridge/ai/mock_data.py:
   - Adicione um warning no topo do arquivo:
   ```python
   """
   ATENCAO: Este modulo contem dados mock para desenvolvimento.
   NAO deve ser usado em producao. Todas as chamadas devem ser
   substituidas por dados reais do Supabase.
   """
   import logging
   logging.getLogger(__name__).warning("mock_data.py carregado - NAO usar em producao")
   ```

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 3.5 - Limpar styles.py e componentes mortos menores

```
1. Em labbridge/styles.py:
   - Remova os 5 estilos de tabela nunca usados:
     TABLE_STYLE, TABLE_HEADER_STYLE, TABLE_CELL_STYLE, TABLE_ROW_STYLE, TABLE_ROW_EVEN_STYLE
   - Remova `Animation.FADE_IN_UP` (nunca usado)
   - Unifique `TEXT_MUTED` e `TEXT_SECONDARY` (sao identicos "#64748B").
     Mantenha apenas `TEXT_MUTED` e faca find-replace de `TEXT_SECONDARY` -> `TEXT_MUTED`
     em todos os arquivos do projeto.
   - Corrija `WARNING_DARK`: esta como `#92400E` (Amber) mas `WARNING` e `#84CC16` (Lime).
     Mude WARNING_DARK para `#65A30D` (Lime 600) para manter a mesma familia de cores.
   - Adicione `RADIUS_XXL = "20px"` na classe Design (referenciado por file_upload.py com hasattr)

2. Em labbridge/components/navbar.py:
   - Remova a funcao `mobile_nav()` (retorna fragmento vazio)
   - Remova a exportacao de `mobile_nav` em components/__init__.py
   - Em labbridge/labbridge.py, remova o import de `mobile_nav`

3. Em labbridge/states/__init__.py:
   - Adicione os exports faltantes: `DetectiveState`, `NotificationState`

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

---

## FASE 4 - UI/UX FIXES

### Prompt 4.1 - Adicionar confirmacao em acoes destrutivas

```
Adicione dialogos de confirmacao para todas as acoes destrutivas:

1. Em labbridge/pages/reports.py:
   O botao de delete chama `AnalysisState.delete_saved_analysis(analysis["id"])` direto.
   Envolva com um AlertDialog:
   ```python
   rx.alert_dialog.root(
       rx.alert_dialog.trigger(
           rx.icon_button(rx.icon("trash-2", size=14), variant="ghost", color_scheme="red", size="1"),
       ),
       rx.alert_dialog.content(
           rx.alert_dialog.title("Excluir Analise"),
           rx.alert_dialog.description("Tem certeza que deseja excluir esta analise? Esta acao nao pode ser desfeita."),
           rx.flex(
               rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
               rx.alert_dialog.action(
                   rx.button("Excluir", color_scheme="red",
                       on_click=AnalysisState.delete_saved_analysis(analysis["id"])),
               ),
               spacing="3", justify="end",
           ),
       ),
   )
   ```

2. Em labbridge/pages/team.py:
   Mesmo padrao para "Remover Membro" e "Desativar".

3. Em labbridge/pages/settings.py:
   Mesmo padrao para "Solicitar Exclusao de Conta". Este e especialmente critico.

4. Em labbridge/components/save_analysis_modal.py:
   Adicione confirmacao no delete de analise salva.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 4.2 - Fix dialog close prematuro e on_mount faltantes

```
1. Em TODOS os modais que tem botao de acao dentro de rx.dialog.close,
   o dialog fecha ANTES da acao async completar. Corrija:

   Em labbridge/pages/team.py (invite modal):
   - Remova o `rx.dialog.close` wrapper do botao "Enviar Convite"
   - Em vez disso, feche o modal programaticamente no event handler `send_invite()`
     ao final (setar `self.show_invite_modal = False`)

   Em labbridge/pages/integrations.py (config modal):
   - Mesmo fix: remova rx.dialog.close do "Salvar", feche em `save_config()`

   Em labbridge/pages/help.py (contact modal):
   - Mesmo fix: remova rx.dialog.close do "Enviar", feche em `send_contact()`

2. Adicione on_mount handlers faltantes:

   Em labbridge/pages/settings.py:
   ```python
   @rx.page(route="/settings", on_load=SettingsState.load_settings)
   ```
   Ou adicione no rx.box principal: `on_mount=SettingsState.load_settings`

   Em labbridge/pages/subscription.py:
   Crie um handler `load_subscription` em SubscriptionState que busca o plano atual:
   ```python
   async def load_subscription(self):
       if self.current_tenant:
           self.current_plan = self.current_tenant.plan_type or "starter"
   ```
   E adicione como on_mount na pagina.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 4.3 - Fix analise.py e conversor.py UI issues

```
1. Em labbridge/pages/analise.py:
   - Remova o import nao usado: `from typing import Any`
   - Corrija o painel direito que mostra "Gerando PDF..." quando nenhuma geracao
     esta acontecendo. Use rx.cond para mostrar texto diferente:
     ```python
     rx.cond(
         State.is_generating_pdf,  # ou a var correta que indica geracao em andamento
         rx.text("Gerando PDF..."),
         rx.cond(
             State.pdf_url != "",
             rx.text("PDF pronto para download"),
             rx.text("Clique em 'Gerar PDF' para criar o relatorio"),
         ),
     )
     ```
   - Remova os botoes duplicados de export (manter apenas os do painel direito
     OU apenas os da action bar, nao ambos)

2. Em labbridge/pages/conversor.py:
   - Remova o import nao usado: `Typography`
   - Corrija Step 3 que nunca completa: mude `is_completed=False` para
     `is_completed=State.csv_generated` (ou a var equivalente)
   - Corrija o texto falso "Os arquivos sao processados localmente e nunca
     deixam seu computador" para: "Os arquivos sao processados de forma segura
     em nossos servidores e nao sao armazenados apos o processamento."
   - Para os downloads base64 de arquivos grandes: considere gerar um link
     de download temporario ao inves de data URIs inline.

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 4.4 - Fix team.py, login.py e help_state.py

```
1. Em labbridge/pages/team.py:
   - O role select mostra valores raw ("admin_lab", "viewer"). Substitua por labels:
     ```python
     rx.select(
         items=[
             {"label": "Visualizador", "value": "viewer"},
             {"label": "Analista", "value": "analyst"},
             {"label": "Admin Lab", "value": "admin_lab"},
             {"label": "Admin Global", "value": "admin_global"},
         ],
         ...
     )
     ```
     (ou use rx.select.item com label e value separados, conforme API do Reflex)
   - O avatar fallback recebe o nome completo. Mude para iniciais:
     use apenas as 2 primeiras letras ou compute iniciais.

2. Em labbridge/pages/login.py:
   - Substitua as URLs externas de favicon (google.com/favicon.ico, microsoft.com/favicon.ico)
     por icones locais ou Lucide icons:
     ```python
     rx.icon("chrome", size=18)  # ou um SVG local
     ```
   - Adicione `href="#"` nos `rx.link` que usam apenas `on_click` sem href
   - Remova imports nao usados

3. Em labbridge/states/help_state.py:
   - Corrija `send_contact` que mostra sucesso mesmo quando email falha:
     ```python
     if not result.get("success"):
         self.contact_error = "Nao foi possivel enviar a mensagem. Tente novamente."
         self.contact_success = False
         return
     ```
   - Atualize `whatsapp_number` de "5511999999999" para o numero real
     (ou remova o botao de WhatsApp se nao houver numero real)

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 4.5 - Fix notification_bell e insight_chat

```
1. Em labbridge/components/notification_bell.py:
   - Substitua todas as cores Radix `rx.color("gray", 10)` etc. pelos tokens
     do design system: `Color.TEXT_PRIMARY`, `Color.TEXT_MUTED`, `Color.SURFACE`, etc.
   - Adicione click-outside dismiss: use `rx.popover` ao inves de posicionamento
     absoluto manual, OU adicione um overlay transparente que fecha o dropdown

2. Em labbridge/pages/insight_chat.py:
   - Substitua as alturas fixas (`height="500px"`, `height="620px"`) por
     alturas responsivas: `height="calc(100vh - 200px)"` ou `min_height="400px"`, `max_height="80vh"`
   - Substitua cores hardcoded `"rgba(76, 175, 80, 0.1)"` por tokens do design system
   - Adicione um empty state quando nao ha mensagens:
     ```python
     rx.cond(
         State.messages.length() == 0,
         rx.center(
             rx.vstack(
                 rx.icon("message-circle", size=48, color=Color.TEXT_MUTED),
                 rx.text("Faca uma pergunta sobre seus dados", color=Color.TEXT_MUTED),
                 align="center",
             ),
             height="100%",
         ),
         # ... chat messages ...
     )
     ```

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

---

## FASE 5 - REFATORACAO E DRY

### Prompt 5.1 - Extrair funcoes de normalizacao duplicadas

```
Crie um modulo compartilhado para funcoes duplicadas em 4+ arquivos:

1. Crie o arquivo labbridge/utils/normalize.py com as funcoes canonicas:
   ```python
   """Funcoes de normalizacao compartilhadas - fonte unica de verdade."""
   import re
   import unicodedata
   from decimal import Decimal, InvalidOperation

   def normalize_patient_name(name: str) -> str:
       """Normaliza nome de paciente para comparacao."""
       if not name:
           return ""
       name = unicodedata.normalize("NFKD", name)
       name = name.encode("ascii", "ignore").decode("ascii")
       name = name.upper().strip()
       name = re.sub(r"\s+", " ", name)
       return name

   def normalize_exam_name(name: str) -> str:
       """Normaliza nome de exame para comparacao."""
       if not name:
           return ""
       name = unicodedata.normalize("NFKD", name)
       name = name.encode("ascii", "ignore").decode("ascii")
       name = name.upper().strip()
       name = re.sub(r"\s+", " ", name)
       name = re.sub(r"[^\w\s]", "", name)
       return name

   def safe_decimal(value, default=Decimal("0")) -> Decimal:
       """Converte valor para Decimal de forma segura."""
       if value is None:
           return default
       try:
           if isinstance(value, str):
               value = value.replace(".", "").replace(",", ".")
               value = re.sub(r"[^\d.\-]", "", value)
           return Decimal(str(value))
       except (InvalidOperation, ValueError):
           return default

   def format_currency_br(value) -> str:
       """Formata valor como moeda brasileira."""
       try:
           v = float(value) if not isinstance(value, float) else value
           formatted = f"{v:,.2f}"
           formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
           return f"R$ {formatted}"
       except (ValueError, TypeError):
           return "R$ 0,00"
   ```

2. Atualize labbridge/utils/__init__.py para exportar essas funcoes

3. Em CADA arquivo que tem copias locais dessas funcoes, substitua por imports:
   - labbridge/utils/comparison.py
   - labbridge/utils/ai_analysis.py
   - labbridge/utils/analysis_module.py
   - labbridge/utils/pdf_processor.py

   Em cada um, remova a definicao local e adicione:
   ```python
   from .normalize import normalize_patient_name, normalize_exam_name, safe_decimal, format_currency_br
   ```

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 5.2 - Resolver conflito de nomes generate_analysis_pdf

```
Ha duas funcoes chamadas `generate_analysis_pdf` com assinaturas diferentes:
- labbridge/utils/analysis_pdf_report.py
- labbridge/utils/pdf_report.py

1. Leia ambos os arquivos e determine qual e o mais completo/atualizado.
2. Renomeie o de pdf_report.py para `generate_simple_pdf_report()`.
3. Atualize todos os imports no projeto que referenciam a funcao renomeada.
4. Adicione um comentario no topo de cada arquivo explicando quando usar qual:
   - analysis_pdf_report.py: relatorio completo com todas as secoes
   - pdf_report.py: relatorio simplificado/resumido

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 5.3 - Fix config.py e rbac_middleware

```
1. Em labbridge/config.py:
   - Descomente e implemente a funcao `validate()`:
   ```python
   @classmethod
   def validate(cls):
       missing = []
       if not cls.SUPABASE_URL:
           missing.append("SUPABASE_URL")
       if not cls.SUPABASE_KEY:
           missing.append("SUPABASE_KEY")
       if missing:
           import logging
           logging.getLogger(__name__).warning(
               f"Variaveis de ambiente faltando: {', '.join(missing)}. "
               "Algumas funcionalidades podem nao funcionar."
           )
   ```
   - Remova `AUTH_EMAIL` e `AUTH_PASSWORD` como atributos de classe.
     Se necessarios para dev, leia-os apenas dentro de auth_service.py
     com os.environ.get() diretamente.

2. Em labbridge/middleware/rbac_middleware.py:
   - Mude o default para rotas desconhecidas de `True` para `False`:
     ```python
     # Rotas desconhecidas sao bloqueadas por padrao
     return False
     ```
   - Adicione um comentario de TODO para integrar com o Reflex routing:
     ```python
     # TODO: Integrar com app.middleware ou usar como decorator nos event handlers
     ```
   - Substitua os `print()` por logging adequado

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

### Prompt 5.4 - Fix team_state await pattern e integration_state

```
1. Em labbridge/states/team_state.py:
   - Em `save_member_edit`, `toggle_member_status`, e `remove_member`:
     Substitua `await self.load_team_members()` por:
     ```python
     # load_team_members e async generator (usa yield), nao pode usar await
     async for _ in self.load_team_members():
         yield
     ```
   - Em `get_role_display()`: adicione os roles faltantes:
     ```python
     role_map = {
         "owner": "Proprietario",
         "admin_global": "Admin Global",
         "admin_lab": "Admin Lab",
         "admin": "Administrador",
         "analyst": "Analista",
         "member": "Membro",
         "viewer": "Visualizador",
     }
     ```

2. Em labbridge/states/integration_state.py:
   - Corrija `format_last_sync` que retorna None quando deveria retornar str:
     ```python
     def format_last_sync(self, dt_str: str) -> str:
         if not dt_str:
             return "Nunca sincronizado"
         # ... logica existente ...
         return "Data invalida"  # ao inves de return None
     ```

3. Em labbridge/states/notification_state.py:
   - Em todos os metodos estaticos (notify_analysis_complete, etc.),
     adicione `tenant_id` como parametro obrigatorio e passe-o para
     `create_notification`:
     ```python
     @staticmethod
     async def notify_analysis_complete(tenant_id: str, analysis_name: str):
         await NotificationState.create_notification(
             tenant_id=tenant_id,
             title="Analise Concluida",
             ...
         )
     ```

Base path: c:\Users\otavi\Desktop\New_LabBridge\New LabBridge\labbridge\labbridge\
```

---

## SCRIPT DE VERIFICACAO POS-CORRECOES

### Prompt FINAL - Validacao completa

```
Execute uma verificacao completa do projeto apos todas as correcoes:

1. Busque por restos de problemas conhecidos:
   - `grep -r 'tenant_id.*=.*"local"'` em todos os .py (deve retornar 0 resultados)
   - `grep -r 'tenant_id.*=.*"default"'` (deve retornar 0)
   - `grep -rn 'f".*{State\.' labbridge/pages/` (f-strings com State vars - deve retornar 0)
   - `grep -rn 'lambda.*:.*State\.' labbridge/pages/` dentro de foreach (deve retornar 0)
   - `grep -rn '\.get(' labbridge/pages/` onde o argumento vem de rx.foreach (deve retornar 0)

2. Verifique imports:
   - Execute `python -c "from labbridge.states import *"` para verificar se todos
     os states importam sem erro
   - Execute `python -c "from labbridge.components import *"` idem
   - Execute `python -c "from labbridge.services import *"` idem (pode falhar por
     deps externas, mas nao deve falhar por imports quebrados)

3. Verifique se nao ha arquivos orfaos:
   - Liste todos os .py em components/ e verifique que cada um e importado em algum lugar
   - Liste todos os .py em states/ e verifique que cada um esta em __init__.py

4. Execute o Reflex para verificar se compila:
   ```
   cd labbridge
   reflex init  # se necessario
   reflex run
   ```
   Verifique se nao ha erros no console.

5. Relate quaisquer issues residuais encontrados.
```

---

## RESUMO DO PLANO

| Fase | Prompts | Foco | Dependencias |
|------|---------|------|-------------|
| **F0** | 0.1 - 0.4 | Crashes (4 bugs) | Nenhuma - executar primeiro |
| **F1** | 1.1 - 1.5 | Seguranca (8 vulns) | Apos F0 |
| **F2** | 2.1 - 2.6 | Bugs funcionais (10) | Apos F1 (1.2 e 1.4 especificamente) |
| **F3** | 3.1 - 3.5 | Dead code + mock data | Paralelo com F2 |
| **F4** | 4.1 - 4.5 | UI/UX (12 fixes) | Apos F2 |
| **F5** | 5.1 - 5.4 | Refatoracao DRY | Apos F3 e F4 |
| **FINAL** | 1 prompt | Validacao | Apos tudo |

**Total: 28 prompts + 1 validacao = 29 acoes**

### Ordem de execucao recomendada:

```
F0.1 -> F0.2 -> F0.3 -> F0.4 (sequencial, rapido)
  |
  v
F1.1 + F1.2 + F1.3 (paralelo)
  |
  v
F1.4 + F1.5 (paralelo)
  |
  v
F2.1 + F2.2 + F2.3 (paralelo)
  |
  v
F2.4 + F2.5 (paralelo, depende de F1.2 para tenant isolation)
  |
  v
F2.6 (depende de F2.5 para dashboard_state removido)
  |
F3.1 + F3.2 + F3.3 (paralelo, pode comecar junto com F2)
  |
  v
F3.4 + F3.5 (paralelo)
  |
  v
F4.1 + F4.2 + F4.3 (paralelo)
  |
  v
F4.4 + F4.5 (paralelo)
  |
  v
F5.1 -> F5.2 -> F5.3 -> F5.4 (sequencial)
  |
  v
FINAL (validacao)
```
