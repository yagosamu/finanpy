# Finanpy

Sistema de gestao de financas pessoais desenvolvido em Python/Django, focado em simplicidade e eficiencia. Interface web moderna com tema escuro e design responsivo.

## Funcionalidades

- **Autenticacao por email** - Cadastro e login sem username
- **Gestao de contas** - Conta corrente, poupanca, carteira e investimentos
- **Transacoes** - Controle de receitas e despesas com categorizacao
- **Categorias** - Categorias padrao + personalizadas com cores
- **Dashboard** - Resumo financeiro com graficos interativos
- **Responsivo** - Funciona em desktop, tablet e mobile

## Tecnologias

| Tecnologia | Versao | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem principal |
| Django | 5.2+ | Framework web |
| SQLite3 | - | Banco de dados |
| TailwindCSS | 4.1+ | Estilizacao |
| JavaScript | ES6+ | Interacoes no frontend |

## Estrutura do Projeto

```
finanpy/
├── core/                    # Configuracao principal do Django
│   ├── settings.py          # Configuracoes do projeto
│   ├── urls.py              # Roteamento principal
│   └── views.py             # Dashboard e handlers de erro
├── users/                   # Autenticacao (email-based)
│   ├── models.py            # CustomUser model
│   ├── views.py             # SignUp, Login, Logout
│   └── forms.py             # Formularios de autenticacao
├── profiles/                # Perfil do usuario (1:1 com User)
│   ├── models.py            # Profile model
│   ├── signals.py           # Auto-criacao de perfil
│   └── views.py             # Visualizacao e edicao
├── accounts/                # Contas bancarias
│   ├── models.py            # Account model
│   ├── views.py             # CRUD de contas
│   ├── forms.py             # Formularios com validacao
│   └── templatetags/        # Filtros de formatacao (moeda, data)
├── categories/              # Categorias de transacao
│   ├── models.py            # Category model
│   ├── views.py             # CRUD de categorias
│   └── management/commands/ # Comando para categorias padrao
├── transactions/            # Transacoes financeiras
│   ├── models.py            # Transaction model
│   ├── views.py             # CRUD com filtros
│   ├── forms.py             # Formulario com filtro dinamico
│   └── signals.py           # Atualizacao automatica de saldo
├── templates/               # Templates Django
│   ├── base.html            # Base do site publico
│   ├── base_dashboard.html  # Base do dashboard (sidebar + navbar)
│   ├── dashboard.html       # Pagina principal com graficos
│   └── components/          # Componentes reutilizaveis
├── static/                  # Arquivos estaticos
│   ├── css/                 # TailwindCSS + estilos customizados
│   ├── js/                  # JavaScript modular
│   └── images/              # Imagens e icones
├── docs/                    # Documentacao detalhada
├── requirements.txt         # Dependencias Python
├── package.json             # Dependencias Node (TailwindCSS)
└── manage.py                # Script de gerenciamento Django
```

## Instalacao

### Requisitos

- Python 3.11 ou superior
- Node.js 18+ e npm (para TailwindCSS)
- Git

### 1. Clonar o repositorio

```bash
git clone https://github.com/yagosamu/finanpy.git
cd finanpy
```

### 2. Criar e ativar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
npm install
```

### 4. Configurar variaveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configuracoes
# Gerar SECRET_KEY:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Aplicar migracoes e criar dados iniciais

```bash
python manage.py migrate
python manage.py create_default_categories
```

### 6. Criar usuario administrador

```bash
python manage.py createsuperuser
# Usa email como identificador (nao username)
```

### 7. Compilar CSS

```bash
npm run build:css
```

### 8. Executar servidor

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`

## Comandos Uteis

| Comando | Descricao |
|---------|-----------|
| `python manage.py runserver` | Inicia servidor de desenvolvimento |
| `python manage.py migrate` | Aplica migracoes pendentes |
| `python manage.py makemigrations` | Cria novas migracoes |
| `python manage.py createsuperuser` | Cria usuario administrador |
| `python manage.py create_default_categories` | Cria categorias padrao |
| `python manage.py shell` | Abre shell interativo |
| `npm run build:css` | Compila TailwindCSS |
| `npm run watch:css` | Compila CSS em modo watch |
| `npm run build:minify` | Build de producao (CSS + JS minificados) |

## Modelo de Dados

```
User (email-based)
  ├── Profile (1:1) - Nome, telefone, data de nascimento
  ├── Account (1:N) - Contas bancarias com saldo calculado
  ├── Category (1:N) - Categorias personalizadas + padrao
  └── Transaction (1:N) - Receitas e despesas
        ├── → Account (FK)
        └── → Category (FK)
```

## Rotas Principais

| Rota | Descricao |
|------|-----------|
| `/` | Landing page |
| `/dashboard/` | Dashboard com resumo financeiro |
| `/usuarios/cadastro/` | Cadastro de usuario |
| `/usuarios/login/` | Login |
| `/perfil/` | Perfil do usuario |
| `/accounts/` | Gestao de contas bancarias |
| `/categorias/` | Gestao de categorias |
| `/transacoes/` | Gestao de transacoes |
| `/admin/` | Painel administrativo Django |

## Variaveis de Ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | Obrigatoria em producao |
| `DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por virgula) | vazio |

Veja `.env.example` para um modelo de configuracao.

## Producao

Para deploy em producao:

1. Defina `DEBUG=False` no `.env`
2. Configure uma `SECRET_KEY` segura
3. Configure `ALLOWED_HOSTS` com seu dominio
4. Compile assets minificados: `npm run build:minify`
5. Colete arquivos estaticos: `python manage.py collectstatic`
6. Configure HTTPS (obrigatorio - HSTS habilitado automaticamente)
7. Considere usar PostgreSQL no lugar de SQLite

## Documentacao

Documentacao detalhada disponivel na pasta `docs/`:

- [Instalacao](docs/instalacao.md) - Guia completo de instalacao
- [Estrutura](docs/estrutura.md) - Estrutura do projeto
- [Arquitetura](docs/arquitetura.md) - Decisoes arquiteturais
- [Codigo](docs/codigo.md) - Convencoes de codigo
- [Design System](docs/design-system.md) - Sistema de design

## Licenca

ISC
