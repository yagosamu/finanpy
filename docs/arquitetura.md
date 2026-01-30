# Arquitetura

## Stack Tecnologica

### Backend

| Tecnologia | Versao | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem principal |
| Django | 5.2+ | Framework web |
| SQLite3 | - | Banco de dados |

### Frontend

| Tecnologia | Uso |
|------------|-----|
| Django Template Language | Templates HTML |
| TailwindCSS | Estilizacao |
| JavaScript vanilla | Interacoes minimas |

## Banco de Dados

O projeto usa SQLite3 para desenvolvimento. O arquivo `db.sqlite3` esta na raiz do projeto.

### Modelo de Dados

```
User (Django built-in + customizado)
  │
  ├── Profile (1:1)
  │     - first_name
  │     - last_name
  │     - phone
  │     - birth_date
  │
  ├── Account (1:N)
  │     - name
  │     - account_type
  │     - bank
  │     - initial_balance
  │     - current_balance
  │
  ├── Category (1:N)
  │     - name
  │     - category_type (income/expense)
  │     - color
  │     - is_default
  │
  └── Transaction (1:N)
        - account (FK)
        - category (FK)
        - transaction_type
        - amount
        - date
        - description
```

## Autenticacao

O sistema usa autenticacao baseada em email (nao username). Configuracoes necessarias:

- `AUTH_USER_MODEL` apontando para modelo customizado
- `USERNAME_FIELD = 'email'` no modelo de usuario

## Configuracoes Django

Principais configuracoes em `core/settings.py`:

```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps do projeto
    'accounts',
    'categories',
    'profiles',
    'transactions',
    'users',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Padrao de URLs

Estrutura de URLs por app:

| App | Prefixo | Exemplo |
|-----|---------|---------|
| accounts | `/accounts/` | `/accounts/nova/` |
| categories | `/categorias/` | `/categorias/nova/` |
| transactions | `/transacoes/` | `/transacoes/nova/` |
| profiles | `/perfil/` | `/perfil/editar/` |
| users | `/` | `/login/`, `/cadastro/` |

## Principios

1. **Simplicidade** - Evitar over-engineering
2. **Separacao de responsabilidades** - Cada app com funcao especifica
3. **Seguranca** - Validacoes em frontend e backend, protecao CSRF
