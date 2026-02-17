# Guia de Deploy - FinanPy

Este guia cobre o processo completo de deploy do FinanPy em um servidor Linux com PostgreSQL, Gunicorn e Nginx.

---

## Pre-requisitos

- Servidor Linux (Ubuntu 22.04 LTS recomendado)
- Python 3.11+
- PostgreSQL 14+
- Nginx
- Acesso root ou usuario com sudo
- Dominio apontando para o IP do servidor (para SSL)

---

## 1. Preparacao do Servidor

### 1.1 Atualizacao do sistema e dependencias

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    build-essential \
    libpq-dev
```

### 1.2 Criacao do usuario do sistema

Crie um usuario dedicado para rodar a aplicacao. Nunca rode a aplicacao como root.

```bash
sudo useradd --system --create-home --shell /bin/bash finanpy
```

---

## 2. Configuracao do Projeto

### 2.1 Clone do repositorio

```bash
sudo mkdir -p /var/www/finanpy
sudo chown finanpy:finanpy /var/www/finanpy

sudo -u finanpy git clone https://github.com/seu-usuario/finanpy.git /var/www/finanpy
```

### 2.2 Criacao do ambiente virtual

```bash
sudo -u finanpy python3.11 -m venv /var/www/finanpy/venv
```

### 2.3 Instalacao das dependencias

```bash
sudo -u finanpy /var/www/finanpy/venv/bin/pip install --upgrade pip
sudo -u finanpy /var/www/finanpy/venv/bin/pip install -r /var/www/finanpy/requirements.txt
```

### 2.4 Configuracao das variaveis de ambiente

Crie o arquivo `.env` no diretorio raiz do projeto. **Este arquivo nunca deve ser versionado no git.**

```bash
sudo -u finanpy nano /var/www/finanpy/.env
```

Conteudo do arquivo `.env`:

```env
# Seguranca
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria-aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br

# Banco de dados
DATABASE_URL=postgres://finanpy_user:senha_segura@localhost:5432/finanpy_db

# E-mail (SMTP)
EMAIL_HOST=smtp.seuprovedor.com.br
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@seudominio.com.br
EMAIL_HOST_PASSWORD=senha-do-email
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=FinanPy <noreply@seudominio.com.br>

# Administradores (recebem erros por e-mail)
# Formato: Nome,email|Nome2,email2
ADMINS=Administrador,admin@seudominio.com.br
```

Gere uma SECRET_KEY segura com o comando abaixo:

```bash
/var/www/finanpy/venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Proteja as permissoes do arquivo `.env`:

```bash
sudo chmod 600 /var/www/finanpy/.env
sudo chown finanpy:finanpy /var/www/finanpy/.env
```

---

## 3. Banco de Dados

### 3.1 Criacao do banco e usuario PostgreSQL

```bash
sudo -u postgres psql
```

Dentro do shell do PostgreSQL:

```sql
CREATE DATABASE finanpy_db;
CREATE USER finanpy_user WITH PASSWORD 'senha_segura';
ALTER ROLE finanpy_user SET client_encoding TO 'utf8';
ALTER ROLE finanpy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE finanpy_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE finanpy_db TO finanpy_user;
\q
```

### 3.2 Execucao das migracoes

```bash
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py migrate --no-input
"
```

### 3.3 Criacao do superusuario

```bash
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py createsuperuser
"
```

### 3.4 Carga das categorias padrao

```bash
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py create_default_categories
"
```

---

## 4. Arquivos Estaticos

O FinanPy usa WhiteNoise para servir os arquivos estaticos diretamente pelo Django, sem necessidade de configuracao adicional no Nginx para isso. O CSS do TailwindCSS ja esta pre-compilado no repositorio.

### 4.1 Coleta dos arquivos estaticos

```bash
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py collectstatic --no-input
"
```

Os arquivos serao coletados em `/var/www/finanpy/staticfiles/` e servidos automaticamente pelo WhiteNoise via middleware do Django.

---

## 5. Gunicorn

### 5.1 Teste manual do Gunicorn

Antes de configurar o servico, valide que o Gunicorn funciona:

```bash
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/gunicorn \
        --workers 3 \
        --bind 127.0.0.1:8000 \
        core.wsgi:application
"
```

Pressione `Ctrl+C` para encerrar o teste.

### 5.2 Calculo do numero de workers

A formula recomendada para o numero de workers e:

```
workers = (2 x numero_de_cpus) + 1
```

Verifique o numero de CPUs do servidor:

```bash
nproc
```

### 5.3 Criacao do servico systemd

Crie o arquivo de servico:

```bash
sudo nano /etc/systemd/system/finanpy.service
```

Conteudo do arquivo:

```ini
[Unit]
Description=Gunicorn - FinanPy Django Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=finanpy
Group=finanpy
WorkingDirectory=/var/www/finanpy
EnvironmentFile=/var/www/finanpy/.env
Environment="DJANGO_SETTINGS_MODULE=core.settings_production"

ExecStart=/var/www/finanpy/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --timeout 60 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/www/finanpy/logs/gunicorn_access.log \
    --error-logfile /var/www/finanpy/logs/gunicorn_error.log \
    --log-level info \
    core.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5.4 Criacao do diretorio de logs

```bash
sudo -u finanpy mkdir -p /var/www/finanpy/logs
```

### 5.5 Habilitacao e inicializacao do servico

```bash
sudo systemctl daemon-reload
sudo systemctl enable finanpy
sudo systemctl start finanpy
sudo systemctl status finanpy
```

---

## 6. Nginx

### 6.1 Configuracao do bloco de servidor

Crie o arquivo de configuracao do Nginx:

```bash
sudo nano /etc/nginx/sites-available/finanpy
```

Conteudo do arquivo (substitua `seudominio.com.br` pelo seu dominio real):

```nginx
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;

    # Redireciona todo HTTP para HTTPS (ativado apos configurar SSL)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name seudominio.com.br www.seudominio.com.br;

    # Certificados SSL (preenchidos automaticamente pelo certbot)
    ssl_certificate /etc/letsencrypt/live/seudominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log /var/log/nginx/finanpy_access.log;
    error_log /var/log/nginx/finanpy_error.log;

    # Limite de tamanho de upload
    client_max_body_size 10M;

    # Headers de seguranca
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Proxy reverso para o Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Arquivos de midia enviados por usuarios
    location /media/ {
        alias /var/www/finanpy/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6.2 Ativacao do site

```bash
sudo ln -s /etc/nginx/sites-available/finanpy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6.3 SSL com Let's Encrypt (Certbot)

Obtenha o certificado SSL gratuito. O Certbot preenchera automaticamente os campos de SSL no arquivo de configuracao do Nginx.

Antes de rodar o certbot, configure temporariamente o Nginx para servir apenas na porta 80 (sem o bloco SSL e sem o redirect), para que o certbot consiga validar o dominio. Apos obter o certificado, restaure a configuracao completa.

```bash
# Obtencao do certificado
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br

# Teste de renovacao automatica
sudo certbot renew --dry-run
```

O Certbot configura automaticamente a renovacao via cron ou systemd timer. Verifique:

```bash
sudo systemctl status certbot.timer
```

---

## 7. Checklist de Deploy

Antes de considerar o deploy concluido, valide cada item:

### Servidor e Ambiente
- [ ] Sistema operacional atualizado
- [ ] Python 3.11+ instalado
- [ ] Usuario `finanpy` criado sem privilegios de root
- [ ] Repositorio clonado em `/var/www/finanpy`
- [ ] Ambiente virtual criado e dependencias instaladas

### Configuracao
- [ ] Arquivo `.env` criado com todas as variaveis obrigatorias
- [ ] `SECRET_KEY` gerada com `get_random_secret_key()` (minimo 50 caracteres)
- [ ] `DEBUG=False` no `.env`
- [ ] `ALLOWED_HOSTS` contendo o dominio de producao
- [ ] `DATABASE_URL` apontando para o PostgreSQL local
- [ ] Permissoes do `.env` definidas como `600`

### Banco de Dados
- [ ] Banco `finanpy_db` criado no PostgreSQL
- [ ] Usuario `finanpy_user` criado com senha segura
- [ ] Migracoes executadas sem erros (`migrate`)
- [ ] Superusuario criado
- [ ] Categorias padrao carregadas (`create_default_categories`)

### Arquivos Estaticos
- [ ] `collectstatic` executado sem erros
- [ ] Diretorio `staticfiles/` populado

### Gunicorn
- [ ] Teste manual do Gunicorn funcionou
- [ ] Servico `finanpy.service` criado em `/etc/systemd/system/`
- [ ] Servico habilitado (`systemctl enable finanpy`)
- [ ] Servico rodando (`systemctl status finanpy` mostra `active (running)`)

### Nginx
- [ ] Configuracao criada em `/etc/nginx/sites-available/finanpy`
- [ ] Link simbolico criado em `sites-enabled`
- [ ] `nginx -t` retorna `syntax is ok`
- [ ] Nginx recarregado apos configuracao

### SSL e Seguranca
- [ ] Certificado SSL emitido pelo Certbot
- [ ] Acesso via HTTPS funcionando
- [ ] Redirect HTTP -> HTTPS ativo
- [ ] Headers de seguranca presentes na resposta HTTP

### Verificacao Final
- [ ] Login com superusuario funciona
- [ ] Criacao de conta bancaria funciona
- [ ] Criacao de transacao funciona
- [ ] Logs sem erros criticos (`/var/www/finanpy/logs/errors.log`)

---

## 8. Plano de Rollback

### 8.1 Quando executar o rollback

Execute o rollback quando:
- A aplicacao retorna erro 500 apos o deploy
- As migracoes falharam parcialmente
- O comportamento critico da aplicacao foi quebrado

### 8.2 Rollback do codigo

```bash
# Verificar o historico de commits
sudo -u finanpy git -C /var/www/finanpy log --oneline -10

# Voltar para o commit anterior (substitua HASH pelo hash do commit estavel)
sudo -u finanpy git -C /var/www/finanpy checkout HASH

# Reinstalar dependencias caso necessario
sudo -u finanpy /var/www/finanpy/venv/bin/pip install -r /var/www/finanpy/requirements.txt

# Reiniciar a aplicacao
sudo systemctl restart finanpy
```

### 8.3 Rollback do banco de dados

**Atencao:** Sempre faca backup antes de migrar em producao.

```bash
# Backup antes de qualquer migracao (execute isso ANTES do deploy)
sudo -u postgres pg_dump finanpy_db > /var/backups/finanpy_db_$(date +%Y%m%d_%H%M%S).sql

# Para desfazer a ultima migracao de um app especifico
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py migrate nome_do_app MIGRACAO_ANTERIOR
"

# Para restaurar um backup completo
sudo -u postgres psql finanpy_db < /var/backups/finanpy_db_YYYYMMDD_HHMMSS.sql
```

Verifique o nome da migracao anterior com:

```bash
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py showmigrations
"
```

### 8.4 Reinicializacao dos servicos apos rollback

```bash
sudo systemctl restart finanpy
sudo systemctl reload nginx
sudo systemctl status finanpy nginx
```

---

## 9. Manutencao

### 9.1 Monitoramento de logs

```bash
# Log geral da aplicacao
tail -f /var/www/finanpy/logs/general.log

# Log de erros da aplicacao
tail -f /var/www/finanpy/logs/errors.log

# Log de acesso do Gunicorn
tail -f /var/www/finanpy/logs/gunicorn_access.log

# Log de erros do Gunicorn
tail -f /var/www/finanpy/logs/gunicorn_error.log

# Log de acesso do Nginx
sudo tail -f /var/log/nginx/finanpy_access.log

# Log de erros do Nginx
sudo tail -f /var/log/nginx/finanpy_error.log

# Status dos servicos
sudo systemctl status finanpy nginx postgresql
```

### 9.2 Backup do banco de dados

Crie um script de backup automatico:

```bash
sudo nano /usr/local/bin/finanpy_backup.sh
```

Conteudo do script:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/finanpy"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/finanpy_db_$DATE.sql.gz"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Gera o backup comprimido
sudo -u postgres pg_dump finanpy_db | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[$DATE] Backup realizado com sucesso: $BACKUP_FILE"
else
    echo "[$DATE] ERRO ao realizar backup" >&2
    exit 1
fi

# Remove backups mais antigos que RETENTION_DAYS dias
find "$BACKUP_DIR" -name "finanpy_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[$DATE] Backups antigos removidos (retencao: $RETENTION_DAYS dias)"
```

Torne o script executavel e configure o cron:

```bash
sudo chmod +x /usr/local/bin/finanpy_backup.sh

# Abre o crontab do root
sudo crontab -e
```

Adicione a linha para executar o backup todos os dias as 02:00:

```cron
0 2 * * * /usr/local/bin/finanpy_backup.sh >> /var/log/finanpy_backup.log 2>&1
```

### 9.3 Atualizacao da aplicacao

Procedimento padrao para atualizar o FinanPy em producao:

```bash
# 1. Faca backup do banco antes de qualquer atualizacao
sudo /usr/local/bin/finanpy_backup.sh

# 2. Busque as atualizacoes do repositorio
sudo -u finanpy git -C /var/www/finanpy pull origin main

# 3. Atualize as dependencias caso o requirements.txt tenha mudado
sudo -u finanpy /var/www/finanpy/venv/bin/pip install -r /var/www/finanpy/requirements.txt

# 4. Execute as migracoes
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py migrate --no-input
"

# 5. Colete os arquivos estaticos
sudo -u finanpy bash -c "
    cd /var/www/finanpy &&
    DJANGO_SETTINGS_MODULE=core.settings_production \
    /var/www/finanpy/venv/bin/python manage.py collectstatic --no-input
"

# 6. Reinicie o Gunicorn
sudo systemctl restart finanpy

# 7. Verifique o status
sudo systemctl status finanpy
```

### 9.4 Verificacao de saude da aplicacao

```bash
# Verifica se o Gunicorn esta respondendo localmente
curl -I http://127.0.0.1:8000

# Verifica se o Nginx esta respondendo externamente
curl -I https://seudominio.com.br

# Verifica uso de disco
df -h /var/www/finanpy

# Verifica uso de memoria pelo Gunicorn
ps aux | grep gunicorn

# Verifica conexoes abertas com o banco
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'finanpy_db';"
```
