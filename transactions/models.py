from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models


class Transaction(models.Model):
    # Constants for choices at the top
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Receita'),
        (EXPENSE, 'Despesa'),
    ]

    # ForeignKey fields first
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Usuário'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Conta'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Categoria'
    )

    # Regular fields
    transaction_type = models.CharField(
        'Tipo de Transação',
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2
    )
    date = models.DateField('Data')
    description = models.TextField(
        'Descrição',
        blank=True,
        validators=[MaxLengthValidator(500)]
    )

    # Timestamp fields last
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f'{self.get_transaction_type_display()} - R$ {self.amount}'
