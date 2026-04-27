import calendar
import json
import logging
import re
from datetime import date

from django.conf import settings
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from openai import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _validate_user_id(user_id: int) -> None:
    '''Garante que o user_id pertence a um usuário ativo.

    Levanta ValueError se o usuário não existir ou estiver inativo,
    impedindo que o agente acesse dados de outros usuários.
    '''
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(id=user_id, is_active=True).exists():
        raise ValueError(f'Usuário {user_id} não encontrado ou inativo.')


# ---------------------------------------------------------------------------
# Tools — cada uma valida user_id antes de qualquer acesso ao banco
# ---------------------------------------------------------------------------

@tool
def get_user_transactions(user_id: int, start_date: str, end_date: str) -> str:
    '''Busca as transações financeiras do usuário em um período.

    Limitado às 200 transações mais recentes para evitar estouro de contexto.

    Args:
        user_id: ID do usuário no banco de dados.
        start_date: Data inicial no formato YYYY-MM-DD.
        end_date: Data final no formato YYYY-MM-DD.

    Returns:
        JSON com lista de transações do período.
    '''
    _validate_user_id(user_id)

    from transactions.models import Transaction

    qs = (
        Transaction.objects
        .filter(user_id=user_id, date__gte=start_date, date__lte=end_date)
        .select_related('category', 'account')
        .order_by('-date')[:200]
    )
    result = [
        {
            'date': str(t.date),
            'type': t.transaction_type,
            'type_label': t.get_transaction_type_display(),
            'amount': float(t.amount),
            'category': t.category.name,
            'account': t.account.name,
            'description': t.description or '',
        }
        for t in qs
    ]
    return json.dumps(result, ensure_ascii=False)


@tool
def get_category_summary(user_id: int, start_date: str, end_date: str) -> str:
    '''Agrega o total de receitas e despesas por categoria em um período.

    Usa aggregação SQL para eficiência máxima.

    Args:
        user_id: ID do usuário no banco de dados.
        start_date: Data inicial no formato YYYY-MM-DD.
        end_date: Data final no formato YYYY-MM-DD.

    Returns:
        JSON com totais por categoria, ordenado pelo maior valor.
    '''
    _validate_user_id(user_id)

    from django.db.models import Count, Sum

    from transactions.models import Transaction

    rows = (
        Transaction.objects
        .filter(user_id=user_id, date__gte=start_date, date__lte=end_date)
        .values('transaction_type', 'category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    result = [
        {
            'category': row['category__name'],
            'type': row['transaction_type'],
            'type_label': 'Receita' if row['transaction_type'] == 'income' else 'Despesa',
            'total': round(float(row['total']), 2),
            'count': row['count'],
        }
        for row in rows
    ]
    return json.dumps(result, ensure_ascii=False)


@tool
def get_account_balances(user_id: int) -> str:
    '''Retorna os saldos atuais de todas as contas ativas do usuário.

    Args:
        user_id: ID do usuário no banco de dados.

    Returns:
        JSON com saldo de cada conta e saldo total consolidado.
    '''
    _validate_user_id(user_id)

    from accounts.models import Account

    qs = Account.objects.filter(user_id=user_id, is_active=True).order_by('name')
    accounts = []
    total = 0.0
    for a in qs:
        balance = float(a.current_balance)
        total += balance
        accounts.append({
            'name': a.name,
            'bank': a.bank or '',
            'type': a.account_type,
            'type_label': a.get_account_type_display(),
            'balance': balance,
        })

    return json.dumps(
        {'accounts': accounts, 'total_balance': round(total, 2)},
        ensure_ascii=False,
    )


@tool
def get_monthly_comparison(user_id: int) -> str:
    '''Compara receitas, despesas e saldo do mês atual com o mês anterior.

    Args:
        user_id: ID do usuário no banco de dados.

    Returns:
        JSON com comparativo mensal e variações absolutas.
    '''
    _validate_user_id(user_id)

    from django.db.models import Sum

    from transactions.models import Transaction

    today = date.today()

    current_start = today.replace(day=1)
    current_end = today.replace(
        day=calendar.monthrange(today.year, today.month)[1]
    )

    if today.month == 1:
        prev_start = date(today.year - 1, 12, 1)
    else:
        prev_start = date(today.year, today.month - 1, 1)
    prev_end = prev_start.replace(
        day=calendar.monthrange(prev_start.year, prev_start.month)[1]
    )

    def _totals(start, end):
        rows = (
            Transaction.objects
            .filter(user_id=user_id, date__gte=start, date__lte=end)
            .values('transaction_type')
            .annotate(total=Sum('amount'))
        )
        totals = {row['transaction_type']: float(row['total'] or 0) for row in rows}
        income = round(totals.get('income', 0.0), 2)
        expense = round(totals.get('expense', 0.0), 2)
        return {'income': income, 'expense': expense, 'balance': round(income - expense, 2)}

    current = _totals(current_start, current_end)
    previous = _totals(prev_start, prev_end)

    result = {
        'current_month': {'period': f'{current_start} a {current_end}', **current},
        'previous_month': {'period': f'{prev_start} a {prev_end}', **previous},
        'variation': {
            'income': round(current['income'] - previous['income'], 2),
            'expense': round(current['expense'] - previous['expense'], 2),
            'balance': round(current['balance'] - previous['balance'], 2),
        },
    }
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tools list
# ---------------------------------------------------------------------------

TOOLS = [
    get_user_transactions,
    get_category_summary,
    get_account_balances,
    get_monthly_comparison,
]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    'Você é um assistente financeiro pessoal especializado em finanças brasileiras. '
    'Analise apenas os dados do usuário atual. '
    'Não solicite informações adicionais nem mencione outros usuários.\n\n'
    'Use as ferramentas disponíveis e estruture sua resposta com:\n\n'
    '1. **Situação Atual** — saldo consolidado e patrimônio\n'
    '2. **Análise do Período** — receitas vs despesas, fluxo de caixa\n'
    '3. **Padrões de Gastos** — categorias com maiores valores\n'
    '4. **Comparativo Mensal** — mês atual vs anterior\n'
    '5. **Dicas Personalizadas** — 3 recomendações práticas baseadas nos dados reais\n'
    '6. **Alertas** — situações preocupantes (saldo negativo, gastos excessivos, etc.)\n\n'
    'Responda em português brasileiro, de forma clara e empática. '
    'Use valores em reais (R$) com formatação brasileira.\n\n'
    'Inclua ao final da análise o aviso: '
    '"Esta análise é gerada automaticamente e não constitui aconselhamento financeiro profissional."\n\n'
    'Após o aviso, adicione uma linha separada começando EXATAMENTE com "RESUMO: " '
    'seguida de um resumo de até 2 frases (máximo 500 caracteres).'
)


# ---------------------------------------------------------------------------
# Singleton do agente — compilado uma única vez por processo
# ---------------------------------------------------------------------------

_AGENT = None


def _get_agent():
    '''Retorna o agente compilado, inicializando-o na primeira chamada.'''
    global _AGENT
    if _AGENT is None:
        llm = ChatOpenAI(
            model=settings.AI_MODEL,
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )
        _AGENT = create_agent(model=llm, tools=TOOLS, system_prompt=_SYSTEM_PROMPT)
    return _AGENT


# ---------------------------------------------------------------------------
# Public API — subtarefa 8.3.3
# ---------------------------------------------------------------------------

def run_analysis_for_user(user, period_start, period_end) -> dict:
    '''Executa a análise financeira completa para um usuário no período informado.

    Args:
        user: instância do model User.
        period_start: date — início do período.
        period_end: date — fim do período.

    Returns:
        dict com chaves:
            content (str)     — análise completa gerada pela IA
            summary (str)     — resumo de até 500 caracteres
            tokens_used (int) — total de tokens consumidos na execução
    '''
    human_input = (
        f'Analise as finanças do usuário (ID: {user.id}) '
        f'no período de {period_start} até {period_end}. '
        f'Use todas as ferramentas disponíveis para uma análise completa.'
    )

    try:
        agent = _get_agent()
        result = agent.invoke(
            {'messages': [HumanMessage(content=human_input)]},
            config={'recursion_limit': 20},
        )
    except (AuthenticationError, RateLimitError):
        raise
    except Exception as exc:
        logger.error(
            'Falha ao executar análise de IA',
            extra={'user_id': user.id, 'error': str(exc)},
            exc_info=True,
        )
        return {
            'content': (
                'Não foi possível gerar a análise no momento. '
                'Tente novamente mais tarde.'
            ),
            'summary': 'Análise indisponível no momento.',
            'tokens_used': 0,
        }

    # Extrai conteúdo — garante que a última mensagem é uma AIMessage com texto
    messages = result.get('messages', [])
    last = messages[-1] if messages else None
    content = (
        last.content
        if isinstance(last, AIMessage) and isinstance(last.content, str)
        else ''
    )

    if not content:
        logger.warning(
            'Agente encerrou sem AIMessage final',
            extra={'user_id': user.id},
        )
        return {
            'content': 'Análise não disponível.',
            'summary': 'Análise não disponível.',
            'tokens_used': 0,
        }

    # Soma tokens de todas as chamadas ao modelo na execução
    tokens_used = sum(
        msg.usage_metadata.get('total_tokens', 0)
        for msg in messages
        if isinstance(msg, AIMessage) and msg.usage_metadata is not None
    )

    # Extrai RESUMO com regex — robusto para Markdown bold (**RESUMO:**)
    summary = ''
    match = re.search(r'(?:^|\n)\*{0,2}RESUMO:\*{0,2}\s*(.+)', content, re.IGNORECASE)
    if match:
        summary = match.group(1).strip()[:500]
    if not summary:
        summary = content[:500].strip()

    return {
        'content': content,
        'summary': summary,
        'tokens_used': tokens_used,
    }
