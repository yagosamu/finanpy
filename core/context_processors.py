from django.db import models
from django.utils import timezone

from budgets.views import get_budget_queryset
from recurrences.services import get_pending_recurrences_count


def budget_sidebar_context(request):
    if not request.user.is_authenticated:
        return {
            'budgets_exceeded_count': 0,
            'pending_recurrences_count': 0,
        }

    current_month = timezone.localdate().replace(day=1)
    exceeded_count = get_budget_queryset(
        request.user,
        current_month,
    ).filter(spent__gt=models.F('amount')).count()
    return {
        'budgets_exceeded_count': exceeded_count,
        'pending_recurrences_count': get_pending_recurrences_count(request.user),
    }
