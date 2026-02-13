from django.conf import settings
from django.db import models


class Account(models.Model):
    # Constants for choices at the top
    CHECKING = 'checking'
    SAVINGS = 'savings'
    WALLET = 'wallet'
    INVESTMENT = 'investment'

    ACCOUNT_TYPE_CHOICES = [
        (CHECKING, 'Conta Corrente'),
        (SAVINGS, 'Poupança'),
        (WALLET, 'Carteira'),
        (INVESTMENT, 'Investimentos'),
    ]

    # ForeignKey fields first
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name='Usuário'
    )

    # Regular fields
    name = models.CharField('Nome', max_length=100)
    account_type = models.CharField(
        'Tipo de Conta',
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES
    )
    bank = models.CharField('Banco', max_length=100, blank=True)
    initial_balance = models.DecimalField(
        'Saldo Inicial',
        max_digits=10,
        decimal_places=2
    )
    current_balance = models.DecimalField(
        'Saldo Atual',
        max_digits=10,
        decimal_places=2
    )
    is_active = models.BooleanField('Ativa', default=True)

    # Timestamp fields last
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name}'

    def get_balance(self):
        """Calculate balance based on transactions.

        For now, returns current_balance.
        Will be implemented to sum transactions in the future.
        """
        return self.current_balance

    def save(self, *args, **kwargs):
        """Set current_balance from initial_balance on creation."""
        if not self.pk:
            self.current_balance = self.initial_balance
        super().save(*args, **kwargs)
