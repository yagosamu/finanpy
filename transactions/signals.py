from django.db.models import F
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from accounts.models import Account
from .models import Transaction


@receiver(pre_save, sender=Transaction)
def store_old_transaction_values(sender, instance, **kwargs):
    """
    Signal to store old transaction values before editing.

    This signal runs before a transaction is saved (on update only).
    It stores the old values (account, amount, transaction_type) in instance
    attributes so they can be used in post_save to reverse the old transaction effect.

    Args:
        sender: The model class (Transaction)
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    if instance.pk:  # Only for existing transactions (updates)
        try:
            old_transaction = Transaction.objects.get(pk=instance.pk)
            instance._old_account = old_transaction.account
            instance._old_amount = old_transaction.amount
            instance._old_transaction_type = old_transaction.transaction_type
        except Transaction.DoesNotExist:
            # In case the transaction was deleted between pre_save and now
            instance._old_account = None
            instance._old_amount = None
            instance._old_transaction_type = None


@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    """
    Signal to update account balance when a transaction is created or edited.

    Logic:
    - On CREATE: Apply transaction effect (income adds, expense subtracts)
    - On EDIT: Reverse old transaction effect, then apply new transaction effect
      (handles account changes too)

    Args:
        sender: The model class (Transaction)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created:
        # New transaction: apply the transaction effect
        _apply_transaction_to_account(
            instance.account,
            instance.amount,
            instance.transaction_type
        )
    else:
        # Editing existing transaction
        # First, reverse the old transaction effect
        if hasattr(instance, '_old_account') and instance._old_account:
            _reverse_transaction_from_account(
                instance._old_account,
                instance._old_amount,
                instance._old_transaction_type
            )

        # Then, apply the new transaction effect
        _apply_transaction_to_account(
            instance.account,
            instance.amount,
            instance.transaction_type
        )


@receiver(pre_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    """
    Signal to reverse transaction effect when a transaction is deleted.

    Logic:
    - If income: subtract from account balance
    - If expense: add back to account balance

    Args:
        sender: The model class (Transaction)
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments
    """
    _reverse_transaction_from_account(
        instance.account,
        instance.amount,
        instance.transaction_type
    )


def _apply_transaction_to_account(account, amount, transaction_type):
    """
    Apply a transaction effect to an account balance using atomic F() expressions.

    Args:
        account: Account instance to update
        amount: Transaction amount (Decimal)
        transaction_type: 'income' or 'expense'
    """
    if transaction_type == Transaction.INCOME:
        Account.objects.filter(pk=account.pk).update(
            current_balance=F('current_balance') + amount
        )
    elif transaction_type == Transaction.EXPENSE:
        Account.objects.filter(pk=account.pk).update(
            current_balance=F('current_balance') - amount
        )
    account.refresh_from_db()


def _reverse_transaction_from_account(account, amount, transaction_type):
    """
    Reverse a transaction effect from an account balance using atomic F() expressions.

    This is the opposite of apply: income subtracts, expense adds.

    Args:
        account: Account instance to update
        amount: Transaction amount (Decimal)
        transaction_type: 'income' or 'expense'
    """
    if transaction_type == Transaction.INCOME:
        Account.objects.filter(pk=account.pk).update(
            current_balance=F('current_balance') - amount
        )
    elif transaction_type == Transaction.EXPENSE:
        Account.objects.filter(pk=account.pk).update(
            current_balance=F('current_balance') + amount
        )
    account.refresh_from_db()
