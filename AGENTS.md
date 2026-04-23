# AGENTS.md — Finova

## Project Overview

**Finova** is a personal finance management web app built with Python/Django. It targets young adults and freelancers who want to track income, expenses, goals, budgets, and installments — with WhatsApp integration and AI-powered financial analysis as key differentiators.

Design identity: dark theme, black + green palette (`#0a0a0a` background, `#22c55e` accent), Inter font, minimalist.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Django 5.2+ |
| Database | SQLite3 (dev), PostgreSQL (prod future) |
| Frontend | Django Template Language, TailwindCSS 4.1+, Chart.js, Lucide Icons |
| JavaScript | ES6+ vanilla, one file per feature (`static/js/`) |
| AI | LangChain 1.0+, OpenAI gpt-4o-mini (analysis), Whisper (audio), GPT-4o Vision (images) |
| WhatsApp | Twilio webhook + LangChain agent |
| CSS build | `npm run build:css` (TailwindCSS CLI) |

**Key env vars:**
```
OPENAI_API_KEY, AI_MODEL=gpt-4o-mini, AI_MAX_TOKENS=2048, AI_TEMPERATURE=0.3
TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
```

---

## Architecture

### Django Apps

| App | Responsibility |
|-----|---------------|
| `core` | settings, main URLs, dashboard view, public views |
| `users` | email-based auth (`USERNAME_FIELD = 'email'`) |
| `profiles` | Profile model (1:1 with User), auto-created via signal |
| `accounts` | Bank accounts (checking/savings/wallet/investment), transfers |
| `categories` | Income/expense categories (default + custom, with color) |
| `transactions` | Financial transactions; signals update account balance |
| `goals` | Financial goals with deposit tracking |
| `reports` | Aggregated read-only reports (no new models) |
| `ai` | AIAnalysis model, LangChain agent, analysis service |
| `budgets` | Monthly spending limits per category *(planned)* |
| `recurrences` | Recurring income/expenses with auto-generation *(planned)* |
| `installments` | Installment plans and individual installment tracking *(planned)* |
| `whatsapp` | Twilio webhook, WhatsApp agent, notifications *(planned)* |

### Data Model (core relations)

```
User (email-based)
  ├── Profile (1:1)
  ├── Account (1:N) — bank_code, is_default, current_balance
  ├── Category (1:N) — type: income|expense, color
  ├── Transaction (1:N) → Account + Category
  ├── Goal (1:N) — target_amount, current_amount, deadline
  ├── Budget (1:N) — category + month + amount limit
  ├── Recurrence (1:N) — day_of_month, last_generated_date
  ├── InstallmentPlan (1:N) → Installment (1:N)
  ├── AIAnalysis (1:N)
  └── Notification (1:N)
```

### URL Patterns (Portuguese paths)

```
/                    → landing page
/dashboard/          → main dashboard
/accounts/           → bank accounts
/transacoes/         → transactions
/categorias/         → categories
/metas/              → goals
/relatorios/         → reports
/orcamentos/         → budgets
/recorrencias/       → recurrences
/parcelamentos/      → installments
/cartoes/            → credit cards
/whatsapp/           → WhatsApp integration
/ia/                 → AI analysis
```

### Balance Updates

Account `current_balance` is updated automatically via Django signals (`post_save`, `pre_delete`) on Transaction. Never update balance manually — go through the signal chain.

---

## Current Priorities

### Sprint 12 — Reports (IN PROGRESS)

1. Create `reports` app, register in `INSTALLED_APPS`
2. `ReportView` (GET, `LoginRequiredMixin`) with query params `?period=` and `?account=`
   - Aggregates: total income/expense, net balance, avg daily expense, biggest income/expense
   - By category (income + expense): name, color, total, %, transaction count
   - Daily evolution: income + expense per day (for Chart.js bar chart)
   - Per account: name, type, current balance, period inflows/outflows
   - Top 5 expenses and top 5 incomes
   - Use Django ORM aggregates (`Sum`, `Count`) — not Python loops
3. `reports/urls.py`: `/relatorios/` → `reports:index`
4. Register in `core/urls.py`
5. `report.html` template with filter bar, summary cards, Chart.js bar chart, category bars, account table, top transactions
6. Update sidebar: replace disabled `<span>` with `<a href="{% url 'reports:index' %}">`, remove "Em breve" badge

### Sprint 13 — Bank Binding & Transfers (NEXT)

- Add `bank_code` (choices: nubank/itau/bradesco/santander/bb/caixa/inter/c6/other) and `is_default` to `Account`
- SVG bank icons in `static/images/banks/`
- `accounts/services.py`: `debit_account()`, `get_default_account()`
- `TransferView` + `TransferForm`: debit origin, credit destination, create 2 linked transactions
- Pre-select default account in `TransactionForm` and `GoalDepositForm`
- Alert (never block) when balance would go negative

### Sprints 14–19 (PLANNED, in order)

| Sprint | Feature |
|--------|---------|
| 14 | Budgets — monthly category spending limits with alerts |
| 15 | Recurrences — fixed income/expenses with `generate_recurrences` management command |
| 16 | Installments — `InstallmentPlan` + `Installment`, auto-generated via signal |
| 17 | Credit Cards — `CreditCard`, `CardBill`, bill payment flow |
| 18 | WhatsApp — Twilio webhook, LangChain agent, audio/image handlers, proactive notifications |
| 19 | Public site — multi-page with feature pages, pricing, about |

---

## Coding Guidelines

### Style

- PEP 8, single quotes for strings
- Code (variables, functions, models, comments) in **English**
- UI text, verbose_name, error messages in **Portuguese**
- No unnecessary comments — only when the WHY is non-obvious

### Views

- Always use **Class-Based Views** with `LoginRequiredMixin`
- Use `UserPassesTestMixin` for ownership checks on update/delete
- Filter all querysets by `user=self.request.user` — never expose cross-user data
- Use `select_related` / `prefetch_related` for FK relationships

### Models

- Financial amounts: `DecimalField`
- Dates: `DateField` (not `DateTimeField`) unless timestamp is needed
- Soft delete via `is_active=False` where appropriate (e.g., recurrences)
- `unique_together` to prevent duplicates (e.g., Budget: user + category + month)

### Security

- CSRF protection on all forms
- Validate Twilio request signatures on webhook
- Ownership check on every queryset and object operation
- Never block on insufficient balance — always warn and allow

### Forms & Validation

- Validate at form level, not just view level
- Pre-select default account where applicable
- Show real-time balance/preview feedback via vanilla JS

### JavaScript

- One file per feature in `static/js/`
- Vanilla JS only — no jQuery, no frameworks
- Use `json_script` Django tag to pass data to JS (XSS prevention)

### Design System

| Token | Value |
|-------|-------|
| Background | `#0a0a0a` |
| Card surface | `#111111` |
| Elevated (modals) | `#1a1a1a` |
| Borders | `#262626` |
| Accent green | `#22c55e` |
| Accent hover | `#16a34a` |
| Text primary | `#f5f5f5` |
| Text secondary | `#a3a3a3` |

- Font: Inter (300 body, 600 headings), financial numbers in `font-mono`
- Progress bars: green < 70%, yellow 70–99%, red ≥ 100%
- Hover transitions: 150ms
- Toast notifications: fixed bottom-right, auto-dismiss

### Commands

```bash
# Run dev server
python manage.py runserver

# Migrations
python manage.py makemigrations <app>
python manage.py migrate

# Build CSS (required after template changes)
npm run build:css
```

---

## Important Notes

- **Auth is email-based**: `USERNAME_FIELD = 'email'`. Never reference `username`.
- **Balance is signal-driven**: Account balance updates fire automatically on Transaction save/delete. Do not recompute manually.
- **Default account**: only one `is_default=True` per user. Enforce in `Account.save()` by clearing others.
- **Budget/recurrence months**: store as first day of month (`2026-04-01`), use `unique_together` to prevent duplicates.
- **Installments**: generated automatically via `post_save` signal on `InstallmentPlan`. Do not create them manually in views.
- **WhatsApp confirmation flow**: use Django cache (5-minute TTL) to hold pending actions before user confirms.
- **AI analysis**: always handle missing `OPENAI_API_KEY` gracefully — show a user-friendly message, never raise an unhandled exception.
- **Reports app**: no new models — read-only aggregation over existing data using Django ORM.

---

## Execution Style

- Read existing model/view code before writing anything — inspect the relevant app file first.
- Implement exactly what the task specifies. Do not add extra fields, views, or abstractions beyond scope.
- After creating a new app: register it in `INSTALLED_APPS` and add its URL include to `core/urls.py`.
- After any model change: run `makemigrations <app>` and `migrate`.
- After any template change: run `npm run build:css`.
- Never skip `LoginRequiredMixin` or user-scoped queryset filtering.
- Use Django messages framework for user feedback (success, warning, error).
- Empty states in templates must be elegant — never show a blank page.
- Match the design system exactly: colors, spacing, typography tokens defined above.
