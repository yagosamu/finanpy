# Aurum Finance

![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/django-5.2-092E20?style=flat-square&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-4.1-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Status](https://img.shields.io/badge/status-active-22c55e?style=flat-square)

Personal finance management platform built with Django. Combining a sophisticated dark interface, AI-powered financial analysis, and WhatsApp integration to make expense tracking effortless.

---

## Overview

Aurum Finance is a full-stack web application that gives users complete visibility and control over their personal finances. Beyond standard income and expense tracking, it features an AI agent that analyzes spending patterns and delivers personalized insights, plus a WhatsApp integration that allows users to log transactions by sending a text message, voice note, or photo of a receipt, without opening the app.

---

## Features

### Financial Management

- Multi-account support with integration for Brazil's 8 largest banks
- Credit card management with billing cycle control, limit tracking and invoice payment
- Transactions with automatic account debit, balance alerts and credit card linking
- Account-to-account transfers with full transaction history
- Installment plans with automatic payment schedule generation
- Recurring transactions, fixed income and expenses launched automatically each month
- Financial goals with progress tracking and account-linked deposits
- Category budgets with real-time usage and overspend alerts

### Intelligence & Analytics

- AI financial analysis powered by LangChain and OpenAI GPT-4o mini
- Personalized spending insights and recommendations delivered in Portuguese
- WhatsApp integration, log transactions via text, voice message or receipt photo
- Monthly evolution dashboard with interactive Chart.js line graphs
- Detailed reports filterable by period, account and category
- Automatic weekly financial summary sent via WhatsApp every Monday

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 5.2 |
| Frontend | TailwindCSS 4.1, JavaScript ES6+, Chart.js |
| AI | LangChain, OpenAI GPT-4o mini, Whisper API |
| WhatsApp | Twilio |
| Icons | Lucide Icons |
| Database | SQLite (development) / PostgreSQL (production) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key _(optional — required for AI analysis and WhatsApp voice/image processing)_
- Twilio account _(optional — required for WhatsApp integration)_

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/aurum-finance.git
cd aurum-finance

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies and build CSS
npm install
npm run build:css

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Create default categories
python manage.py create_default_categories

# Seed sample data (optional)
python manage.py seed_data

# Start the development server
python manage.py runserver
```

---

## Screenshots

> Screenshots coming soon.

---

## Roadmap

- [ ] WhatsApp integration — text, voice and receipt photo support
- [ ] Public site restructure with dedicated feature pages
- [ ] Automated test suite
- [ ] Docker setup and CI/CD pipeline
