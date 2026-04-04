# AI Integration Expert — Referência Técnica

Guia para desenvolvedores sobre como estender e manter a funcionalidade de IA do Finanpy.

---

## Estrutura do módulo `ai/agents/`

```
ai/agents/
├── __init__.py
└── finance_insight_agent.py   # agente principal — tools, prompt, singleton e API pública
```

---

## Como o agente funciona

O agente usa `langchain.agents.create_agent` (LangChain 1.x) que compila um
`CompiledStateGraph` com as 4 tools financeiras. A invocação segue o protocolo
LangGraph — input como `{"messages": [HumanMessage(...)]}`.

```
_get_agent()                    # retorna singleton CompiledStateGraph
    └── create_agent(llm, TOOLS, system_prompt=_SYSTEM_PROMPT)

run_analysis_for_user(user, period_start, period_end)
    ├── _get_agent().invoke({"messages": [HumanMessage(...)]})
    ├── extrai content de result["messages"][-1].content
    ├── soma tokens de AIMessage.usage_metadata
    └── extrai RESUMO com regex
```

---

## Adicionar uma nova tool

1. Crie a função decorada com `@tool` em `finance_insight_agent.py`:

```python
@tool
def get_budget_alerts(user_id: int) -> str:
    '''Verifica se alguma categoria ultrapassou o limite mensal do usuário.

    Args:
        user_id: ID do usuário no banco de dados.

    Returns:
        JSON com lista de alertas de orçamento.
    '''
    _validate_user_id(user_id)          # OBRIGATÓRIO — sempre primeira linha
    # ... lógica ORM aqui, filtrar sempre por user_id ...
    return json.dumps(result, ensure_ascii=False)
```

2. Adicione-a à lista `TOOLS` no mesmo arquivo:

```python
TOOLS = [
    get_user_transactions,
    get_category_summary,
    get_account_balances,
    get_monthly_comparison,
    get_budget_alerts,           # nova tool
]
```

3. O singleton `_AGENT` será recriado automaticamente na próxima execução
   (a variável global é `None` após reinicialização do processo).

---

## Regras obrigatórias para toda tool

| Regra | Por quê |
|-------|---------|
| Chamar `_validate_user_id(user_id)` como primeira linha | Impede acesso a dados de outros usuários |
| Filtrar todos os querysets com `user_id=user_id` | Isolamento de dados por usuário |
| Usar `select_related` / `prefetch_related` | Evita N+1 queries |
| Limitar querysets com `[:N]` | Evita estouro do contexto do modelo |
| Usar aggregação SQL (`.annotate(Sum(...))`) em vez de Python | Performance |
| Retornar `json.dumps(..., ensure_ascii=False)` | Compatibilidade com o agente |
| Docstring descritiva | O LLM usa para decidir quando chamar a tool |

---

## Trocar o modelo LLM

Altere `AI_MODEL` no `.env`. O singleton é recriado no próximo start do processo.

```env
AI_MODEL=gpt-4o          # mais capaz, mais caro
AI_MODEL=gpt-4o-mini     # padrão — boa relação custo/benefício
```

---

## Ajustar o system prompt

Edite `_SYSTEM_PROMPT` em `finance_insight_agent.py`. Mantenha:
- A instrução `"Analise apenas os dados do usuário atual"`
- A cláusula de privacidade (não mencionar outros usuários)
- O disclaimer LGPD no corpo da análise
- A instrução de formato `"RESUMO: ..."` — o regex depende dela

---

## Consultar documentação atualizada do LangChain

Use o MCP Server Context7 antes de integrar qualquer API nova:

```
mcp__context7__resolve-library-id("langchain")
mcp__context7__get-library-docs(library_id, topic="tools")
mcp__context7__get-library-docs(library_id, topic="agents")
```

---

## Sub-agente Claude para revisão de código

O agente especialista `.claude/agents/ai-integration-expert.md` pode revisar
código de IA, auditar segurança e sugerir melhorias. Use-o via Claude Code:

```
usando o agente ai-integration-expert, revise o arquivo ai/agents/finance_insight_agent.py
```
