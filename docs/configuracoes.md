# Configuracoes

## Variaveis de Ambiente

O projeto usa o pacote `python-dotenv` para carregar variaveis de ambiente do arquivo `.env` na raiz do projeto. Copie `.env.example` para `.env` antes de executar o projeto.

### Variaveis Disponiveis

| Variavel | Obrigatoria | Descricao | Valor Padrao |
|----------|:-----------:|-----------|:------------:|
| `SECRET_KEY` | Em producao | Chave secreta do Django para criptografia | Auto-gerada em debug |
| `DEBUG` | Nao | Ativa modo debug (`True`/`False`) | `False` |
| `ALLOWED_HOSTS` | Em producao | Hosts permitidos, separados por virgula | vazio |

### Gerando SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Exemplo de .env

```env
SECRET_KEY='sua-chave-secreta-aqui'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Banco de Dados

O projeto usa SQLite3 por padrao. O arquivo `db.sqlite3` e criado automaticamente na raiz do projeto.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Para usar PostgreSQL em producao, instale `psycopg2-binary` e configure:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finanpy',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Autenticacao

O sistema usa email como identificador principal (sem username):

```python
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
```

A sessao expira em 8 horas (`SESSION_COOKIE_AGE = 28800`).

## Localizacao

```python
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
```

## Arquivos Estaticos

```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'    # Destino do collectstatic
STATICFILES_DIRS = [BASE_DIR / 'static']  # Fontes dos arquivos
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Para coletar arquivos estaticos em producao:

```bash
python manage.py collectstatic
```

## Seguranca

### Sempre ativas

| Configuracao | Valor | Descricao |
|-------------|-------|-----------|
| `SECURE_BROWSER_XSS_FILTER` | `True` | Filtro XSS do navegador |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Previne MIME type sniffing |
| `X_FRAME_OPTIONS` | `DENY` | Previne clickjacking |
| `SESSION_COOKIE_HTTPONLY` | `True` | Cookie de sessao inacessivel via JS |
| `CSRF_COOKIE_HTTPONLY` | `True` | Cookie CSRF inacessivel via JS |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Protecao contra CSRF em cookies |

### Apenas em producao (DEBUG=False)

| Configuracao | Valor | Descricao |
|-------------|-------|-----------|
| `CSRF_COOKIE_SECURE` | `True` | Cookie CSRF apenas via HTTPS |
| `SESSION_COOKIE_SECURE` | `True` | Cookie de sessao apenas via HTTPS |
| `SECURE_SSL_REDIRECT` | `True` | Redireciona HTTP para HTTPS |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS habilitado por 1 ano |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | HSTS inclui subdominios |
| `SECURE_HSTS_PRELOAD` | `True` | Permite preload de HSTS |

## Logging

Os logs sao salvos na pasta `logs/` (criada automaticamente):

| Arquivo | Conteudo | Nivel |
|---------|----------|-------|
| `logs/errors.log` | Erros de todas as apps | ERROR |
| `logs/general.log` | Logs gerais das apps do projeto | INFO |

Apps monitoradas: `accounts`, `transactions`, `categories`, `users`.

## Configuracao de Producao

Checklist para deploy:

1. Defina `DEBUG=False`
2. Configure `SECRET_KEY` com valor seguro
3. Configure `ALLOWED_HOSTS` com seu dominio
4. Configure HTTPS no servidor web
5. Execute `npm run build:minify` para minificar assets
6. Execute `python manage.py collectstatic`
7. Configure um banco PostgreSQL (recomendado)
8. Configure um servidor WSGI (Gunicorn)
9. Configure um servidor web reverso (Nginx)
10. Verifique: `python manage.py check --deploy`
