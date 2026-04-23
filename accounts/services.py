from django.utils import timezone

from categories.models import Category
from transactions.models import Transaction

from .models import Account


def get_default_account(user):
    if not user:
        return None

    return Account.objects.filter(
        user=user,
        is_active=True,
        is_default=True,
    ).first()


def debit_account(account, amount, description, category=None, date=None):
    if category is None:
        category, _ = Category.objects.get_or_create(
            user=None,
            name='Transferência',
            defaults={
                'category_type': Category.EXPENSE,
                'color': '#525252',
                'is_default': True,
                'is_active': True,
            },
        )

    transaction_date = date or timezone.localdate()

    return Transaction.objects.create(
        user=account.user,
        account=account,
        category=category,
        transaction_type=Transaction.EXPENSE,
        amount=amount,
        date=transaction_date,
        description=description or '',
    )
