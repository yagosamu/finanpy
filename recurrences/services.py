from .models import Recurrence


def get_active_recurrences(user):
    return Recurrence.objects.filter(
        user=user,
        is_active=True,
    ).select_related('category', 'account')


def get_pending_recurrences(user):
    return [recurrence for recurrence in get_active_recurrences(user) if recurrence.is_due_this_month]


def get_pending_recurrences_count(user):
    return len(get_pending_recurrences(user))
