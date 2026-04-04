---
name: Sprint 8 AI Agent Implementation - finance_insight_agent.py
description: Key findings from the Sprint 8.3 code review of the LangChain/LangGraph finance agent; issues to track for fixes
type: project
---

Reviewed `ai/agents/finance_insight_agent.py` on 2026-04-04 as part of Sprint 8.3 (Criação do Agente LangChain).

Key findings:

- `create_react_agent` from `langgraph.prebuilt` is deprecated in langgraph 1.1.6 in favor of `langchain.agents.create_agent`. The code is functional but carries a deprecation warning.
- `tokens_used` is hardcoded to 0. The correct fix is to iterate `result['messages']` and sum `msg.usage_metadata['total_tokens']` for each AIMessage that has non-None usage_metadata.
- `_build_agent()` is called on every request, reconstructing the LLM and compiling the graph each time. The compiled graph should be cached at module level.
- `get_category_summary` and `get_user_transactions` have no `:N` result slice, so they can return unbounded data.
- `get_monthly_comparison` executes 4 separate DB queries; should use a single annotated aggregate.
- No `_validate_user_id` guard on any of the 4 tools — mandatory per project standards.
- No `try/except` around `agent.invoke()` — any OpenAI API failure crashes the caller with no fallback.
- The system prompt lacks the mandatory LGPD disclaimer ("não constitui aconselhamento financeiro").
- `result['messages'][-1]` may not be an AIMessage if `recursion_limit` is hit (last message could be ToolMessage).
- `max_tokens` in `ChatOpenAI` expects `int | None` — settings already cast it via `int()`, so no bug, but the comment is worth documenting.
- `get_category_summary` uses a Python loop aggregation instead of DB-level `values().annotate(Sum(...))`, which is less efficient.

**Why:** These issues were discovered during the Sprint 8.3 technical review before any production deployment.
**How to apply:** Use these findings to scope the Sprint 8.3 bug-fix pass. Prioritize: missing try/except, missing _validate_user_id, tokens_used=0, and unbounded querysets.
