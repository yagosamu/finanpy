# Agente de IA Financeiro — Documentação Técnica

## Visão Geral

O **Agente de IA Financeiro** é uma funcionalidade do Finanpy que utiliza LangChain 1.0 e a API da OpenAI para gerar análises e insights personalizados sobre as finanças de cada usuário. A análise é baseada nos dados reais do usuário (transações, contas, categorias) e é armazenada no banco de dados para consulta futura.

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
│   ├── finance_insight_agent.py       # Agente LangChain com tools financeiras
│   └── ai_integration_expert.md      # Referência técnica para criação de agentes
├── services/
│   └── analysis_service.py           # Orquestra análise e persistência
└── management/
    └── commands/
        └── run_finance_analysis.py    # Django Command de execução
```

---

## Modelo de Dados: AIAnalysis

```python
class AIAnalysis(models.Model):
    user         = ForeignKey(User)       # usuário dono da análise
    content      = TextField()            # análise completa gerada pela IA
    summary      = CharField(max_length=500)  # resumo para o dashboard
    period_start = DateField()            # início do período analisado
    period_end   = DateField()            # fim do período analisado
    tokens_used  = IntegerField()         # custo em tokens da chamada à API
    created_at   = DateTimeField(auto_now_add=True)
```

Cada usuário pode ter múltiplas análises. A mais recente (`ordering = ['-created_at']`) é exibida no dashboard.

---

## Fluxo de Funcionamento

```
1. Operador executa: python manage.py run_finance_analysis
          |
          v
2. run_finance_analysis.py (Management Command)
   - Lê argumentos --user e --month
   - Chama analysis_service
          |
          v
3. analysis_service.analyze_user(user, period_start, period_end)
   - Define período padrão (mês atual) se não informado
   - Chama o agente LangChain
          |
          v
4. finance_insight_agent.run_analysis_for_user(user, period_start, period_end)
   - Constrói o AgentExecutor com tools financeiras
   - Tools acessam o banco de dados Django (filtrado por user_id)
   - GPT analisa os dados e gera o texto de insights
   - Extrai resumo curto do output
          |
          v
5. analysis_service persiste AIAnalysis no banco
          |
          v
6. DashboardView carrega a última AIAnalysis do usuário
   e exibe o card de "Análise de IA" no dashboard
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

2. Dependências instaladas:
   ```bash
   pip install langchain langchain-openai openai
   ```

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

O agente LangChain possui tools que acessam o banco de dados Django com segurança (sempre filtradas por `user_id`):

| Tool | Parâmetros | O que retorna |
|------|-----------|---------------|
| `get_user_transactions` | user_id, start_date, end_date | Lista de transações no período |
| `get_account_balances` | user_id | Saldos de todas as contas ativas |
| `get_category_summary` | user_id, start_date, end_date | Gastos agregados por categoria |
| `get_monthly_comparison` | user_id | Comparação mês atual vs anterior |

---

## Integração com o Dashboard

A `DashboardView` (`core/views.py`) inclui no contexto:

```python
context['latest_analysis'] = (
    AIAnalysis.objects
    .filter(user=self.request.user)
    .first()  # ordenado por -created_at
)
```

O template `dashboard.html` exibe o card de análise quando `latest_analysis` está presente:
- **Resumo** (`summary`) em destaque
- **Data** da geração
- **Badge** "IA" para identificação visual
- **Link** para ver a análise completa

---

## Tecnologias Utilizadas

| Componente | Tecnologia |
|-----------|-----------|
| Framework de agente | LangChain 1.0 |
| Modelo de linguagem | OpenAI GPT (gpt-4o-mini) |
| Integração LLM | langchain-openai |
| Persistência | Django ORM + SQLite |
| Execução | Django Management Command |

---

## Segurança

- A `OPENAI_API_KEY` nunca é exposta em logs, templates ou no código-fonte
- Todas as tools filtram dados por `user_id`, garantindo isolamento entre usuários
- Chamadas à API são envolvidas em `try/except` — falha de um usuário não afeta os demais
- O campo `content` não é renderizado como HTML raw — XSS não é uma ameaça

---

## Manutenção e Expansão

### Trocar o modelo LLM

Altere a variável de ambiente `AI_MODEL` no `.env`. O agente usará o novo modelo automaticamente na próxima execução.

### Adicionar novas tools

1. Crie uma função Python decorada com `@tool` em `finance_insight_agent.py`
2. Adicione-a à lista `tools` dentro de `build_agent()`
3. Docstring da função deve ser descritiva — o LLM usa para decidir quando chamar a tool

### Agendar execução automática

Opções para automatizar em produção:
- **Cron do sistema operacional:** `0 8 1 * * cd /app && python manage.py run_finance_analysis`
- **Celery Beat:** configurar `PeriodicTask` apontando para o command
- **CI/CD agendado:** GitHub Actions com `schedule` trigger

### Adicionar interface de usuário para solicitar análise

Criar uma view com formulário que chame `analyze_user()` diretamente e redirecione para o dashboard. Atenção: chamadas síncronas à OpenAI podem ser lentas — considerar Celery para processamento assíncrono.

---

## Referência Técnica Adicional

Para implementar ou expandir agentes de IA no projeto, consulte o agente especialista:

```
.claude/agents/ai-integration-expert.md
```

Esse documento contém padrões de código, boas práticas, checklist de implementação e instruções sobre como usar o MCP Server Context7 para buscar documentação atualizada do LangChain.
