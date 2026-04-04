# Agentes de Desenvolvimento

Agentes especializados para o desenvolvimento do Finanpy.

## Agentes Disponiveis

| Agente | Arquivo | Uso |
|--------|---------|-----|
| Backend Django | [django-backend-dev.md](django-backend-dev.md) | Models, views, forms, URLs, signals, migrations |
| Frontend Tailwind | [frontend-tailwind-django.md](frontend-tailwind-django.md) | Templates DTL, TailwindCSS, componentes UI |
| QA Tester | [qa-tester-playwright.md](qa-tester-playwright.md) | Testes E2E, validacao de UI, verificacao de fluxos |
| AI Integration Expert | [ai_integration_expert.md](ai_integration_expert.md) | Criacao e integracao de agentes de IA com LangChain 1.0 |

## Quando Usar Cada Agente

### Backend Django

Use para:
- Criar ou modificar models
- Implementar views (CBVs)
- Criar forms e validacoes
- Configurar URLs
- Implementar signals
- Criar management commands
- Configurar admin

### Frontend Tailwind

Use para:
- Criar templates HTML
- Estilizar com TailwindCSS
- Implementar componentes reutilizaveis
- Criar layouts responsivos
- Adicionar interacoes JavaScript

### QA Tester

Use para:
- Testar fluxos completos do usuario
- Validar design e responsividade
- Verificar formularios e validacoes
- Testar autenticacao e autorizacao
- Identificar bugs visuais ou funcionais

### AI Integration Expert

Use para:
- Implementar ou expandir a app `ai` do Finanpy
- Criar novos agentes LangChain 1.0 integrados ao Django
- Adicionar novas tools ao agente financeiro
- Configurar integracoes com a API da OpenAI
- Consultar padroes e boas praticas de IA no projeto
- Entender o fluxo completo de geracao de analises financeiras
- Planejar expansao futura da funcionalidade (agendamento, chat interativo, etc.)

Este agente atua como **guia de referencia e automacao** para todas as futuras implementacoes de IA no sistema. Ele conhece os padroes da codebase Finanpy e as convencoes do LangChain 1.0, e sabe como usar o MCP Server Context7 para buscar documentacao atualizada das bibliotecas.

## MCP Servers

Os agentes utilizam MCP servers especializados:

- **Context7**: Documentacao atualizada das tecnologias (Django, TailwindCSS, Python, LangChain, OpenAI)
- **Playwright**: Automacao de testes E2E no navegador
