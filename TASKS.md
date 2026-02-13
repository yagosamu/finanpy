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
  - Adicionar configuração para usar aspas simples no código
  - Configurar LANGUAGE_CODE = 'pt-br'
  - Configurar TIME_ZONE = 'America/Sao_Paulo'
  - Configurar STATIC_URL e STATIC_ROOT
  - Configurar MEDIA_URL e MEDIA_ROOT
  - Configurar USE_I18N = True
  - Configurar USE_TZ = True
  - Adicionar configurações de segurança básicas

#### Tarefa 0.2: Criação das Apps Django
- [X] **0.2.1** - Criar app users
  - Executar: `python manage.py startapp users`
  - Adicionar em INSTALLED_APPS
  - Criar arquivo urls.py dentro da app
  
- [X] **0.2.2** - Criar app profiles
  - Executar: `python manage.py startapp profiles`
  - Adicionar em INSTALLED_APPS
  - Criar arquivo urls.py dentro da app
  
- [X] **0.2.3** - Criar app accounts
  - Executar: `python manage.py startapp accounts`
  - Adicionar em INSTALLED_APPS
  - Criar arquivo urls.py dentro da app
  
- [X] **0.2.4** - Criar app categories
  - Executar: `python manage.py startapp categories`
  - Adicionar em INSTALLED_APPS
  - Criar arquivo urls.py dentro da app
  
- [X] **0.2.5** - Criar app transactions
  - Executar: `python manage.py startapp transactions`
  - Adicionar em INSTALLED_APPS
  - Criar arquivo urls.py dentro da app

#### Tarefa 0.3: Configuração do TailwindCSS
- [X] **0.3.1** - Instalar Node.js e npm
  - Verificar instalação: `node --version`
  - Verificar npm: `npm --version`

- [X] **0.3.2** - Configurar TailwindCSS via CDN (temporário)
  - Criar arquivo base.html
  - Adicionar CDN do Tailwind no <head>
  - Testar classes básicas
  
- [X] **0.3.3** - Configurar TailwindCSS local (opcional posterior)
  - Instalar: `npm install -D tailwindcss`
  - Executar: `npx tailwindcss init`
  - Configurar tailwind.config.js
  - Criar arquivo CSS de entrada
  - Configurar script de build

#### Tarefa 0.4: Estrutura de Templates Base
- [X] **0.4.1** - Criar diretório de templates
  - Criar: `templates/` na raiz do projeto
  - Configurar TEMPLATES em settings.py
  - Adicionar DIRS: [BASE_DIR / 'templates']

- [X] **0.4.2** - Criar template base.html
  - Estrutura HTML5 básica
  - Inclusão do TailwindCSS
  - Blocks: title, extra_css, content, extra_js
  - Meta tags responsivas

- [X] **0.4.3** - Criar template base_dashboard.html
  - Herdar de base.html
  - Adicionar navbar
  - Adicionar sidebar
  - Estrutura de conteúdo principal
  - Footer

#### Tarefa 0.5: Configuração de Arquivos Estáticos
- [X] **0.5.1** - Criar estrutura de pastas static
  - Criar: `static/css/`
  - Criar: `static/js/`
  - Criar: `static/images/`

- [X] **0.5.2** - Configurar collectstatic
  - Definir STATIC_ROOT em settings.py
  - Testar: `python manage.py collectstatic`

- [X] **0.5.3** - Criar arquivo CSS customizado
  - Criar: `static/css/custom.css`
  - Adicionar estilos complementares ao Tailwind
  - Importar no base.html

#### Tarefa 0.6: Configuração do Git
- [X] **0.6.1** - Inicializar repositório Git
  - Executar: `git init`
  - Criar arquivo .gitignore
  - Adicionar padrões Python/Django ao .gitignore
  
- [X] **0.6.2** - Configurar .gitignore
  - Adicionar venv/
  - Adicionar __pycache__/
  - Adicionar *.pyc
  - Adicionar db.sqlite3
  - Adicionar .env
  - Adicionar node_modules/ (se usar npm local)
  
- [X] **0.6.3** - Primeiro commit
  - `git add .`
  - `git commit -m "Initial project setup"`

### [X] Sprint 1: Autenticação e Sistema de Usuários (1 semana)

#### Tarefa 1.1: Model de Usuário Customizado
- [X] **1.1.1** - Criar CustomUser model em users/models.py
  - Herdar de AbstractUser
  - Definir USERNAME_FIELD = 'email'
  - Adicionar campo email como único
  - Adicionar campos created_at e updated_at
  - Remover campo username dos REQUIRED_FIELDS

- [X] **1.1.2** - Criar CustomUserManager
  - Sobrescrever create_user para usar email
  - Sobrescrever create_superuser para usar email
  - Validar formato de email

- [X] **1.1.3** - Configurar AUTH_USER_MODEL
  - Adicionar em settings.py: AUTH_USER_MODEL = 'users.CustomUser'
  - Verificar configuração

- [X] **1.1.4** - Criar e aplicar migrations
  - `python manage.py makemigrations`
  - `python manage.py migrate`
  - Verificar tabela no SQLite

#### Tarefa 1.2: Model de Profile
- [X] **1.2.1** - Criar Profile model em profiles/models.py
  - Campo user (OneToOneField para User)
  - Campo first_name (CharField)
  - Campo last_name (CharField)
  - Campo phone (CharField, opcional)
  - Campo birth_date (DateField, opcional)
  - Campos created_at e updated_at

- [X] **1.2.2** - Criar signal para criar Profile automaticamente
  - Criar arquivo profiles/signals.py
  - Signal post_save no User para criar Profile
  - Importar signals no apps.py

- [X] **1.2.3** - Registrar Profile no admin
  - Criar ProfileAdmin em profiles/admin.py
  - Configurar list_display
  - Configurar campos de busca

- [X] **1.2.4** - Criar e aplicar migrations
  - `python manage.py makemigrations profiles`
  - `python manage.py migrate`

#### Tarefa 1.3: Views de Autenticação
- [X] **1.3.1** - Criar SignUpView (Class Based View)
  - Herdar de CreateView
  - Form para cadastro com email e senha
  - Validação de email único
  - Validação de força de senha
  - Redirecionar para dashboard após cadastro
  - Fazer login automático após cadastro

- [X] **1.3.2** - Criar LoginView customizada
  - Usar LoginView do Django
  - Customizar template
  - Configurar LOGIN_URL e LOGIN_REDIRECT_URL
  - Usar email ao invés de username

- [X] **1.3.3** - Criar LogoutView
  - Usar LogoutView do Django
  - Configurar LOGOUT_REDIRECT_URL
  - Mensagem de sucesso

- [X] **1.3.4** - Criar PasswordResetView (opcional)
  - Configurar fluxo de recuperação de senha
  - Templates de email
  - Views de confirmação

#### Tarefa 1.4: Forms de Autenticação
- [X] **1.4.1** - Criar SignUpForm em users/forms.py
  - Campos: email, password1, password2
  - Validação de email único
  - Validação de senha forte
  - Clean methods customizados

- [X] **1.4.2** - Criar CustomAuthenticationForm
  - Herdar de AuthenticationForm
  - Usar email ao invés de username
  - Mensagens de erro customizadas

- [X] **1.4.3** - Criar ProfileForm em profiles/forms.py
  - Campos do Profile
  - Validações de data de nascimento
  - Validação de telefone (formato brasileiro)

#### Tarefa 1.5: Templates de Autenticação
- [X] **1.5.1** - Criar template signup.html
  - Formulário de cadastro estilizado
  - Validações em tempo real (JavaScript)
  - Link para página de login
  - Design com gradientes e tema escuro

- [X] **1.5.2** - Criar template login.html
  - Formulário de login estilizado
  - Link para cadastro
  - Link para recuperar senha (se implementado)
  - Mensagens de erro claras

- [X] **1.5.3** - Criar template profile.html
  - Exibição de dados do perfil
  - Botão para editar perfil
  - Layout consistente com dashboard

- [X] **1.5.4** - Criar template profile_edit.html
  - Formulário de edição de perfil
  - Campos preenchidos com dados atuais
  - Botão para alterar senha
  - Validações visuais

#### Tarefa 1.6: URLs de Autenticação
- [X] **1.6.1** - Configurar users/urls.py
  - Rota para signup
  - Rota para login
  - Rota para logout
  - Rota para recuperar senha (se implementado)

- [X] **1.6.2** - Configurar profiles/urls.py
  - Rota para visualizar perfil
  - Rota para editar perfil
  - Rota para alterar senha

- [X] **1.6.3** - Incluir URLs no core/urls.py
  - Include de users.urls
  - Include de profiles.urls
  - Configurar namespace se necessário

#### Tarefa 1.7: Testes Manuais de Autenticação
- [X] **1.7.1** - Testar fluxo de cadastro
  - Cadastrar novo usuário
  - Verificar criação de Profile
  - Verificar redirecionamento
  
- [X] **1.7.2** - Testar fluxo de login
  - Login com email
  - Verificar sessão mantida
  - Testar credenciais inválidas
  
- [X] **1.7.3** - Testar proteção de rotas
  - Tentar acessar rotas autenticadas sem login
  - Verificar redirecionamento para login

---

### [X] Sprint 2: Site Público e Landing Page (1 semana)

#### Tarefa 2.1: Estrutura da Landing Page
- [X] **2.1.1** - Criar app home (opcional) ou views no core
  - Criar view para landing page
  - Configurar como página inicial (/)

- [X] **2.1.2** - Criar template home.html
  - Header com logo e navegação
  - Hero section com call-to-action
  - Seção de benefícios/features
  - Seção de depoimentos (mockup)
  - Footer com links e informações

- [X] **2.1.3** - Implementar navegação responsiva
  - Menu hamburguer para mobile
  - Transições suaves
  - Links para cadastro e login destacados

#### Tarefa 2.2: Seções da Landing Page
- [X] **2.2.1** - Hero Section
  - Título impactante
  - Subtítulo explicativo
  - Botões CTA (Cadastre-se, Login)
  - Imagem ou ilustração (mockup)
  - Gradientes e animações sutis

- [X] **2.2.2** - Features Section
  - Cards com principais funcionalidades
  - Ícones representativos
  - Descrições curtas e objetivas
  - Grid responsivo (3 colunas desktop, 1 mobile)

- [X] **2.2.3** - Benefits Section
  - Lista de benefícios
  - Visual atrativo com ícones
  - Texto persuasivo

- [X] **2.2.4** - CTA Section
  - Chamada final para ação
  - Botão grande de cadastro
  - Argumento de valor

#### Tarefa 2.3: Estilização Avançada
- [X] **2.3.1** - Implementar gradientes no hero
  - Gradiente de fundo animado
  - Efeito de brilho nos botões
  - Sombras e profundidade

- [X] **2.3.2** - Adicionar animações CSS
  - Fade in ao carregar seções
  - Hover effects nos cards
  - Transições suaves
  - Usar classes Tailwind de transição

- [X] **2.3.3** - Otimizar responsividade
  - Testar em diferentes resoluções
  - Ajustar espaçamentos mobile
  - Reordenar elementos se necessário

#### Tarefa 2.4: Componentes Reutilizáveis
- [X] **2.4.1** - Criar componente de navbar
  - Template include navbar.html
  - Logo com gradiente
  - Links de navegação
  - Botões de ação

- [X] **2.4.2** - Criar componente de footer
  - Template include footer.html
  - Links úteis
  - Informações de contato (mockup)
  - Copyright

- [X] **2.4.3** - Criar componente de card
  - Template include card.html
  - Parâmetros: título, descrição, ícone
  - Estilo consistente com design system

#### Tarefa 2.5: Conteúdo e Copywriting
- [X] **2.5.1** - Escrever textos da landing page
  - Título principal impactante
  - Descrição de funcionalidades
  - Benefícios claros
  - Chamadas para ação persuasivas

- [X] **2.5.2** - Preparar assets visuais
  - Ícones (usar biblioteca como Heroicons)
  - Imagens placeholder (ou ilustrações)
  - Logo do Finanpy

#### Tarefa 2.6: SEO Básico
- [X] **2.6.1** - Configurar meta tags
  - Meta description
  - Meta keywords
  - Open Graph tags (Facebook)
  - Twitter cards

- [X] **2.6.2** - Otimizar performance
  - Minificar CSS (postergar se necessário)
  - Otimizar imagens
  - Lazy loading de imagens

---

### [X] Sprint 3: Models e Admin de Contas e Categorias (1 semana)

#### Tarefa 3.1: Model de Account
- [X] **3.1.1** - Criar Account model em accounts/models.py
  - Campo user (ForeignKey para User)
  - Campo name (CharField, max_length=100)
  - Campo account_type (CharField com choices)
  - Campo bank (CharField, max_length=100, opcional)
  - Campo initial_balance (DecimalField)
  - Campo current_balance (DecimalField)
  - Campo is_active (BooleanField, default=True)
  - Campos created_at e updated_at

- [X] **3.1.2** - Definir choices para account_type
  - CHECKING = 'checking' - Conta Corrente
  - SAVINGS = 'savings' - Poupança
  - WALLET = 'wallet' - Carteira
  - INVESTMENT = 'investment' - Investimentos

- [X] **3.1.3** - Implementar método __str__
  - Retornar nome da conta

- [X] **3.1.4** - Implementar método get_balance
  - Calcular saldo baseado em transações
  - Considerar tipo de transação (receita/despesa)

- [X] **3.1.5** - Criar migrations e aplicar
  - `python manage.py makemigrations accounts`
  - `python manage.py migrate`

#### Tarefa 3.2: Model de Category
- [X] **3.2.1** - Criar Category model em categories/models.py
  - Campo user (ForeignKey para User, null=True para categorias padrão)
  - Campo name (CharField, max_length=50)
  - Campo category_type (CharField com choices)
  - Campo color (CharField, max_length=7, hex color)
  - Campo is_default (BooleanField, default=False)
  - Campo is_active (BooleanField, default=True)
  - Campos created_at e updated_at

- [X] **3.2.2** - Definir choices para category_type
  - INCOME = 'income' - Receita
  - EXPENSE = 'expense' - Despesa

- [X] **3.2.3** - Implementar método __str__
  - Retornar nome da categoria

- [X] **3.2.4** - Implementar Meta class
  - unique_together = ['user', 'name']
  - ordering = ['name']

- [X] **3.2.5** - Criar migrations e aplicar
  - `python manage.py makemigrations categories`
  - `python manage.py migrate`

#### Tarefa 3.3: Categorias Padrão
- [X] **3.3.1** - Criar management command
  - Criar arquivo: categories/management/commands/create_default_categories.py

- [X] **3.3.2** - Implementar lógica do command
  - Lista de categorias padrão de despesas: Alimentação, Transporte, Moradia, Saúde, Educação, Lazer, Vestuário, Outros
  - Lista de categorias padrão de receitas: Salário, Freelance, Investimentos, Outros
  - Verificar se já existem antes de criar
  - Criar com user=None e is_default=True

- [X] **3.3.3** - Executar command
  - `python manage.py create_default_categories`
  - Verificar criação no admin

#### Tarefa 3.4: Admin de Accounts
- [X] **3.4.1** - Criar AccountAdmin em accounts/admin.py
  - Registrar model Account
  - Configurar list_display
  - Configurar list_filter
  - Configurar search_fields
  - Configurar readonly_fields (current_balance)

- [X] **3.4.2** - Customizar formulário do admin
  - Organizar fieldsets
  - Adicionar help_text nos campos

- [X] **3.4.3** - Adicionar ações personalizadas
  - Ação para ativar/desativar múltiplas contas

#### Tarefa 3.5: Admin de Categories
- [X] **3.5.1** - Criar CategoryAdmin em categories/admin.py
  - Registrar model Category
  - Configurar list_display com cor visual
  - Configurar list_filter (type, is_default)
  - Configurar search_fields

- [X] **3.5.2** - Adicionar widget de cor no admin
  - Usar widget de input color HTML5
  - Preview da cor selecionada

- [X] **3.5.3** - Configurar ordering e filtros
  - Ordenar por tipo e nome
  - Filtrar categorias padrão vs personalizadas

#### Tarefa 3.6: Testes Manuais no Admin
- [X] **3.6.1** - Criar superusuário
  - `python manage.py createsuperuser`
  - Usar email como identificador
  
- [X] **3.6.2** - Testar CRUD de Accounts
  - Criar conta via admin ✓
  - Editar conta ✓
  - Verificar campos obrigatórios ✓
  - Testar filtros e busca ✓
  - Status: APROVADO (100% - 10/10 testes)

- [X] **3.6.3** - Testar CRUD de Categories
  - Visualizar categorias padrão ✓
  - Criar categoria personalizada ✓
  - Editar cor ✓ (funcional, teste automatizado com problema menor)
  - Testar filtros ✓
  - Status: APROVADO (90% - 9/10 testes)

---

### [X] Sprint 4: Views e Templates de Contas (1 semana)

#### Tarefa 4.1: Views de Account
- [X] **4.1.1** - Criar AccountListView em accounts/views.py
  - Herdar de LoginRequiredMixin e ListView
  - Filtrar contas do usuário logado
  - Ordenar por nome
  - Adicionar saldo total no context

- [X] **4.1.2** - Criar AccountCreateView
  - Herdar de LoginRequiredMixin e CreateView
  - Associar automaticamente ao user logado
  - Validar dados
  - Redirecionar para lista após criar
  - Mensagem de sucesso

- [X] **4.1.3** - Criar AccountUpdateView
  - Herdar de LoginRequiredMixin e UpdateView
  - Garantir que apenas dono pode editar
  - Campos editáveis (exceto current_balance)
  - Mensagem de sucesso

- [X] **4.1.4** - Criar AccountDeleteView
  - Herdar de LoginRequiredMixin e DeleteView
  - Soft delete (is_active = False)
  - Confirmação obrigatória
  - Mensagem de sucesso

- [X] **4.1.5** - Criar AccountDetailView
  - Herdar de LoginRequiredMixin e DetailView
  - Mostrar detalhes da conta
  - Listar últimas transações da conta
  - Mostrar gráfico de evolução (postergar)

#### Tarefa 4.2: Forms de Account
- [X] **4.2.1** - Criar AccountForm em accounts/forms.py
  - Campos: name, account_type, bank, initial_balance
  - Validação de initial_balance (decimal positivo ou negativo)
  - Choices traduzidas para português
  - Help texts claros

- [X] **4.2.2** - Customizar widgets dos campos
  - Input com classes Tailwind
  - Select estilizado
  - Placeholder nos campos

#### Tarefa 4.3: Templates de Account
- [X] **4.3.1** - Criar account_list.html
  - Herdar de base_dashboard.html
  - Cards para cada conta
  - Informações: nome, banco, tipo, saldo
  - Botões de ação (editar, excluir, ver detalhes)
  - Card de saldo total destacado
  - Botão para criar nova conta
  - Grid responsivo

- [X] **4.3.2** - Criar account_form.html
  - Formulário estilizado
  - Labels em português
  - Validações visuais
  - Botão de salvar com loading state
  - Botão de cancelar
  - Usar componentes do design system

- [X] **4.3.3** - Criar account_confirm_delete.html
  - Mensagem de confirmação clara
  - Avisos sobre consequências
  - Botões de confirmar e cancelar
  - Design alinhado com tema

- [X] **4.3.4** - Criar account_detail.html
  - Informações completas da conta
  - Histórico de transações
  - Estatísticas da conta
  - Botões de ação

#### Tarefa 4.4: URLs de Account
- [X] **4.4.1** - Configurar accounts/urls.py
  - Path para list: 'accounts/'
  - Path para create: 'accounts/nova/'
  - Path para update: 'accounts/<pk>/editar/'
  - Path para delete: 'accounts/<pk>/excluir/'
  - Path para detail: 'accounts/<pk>/'
  - Nomear URLs adequadamente

- [X] **4.4.2** - Incluir em core/urls.py
  - Include de accounts.urls
  - Configurar namespace 'accounts'

#### Tarefa 4.5: Componentes de UI para Contas
- [X] **4.5.1** - Criar componente de card de conta
  - Template include: components/account_card.html
  - Parâmetros: account
  - Cor baseada no tipo de conta
  - Ícone por tipo de conta

- [X] **4.5.2** - Criar componente de saldo total
  - Destaque visual
  - Formatação monetária
  - Indicador de crescimento (postergar)

#### Tarefa 4.6: JavaScript para Interações
- [X] **4.6.1** - Criar accounts.js em static/js/
  - Confirmação de exclusão com modal
  - Validação de formulário em tempo real
  - Formatação de valores monetários

- [X] **4.6.2** - Implementar feedback visual
  - Loading states nos botões
  - Transições suaves
  - Mensagens toast/alert

#### Tarefa 4.7: Testes Manuais de Accounts
- [X] **4.7.1** - Testar criação de conta
  - Preencher formulário
  - Verificar validações
  - Confirmar criação no banco

- [X] **4.7.2** - Testar listagem
  - Verificar exibição de contas
  - Testar responsividade
  - Verificar cálculo de saldo total

- [X] **4.7.3** - Testar edição e exclusão
  - Editar dados de conta
  - Soft delete
  - Verificar redirecionamentos

---

### [X] Sprint 5: Views e Templates de Categorias (1 semana)

#### Tarefa 5.1: Views de Category
- [X] **5.1.1** - Criar CategoryListView em categories/views.py
  - Herdar de LoginRequiredMixin e ListView
  - Listar categorias padrão + personalizadas do usuário
  - Separar por tipo (receita/despesa) no context
  - Ordenar por nome

- [X] **5.1.2** - Criar CategoryCreateView
  - Herdar de LoginRequiredMixin e CreateView
  - Associar ao user logado
  - Validar nome único por usuário
  - Mensagem de sucesso

- [X] **5.1.3** - Criar CategoryUpdateView
  - Apenas categorias não-padrão podem ser editadas
  - Validação de permissão
  - Atualizar informações
  - Mensagem de sucesso

- [X] **5.1.4** - Criar CategoryDeleteView
  - Apenas categorias sem transações
  - Verificar uso antes de excluir
  - Soft delete (is_active = False)
  - Mensagem de erro se em uso

#### Tarefa 5.2: Forms de Category
- [X] **5.2.1** - Criar CategoryForm em categories/forms.py
  - Campos: name, category_type, color
  - Validação de nome único
  - Widget de cor (color picker)
  - Choices de tipo traduzidas

- [X] **5.2.2** - Implementar validação de cor
  - Formato hexadecimal (#RRGGBB)
  - Sugestões de cores padrão

- [X] **5.2.3** - Adicionar preview de cor
  - JavaScript para mostrar cor selecionada
  - Atualização em tempo real

#### Tarefa 5.3: Templates de Category
- [X] **5.3.1** - Criar category_list.html
  - Herdar de base_dashboard.html
  - Duas seções: Receitas e Despesas
  - Cards/badges para cada categoria
  - Mostrar cor, nome e tipo
  - Indicador de categoria padrão
  - Botões de ação (editar/excluir) apenas para personalizadas
  - Botão para criar nova categoria

- [X] **5.3.2** - Criar category_form.html
  - Formulário estilizado
  - Color picker integrado
  - Preview da cor selecionada
  - Paleta de cores sugeridas
  - Validações visuais

- [X] **5.3.3** - Criar category_confirm_delete.html
  - Confirmação de exclusão
  - Aviso se categoria estiver em uso
  - Botões estilizados

#### Tarefa 5.4: URLs de Category
- [X] **5.4.1** - Configurar categories/urls.py
  - Path para list: 'categorias/'
  - Path para create: 'categorias/nova/'
  - Path para update: 'categorias/<pk>/editar/'
  - Path para delete: 'categorias/<pk>/excluir/'

- [X] **5.4.2** - Incluir em core/urls.py
  - Include de categories.urls
  - Namespace 'categories'

#### Tarefa 5.5: Componentes de UI para Categorias
- [X] **5.5.1** - Criar badge de categoria
  - Template include: components/category_badge.html
  - Parâmetros: category
  - Cor de fundo baseada em category.color
  - Ícone por tipo (receita/despesa)
  
- [X] **5.5.2** - Criar seletor de categoria
  - Componente para usar em formulários
  - Visual com cores
  - Filtro por tipo

#### Tarefa 5.6: JavaScript para Categorias
- [X] **5.6.1** - Criar categories.js
  - Color picker customizado
  - Preview de cor em tempo real
  - Validação de formato hexadecimal
  
- [X] **5.6.2** - Implementar paleta de cores
  - Cores pré-definidas clicáveis
  - Aplicar cor ao clicar

#### Tarefa 5.7: Testes Manuais de Categories
- [X] **5.7.1** - Testar listagem
  - Verificar categorias padrão
  - Verificar separação por tipo
  - Testar responsividade
  
- [X] **5.7.2** - Testar criação de categoria
  - Criar categoria de receita
  - Criar categoria de despesa
  - Testar validação de nome único
  - Testar color picker
  
- [X] **5.7.3** - Testar edição e exclusão
  - Tentar editar categoria padrão (deve falhar)
  - Editar categoria personalizada
  - Tentar excluir categoria em uso

---

### [X] Sprint 6: Model e Views de Transações (2 semanas)

#### Tarefa 6.1: Model de Transaction
- [X] **6.1.1** - Criar Transaction model em transactions/models.py
  - Campo user (ForeignKey para User)
  - Campo account (ForeignKey para Account)
  - Campo category (ForeignKey para Category)
  - Campo transaction_type (CharField com choices)
  - Campo amount (DecimalField, max_digits=10, decimal_places=2)
  - Campo date (DateField)
  - Campo description (TextField, opcional)
  - Campos created_at e updated_at

- [X] **6.1.2** - Definir choices para transaction_type
  - INCOME = 'income' - Receita
  - EXPENSE = 'expense' - Despesa

- [X] **6.1.3** - Implementar método __str__
  - Retornar descrição resumida

- [X] **6.1.4** - Implementar Meta class
  - ordering = ['-date', '-created_at']
  - indexes para otimização

- [X] **6.1.5** - Criar migrations e aplicar
  - `python manage.py makemigrations transactions`
  - `python manage.py migrate`

#### Tarefa 6.2: Signals para Atualizar Saldo
- [X] **6.2.1** - Criar transactions/signals.py
  - Signal post_save para criar/editar transação
  - Signal pre_delete para excluir transação
  - Signal pre_save para guardar valor antigo

- [X] **6.2.2** - Implementar lógica de atualização de saldo
  - Calcular diferença ao editar
  - Adicionar valor em receitas
  - Subtrair valor em despesas
  - Atualizar Account.current_balance

- [X] **6.2.3** - Importar signals no apps.py
  - Garantir que signals sejam registrados

- [X] **6.2.4** - Testar signals manualmente
  - Criar transação e verificar saldo
  - Editar transação e verificar recálculo
  - Excluir transação e verificar ajuste

#### Tarefa 6.3: Admin de Transactions
- [X] **6.3.1** - Criar TransactionAdmin em transactions/admin.py
  - Registrar model
  - Configurar list_display
  - Configurar list_filter (tipo, categoria, data)
  - Configurar search_fields
  - Configurar date_hierarchy

- [X] **6.3.2** - Customizar formulário
  - Organizar fieldsets
  - Filtrar categorias por tipo
  - Readonly field para created_at/updated_at

#### Tarefa 6.4: Views de Transaction
- [X] **6.4.1** - Criar TransactionListView
  - Herdar de LoginRequiredMixin e ListView
  - Filtrar transações do usuário
  - Implementar paginação (20 por página)
  - Adicionar totais no context

- [X] **6.4.2** - Implementar filtros na ListView
  - Filtro por período (data inicial e final)
  - Filtro por categoria
  - Filtro por tipo (receita/despesa)
  - Filtro por conta
  - Usar query parameters GET

- [X] **6.4.3** - Criar TransactionCreateView
  - Associar ao user logado
  - Validar data (não pode ser futura)
  - Validar categoria compatível com tipo
  - Redirecionar para lista
  - Mensagem de sucesso

- [X] **6.4.4** - Criar TransactionUpdateView
  - Garantir permissão de edição
  - Recalcular saldo ao editar
  - Validações

- [X] **6.4.5** - Criar TransactionDeleteView
  - Confirmação obrigatória
  - Ajustar saldo ao excluir
  - Mensagem de sucesso

#### Tarefa 6.5: Forms de Transaction
- [X] **6.5.1** - Criar TransactionForm em transactions/forms.py
  - Campos: transaction_type, amount, date, category, account, description
  - Validação de valor positivo
  - Validação de data
  - Filtrar categorias por tipo
  
- [X] **6.5.2** - Implementar lógica de filtro de categorias
  - JavaScript para mostrar apenas categorias do tipo selecionado
  - Atualização dinâmica do select
  
- [X] **6.5.3** - Adicionar máscaras e formatação
  - Máscara para valor monetário
  - Date picker para campo data
  - Placeholder nos campos

#### Tarefa 6.6: Templates de Transaction
- [X] **6.6.1** - Criar transaction_list.html
  - Herdar de base_dashboard.html
  - Filtros no topo (formulário de filtro)
  - Tabela de transações responsiva
  - Colunas: Data, Descrição, Categoria, Conta, Valor
  - Cores diferentes para receita/despesa
  - Ações por linha (editar, excluir)
  - Paginação no rodapé
  - Cards de resumo (total receitas, despesas, saldo)
  
- [X] **6.6.2** - Criar transaction_form.html
  - Formulário estilizado
  - Campos organizados logicamente
  - Validações visuais
  - Botões de ação
  - Select de categoria dinâmico
  
- [X] **6.6.3** - Criar transaction_confirm_delete.html
  - Confirmação de exclusão
  - Mostrar detalhes da transação
  - Aviso sobre ajuste de saldo

#### Tarefa 6.7: URLs de Transaction
- [X] **6.7.1** - Configurar transactions/urls.py
  - Path para list: 'transacoes/'
  - Path para create: 'transacoes/nova/'
  - Path para update: 'transacoes/<pk>/editar/'
  - Path para delete: 'transacoes/<pk>/excluir/'

- [X] **6.7.2** - Incluir em core/urls.py
  - Include de transactions.urls
  - Namespace 'transactions'

#### Tarefa 6.8: JavaScript para Transações
- [X] **6.8.1** - Criar transactions.js
  - Filtro dinâmico de categorias por tipo
  - Máscara de valor monetário
  - Validações em tempo real
  - Confirmação de exclusão

- [X] **6.8.2** - Implementar formatação de moeda
  - Formatar valores para real brasileiro
  - Casas decimais fixas
  - Separador de milhares

#### Tarefa 6.9: Testes Manuais de Transactions
- [X] **6.9.1** - Testar criação de transação
  - Criar receita
  - Criar despesa
  - Verificar atualização de saldo
  - Testar validações
  
- [X] **6.9.2** - Testar listagem e filtros
  - Aplicar filtro por data
  - Aplicar filtro por categoria
  - Testar paginação
  - Verificar responsividade
  
- [X] **6.9.3** - Testar edição e exclusão
  - Editar valor de transação
  - Verificar recálculo de saldo
  - Excluir transação
  - Confirmar ajuste de saldo

---

### [X] Sprint 7: Dashboard e Visualizações (2 semanas)

#### Tarefa 7.1: View do Dashboard
- [X] **7.1.1** - Criar DashboardView em core
  - Herdar de LoginRequiredMixin e TemplateView
  - Calcular saldo total de todas as contas
  - Calcular totais do mês atual (receitas e despesas)
  - Buscar últimas 5 transações
  - Buscar distribuição por categorias

- [X] **7.1.2** - Implementar cálculos estatísticos
  - Total de receitas do mês
  - Total de despesas do mês
  - Diferença (economia ou déficit)
  - Comparação com mês anterior (postergar)

- [X] **7.1.3** - Preparar dados para gráficos
  - Agregação por categoria
  - Percentual de cada categoria
  - Top 5 categorias de despesas

#### Tarefa 7.2: Template do Dashboard
- [X] **7.2.1** - Criar dashboard.html
  - Herdar de base_dashboard.html
  - Grid de cards no topo
  - Seção de gráficos
  - Lista de transações recentes
  - Atalhos rápidos

- [X] **7.2.2** - Criar cards de resumo financeiro
  - Card de saldo total (destaque)
  - Card de receitas do mês
  - Card de despesas do mês
  - Card de economia/déficit
  - Gradientes e cores por tipo
  - Ícones representativos

- [X] **7.2.3** - Implementar seção de gráficos
  - Placeholder para gráfico de pizza (categorias)
  - Placeholder para gráfico de linha (evolução)
  - Usar biblioteca de charts

#### Tarefa 7.3: Gráfico de Categorias (Donut/Pizza)
- [X] **7.3.1** - Escolher biblioteca de gráficos
  - Avaliar: Chart.js, ApexCharts, ou Plotly
  - Priorizar leveza e responsividade
  - Instalar/configurar biblioteca escolhida
  
- [X] **7.3.2** - Preparar dados no backend
  - Agregação de transações por categoria
  - Filtrar por período (mês atual)
  - Calcular percentuais
  - Serializar para JSON
  
- [X] **7.3.3** - Implementar gráfico no frontend
  - Canvas/elemento para renderização
  - JavaScript para criar gráfico
  - Cores baseadas nas categorias
  - Tooltips informativos
  - Responsivo

#### Tarefa 7.4: Atalhos Rápidos no Dashboard
- [X] **7.4.1** - Criar seção de ações rápidas
  - Botão grande: Nova Transação
  - Botão: Nova Conta
  - Botão: Nova Categoria
  - Grid responsivo de botões

#### Tarefa 7.5: Responsividade do Dashboard
- [X] **7.5.1** - Otimizar layout mobile
  - Cards empilhados
  - Gráficos redimensionados
  - Tabela rolável horizontalmente

- [X] **7.5.2** - Testar em diferentes resoluções
  - Mobile (375px)
  - Tablet (768px)
  - Desktop (1280px+)
  - Ajustar espaçamentos

#### Tarefa 7.6: Configurar URL do Dashboard
- [X] **7.6.1** - Definir rota do dashboard
  - Path: 'dashboard/'
  - Redirecionar após login para dashboard

- [X] **7.6.2** - Proteger rota
  - LoginRequiredMixin
  - Redirecionar não autenticados

#### Tarefa 7.7: Testes Manuais do Dashboard
- [X] **7.7.1** - Testar cálculos
  - Verificar saldo total correto
  - Verificar totais mensais
  - Criar transações e ver atualização

- [X] **7.7.2** - Testar gráficos
  - Verificar renderização
  - Testar interatividade
  - Verificar responsividade

---

### Sprint 8: Refinamentos e Preparação para MVP (1 semana)

#### [X] Tarefa 8.1: Melhorias de UX
- [X] **8.1.1** - Implementar mensagens de feedback
  - Toast notifications para ações
  - Mensagens de sucesso/erro consistentes
  - Timeout automático
  - Posicionamento fixo
  
- [X] **8.1.2** - Adicionar confirmações de ações críticas
  - Modal de confirmação de exclusão
  - Aviso antes de perder dados não salvos
  - Loading states em botões de ação
  
- [X] **8.1.3** - Melhorar navegação
  - Breadcrumbs em páginas internas
  - Active state em menu lateral
  - Botão de voltar onde aplicável

#### [X] Tarefa 8.2: Validações Avançadas
- [X] **8.2.1** - Validações frontend
  - Validação em tempo real de formulários
  - Feedback visual de erros
  - Prevenir submit de formulários inválidos

- [X] **8.2.2** - Validações backend robustas
  - Validar todos os inputs
  - Tratar casos extremos
  - Mensagens de erro claras

- [X] **8.2.3** - Validações de negócio
  - Impedir exclusão de categoria em uso
  - Validar datas lógicas

#### [X] Tarefa 8.3: Formatações e Padronizações
- [X] **8.3.1** - Padronizar formatação de datas
  - Usar locale pt-BR
  - Formato DD/MM/YYYY
  - Formato relativo onde aplicável
  
- [X] **8.3.2** - Padronizar formatação de valores
  - R$ 1.234,56 (padrão brasileiro)
  - Cores por valor (positivo/negativo)
  - Sinal de + ou - onde aplicável
  
- [X] **8.3.3** - Padronizar textos e labels
  - Revisar todos os textos da interface
  - Garantir português correto
  - Tom consistente

#### [X] Tarefa 8.4: Acessibilidade
- [X] **8.4.1** - Adicionar atributos ARIA
  - Labels descritivos
  - Roles adequados
  - Estados de elementos

- [X] **8.4.2** - Garantir navegação por teclado
  - Tab order lógica
  - Focus visible

- [X] **8.4.3** - Contraste e legibilidade
  - Verificar contraste de cores
  - Tamanhos de fonte adequados
  - Espaçamento suficiente

#### [X] Tarefa 8.5: Tratamento de Erros
- [X] **8.5.1** - Criar páginas de erro customizadas
  - 404.html
  - 500.html
  - 403.html
  - Design consistente com tema

- [X] **8.5.2** - Implementar logging
  - Configurar logging em settings.py
  - Logs de erros
  - Logs de ações críticas

- [X] **8.5.3** - Tratamento de exceções
  - Try-catch em views críticas
  - Mensagens amigáveis ao usuário
  - Não expor detalhes técnicos

#### [X] Tarefa 8.6: Segurança
- [X] **8.6.1** - Revisar configurações de segurança
  - DEBUG = False em produção
  - SECRET_KEY segura
  - ALLOWED_HOSTS configurado
  - CSRF_COOKIE_SECURE = True
  - SESSION_COOKIE_SECURE = True
  
- [X] **8.6.2** - Proteção de rotas
  - Todas as views autenticadas protegidas
  - Verificação de ownership em updates/deletes
  - Prevenir IDOR
  
- [X] **8.6.3** - Sanitização de inputs
  - Escape de HTML em outputs
  - Limitar tamanho de inputs

#### [X] Tarefa 8.7: Performance
- [X] **8.7.1** - Otimizar queries do banco
  - Usar select_related onde necessário
  - Usar prefetch_related
  - Adicionar índices em campos filtrados
  
- [X] **8.7.2** - Minificar assets
  - Minificar CSS customizado
  - Minificar JavaScript
  - Otimizar imagens

#### [X] Tarefa 8.8: Documentação
- [X] **8.8.1** - Criar README.md completo
  - Descrição do projeto
  - Instruções de instalação
  - Como executar
  - Tecnologias usadas
  - Estrutura do projeto
  
- [X] **8.8.2** - Documentar configurações
  - Variáveis de ambiente
  - Configurações de banco
  - Configurações de produção
  
- [X] **8.8.3** - Comentar código complexo
  - Docstrings em classes e métodos
  - Comentários em lógicas complexas
  - TODO's para melhorias futuras

#### Tarefa 8.9: Testes Finais e QA
- [ ] **8.9.1** - Teste completo de fluxo de usuário
  - Cadastro > Login > Criar conta > Criar transação > Ver dashboard
  - Testar em navegadores diferentes
  - Testar em dispositivos móveis
  
- [ ] **8.9.2** - Teste de edge cases
  - Contas sem transações
  - Usuários sem contas
  - Valores extremos
  - Datas limites
  
- [ ] **8.9.3** - Teste de carga básico
  - Criar 100+ transações
  - Verificar performance do dashboard
  - Verificar paginação

#### Tarefa 8.10: Preparação para Deploy
- [ ] **8.10.1** - Configurar settings para produção
  - Criar settings/production.py
  - Variáveis de ambiente
  - Configurações de email
  
- [ ] **8.10.2** - Criar requirements.txt final
  - Listar todas as dependências
  - Especificar versões
  
- [ ] **8.10.3** - Criar guia de deploy
  - Instruções passo a passo
  - Checklist de deploy
  - Rollback plan

---

### Sprints Futuras

#### Sprint 9: Testes Automatizados
- Setup de testes (pytest, pytest-django)
- Testes unitários (models, forms, signals)
- Testes de integração (views, fluxos completos)
- Testes E2E com Selenium

#### Sprint 10: Containerização e CI/CD
- Criar Dockerfile e docker-compose.yml
- Configurar volumes e redes
- Setup de GitHub Actions ou GitLab CI
- Pipelines de testes e deploy
- Ambientes staging/production

---

## 14. Cronograma Estimado

| Sprint | Duração | Descrição | Entregáveis |
|--------|---------|-----------|-------------|
| Sprint 0 | 1 semana | Setup e Configuração | Projeto configurado, apps criadas, TailwindCSS integrado |
| Sprint 1 | 1 semana | Autenticação e Usuários | Sistema de login, cadastro e perfil funcionando |
| Sprint 2 | 1 semana | Site Público | Landing page responsiva e atrativa |
| Sprint 3 | 1 semana | Models de Contas e Categorias | Models criados, admin funcional, categorias padrão |
| Sprint 4 | 1 semana | Views e Templates de Contas | CRUD completo de contas bancárias |
| Sprint 5 | 1 semana | Views e Templates de Categorias | CRUD completo de categorias |
| Sprint 6 | 2 semanas | Transações | CRUD completo de transações com signals |
| Sprint 7 | 2 semanas | Dashboard e Visualizações | Dashboard com gráficos e estatísticas |
| Sprint 8 | 1 semana | Refinamentos e MVP | Melhorias de UX, segurança e preparação |
| **Total** | **10 semanas** | **MVP Completo** | Sistema funcional e testado |

---