# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (uses email, not username)
python manage.py createsuperuser

# Django shell
python manage.py shell

# TailwindCSS (requires Node.js)
npm run build:css          # Build CSS once
npm run watch:css          # Watch for changes and rebuild
npm run build:css:minify   # Build minified CSS for production
```

## Architecture

**Stack:** Python 3.11+, Django 5.2+, SQLite3, TailwindCSS, Django Template Language

**Django Apps:**
- `users` - Custom user model with email-based authentication (USERNAME_FIELD = 'email')
- `profiles` - User profile data (1:1 with User)
- `accounts` - Bank accounts (checking, savings, wallet, investments)
- `categories` - Transaction categories with income/expense types
- `transactions` - Financial transactions linked to accounts and categories

**Data Flow:**
```
User → Profile (1:1)
User → Account (1:N) → Transaction (1:N)
User → Category (1:N) → Transaction (1:N)
```

**URL Pattern:** Portuguese paths (`/transacoes/`, `/categorias/`, `/accounts/`)

## Project Structure

```
finanpy/
├── .claude/            # Claude Code configs + agents
├── core/               # Django project settings and URLs
├── accounts/           # Django app - bank accounts
├── categories/         # Django app - transaction categories
├── profiles/           # Django app - user profiles
├── transactions/       # Django app - financial transactions
├── users/              # Django app - custom user model
├── templates/          # Django templates (DTL + TailwindCSS)
├── static/             # Static files source
├── docs/               # Project documentation
├── tests/              # Test files (e2e, edge_cases, load, reports)
├── manage.py
├── requirements.txt
├── PRD.md              # Product requirements
└── TASKS.md            # Sprint tracking
```

## Code Style

- **PEP 8** with single quotes for strings
- **Code in English**, UI text in Portuguese
- **Class-Based Views** with `LoginRequiredMixin`
- Always filter querysets by `user=self.request.user`
- Use `select_related`/`prefetch_related` for FK relationships

## Key Files

- `core/settings.py` - Django configuration
- `core/urls.py` - Main URL routing
- `PRD.md` - Full product requirements
- `docs/` - Project documentation
