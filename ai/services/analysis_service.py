import calendar
import logging
from datetime import date, timedelta

from django.contrib.auth import get_user_model

from ai.agents.finance_insight_agent import run_analysis_for_user
from ai.models import AIAnalysis

logger = logging.getLogger(__name__)

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _default_period() -> tuple[date, date]:
    '''Retorna o primeiro e último dia do mês corrente.'''
    today = date.today()
    period_start = today.replace(day=1)
    period_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return period_start, period_end


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def analyze_user(user, period_start=None, period_end=None) -> AIAnalysis:
    '''Executa a análise financeira de IA para um único usuário e persiste o resultado.

    Usa o mês corrente como período padrão quando não informado.

    Args:
        user: instância do model User.
        period_start: date opcional — início do período analisado.
        period_end: date opcional — fim do período analisado.

    Returns:
        Instância de AIAnalysis recém-criada com o resultado da análise.

    Raises:
        Exception: propaga qualquer erro inesperado após logar.
    '''
    if period_start is None or period_end is None:
        period_start, period_end = _default_period()

    logger.info(
        'Iniciando análise de IA',
        extra={'user_id': user.id, 'period_start': str(period_start), 'period_end': str(period_end)},
    )

    result = run_analysis_for_user(user, period_start, period_end)

    analysis = AIAnalysis.objects.create(
        user=user,
        content=result['content'],
        summary=result['summary'],
        period_start=period_start,
        period_end=period_end,
        tokens_used=result['tokens_used'],
    )

    logger.info(
        'Análise de IA concluída',
        extra={'user_id': user.id, 'analysis_id': analysis.id, 'tokens_used': result['tokens_used']},
    )

    return analysis


def analyze_all_active_users(period_start=None, period_end=None) -> dict:
    '''Executa a análise financeira de IA para todos os usuários ativos.

    Continua a execução mesmo se um usuário falhar — erros são logados individualmente.

    Args:
        period_start: date opcional — início do período analisado.
        period_end: date opcional — fim do período analisado.

    Returns:
        dict com chaves:
            success (int)       — quantidade de análises geradas com sucesso
            errors (list[dict]) — lista de {'user_email': str, 'error': str} para falhas
    '''
    if period_start is None or period_end is None:
        period_start, period_end = _default_period()

    users = User.objects.filter(is_active=True)
    total = users.count()

    logger.info(
        'Iniciando análise em lote',
        extra={'total_users': total, 'period_start': str(period_start), 'period_end': str(period_end)},
    )

    success = 0
    errors = []

    for user in users:
        try:
            analyze_user(user, period_start, period_end)
            success += 1
        except Exception as exc:
            logger.error(
                'Falha na análise do usuário',
                extra={'user_id': user.id, 'user_email': user.email, 'error': str(exc)},
                exc_info=True,
            )
            errors.append({'user_email': user.email, 'error': str(exc)})

    logger.info(
        'Análise em lote concluída',
        extra={'success': success, 'errors': len(errors)},
    )

    return {'success': success, 'errors': errors}
