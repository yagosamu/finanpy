from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Usuário'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Categoria'
    )
    amount = models.DecimalField(
        'Limite Mensal',
        max_digits=10,
        decimal_places=2
    )
    month = models.DateField('Mês de Referência')
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        unique_together = ['user', 'category', 'month']
        ordering = ['-month', 'category__name']
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'

    def __str__(self):
        return f'{self.category.name} - {self.month:%Y-%m}'

    @property
    def spent_amount(self):
        total = self.category.transactions.filter(
            user=self.user,
            transaction_type='expense',
            date__year=self.month.year,
            date__month=self.month.month,
        ).aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')

    @property
    def remaining_amount(self):
        return self.amount - self.spent_amount

    @property
    def usage_percentage(self):
        if self.amount <= 0:
            return Decimal('0.00')

        percentage = (self.spent_amount / self.amount) * Decimal('100')
        return min(percentage.quantize(Decimal('0.01')), Decimal('100.00'))

    @property
    def is_exceeded(self):
        return self.spent_amount > self.amount

    @property
    def exceeded_amount(self):
        if not self.is_exceeded:
            return Decimal('0.00')
        return self.spent_amount - self.amount
