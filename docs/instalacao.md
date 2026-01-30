# Instalacao

## Requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

## Configuracao do Ambiente

### 1. Clonar o repositorio

```bash
git clone <url-do-repositorio>
cd finanpy
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

### 3. Ativar ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Aplicar migracoes

```bash
python manage.py migrate
```

### 6. Executar servidor de desenvolvimento

```bash
python manage.py runserver
```

O servidor estara disponivel em `http://127.0.0.1:8000/`

## Dependencias

As dependencias do projeto estao listadas em `requirements.txt`:

- Django 5.2.10
- asgiref 3.11.0
- sqlparse 0.5.5
- tzdata 2025.3

## Comandos Uteis

| Comando | Descricao |
|---------|-----------|
| `python manage.py runserver` | Inicia servidor de desenvolvimento |
| `python manage.py migrate` | Aplica migracoes pendentes |
| `python manage.py makemigrations` | Cria novas migracoes |
| `python manage.py createsuperuser` | Cria usuario administrador |
| `python manage.py shell` | Abre shell interativo do Django |
