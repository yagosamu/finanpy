# Agentes de Desenvolvimento

Agentes especializados para o desenvolvimento do Finanpy.

## Agentes Disponiveis

| Agente | Arquivo | Uso |
|--------|---------|-----|
| Backend Django | [backend-django.md](backend-django.md) | Models, views, forms, URLs, signals, migrations |
| Frontend Tailwind | [frontend-tailwind.md](frontend-tailwind.md) | Templates DTL, TailwindCSS, componentes UI |
| QA Tester | [qa-tester.md](qa-tester.md) | Testes E2E, validacao de UI, verificacao de fluxos |

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

## MCP Servers

Os agentes utilizam MCP servers especializados:

- **Context7**: Documentacao atualizada das tecnologias (Django, TailwindCSS, Python)
- **Playwright**: Automacao de testes E2E no navegador
