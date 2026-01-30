# Estrutura do Projeto

## Visao Geral

```
finanpy/
├── core/                   # Configuracao principal do Django
│   ├── __init__.py
│   ├── settings.py         # Configuracoes do projeto
│   ├── urls.py             # Roteamento principal
│   ├── wsgi.py             # Entrada WSGI
│   └── asgi.py             # Entrada ASGI
├── users/                  # App de usuarios
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── profiles/               # App de perfis
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── accounts/               # App de contas bancarias
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── categories/             # App de categorias
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── transactions/           # App de transacoes
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── manage.py               # Script de gerenciamento Django
├── db.sqlite3              # Banco de dados SQLite
├── requirements.txt        # Dependencias Python
├── PRD.md                  # Documento de requisitos
└── docs/                   # Documentacao
```

## Apps Django

### users

Responsavel pelo gerenciamento de usuarios e autenticacao. O sistema usa email como identificador principal (nao username).

### profiles

Armazena informacoes complementares do usuario como nome, telefone e data de nascimento.

### accounts

Gerencia contas bancarias do usuario (conta corrente, poupanca, carteira, investimentos).

### categories

Gerencia categorias para classificacao de transacoes. Inclui categorias padrao e personalizadas.

### transactions

Gerencia receitas e despesas do usuario, vinculadas a contas e categorias.

## Diagrama de Dependencias

```
core
  └── users
        └── profiles
        └── accounts
        └── categories
              └── transactions
                    ├── accounts
                    └── categories
```

## Arquivos de Configuracao

| Arquivo | Descricao |
|---------|-----------|
| `core/settings.py` | Configuracoes do Django |
| `core/urls.py` | URLs principais do projeto |
| `requirements.txt` | Dependencias Python |
| `manage.py` | Comandos de gerenciamento |
