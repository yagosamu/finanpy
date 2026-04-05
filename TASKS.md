## Lista de Tarefas

### [X] Sprint 0: Setup e Configuração (1 semana)

#### Tarefa 0.1: Configuração Inicial do Projeto
- [X] **0.1.1** - Criar ambiente virtual Python
  - Instalar Python 3.11+
  - Criar venv: `python -m venv venv`
  - Ativar ambiente virtual
  - Documentar comandos no README

- [X] **0.1.2** - Instalar Django e dependências
  - Instalar Django 5.0+: `pip install django`
  - Instalar Pillow (se necessário para imagens)
  - Gerar requirements.txt: `pip freeze > requirements.txt`

- [X] **0.1.3** - Criar projeto Django
  - Executar: `django-admin startproject core .`
  - Verificar estrutura criada
  - Testar servidor: `python manage.py runserver`

- [X] **0.1.4** - Configurar settings.py
  - Criar arquivo .env na raiz do projeto
  - Mover SECRET_KEY para arquivo .env
  - Configurar DEBUG através de variável de ambiente
  - Configurar ALLOWED_HOSTS
  - Configurar LANGUAGE_CODE = 'pt-br'
  - Configurar TIME_ZONE = 'America/Sao_Paulo'
  - Configurar STATIC_URL e STATIC_ROOT
  - Configurar MEDIA_URL e MEDIA_ROOT
  - Configurar USE_I18N = True
  - Configurar USE_TZ = True
  - Adicionar configurações de segurança básicas

#### Tarefa 0.2: Criação das Apps Django
- [X] **0.2.1** - Criar app users
- [X] **0.2.2** - Criar app profiles
- [X] **0.2.3** - Criar app accounts
- [X] **0.2.4** - Criar app categories
- [X] **0.2.5** - Criar app transactions

#### Tarefa 0.3: Configuração do TailwindCSS
- [X] **0.3.1** - Instalar Node.js e npm
- [X] **0.3.2** - Configurar TailwindCSS via CDN (temporário)
- [X] **0.3.3** - Configurar TailwindCSS local

#### Tarefa 0.4: Estrutura de Templates Base
- [X] **0.4.1** - Criar diretório de templates
- [X] **0.4.2** - Criar template base.html
- [X] **0.4.3** - Criar template base_dashboard.html

#### Tarefa 0.5: Configuração de Arquivos Estáticos
- [X] **0.5.1** - Criar estrutura de pastas static
- [X] **0.5.2** - Configurar collectstatic
- [X] **0.5.3** - Criar arquivo CSS customizado

#### Tarefa 0.6: Configuração do Git
- [X] **0.6.1** - Inicializar repositório Git
- [X] **0.6.2** - Configurar .gitignore
- [X] **0.6.3** - Primeiro commit

---

### [X] Sprint 1: Autenticação e Sistema de Usuários (1 semana)

#### Tarefa 1.1: Model de Usuário Customizado
- [X] **1.1.1** - Criar CustomUser model (email-based)
- [X] **1.1.2** - Criar CustomUserManager
- [X] **1.1.3** - Configurar AUTH_USER_MODEL
- [X] **1.1.4** - Criar e aplicar migrations

#### Tarefa 1.2: Model de Profile
- [X] **1.2.1** - Criar Profile model (1:1 com User)
- [X] **1.2.2** - Criar signal para criar Profile automaticamente
- [X] **1.2.3** - Registrar Profile no admin
- [X] **1.2.4** - Criar e aplicar migrations

#### Tarefa 1.3: Views de Autenticação
- [X] **1.3.1** - Criar SignUpView
- [X] **1.3.2** - Criar LoginView customizada
- [X] **1.3.3** - Criar LogoutView com redirecionamento para landing page
- [X] **1.3.4** - Corrigir logout para encerrar sessão e permitir novo login

#### Tarefa 1.4: Forms de Autenticação
- [X] **1.4.1** - Criar SignUpForm
- [X] **1.4.2** - Criar CustomAuthenticationForm
- [X] **1.4.3** - Criar ProfileForm

#### Tarefa 1.5: Templates de Autenticação
- [X] **1.5.1** - Criar template signup.html
- [X] **1.5.2** - Criar template login.html
- [X] **1.5.3** - Criar template profile.html
- [X] **1.5.4** - Criar template profile_edit.html

#### Tarefa 1.6: URLs de Autenticação
- [X] **1.6.1** - Configurar users/urls.py
- [X] **1.6.2** - Configurar profiles/urls.py
- [X] **1.6.3** - Incluir URLs no core/urls.py

---

### [X] Sprint 2: Site Público e Landing Page (1 semana)

#### Tarefa 2.1: Estrutura da Landing Page
- [X] **2.1.1** - Criar view para landing page
- [X] **2.1.2** - Criar template home.html
- [X] **2.1.3** - Implementar navegação responsiva

#### Tarefa 2.2: Seções da Landing Page
- [X] **2.2.1** - Hero Section com CTAs
- [X] **2.2.2** - Features Section
- [X] **2.2.3** - Benefits Section
- [X] **2.2.4** - CTA Section

#### Tarefa 2.3: Estilização e Responsividade
- [X] **2.3.1** - Implementar gradientes e efeitos visuais
- [X] **2.3.2** - Adicionar animações CSS
- [X] **2.3.3** - Otimizar responsividade

---

### [X] Sprint 3: Models e Admin de Contas e Categorias (1 semana)

- [X] **3.x** - Model Account com choices (checking, savings, wallet, investment)
- [X] **3.x** - Model Category com choices (income, expense) e categorias padrão
- [X] **3.x** - Admin configurado para ambos os models
- [X] **3.x** - Management command create_default_categories

---

### [X] Sprint 4: Views e Templates de Contas (1 semana)

- [X] **4.x** - CRUD completo de contas (List, Create, Update, Delete, Detail)
- [X] **4.x** - AccountForm com validações
- [X] **4.x** - Templates estilizados com tema escuro
- [X] **4.x** - URLs configuradas com namespace 'accounts'

---

### [X] Sprint 5: Views e Templates de Categorias (1 semana)

- [X] **5.x** - CRUD completo de categorias
- [X] **5.x** - CategoryForm com color picker
- [X] **5.x** - Templates com separação receita/despesa
- [X] **5.x** - URLs configuradas com namespace 'categories'

---

### [X] Sprint 6: Model e Views de Transações (2 semanas)

- [X] **6.x** - Transaction model com FKs para Account e Category
- [X] **6.x** - Signals para atualizar saldo automaticamente (post_save, pre_delete)
- [X] **6.x** - CRUD completo com filtros (data, categoria, tipo, conta)
- [X] **6.x** - Paginação e formatação brasileira

---

### [X] Sprint 7: Dashboard e Visualizações (2 semanas)

- [X] **7.x** - DashboardView com cálculos mensais (receitas, despesas, saldo)
- [X] **7.x** - Gráfico de pizza por categoria (Chart.js)
- [X] **7.x** - Gráfico de evolução mensal — últimos 6 meses (Chart.js, 3 séries)
- [X] **7.x** - MonthlyEvolutionView com endpoint JSON /dashboard/evolucao-mensal/
- [X] **7.x** - static/js/dashboard.js com fetch e renderização de gráfico de linhas
- [X] **7.x** - Cards de resumo financeiro e atalhos rápidos

---

### [X] Sprint 8: Agente de IA Financeiro (2 semanas)

- [X] **8.x** - App `ai` com model AIAnalysis
- [X] **8.x** - Agente LangChain com 4 tools (transações, categorias, contas, comparação)
- [X] **8.x** - analysis_service.py com analyze_user() e analyze_all_active_users()
- [X] **8.x** - Management command run_finance_analysis
- [X] **8.x** - RunAnalysisView (POST, login_required) com tratamento de erro amigável
- [X] **8.x** - ai/urls.py e registro em core/urls.py
- [X] **8.x** - Dashboard integrado: botão "Gerar análise" e exibição de summary + modal

---

### [X] Sprint 9: Refinamentos e MVP (1 semana)

- [X] **9.x** - Toast notifications e mensagens de feedback
- [X] **9.x** - Validações frontend e backend robustas
- [X] **9.x** - Formatação de moeda (R$ 1.234,56) e datas (DD/MM/YYYY) padronizadas
- [X] **9.x** - Páginas de erro customizadas (404, 500, 403)
- [X] **9.x** - Logging configurado
- [X] **9.x** - Proteção de rotas e verificação de ownership
- [X] **9.x** - Otimização de queries (select_related, prefetch_related)
- [X] **9.x** - README.md completo
- [X] **9.x** - Seed de dados (management command seed_data com 2 usuários e ~40 transações)

---

### [X] Sprint 10: Redesign Visual Completo — Finova (1 semana)

> Rebranding de Finanpy para **Finova**. Redesign completo com nova identidade visual.

#### Tarefa 10.1: Nova Paleta e Design System
- [X] **10.1.1** - Definir paleta oficial
  - Fundo principal: #0a0a0a
  - Cards/surfaces: #111111
  - Elementos elevados: #1a1a1a
  - Bordas: #262626
  - Primária/destaque: #22c55e (verde)
  - Verde hover: #16a34a
  - Verde sutil: rgba(34,197,94,0.08)
  - Texto principal: #f5f5f5
  - Texto secundário: #a3a3a3
  - Texto terciário: #525252

- [X] **10.1.2** - Adicionar tokens de cor no Tailwind config
  - Cores nomeadas: bg-card, bg-elevated, border-subtle, accent, text-secondary, etc.

- [X] **10.1.3** - Criar preview estático aprovado (preview_redesign.html)
  - Landing page, dashboard, componentes isolados
  - Aprovado antes de aplicar nos templates reais

#### Tarefa 10.2: Aplicar Redesign nos Templates
- [X] **10.2.1** - base.html e base_dashboard.html (sidebar, navbar, estrutura)
- [X] **10.2.2** - Landing page (hero, features, footer)
- [X] **10.2.3** - dashboard.html (cards, gráficos, transações recentes, análise IA)
- [X] **10.2.4** - accounts/ templates
- [X] **10.2.5** - categories/ templates
- [X] **10.2.6** - transactions/ templates
- [X] **10.2.7** - profiles/ templates
- [X] **10.2.8** - Componentes globais (botões, inputs, badges, mensagens Django)

#### Tarefa 10.3: Rebranding para Finova
- [X] **10.3.1** - Substituir todas as ocorrências de "Finanpy" por "Finova"
  - Templates, <title>, rodapés, sidebar, README.md, settings.py

#### Tarefa 10.4: Ajustes de Tipografia e UX
- [X] **10.4.1** - Inter via Google Fonts (300 para corpo, 600 para títulos)
- [X] **10.4.2** - Números financeiros em font-mono
- [X] **10.4.3** - Hover states com transição 150ms
- [X] **10.4.4** - Compilar Tailwind: `npm run build:css`

---

### [X] Sprint 11: App de Metas (Goals) (1 semana)

#### Tarefa 11.1: Backend
- [X] **11.1.1** - Criar app `goals` e registrar em INSTALLED_APPS
- [X] **11.1.2** - Model Goal
  - Campos: user (FK), name, description, target_amount, current_amount, deadline, category (FK opcional), color, icon, is_completed, created_at, updated_at
  - Property `progress_percentage`: (current_amount / target_amount) * 100, máx 100
  - Property `remaining_amount`: target_amount - current_amount
  - is_completed atualizado automaticamente no save()
- [X] **11.1.3** - GoalForm (CRUD) e GoalDepositForm com validações
- [X] **11.1.4** - Views: GoalListView, GoalCreateView, GoalUpdateView, GoalDeleteView (UserPassesTestMixin), GoalDepositView (POST-only)
- [X] **11.1.5** - goals/urls.py com 5 rotas (namespace 'goals')
- [X] **11.1.6** - Registrar em core/urls.py: path('metas/', ...)
- [X] **11.1.7** - Migration criada e aplicada

#### Tarefa 11.2: Templates
- [X] **11.2.1** - goals/goal_list.html — cards com barra de progresso colorida, badge de status, modal de depósito inline
- [X] **11.2.2** - goals/goal_form.html — formulário com breadcrumb
- [X] **11.2.3** - goals/goal_confirm_delete.html — confirmação com detalhes da meta

#### Tarefa 11.3: Integração com Dashboard e Sidebar
- [X] **11.3.1** - Sidebar: `<span>` desabilitado → `<a href="{% url 'goals:list' %}">` com highlight ativo
- [X] **11.3.2** - DashboardView: passa upcoming_goals, goals_active_count, goals_total_count
- [X] **11.3.3** - dashboard.html: card de resumo com mini progress bars das 3 próximas metas

---

### [ ] Sprint 12: App de Relatórios (Reports) (1 semana)

#### Tarefa 12.1: Backend
- [ ] **12.1.1** - Criar app `reports` e registrar em INSTALLED_APPS
  - Sem models novos — apenas views de leitura que agregam dados existentes

- [ ] **12.1.2** - Criar ReportView (GET, LoginRequiredMixin) em reports/views.py
  - Parâmetros de filtro via query string: ?period=this_month|last_month|last_3_months|last_6_months|this_year
  - Parâmetro opcional: ?account=<id>
  - Calcular e passar ao template:
    - Resumo geral: total_income, total_expense, net_balance, avg_daily_expense, biggest_expense, biggest_income
    - Por categoria (despesas): nome, cor, total, %, quantidade de transações — ordenado por total
    - Por categoria (receitas): mesma estrutura
    - Evolução diária: lista de dias com income e expense por dia (para gráfico de barras)
    - Por conta: nome, tipo, saldo atual, total recebido e total gasto no período
    - Top 5 despesas e top 5 receitas do período
  - Usar Django ORM aggregates (Sum, Count, Avg) — não calcular em Python
  - Empty states elegantes quando não há dados

- [ ] **12.1.3** - Criar reports/urls.py
  - /relatorios/ → ReportView (name: reports:index)

- [ ] **12.1.4** - Registrar em core/urls.py
  - path('relatorios/', include('reports.urls', namespace='reports'))

#### Tarefa 12.2: Template
- [ ] **12.2.1** - Criar reports/report.html
  - Filtros no topo: seletor de período + seletor de conta + botão aplicar (GET)
  - Cards de resumo: Total Receitas (verde), Total Despesas (vermelho), Saldo Líquido, Média diária
  - Maior receita e maior despesa do período (nome + valor)
  - Gráfico de barras Chart.js (evolução diária — receitas verde / despesas vermelho)
    - Dados via json_script tag do Django (evitar XSS)
    - Estilo visual idêntico ao dashboard.js
  - Distribuição por categoria (duas colunas): barras de progresso proporcionais + valor + %
  - Por conta: tabela com conta, tipo, saldo atual, entradas e saídas no período
  - Maiores transações: duas listas lado a lado (top 5 despesas | top 5 receitas)
    - Cada item: data, descrição, categoria, conta, valor

#### Tarefa 12.3: Sidebar
- [ ] **12.3.1** - Substituir `<span>` desabilitado de "Relatórios" por `<a href="{% url 'reports:index' %}">`
- [ ] **12.3.2** - Remover badge "Em breve" do item na sidebar

---

### [ ] Sprint 13: Vínculo Bancário e Transferências entre Contas (2 semanas)

> Objetivo: tornar o controle de contas mais real — cada conta corrente vinculada a um banco real com ícone,
> débito automático ao registrar despesas e transferências entre contas do mesmo usuário.

#### Tarefa 13.1: Vínculo com Banco no Model Account
- [ ] **13.1.1** - Adicionar campo `bank_code` ao model Account
  - CharField com choices dos 8 maiores bancos do Brasil:
    - NUBANK = 'nubank' — Nubank
    - ITAU = 'itau' — Itaú
    - BRADESCO = 'bradesco' — Bradesco
    - SANTANDER = 'santander' — Santander
    - BANCO_DO_BRASIL = 'bb' — Banco do Brasil
    - CAIXA = 'caixa' — Caixa Econômica Federal
    - INTER = 'inter' — Banco Inter
    - C6 = 'c6' — C6 Bank
    - OTHER = 'other' — Outro
  - Campo opcional (null=True, blank=True) — contas do tipo wallet/investment podem não ter banco
  - Inspecione accounts/models.py antes de alterar

- [ ] **13.1.2** - Adicionar campo `is_default` ao model Account
  - BooleanField default=False
  - Apenas uma conta por usuário pode ser is_default=True
  - Implementar lógica no save() para garantir unicidade: ao setar is_default=True, desmarcar as demais contas do usuário

- [ ] **13.1.3** - Criar migration e aplicar
  - `python manage.py makemigrations accounts`
  - `python manage.py migrate`

- [ ] **13.1.4** - Adicionar ícones dos bancos em static/images/banks/
  - SVG ou PNG para cada banco: nubank.svg, itau.svg, bradesco.svg, santander.svg, bb.svg, caixa.svg, inter.svg, c6.svg
  - Usar logos oficiais em versão monocromática ou colorida (verificar licença)
  - Criar template tag ou helper para retornar o caminho do ícone dado o bank_code

- [ ] **13.1.5** - Atualizar AccountForm
  - Adicionar campo bank_code (select com os 8 bancos + ícone preview via JavaScript)
  - Adicionar campo is_default (checkbox "Usar como conta padrão")
  - bank_code obrigatório apenas para account_type = 'checking'

- [ ] **13.1.6** - Atualizar templates de accounts
  - account_list.html: exibir ícone do banco ao lado do nome da conta
  - Destacar visualmente a conta marcada como padrão (badge "Padrão")
  - account_form.html: mostrar preview do ícone do banco ao selecionar

#### Tarefa 13.2: Conta Padrão e Débito Automático
- [ ] **13.2.1** - Atualizar TransactionForm
  - O campo `account` deve pré-selecionar a conta padrão do usuário (is_default=True)
  - Manter possibilidade de selecionar outra conta manualmente

- [ ] **13.2.2** - Atualizar GoalDepositForm
  - Adicionar campo `source_account` — conta de onde o valor será debitado
  - Pré-selecionar a conta padrão do usuário
  - Ao confirmar depósito: incrementa current_amount na meta E debita o valor da source_account via signal ou service

- [ ] **13.2.3** - Criar service accounts/services.py
  - Função `debit_account(account, amount, description)` — debita valor de uma conta e registra a operação
  - Função `get_default_account(user)` — retorna a conta padrão do usuário (ou None se não houver)
  - Usada pelo GoalDepositView e futuramente pelo TransferView

- [ ] **13.2.4** - Atualizar GoalDepositView
  - Chamar `debit_account()` na conta selecionada ao confirmar depósito
  - Exibir aviso se saldo da conta for insuficiente (não bloquear, apenas alertar)
  - Registrar a movimentação como transação do tipo expense na conta debitada (categoria: "Meta" ou similar)

#### Tarefa 13.3: Transferências entre Contas
- [ ] **13.3.1** - Criar TransferView em accounts/views.py
  - View POST, LoginRequiredMixin
  - Campos: from_account, to_account, amount, description, date
  - Validações:
    - from_account != to_account
    - Ambas as contas pertencem ao usuário logado
    - amount > 0
    - Alerta (não bloqueio) se saldo insuficiente em from_account
  - Ao confirmar:
    - Debita `amount` de `from_account`
    - Credita `amount` em `to_account`
    - Cria 2 transações vinculadas (uma saída, uma entrada) com referência cruzada
    - Redireciona para lista de contas com mensagem de sucesso

- [ ] **13.3.2** - Criar TransferForm em accounts/forms.py
  - Campos: from_account (select filtrado pelo usuário), to_account (idem), amount, description, date
  - Validação: from_account != to_account

- [ ] **13.3.3** - Criar template accounts/transfer.html
  - Formulário de transferência com campos estilizados
  - Mostrar saldo atual de cada conta ao selecionar
  - Preview do saldo após a transferência (JavaScript)
  - Alerta visual se saldo insuficiente

- [ ] **13.3.4** - Adicionar URL de transferência
  - /contas/transferir/ → TransferView (name: accounts:transfer)
  - Adicionar botão "Transferir" na account_list.html e no dashboard (atalhos rápidos)

#### Tarefa 13.4: Extrato por Conta
- [ ] **13.4.1** - Atualizar AccountDetailView
  - Incluir transferências recebidas e enviadas no histórico da conta
  - Filtro por período no extrato
  - Mostrar saldo após cada movimentação (saldo corrente)

- [ ] **13.4.2** - Atualizar account_detail.html
  - Coluna "Tipo" para diferenciar transação normal, transferência enviada e transferência recebida
  - Ícone ou badge visual por tipo de movimentação

#### Tarefa 13.5: Alerta de Saldo Insuficiente
- [ ] **13.5.1** - Implementar verificação de saldo no TransactionCreateView
  - Se despesa > saldo atual da conta selecionada: exibir mensagem de aviso (não bloquear)
  - Mensagem: "Atenção: esta despesa deixará sua conta com saldo negativo."

- [ ] **13.5.2** - Implementar alerta visual no frontend (JavaScript)
  - Ao selecionar conta + preencher valor: calcular e exibir saldo resultante em tempo real
  - Cor vermelha se saldo ficar negativo

---

### [ ] Sprint 14: Orçamentos por Categoria (1 semana)

> Permite ao usuário definir um teto de gasto mensal por categoria e acompanhar em tempo real
> quanto já gastou e quanto ainda pode gastar. Diferente de metas (reserva de dinheiro),
> orçamento é um limite de gasto.

#### Tarefa 14.1: Backend

- [ ] **14.1.1** - Criar app `budgets` e registrar em INSTALLED_APPS
  - `python manage.py startapp budgets`
  - Criar estrutura padrão: models, views, forms, urls, admin

- [ ] **14.1.2** - Criar model `Budget` em budgets/models.py
  - Campos:
    - `user` — FK para settings.AUTH_USER_MODEL (on_delete=CASCADE)
    - `category` — FK para Category (on_delete=CASCADE)
    - `amount` — DecimalField — limite mensal de gasto
    - `month` — DateField — primeiro dia do mês de referência (ex: 2026-04-01)
    - `created_at`, `updated_at` — auto
  - Meta: `unique_together = ['user', 'category', 'month']` — um orçamento por categoria por mês
  - Property `spent_amount`: soma das transações do tipo expense nessa categoria no mês
  - Property `remaining_amount`: amount - spent_amount (pode ser negativo se estourou)
  - Property `usage_percentage`: (spent_amount / amount) * 100, máximo 100
  - Property `is_exceeded`: True se spent_amount > amount

- [ ] **14.1.3** - Criar budgets/forms.py
  - `BudgetForm` — campos: category (filtrada por tipo expense do usuário), amount, month
  - Validação: category deve ser do tipo expense
  - Validação: amount > 0
  - Widget de month: input type="month" (YYYY-MM)

- [ ] **14.1.4** - Criar budgets/views.py — CRUD completo
  - `BudgetListView` — lista orçamentos do mês atual por padrão, com filtro de mês
    - Anotação via ORM: gasto real de cada categoria no mês
    - Ordenar por usage_percentage decrescente (os mais estourados primeiro)
  - `BudgetCreateView` — cria orçamento, associa ao usuário logado
  - `BudgetUpdateView` — edita orçamento (UserPassesTestMixin)
  - `BudgetDeleteView` — exclui orçamento (UserPassesTestMixin)
  - `BudgetAPIView` — endpoint JSON GET /orcamentos/api/?month=YYYY-MM
    - Retorna lista de orçamentos com spent, remaining, percentage para uso no dashboard
  - Todas com LoginRequiredMixin

- [ ] **14.1.5** - Criar budgets/urls.py
  - /orcamentos/ → BudgetListView (name: budgets:list)
  - /orcamentos/novo/ → BudgetCreateView (name: budgets:create)
  - /orcamentos/<pk>/editar/ → BudgetUpdateView (name: budgets:update)
  - /orcamentos/<pk>/excluir/ → BudgetDeleteView (name: budgets:delete)
  - /orcamentos/api/ → BudgetAPIView (name: budgets:api)

- [ ] **14.1.6** - Registrar em core/urls.py
  - `path('orcamentos/', include('budgets.urls', namespace='budgets'))`

- [ ] **14.1.7** - Criar migration e aplicar

#### Tarefa 14.2: Templates

- [ ] **14.2.1** - Criar budgets/budget_list.html
  - Header com seletor de mês (navegar entre meses)
  - Card de resumo no topo: total orçado vs total gasto no mês + % geral
  - Lista de orçamentos como cards ou linhas:
    - Ícone e cor da categoria
    - Nome da categoria
    - Barra de progresso colorida: verde < 70%, amarelo 70–99%, vermelho ≥ 100%
    - Valores: "R$ X,XX gastados de R$ Y,YY" + "Resta R$ Z,ZZ" ou "Estourado em R$ Z,ZZ"
    - Percentual de uso
    - Botões editar / excluir
  - Botão "Novo Orçamento" no topo
  - Empty state elegante se não houver orçamentos no mês

- [ ] **14.2.2** - Criar budgets/budget_form.html
  - Formulário com breadcrumb
  - Select de categoria com cor visual
  - Campo de valor com máscara monetária
  - Campo de mês com input type="month"

- [ ] **14.2.3** - Criar budgets/budget_confirm_delete.html
  - Confirmação com nome da categoria e valor do orçamento

#### Tarefa 14.3: Alertas de Orçamento

- [ ] **14.3.1** - Implementar alerta no TransactionCreateView
  - Ao criar despesa: verificar se a categoria tem orçamento no mês
  - Se o gasto ultrapassar o orçamento após a transação: exibir aviso via Django messages
  - Mensagem: "Atenção: você ultrapassou o orçamento de R$ X,XX para [categoria] este mês."

- [ ] **14.3.2** - Notificação visual no dashboard
  - Na DashboardView: buscar orçamentos do mês com usage_percentage >= 80%
  - Passar `budget_alerts` ao contexto
  - No dashboard.html: exibir card de alertas se houver orçamentos críticos

#### Tarefa 14.4: Integração com Dashboard e Sidebar

- [ ] **14.4.1** - Atualizar DashboardView (core/views.py)
  - Passar top 3 orçamentos mais críticos (maior uso %) ao contexto
  - Passar `budgets_count` e `budgets_exceeded_count`

- [ ] **14.4.2** - Atualizar dashboard.html
  - Adicionar card de "Orçamentos" com mini barras de progresso das categorias críticas
  - Link "Ver todos os orçamentos"

- [ ] **14.4.3** - Atualizar sidebar (base_dashboard.html)
  - Adicionar item "Orçamentos" com link para budgets:list
  - Badge numérico se houver orçamentos estourados (ex: badge vermelho "2")

---

### [ ] Sprint 15: Recorrências — Despesas e Receitas Fixas (1 semana)

> Permite registrar despesas e receitas que se repetem mensalmente (aluguel, salário, Netflix, academia)
> e lançá-las automaticamente no início de cada mês, sem intervenção manual.

#### Tarefa 15.1: Backend

- [ ] **15.1.1** - Criar app `recurrences` e registrar em INSTALLED_APPS
  - `python manage.py startapp recurrences`

- [ ] **15.1.2** - Criar model `Recurrence` em recurrences/models.py
  - Campos:
    - `user` — FK para settings.AUTH_USER_MODEL
    - `name` — CharField — descrição da recorrência (ex: "Netflix", "Aluguel")
    - `transaction_type` — CharField choices: INCOME / EXPENSE
    - `amount` — DecimalField
    - `category` — FK para Category
    - `account` — FK para Account — conta que será debitada/creditada
    - `day_of_month` — PositiveIntegerField (1–28) — dia do mês do lançamento
    - `start_date` — DateField — quando começa a recorrência
    - `end_date` — DateField, opcional — quando termina (null = sem fim)
    - `is_active` — BooleanField default=True
    - `last_generated_date` — DateField, null — último mês em que foi lançada
    - `created_at`, `updated_at` — auto
  - Property `is_due_this_month`: True se ainda não foi lançada no mês atual
  - Method `generate_transaction()`: cria uma Transaction com os dados da recorrência

- [ ] **15.1.3** - Criar recurrences/forms.py
  - `RecurrenceForm` — campos: name, transaction_type, amount, category, account, day_of_month, start_date, end_date
  - Validação: day_of_month entre 1 e 28 (evitar problemas com fevereiro)
  - Validação: end_date > start_date se informado

- [ ] **15.1.4** - Criar recurrences/views.py — CRUD completo
  - `RecurrenceListView` — lista recorrências ativas do usuário, separadas por tipo (receitas / despesas)
    - Mostrar próximo lançamento previsto (próximo day_of_month)
    - Indicar se já foi lançada no mês atual
  - `RecurrenceCreateView` — cria recorrência
  - `RecurrenceUpdateView` — edita recorrência (UserPassesTestMixin)
  - `RecurrenceDeleteView` — desativa recorrência (soft delete via is_active=False)
  - `RecurrenceGenerateView` — POST: lança manualmente todas as recorrências pendentes do mês atual
    - Chama `generate_transaction()` para cada recorrência devido no mês
    - Atualiza `last_generated_date`
    - Retorna resumo: quantas foram lançadas

- [ ] **15.1.5** - Criar management command `generate_recurrences`
  - recurrences/management/commands/generate_recurrences.py
  - Lógica: busca recorrências ativas cujo `day_of_month` <= hoje e `last_generated_date` != mês atual
  - Cria Transaction para cada uma e atualiza `last_generated_date`
  - Deve ser idempotente (pode rodar múltiplas vezes no mesmo dia sem duplicar)
  - Argumento opcional `--month YYYY-MM` para gerar para um mês específico
  - Preparado para futura execução via cron job ou Celery

- [ ] **15.1.6** - Criar recurrences/urls.py
  - /recorrencias/ → RecurrenceListView (name: recurrences:list)
  - /recorrencias/nova/ → RecurrenceCreateView (name: recurrences:create)
  - /recorrencias/<pk>/editar/ → RecurrenceUpdateView (name: recurrences:update)
  - /recorrencias/<pk>/excluir/ → RecurrenceDeleteView (name: recurrences:delete)
  - /recorrencias/gerar/ → RecurrenceGenerateView POST (name: recurrences:generate)

- [ ] **15.1.7** - Registrar em core/urls.py e criar migration

#### Tarefa 15.2: Templates

- [ ] **15.2.1** - Criar recurrences/recurrence_list.html
  - Duas seções: Receitas Fixas | Despesas Fixas
  - Card por recorrência: nome, categoria (com cor), conta, valor, dia do mês, próximo lançamento
  - Badge "Lançada este mês" (verde) ou "Pendente" (amarelo)
  - Botão "Lançar agora" → POST para recurrences:generate (lança todas pendentes)
  - Botões editar / desativar por item
  - Total mensal de receitas fixas vs despesas fixas no topo

- [ ] **15.2.2** - Criar recurrences/recurrence_form.html
  - Formulário completo com todos os campos
  - Select de categoria filtrado dinamicamente por transaction_type (via JS)
  - Preview: "Será lançado todo dia X, a partir de MM/YYYY"

- [ ] **15.2.3** - Criar recurrences/recurrence_confirm_delete.html

#### Tarefa 15.3: Integração com Dashboard

- [ ] **15.3.1** - Atualizar DashboardView
  - Buscar recorrências pendentes do mês atual (`is_due_this_month = True`)
  - Passar `pending_recurrences_count` ao contexto

- [ ] **15.3.2** - Atualizar dashboard.html
  - Se houver recorrências pendentes: exibir alerta/card "X lançamentos fixos pendentes este mês"
  - Link direto para recurrences:list

- [ ] **15.3.3** - Atualizar sidebar (base_dashboard.html)
  - Adicionar item "Recorrências" com link para recurrences:list

---

### [ ] Sprint 16: Parcelamentos (2 semanas)

> Controle de compras parceladas — acompanhar cada parcela, quantas restam,
> valor total da dívida e impacto no orçamento mensal.

#### Tarefa 16.1: Backend

- [ ] **16.1.1** - Criar app `installments` e registrar em INSTALLED_APPS
  - `python manage.py startapp installments`

- [ ] **16.1.2** - Criar model `InstallmentPlan` em installments/models.py
  - Representa a compra parcelada (o "contrato" do parcelamento)
  - Campos:
    - `user` — FK para settings.AUTH_USER_MODEL
    - `name` — CharField — descrição da compra (ex: "iPhone 15 Pro — Magazine Luiza")
    - `total_amount` — DecimalField — valor total da compra
    - `installment_count` — PositiveIntegerField — total de parcelas
    - `installment_amount` — DecimalField — valor de cada parcela (calculado ou manual)
    - `start_date` — DateField — data da primeira parcela
    - `category` — FK para Category
    - `account` — FK para Account — conta/cartão vinculado
    - `notes` — TextField opcional
    - `created_at`, `updated_at` — auto
  - Property `paid_installments`: quantidade de parcelas já pagas (Installment com status=paid)
  - Property `remaining_installments`: installment_count - paid_installments
  - Property `remaining_amount`: remaining_installments * installment_amount
  - Property `progress_percentage`: (paid_installments / installment_count) * 100
  - Property `is_completed`: True se remaining_installments == 0

- [ ] **16.1.3** - Criar model `Installment` em installments/models.py
  - Representa cada parcela individual
  - Campos:
    - `plan` — FK para InstallmentPlan (on_delete=CASCADE)
    - `number` — PositiveIntegerField — número da parcela (1, 2, 3...)
    - `due_date` — DateField — data de vencimento
    - `amount` — DecimalField — valor desta parcela
    - `status` — CharField choices: PENDING / PAID / OVERDUE
    - `paid_date` — DateField opcional — data em que foi paga
    - `transaction` — FK opcional para Transaction — transação gerada ao pagar
  - Property `is_overdue`: status == PENDING e due_date < hoje

- [ ] **16.1.4** - Signal post_save em InstallmentPlan
  - Ao criar um plano, gerar automaticamente todas as parcelas individuais (Installment)
  - Cada parcela com due_date = start_date + (number - 1) meses
  - Status inicial: PENDING

- [ ] **16.1.5** - Criar installments/forms.py
  - `InstallmentPlanForm` — campos: name, total_amount, installment_count, start_date, category, account, notes
  - `installment_amount` calculado automaticamente: total_amount / installment_count
  - Validação: installment_count entre 2 e 120
  - Validação: total_amount > 0

- [ ] **16.1.6** - Criar installments/views.py
  - `InstallmentPlanListView` — lista todos os planos do usuário
    - Separar: em andamento vs concluídos
    - Ordenar por próxima parcela a vencer
    - Mostrar total de dívida restante consolidada
  - `InstallmentPlanCreateView` — cria plano e gera parcelas automaticamente via signal
  - `InstallmentPlanDetailView` — exibe todas as parcelas do plano com status
  - `InstallmentPlanDeleteView` — exclui plano e todas as parcelas (CASCADE)
  - `InstallmentPayView` — POST: marca uma parcela como paga
    - Atualiza status para PAID e paid_date para hoje
    - Cria Transaction vinculada na conta do plano
    - Atualiza saldo da conta via signal existente
    - Se for a última parcela: marca plan como completed

- [ ] **16.1.7** - Criar installments/urls.py
  - /parcelamentos/ → InstallmentPlanListView (name: installments:list)
  - /parcelamentos/novo/ → InstallmentPlanCreateView (name: installments:create)
  - /parcelamentos/<pk>/ → InstallmentPlanDetailView (name: installments:detail)
  - /parcelamentos/<pk>/excluir/ → InstallmentPlanDeleteView (name: installments:delete)
  - /parcelamentos/parcela/<pk>/pagar/ → InstallmentPayView POST (name: installments:pay)

- [ ] **16.1.8** - Registrar em core/urls.py e criar migrations

#### Tarefa 16.2: Templates

- [ ] **16.2.1** - Criar installments/plan_list.html
  - Card de resumo: total de dívida ativa, total de parcelas pendentes este mês
  - Seção "Em andamento": cards por plano com barra de progresso
    - Nome, categoria, conta vinculada
    - Progresso: "X de Y parcelas pagas"
    - Próxima parcela: data e valor
    - Valor total restante
    - Botão "Ver parcelas"
  - Seção "Concluídos" (colapsável)
  - Botão "Novo Parcelamento"

- [ ] **16.2.2** - Criar installments/plan_detail.html
  - Header com resumo do plano (nome, total, progresso)
  - Tabela de todas as parcelas:
    - Número, data de vencimento, valor, status (badge colorido), data de pagamento
    - Botão "Marcar como paga" para parcelas PENDING
    - Destaque visual para parcela vencida (OVERDUE)
    - Destaque para próxima parcela a vencer

- [ ] **16.2.3** - Criar installments/plan_form.html
  - Formulário com preview automático (JavaScript):
    - Ao digitar valor total + número de parcelas: calcular e exibir valor por parcela
    - Ao digitar data início: mostrar tabela de datas previstas de vencimento

- [ ] **16.2.4** - Criar installments/plan_confirm_delete.html

#### Tarefa 16.3: Integração com Dashboard

- [ ] **16.3.1** - Atualizar DashboardView
  - Buscar parcelas com due_date no mês atual e status PENDING
  - Passar `installments_due_this_month` (lista) e `installments_total_this_month` (soma) ao contexto

- [ ] **16.3.2** - Atualizar dashboard.html
  - Card "Parcelas do Mês": valor total de parcelas vencendo no mês atual
  - Lista das próximas 3 parcelas a vencer com nome do plano, data e valor

- [ ] **16.3.3** - Atualizar sidebar (base_dashboard.html)
  - Adicionar item "Parcelamentos" com link para installments:list

---

### [ ] Sprint 17: Cartões de Crédito (2 semanas)

> Controle dedicado para cartões de crédito: fatura, limite, data de fechamento e vencimento.
> Separado de contas correntes pois tem lógica própria (fatura mensal, limite rotativo).

#### Tarefa 17.1: Backend

- [ ] **17.1.1** - Criar model `CreditCard` em accounts/models.py (ou novo app `cards`)
  - Decisão arquitetural: avaliar se cabe no app `accounts` ou merece app próprio `cards`
  - Inspecione accounts/models.py antes de decidir
  - Campos:
    - `user` — FK para settings.AUTH_USER_MODEL
    - `name` — CharField (ex: "Nubank Roxinho", "Itaú Personnalité")
    - `bank_code` — CharField choices (mesmos 8 bancos do Account)
    - `credit_limit` — DecimalField — limite total do cartão
    - `closing_day` — PositiveIntegerField (1–28) — dia de fechamento da fatura
    - `due_day` — PositiveIntegerField (1–28) — dia de vencimento da fatura
    - `is_active` — BooleanField default=True
    - `color` — CharField (cor para identificação visual)
    - `created_at`, `updated_at` — auto
  - Property `current_bill_amount`: soma das transações no cartão no período de fatura atual
  - Property `available_limit`: credit_limit - current_bill_amount
  - Property `current_billing_period`: tupla (data_inicio, data_fim) do período atual
  - Property `next_due_date`: próxima data de vencimento

- [ ] **17.1.2** - Criar model `CardTransaction` ou adaptar Transaction
  - Avaliar se Transaction existente pode ter FK opcional para CreditCard
  - Adicionar campo `credit_card` — FK opcional para CreditCard em Transaction
  - Se FK null: transação de conta corrente (comportamento atual)
  - Se FK preenchida: transação de cartão (não debita conta imediatamente)
  - Criar migration para adicionar o campo

- [ ] **17.1.3** - Criar model `CardBill` (Fatura)
  - Representa a fatura mensal de um cartão
  - Campos:
    - `credit_card` — FK para CreditCard
    - `reference_month` — DateField (primeiro dia do mês)
    - `closing_date` — DateField
    - `due_date` — DateField
    - `total_amount` — DecimalField (valor total da fatura)
    - `status` — CharField choices: OPEN / CLOSED / PAID
    - `payment_date` — DateField opcional
    - `payment_account` — FK opcional para Account (conta usada para pagar a fatura)
  - Method `pay_bill(account)`: cria transação de débito na conta e marca fatura como PAID

- [ ] **17.1.4** - Criar CRUD de CreditCard em accounts/views.py (ou cards/views.py)
  - CardListView, CardCreateView, CardUpdateView, CardDeleteView
  - CardDetailView — exibe fatura atual, histórico de transações e limite disponível
  - CardBillPayView — POST: paga a fatura da conta corrente selecionada

- [ ] **17.1.5** - Atualizar TransactionForm e TransactionCreateView
  - Adicionar campo opcional `credit_card` no formulário de transação
  - Se credit_card selecionado: não atualizar saldo de conta (será debitado ao pagar a fatura)
  - Se credit_card null: comportamento atual (debita/credita conta)

- [ ] **17.1.6** - Criar URLs de cartão e registrar em core/urls.py
  - /cartoes/ → CardListView
  - /cartoes/novo/ → CardCreateView
  - /cartoes/<pk>/ → CardDetailView
  - /cartoes/<pk>/editar/ → CardUpdateView
  - /cartoes/<pk>/excluir/ → CardDeleteView
  - /cartoes/<pk>/fatura/pagar/ → CardBillPayView POST

- [ ] **17.1.7** - Criar migrations e aplicar

#### Tarefa 17.2: Templates

- [ ] **17.2.1** - Criar cards/card_list.html (ou accounts/card_list.html)
  - Cards visuais por cartão com ícone do banco e cor personalizada
  - Exibir: limite total, limite disponível, valor da fatura atual, próximo vencimento
  - Barra de limite: verde se < 50%, amarelo 50–80%, vermelho > 80%
  - Botão "Ver fatura" e "Pagar fatura"

- [ ] **17.2.2** - Criar cards/card_detail.html
  - Header: nome do cartão, limite, fatura atual, datas de fechamento e vencimento
  - Transações do período atual agrupadas por categoria
  - Botão "Pagar fatura" com modal de seleção de conta
  - Histórico de faturas anteriores (status e valor)

- [ ] **17.2.3** - Criar cards/card_form.html
  - Formulário com seletor de banco (com ícone), cor do cartão, dias de fechamento e vencimento
  - Preview: "Sua próxima fatura fecha em X/MM e vence em Y/MM"

- [ ] **17.2.4** - Atualizar transaction_form.html
  - Adicionar toggle "Pagar com cartão de crédito"
  - Se ativo: mostrar select de cartões do usuário (ocultar campo conta)
  - Se inativo: comportamento atual com select de contas

#### Tarefa 17.3: Integração com Dashboard

- [ ] **17.3.1** - Atualizar DashboardView
  - Passar `cards_summary`: lista de cartões com fatura atual e próximo vencimento
  - Passar `total_card_debt`: soma de todas as faturas abertas

- [ ] **17.3.2** - Atualizar dashboard.html
  - Card "Cartões de Crédito": total de faturas abertas + próximo vencimento
  - Mini lista dos cartões com limite e fatura

- [ ] **17.3.3** - Atualizar sidebar (base_dashboard.html)
  - Adicionar item "Cartões" com link para cards:list

---

### [ ] Sprint 18: Integração com WhatsApp (3 semanas)

> Permite ao usuário registrar transações, consultar saldos e receber resumos
> diretamente pelo WhatsApp, usando IA para interpretar mensagens em linguagem natural.
> Stack: Twilio (webhook) + LangChain Agent (já existente no projeto) + Django.

#### Tarefa 18.1: Configuração da Infraestrutura

- [ ] **18.1.1** - Criar conta no Twilio e configurar WhatsApp Sandbox
  - Acessar console.twilio.com
  - Ativar o WhatsApp Sandbox (para desenvolvimento)
  - Obter Account SID e Auth Token
  - Configurar número de telefone de teste

- [ ] **18.1.2** - Instalar dependências
  - `pip install twilio`
  - Atualizar requirements.txt

- [ ] **18.1.3** - Configurar variáveis de ambiente
  - Adicionar ao .env:
    ```
    TWILIO_ACCOUNT_SID=AC...
    TWILIO_AUTH_TOKEN=...
    TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
    ```
  - Adicionar leitura em core/settings.py

- [ ] **18.1.4** - Criar app `whatsapp` e registrar em INSTALLED_APPS
  - `python manage.py startapp whatsapp`

- [ ] **18.1.5** - Configurar endpoint público para webhook
  - Em desenvolvimento: usar ngrok para expor localhost
  - Documentar: `ngrok http 8000` e configurar URL no Twilio console
  - Em produção: usar URL real do servidor

#### Tarefa 18.2: Model de Vínculo do WhatsApp

- [ ] **18.2.1** - Criar model `WhatsAppProfile` em whatsapp/models.py
  - Vincula número de WhatsApp ao usuário Finova
  - Campos:
    - `user` — OneToOneField para settings.AUTH_USER_MODEL
    - `phone_number` — CharField — número no formato whatsapp:+5511999999999
    - `is_verified` — BooleanField default=False
    - `verification_code` — CharField (6 dígitos, temporário)
    - `verified_at` — DateTimeField opcional
    - `created_at` — auto

- [ ] **18.2.2** - Criar migration e aplicar

- [ ] **18.2.3** - Criar fluxo de verificação do número
  - Usuário informa número de WhatsApp no perfil da plataforma
  - Sistema envia código de 6 dígitos via WhatsApp (usando Twilio)
  - Usuário digita o código na plataforma para confirmar o vínculo
  - Após confirmação: is_verified = True

#### Tarefa 18.3: Webhook e Roteamento de Mensagens

- [ ] **18.3.1** - Criar whatsapp/views.py — WebhookView
  - View POST `/whatsapp/webhook/` — recebe mensagens do Twilio
  - Validar assinatura do Twilio (segurança contra requisições externas)
    ```python
    from twilio.request_validator import RequestValidator
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    ```
  - Extrair: número do remetente, tipo de mensagem (texto/áudio/imagem), conteúdo
  - Buscar `WhatsAppProfile` pelo número — se não encontrado: responder com instrução de cadastro
  - Se encontrado e verificado: passar para o MessageRouter
  - Retornar TwiML response (XML) vazio imediatamente (resposta assíncrona)

- [ ] **18.3.2** - Criar whatsapp/router.py — MessageRouter
  - Recebe a mensagem e decide qual handler chamar:
    - Mensagem de texto → TextMessageHandler
    - Áudio → AudioMessageHandler
    - Imagem → ImageMessageHandler
  - Envia a resposta de volta via Twilio REST API

- [ ] **18.3.3** - Criar whatsapp/urls.py
  - /whatsapp/webhook/ → WebhookView (name: whatsapp:webhook)
  - /whatsapp/vincular/ → WhatsAppLinkView (name: whatsapp:link) — interface da plataforma
  - /whatsapp/verificar/ → WhatsAppVerifyView (name: whatsapp:verify)

- [ ] **18.3.4** - Registrar em core/urls.py
  - `path('whatsapp/', include('whatsapp.urls', namespace='whatsapp'))`

#### Tarefa 18.4: Agente de IA para Processamento de Mensagens

- [ ] **18.4.1** - Criar whatsapp/agent.py — WhatsAppAgent
  - Agente LangChain especializado em interpretar mensagens financeiras em PT-BR
  - Reutilizar as tools existentes de ai/agents/finance_insight_agent.py
  - Adicionar novas tools específicas para o WhatsApp:
    - `create_transaction(user_id, type, amount, category_name, description, date)` — cria transação
    - `get_account_balance(user_id, account_name=None)` — consulta saldo
    - `get_monthly_summary(user_id)` — resumo do mês
    - `get_goal_progress(user_id, goal_name=None)` — progresso de metas
    - `get_budget_status(user_id, category_name=None)` — status do orçamento
  - System prompt em PT-BR adaptado para conversação curta (respostas máx 3 linhas)
  - Retornar sempre:
    - `action`: o que foi feito (created_transaction, answered_question, etc.)
    - `message`: texto de resposta para o usuário
    - `requires_confirmation`: Boolean — se precisa de confirmação antes de executar

- [ ] **18.4.2** - Implementar fluxo de confirmação
  - Se `requires_confirmation = True`: não executa a ação ainda
  - Armazena o contexto pendente em cache (Django cache framework) com TTL de 5 minutos
  - Envia mensagem de confirmação ao usuário: "Entendi! [resumo da ação]. Confirma? (sim/não)"
  - Na próxima mensagem do usuário: verificar se há ação pendente no cache
  - Se "sim": executar ação e limpar cache
  - Se "não" ou timeout: cancelar e informar usuário

- [ ] **18.4.3** - Criar whatsapp/handlers/text_handler.py
  - Recebe texto da mensagem e usuário
  - Verifica se há ação pendente de confirmação no cache
  - Se sim: processar resposta de confirmação
  - Se não: passar ao WhatsAppAgent para interpretar
  - Retornar mensagem de resposta

- [ ] **18.4.4** - Criar whatsapp/handlers/audio_handler.py
  - Receber URL do áudio do Twilio
  - Baixar o arquivo de áudio temporariamente
  - Transcrever usando OpenAI Whisper API (`openai.audio.transcriptions.create`)
  - Passar texto transcrito ao TextMessageHandler
  - Deletar arquivo temporário após processamento

- [ ] **18.4.5** - Criar whatsapp/handlers/image_handler.py
  - Receber URL da imagem do Twilio
  - Passar imagem para a Vision API do OpenAI (GPT-4o com input de imagem)
  - Prompt: "Extraia o valor total, estabelecimento e data desta nota fiscal/comprovante em JSON"
  - Passar dados extraídos ao TextMessageHandler para criar a transação
  - Responder com os dados identificados + confirmação

#### Tarefa 18.5: Notificações Proativas

- [ ] **18.5.1** - Criar whatsapp/notifications.py — NotificationService
  - Função `send_message(phone_number, message)` — envia mensagem via Twilio REST API
  - Função `notify_transaction_created(user, transaction)` — notifica criação via plataforma
    - Mensagem: "✅ Transação registrada: [descrição] R$ [valor] em [categoria]"
  - Função `send_weekly_summary(user)` — resumo semanal
    - Total gasto na semana, categoria que mais gastou, saldo atual
  - Função `notify_budget_exceeded(user, budget, category)` — alerta de orçamento estourado
    - Mensagem: "⚠️ Você ultrapassou o orçamento de [categoria] este mês!"
  - Função `notify_goal_completed(user, goal)` — meta atingida
    - Mensagem: "🎉 Parabéns! Você atingiu sua meta: [nome da meta]!"
  - Função `notify_installment_due(user, installment)` — parcela próxima do vencimento

- [ ] **18.5.2** - Integrar notificações nos signals existentes
  - Em transactions/signals.py: após criar transação, chamar `notify_transaction_created` se usuário tem WhatsApp vinculado
  - Em goals/views.py: após depósito completar meta, chamar `notify_goal_completed`
  - Em budgets/views.py: após criar despesa que estoura orçamento, chamar `notify_budget_exceeded`

- [ ] **18.5.3** - Criar management command `send_weekly_summaries`
  - whatsapp/management/commands/send_weekly_summaries.py
  - Para cada usuário com WhatsApp verificado: chamar `send_weekly_summary(user)`
  - Preparado para execução semanal via cron (toda segunda-feira)

#### Tarefa 18.6: Interface na Plataforma

- [ ] **18.6.1** - Criar template whatsapp/link.html — página de vinculação
  - Formulário para informar número de WhatsApp
  - Instrução: "Você receberá um código de verificação no WhatsApp"
  - Status atual: vinculado / não vinculado

- [ ] **18.6.2** - Criar template whatsapp/verify.html
  - Campo para digitar o código de 6 dígitos recebido
  - Timer de expiração visual (5 minutos)
  - Botão "Reenviar código"

- [ ] **18.6.3** - Adicionar seção WhatsApp na página de perfil
  - Se não vinculado: card com CTA "Vincular WhatsApp" e benefícios
  - Se vinculado: exibir número vinculado, status verificado, botão "Desvincular"

- [ ] **18.6.4** - Adicionar central de notificações na plataforma
  - Model `Notification` em whatsapp/models.py (ou app notifications separado):
    - `user`, `title`, `message`, `notification_type`, `is_read`, `created_at`
  - View `NotificationListView` — lista as últimas notificações do usuário
  - Ícone de sino no navbar com badge de não lidas
  - Ao clicar: marcar como lida

#### Tarefa 18.7: Exemplos de Interação Suportados

- [ ] **18.7.1** - Documentar e testar os seguintes fluxos:

  **Registrar gastos (texto):**
  - "gastei 45 no almoço" → Despesa R$ 45,00 / Alimentação / conta padrão
  - "paguei 89,90 de combustível no posto" → Despesa R$ 89,90 / Transporte
  - "recebi 5800 de salário" → Receita R$ 5.800,00 / Salário
  - "gastei 320,50 no supermercado extra" → Despesa / Alimentação

  **Registrar por áudio:**
  - [áudio] "almoço no restaurante, quarenta e cinco reais" → mesma lógica do texto

  **Registrar por foto:**
  - [foto de cupom fiscal] → extrai valor e estabelecimento automaticamente

  **Consultas:**
  - "qual meu saldo?" → "Seu saldo total é R$ 3.420,50 (Nubank: R$ 2.100,00 | Carteira: R$ 1.320,50)"
  - "quanto gastei esse mês?" → "Em abril você gastou R$ 1.843,20 (↑12% vs março)"
  - "como está minha meta de viagem?" → "Meta Viagem Europa: R$ 2.300/R$ 5.000 — 46% concluída"
  - "quanto falta no orçamento de alimentação?" → "Alimentação: R$ 320,50 de R$ 800,00 — resta R$ 479,50"

  **Resumo automático (segunda-feira):**
  - "📊 Resumo da semana (29/03–04/04): Gastos: R$ 543,80 | Categoria top: Alimentação (R$ 210,00) | Saldo atual: R$ 3.420,50"

---

### [ ] Sprint 19: Reestruturação do Site Público — Múltiplas Páginas (2 semanas)

> Transformar a landing page atual em um site público completo com navegação multi-página,
> copy persuasivo, mocks visuais fiéis ao design system e páginas dedicadas por feature.
> Objetivo: prender a atenção do visitante e converter em cadastro.

#### Tarefa 19.1: Estrutura e Navegação

- [ ] **19.1.1** - Criar views e URLs para todas as páginas públicas em core/views.py e core/urls.py
  - / → LandingView (atualizar existente)
  - /features/dashboard/ → FeatureDashboardView
  - /features/whatsapp/ → FeatureWhatsAppView
  - /features/ia/ → FeatureIAView
  - /features/metas/ → FeatureMetasView
  - /sobre/ → AboutView
  - /precos/ → PricingView
  - Todas as views são simples TemplateView — sem lógica de backend

- [ ] **19.1.2** - Criar estrutura de templates em templates/public/
  - home.html (substituir landing page existente)
  - features/dashboard.html
  - features/whatsapp.html
  - features/ia.html
  - features/metas.html
  - about.html
  - pricing.html

- [ ] **19.1.3** - Atualizar navbar global (base.html ou componente navbar)
  - Logo: "F" verde + "inova" branco, Inter 600
  - Links: "Início" / "Features ▾" (dropdown) / "Sobre" / "Preços"
  - Dropdown "Features" com 4 itens, cada um com ícone Lucide + descrição curta:
    - 📊 Dashboard & Relatórios → /features/dashboard/
    - 💬 WhatsApp → /features/whatsapp/
    - 🤖 IA Financeira → /features/ia/
    - 🎯 Metas & Orçamentos → /features/metas/
  - Botões: "Entrar" (outline verde) + "Começar grátis" (verde sólido)
  - Navbar fixa com fundo #0a0a0a e border-bottom #262626
  - Mobile: hamburguer com menu lateral deslizante (JavaScript vanilla)
  - Active state no link da página atual

- [ ] **19.1.4** - Atualizar footer global
  - Logo Finova à esquerda
  - Colunas: Produto (links das features) / Empresa (Sobre, Preços) / Legal (Termos, Privacidade)
  - "© 2026 Finova. Todos os direitos reservados."
  - Fundo #000000, border-top #262626

#### Tarefa 19.2: Página Início (Landing Principal)

> Página enxuta e persuasiva — apresenta o produto, desperta curiosidade
> e direciona para as páginas de feature. Não tenta explicar tudo.

- [ ] **19.2.1** - Hero Section
  - Badge pill: ✨ "Novo: Controle via WhatsApp" — fundo rgba(34,197,94,0.08), borda verde sutil
  - Headline Inter 600 grande: "Suas finanças. Finalmente sob controle."
  - Subtítulo Inter 300: "Do registro pelo WhatsApp ao relatório completo do mês. O assistente financeiro que você sempre quis."
  - CTAs: "Começar gratuitamente" → {% url 'users:signup' %} / "Ver funcionalidades ↓" (âncora ghost)
  - Prova social: 3 avatares coloridos + "Mais de 1.200 pessoas já usam o Finova"
  - Radial gradient verde suavíssimo centralizado no fundo
  - Mock do dashboard Finova: HTML/CSS puro fiel ao design real (cards de saldo + gráfico de linhas simulado)

- [ ] **19.2.2** - Barra de bancos suportados
  - Texto pequeno text-secondary: "Compatível com os maiores bancos do Brasil"
  - 8 logos em escala de cinza (usar os SVGs de static/images/banks/ já existentes)
  - Layout horizontal com overflow-x scroll suave em mobile

- [ ] **19.2.3** - Seção "Por que o Finova?" (3 cards)
  - Fundo #111111, borda #262626
  - Card 1: ícone Lucide verde + "Registre em segundos" + descrição WhatsApp + IA
  - Card 2: ícone + "Visão completa, zero planilha" + descrição dashboard
  - Card 3: ícone + "IA que entende você" + descrição análise personalizada

- [ ] **19.2.4** - Seção de features em destaque (4 blocos alternados)
  - Layout esquerda/direita alternado a cada bloco
  - Cada bloco: label pequena verde / título Inter 600 / 2 linhas de descrição /
    3 bullets com check verde / mock HTML/CSS da feature / link "Saiba mais →" para página dedicada
  - Bloco 1 — Dashboard & Relatórios: "Tudo que importa em uma tela."
    - Mock: mini cards de saldo + gráfico de linhas simulado
  - Bloco 2 — WhatsApp: "Registre um gasto sem abrir nenhum app."
    - Mock: conversa WhatsApp estilizada com 2-3 balões de exemplo real
  - Bloco 3 — IA Financeira: "Insights que você não saberia sozinho."
    - Mock: card de análise IA com texto simulado de insight financeiro
  - Bloco 4 — Metas & Orçamentos: "Economize com propósito, não com culpa."
    - Mock: dois cards de meta com barra de progresso colorida

- [ ] **19.2.5** - Seção de depoimentos (3 cards)
  - Fundo #111111, borda #262626
  - Avatar (inicial colorida em círculo), nome, profissão, depoimento
  - Depoimentos fictícios mas específicos e realistas — mencionar features reais:
    - Ex: "Descobri que gastava R$ 340 por mês em assinaturas esquecidas. A IA me mostrou isso na primeira semana."
    - Ex: "Mando um áudio no WhatsApp saindo do restaurante. Quando chego em casa tá tudo categorizado."
    - Ex: "Em 3 meses juntei R$ 4.200 para a viagem usando as metas do Finova."

- [ ] **19.2.6** - CTA Final
  - Radial gradient verde suavíssimo no fundo
  - Headline: "Suas finanças merecem um app melhor."
  - Subtítulo: "14 dias grátis para descobrir como é ter controle de verdade."
  - Botão verde grande: "Começar gratuitamente" → {% url 'users:signup' %}
  - Três ícones abaixo: ✓ Sem cartão de crédito / ✓ Cancele quando quiser / ✓ Suporte em português

#### Tarefa 19.3: Página Feature — Dashboard & Relatórios

- [ ] **19.3.1** - Hero da página
  - Label verde: "Dashboard & Relatórios"
  - Headline: "Tudo que importa em uma tela."
  - Subtítulo: "Saldo de todas as contas, evolução dos últimos 6 meses e os gastos do mês — sem abrir extrato de banco."
  - Mock grande do dashboard Finova (HTML/CSS detalhado)

- [ ] **19.3.2** - Seções de detalhe (uma por sub-feature)
  - Saldo consolidado em tempo real — mock: 3 cards de conta com saldo e ícone do banco
  - Gráfico de evolução mensal — mock: gráfico de linhas simulado (SVG ou CSS)
  - Distribuição por categoria — mock: donut chart simulado + lista de categorias
  - Relatórios por período — mock: filtro de período + tabela de categorias com barras
  - Top gastos do mês — mock: lista de 5 transações com valor e categoria

- [ ] **19.3.3** - CTA ao final: "Começar gratuitamente"

#### Tarefa 19.4: Página Feature — WhatsApp

- [ ] **19.4.1** - Hero da página
  - Label verde: "Integração WhatsApp"
  - Headline: "Registre um gasto sem abrir nenhum app."
  - Subtítulo: "Texto, áudio ou foto do comprovante. Nossa IA entende, categoriza e lança automaticamente."
  - Mock: conversa WhatsApp grande e detalhada (4-5 mensagens com exemplos reais)

- [ ] **19.4.2** - Seções de detalhe
  - Registro por texto — mock: balão "gastei 45 no almoço" + resposta da IA confirmando
  - Registro por áudio — mock: balão de áudio + transcrição + confirmação
  - Foto de comprovante — mock: balão de imagem + dados extraídos pela IA
  - Consultas instantâneas — mock: "Qual meu saldo?" + resposta com valores
  - Notificações proativas — mock: mensagem de resumo semanal automático

- [ ] **19.4.3** - CTA ao final: "Vincular meu WhatsApp"

#### Tarefa 19.5: Página Feature — IA Financeira

- [ ] **19.5.1** - Hero da página
  - Label verde: "IA Financeira"
  - Headline: "Insights que você não saberia sozinho."
  - Subtítulo: "Nosso agente analisa seus padrões de gasto e entrega recomendações práticas toda semana."
  - Mock: card de análise IA com texto simulado realista de insight

- [ ] **19.5.2** - Seções de detalhe
  - Como funciona o agente — diagrama simples HTML/CSS (3 passos: dados → IA → insights)
  - Análise de padrões — mock: gráfico de categorias + texto de insight sobre alimentação
  - Recomendações práticas — mock: lista de 3 recomendações com ícone e texto
  - Categorização automática — mock: transação sem categoria → IA → categoria atribuída
  - Histórico de análises — mock: lista de análises passadas com data e resumo

- [ ] **19.5.3** - CTA ao final: "Experimentar grátis"

#### Tarefa 19.6: Página Feature — Metas & Orçamentos

- [ ] **19.6.1** - Hero da página
  - Label verde: "Metas & Orçamentos"
  - Headline: "Economize com propósito, não com culpa."
  - Subtítulo: "Defina onde quer chegar e quanto pode gastar. O Finova acompanha cada passo."
  - Mock: dois cards de meta com barra de progresso + card de orçamento

- [ ] **19.6.2** - Seções de detalhe
  - Criar e acompanhar metas — mock: formulário de meta + card com progresso 67%
  - Depósito vinculado à conta — mock: modal de depósito com seleção de conta
  - Orçamento por categoria — mock: lista de orçamentos com barras verde/amarelo/vermelho
  - Alertas de estouro — mock: notificação WhatsApp de orçamento estourado
  - Parcelamentos e recorrências — mock: card de parcelamento com parcelas restantes

- [ ] **19.6.3** - CTA ao final: "Começar minha primeira meta"

#### Tarefa 19.7: Página Sobre

- [ ] **19.7.1** - Hero: headline + subtítulo sobre a missão do Finova
- [ ] **19.7.2** - História: por que o Finova foi criado (texto narrativo, tom pessoal)
- [ ] **19.7.3** - Missão e valores (3 cards): Simplicidade / Segurança / Inovação
- [ ] **19.7.4** - Segurança e privacidade: criptografia, sem venda de dados, HTTPS
- [ ] **19.7.5** - Números: 1.200+ usuários / 4.8★ avaliação / 100% desenvolvido no Brasil
- [ ] **19.7.6** - CTA: "Conhecer o produto"

#### Tarefa 19.8: Página Preços

- [ ] **19.8.1** - Hero: "Simples. Transparente. Sem surpresas." + destaque do trial de 14 dias
- [ ] **19.8.2** - Dois cards de plano (fundo #111111):
  - Gratuito: funcionalidades básicas listadas
  - Premium (borda verde, badge "Mais popular"): R$ 19,90/mês ou R$ 199/ano — todas as features
- [ ] **19.8.3** - Tabela comparativa: features em linhas, planos em colunas, check verde / X cinza
- [ ] **19.8.4** - FAQ de preços (accordion JavaScript vanilla, 5 perguntas):
  - "Preciso de cartão de crédito para o teste?" / "Posso cancelar quando quiser?" /
    "O que está incluso no plano gratuito?" / "Como funciona o plano anual?" /
    "Meus dados estão seguros?"
- [ ] **19.8.5** - CTA final: "Começar gratuitamente"

#### Tarefa 19.9: Componentes JavaScript e CSS

- [ ] **19.9.1** - Criar static/js/public.js
  - Menu hamburguer mobile (abrir/fechar sidebar)
  - Dropdown de features na navbar (abrir/fechar ao hover e click)
  - Accordion do FAQ (toggle com transição suave de altura)
  - Fade-in ao entrar na viewport (Intersection Observer API)
  - Scroll suave para âncoras

- [ ] **19.9.2** - Garantir responsividade completa
  - Testar breakpoints: 375px / 768px / 1280px
  - Blocos alternados viram coluna única em mobile
  - Mocks HTML/CSS redimensionados corretamente
  - Navbar mobile funcional

- [ ] **19.9.3** - Compilar Tailwind: `npm run build:css`

#### Tarefa 19.10: Qualidade e Revisão

- [ ] **19.10.1** - Revisar todos os links internos ({% url %} em todos os CTAs)
- [ ] **19.10.2** - Garantir que usuário autenticado veja navbar diferente (sem "Entrar"/"Cadastrar", com link para dashboard)
- [ ] **19.10.3** - Meta tags SEO em cada página (title, description únicos por página)
- [ ] **19.10.4** - Testar em Chrome, Firefox e Safari

---

### Sprints Futuras

#### Sprint 20: Testes Automatizados
- Setup de testes (pytest, pytest-django)
- Testes unitários (models, forms, signals, services)
- Testes de integração (views, fluxos completos)
- Testes E2E com Selenium
- Testes para agente de IA (mocking de chamadas OpenAI)
- Testes para webhook do WhatsApp (mocking do Twilio)
- Testes para transferências, parcelamentos e recorrências

#### Sprint 21: Containerização e CI/CD
- Criar Dockerfile e docker-compose.yml
- Configurar volumes e redes
- Setup de GitHub Actions
- Pipelines de testes e deploy
- Ambientes staging/production
- Configurar cron jobs para: generate_recurrences, send_weekly_summaries

---

## Cronograma Estimado (Atualizado)

| Sprint | Duração | Descrição | Status |
|--------|---------|-----------|--------|
| Sprint 0 | 1 semana | Setup e Configuração | ✅ Concluído |
| Sprint 1 | 1 semana | Autenticação e Usuários | ✅ Concluído |
| Sprint 2 | 1 semana | Landing Page | ✅ Concluído |
| Sprint 3 | 1 semana | Models de Contas e Categorias | ✅ Concluído |
| Sprint 4 | 1 semana | Views de Contas | ✅ Concluído |
| Sprint 5 | 1 semana | Views de Categorias | ✅ Concluído |
| Sprint 6 | 2 semanas | Transações | ✅ Concluído |
| Sprint 7 | 2 semanas | Dashboard e Gráficos | ✅ Concluído |
| Sprint 8 | 2 semanas | Agente de IA Financeiro | ✅ Concluído |
| Sprint 9 | 1 semana | Refinamentos e MVP | ✅ Concluído |
| Sprint 10 | 1 semana | Redesign Visual + Rebranding Finova | ✅ Concluído |
| Sprint 11 | 1 semana | App de Metas (Goals) | ✅ Concluído |
| Sprint 12 | 1 semana | App de Relatórios (Reports) | 🔄 Em andamento |
| Sprint 13 | 2 semanas | Vínculo Bancário e Transferências | ⏳ Planejado |
| Sprint 14 | 1 semana | Orçamentos por Categoria | ⏳ Planejado |
| Sprint 15 | 1 semana | Recorrências — Despesas e Receitas Fixas | ⏳ Planejado |
| Sprint 16 | 2 semanas | Parcelamentos | ⏳ Planejado |
| Sprint 17 | 2 semanas | Cartões de Crédito | ⏳ Planejado |
| Sprint 18 | 3 semanas | Integração com WhatsApp | ⏳ Planejado |
| Sprint 19 | 2 semanas | Reestruturação do Site Público | ⏳ Planejado |
| Sprint 20 | 2 semanas | Testes Automatizados | ⏳ Futuro |
| Sprint 21 | 1 semana | Containerização e CI/CD | ⏳ Futuro |
| **Total** | **~32 semanas** | **Produto completo** | |

---
