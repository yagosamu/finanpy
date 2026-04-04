# Agente de IA Financeiro — Documentação Técnica

## Visão Geral

O **Agente de IA Financeiro** é uma funcionalidade do Finanpy que utiliza LangChain 1.x e a API da OpenAI para gerar análises e insights personalizados sobre as finanças de cada usuário. A análise é baseada nos dados reais do usuário (transações, contas, categorias) e é armazenada no banco de dados para consulta futura.

A última análise gerada é exibida diretamente no **dashboard**, proporcionando acesso imediato a insights atualizados.

---

## Estrutura da App `ai`

```
ai/
├── __init__.py
├── apps.py
├── models.py                          # AIAnalysis model
├── admin.py                           # Admin customizado
├── agents/
│   ├── __init__.py
│   ├── finance_insight_agent.py       # tools, prompt, singleton e API pública
│   └── ai_integration_expert.md      # guia para desenvolvedores estenderem a IA
├── services/
│   ├── __init__.py
│   └── analysis_service.py           # orquestra análise e persistência
└── management/
    └── commands/
        ├── __init__.py
        └── run_finance_analysis.py    # Django Command de execução
```

---

## Modelo de Dados: AIAnalysis

```python
class AIAnalysis(models.Model):
    user         = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    content      = TextField()                    # análise completa gerada pela IA
    summary      = CharField(max_length=500)      # resumo para o dashboard
    period_start = DateField()                    # início do período analisado
    period_end   = DateField()                    # fim do período analisado
    tokens_used  = IntegerField(default=0)        # tokens consumidos na chamada
    created_at   = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

Cada usuário pode ter múltiplas análises. A mais recente é exibida no dashboard.

---

## Fluxo de Funcionamento

```
1. Operador executa: python manage.py run_finance_analysis [--user EMAIL] [--month YYYY-MM]
          |
          v
2. run_finance_analysis.py (Management Command)
   - Faz parse de --user e --month
   - Chama analysis_service.analyze_user() ou analyze_all_active_users()
          |
          v
3. analysis_service.analyze_user(user, period_start, period_end)
   - Define período padrão (1º ao último dia do mês corrente) se não informado
   - Chama finance_insight_agent.run_analysis_for_user()
   - Persiste o resultado em AIAnalysis
          |
          v
4. finance_insight_agent.run_analysis_for_user(user, period_start, period_end)
   - Obtém o singleton CompiledStateGraph via _get_agent()
   - Invoca agent.invoke({"messages": [HumanMessage(...)]})
   - Tools acessam o banco de dados Django (sempre filtradas por user_id)
   - Extrai content de result["messages"][-1].content
   - Soma tokens de AIMessage.usage_metadata
   - Extrai RESUMO com regex robusto
          |
          v
5. AIAnalysis salvo no banco com content, summary, tokens_used
          |
          v
6. DashboardView carrega AIAnalysis.objects.filter(user=user).first()
   e exibe o card "Análise Financeira com IA" com modal de conteúdo completo
```

---

## Como Executar

### Pré-requisitos

1. Variáveis de ambiente configuradas no `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   AI_MODEL=gpt-4o-mini
   AI_MAX_TOKENS=2048
   AI_TEMPERATURE=0.3
   ```

2. Dependências já incluídas no `requirements.txt`:
   - `langchain>=1.2.0`
   - `langchain-openai>=1.1.0`
   - `langchain-core>=1.2.0`
   - `langgraph>=1.1.0`
   - `openai>=2.0.0`

3. Migrations aplicadas:
   ```bash
   python manage.py migrate
   ```

### Executar análise

```bash
# Analisar todos os usuários ativos (mês atual)
python manage.py run_finance_analysis

# Analisar apenas um usuário
python manage.py run_finance_analysis --user email@exemplo.com

# Analisar um mês específico
python manage.py run_finance_analysis --month 2026-03

# Combinação: usuário específico em mês específico
python manage.py run_finance_analysis --user email@exemplo.com --month 2026-03
```

---

## Tools do Agente

O agente possui 4 tools que acessam o banco de dados Django com segurança. Todas chamam `_validate_user_id()` como primeira instrução e filtram por `user_id`:

| Tool | Parâmetros | O que retorna |
|------|-----------|---------------|
| `get_user_transactions` | user_id, start_date, end_date | Até 200 transações do período (JSON) |
| `get_category_summary` | user_id, start_date, end_date | Totais por categoria via GROUP BY SQL (JSON) |
| `get_account_balances` | user_id | Saldo de cada conta + total consolidado (JSON) |
| `get_monthly_comparison` | user_id | Receitas/despesas do mês atual vs anterior (JSON) |

---

## Integração com o Dashboard

A `DashboardView` (`core/views.py`) busca a última análise do usuário:

```python
latest_analysis = AIAnalysis.objects.filter(user=user).first()
context['latest_analysis'] = latest_analysis
```

O template `dashboard.html` exibe:
- **Card** com badge "IA", ícone de faísca e data de geração
- **Resumo** (`summary`) em destaque
- **Botão** "Ver análise completa" que abre um modal com `content` completo
- **Empty state** quando nenhuma análise foi gerada ainda

---

## Tecnologias Utilizadas

| Componente | Tecnologia | Versão |
|-----------|-----------|--------|
| Orquestração do agente | `langchain.agents.create_agent` | LangChain 1.2+ |
| Grafo de execução | LangGraph `CompiledStateGraph` | 1.1+ |
| Modelo de linguagem | OpenAI GPT | gpt-4o-mini |
| Cliente OpenAI | `langchain-openai` | 1.1+ |
| Persistência | Django ORM + SQLite | Django 5.2+ |
| Execução | Django Management Command | — |

---

## Segurança

- `OPENAI_API_KEY` nunca é exposta em logs, templates ou código-fonte
- `_validate_user_id()` é chamado como primeira linha de cada tool — impede acesso a dados de outros usuários
- `try/except` em `run_analysis_for_user` e `analyze_all_active_users` — falha de um usuário não afeta os demais
- Logs estruturados com `extra={}` nunca contêm valores financeiros ou dados pessoais
- Conteúdo da análise não é renderizado como HTML raw no template (`linebreaksbr` apenas)

---

## Manutenção e Expansão

### Trocar o modelo LLM

Altere `AI_MODEL` no `.env`. O singleton `_AGENT` é recriado no próximo start do processo.

### Adicionar novas tools

Veja o guia completo em `ai/agents/ai_integration_expert.md`.

### Agendar execução automática

- **Cron do SO:** `0 8 1 * * cd /app && python manage.py run_finance_analysis`
- **Celery Beat:** `PeriodicTask` apontando para o management command
- **CI/CD:** GitHub Actions com `schedule` trigger

### Adicionar interface para o usuário solicitar análise

Criar uma view que chame `analyze_user()` diretamente. Atenção: chamadas à OpenAI são síncronas e podem demorar 10–30s — considerar Celery para processamento assíncrono.

---

## Referência Técnica Adicional

| Recurso | Caminho |
|---------|---------|
| Guia para desenvolvedores | `ai/agents/ai_integration_expert.md` |
| Sub-agente Claude de revisão de código | `.claude/agents/ai-integration-expert.md` |
| PRD com especificação completa | `PRD.md` — seção 13 |
