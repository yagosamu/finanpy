from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from transactions.models import Transaction


class Recurrence(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recurrences',
        verbose_name='Usuário',
    )
    name = models.CharField('Nome', max_length=120)
    transaction_type = models.CharField(
        'Tipo de Transação',
        max_length=10,
        choices=Transaction.TRANSACTION_TYPE_CHOICES,
    )
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='recurrences',
        verbose_name='Categoria',
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='recurrences',
        verbose_name='Conta',
    )
    day_of_month = models.PositiveIntegerField(
        'Dia do Mês',
        validators=[MinValueValidator(1), MaxValueValidator(28)],
    )
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término', null=True, blank=True)
    is_active = models.BooleanField('Ativa', default=True)
    last_generated_date = models.DateField('Último Lançamento', null=True, blank=True)
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        ordering = ['transaction_type', 'day_of_month', 'name']
        verbose_name = 'Recorrência'
        verbose_name_plural = 'Recorrências'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'transaction_type']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_due_this_month(self):
        today = timezone.localdate()
        current_month_start = today.replace(day=1)

        if not self.is_active:
            return False
        if self.start_date > today:
            return False
        if self.end_date and self.end_date < current_month_start:
            return False
        if not self.last_generated_date:
            return True
        return (
            self.last_generated_date.year != today.year
            or self.last_generated_date.month != today.month
        )

    @property
    def next_occurrence_date(self):
        today = timezone.localdate()
        current_month = today.replace(day=1)
        candidate = current_month.replace(day=self.day_of_month)

        if candidate < self.start_date:
            candidate = self.start_date.replace(day=min(self.day_of_month, 28))
        elif candidate <= today and not self.is_due_this_month:
            if current_month.month == 12:
                candidate = date(current_month.year + 1, 1, self.day_of_month)
            else:
                candidate = date(current_month.year, current_month.month + 1, self.day_of_month)

        return candidate

    def generate_transaction(self, target_date=None):
        transaction_date = target_date or timezone.localdate()
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=self.transaction_type,
            amount=self.amount,
            date=transaction_date,
            description=self.name,
        )
        self.last_generated_date = transaction_date
        self.save(update_fields=['last_generated_date', 'updated_at'])
        return transaction
