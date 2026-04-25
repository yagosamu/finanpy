from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from transactions.models import Transaction


def add_months(base_date, months):
    total_months = base_date.month - 1 + months
    year = base_date.year + total_months // 12
    month = total_months % 12 + 1
    day = min(base_date.day, monthrange(year, month)[1])
    return date(year, month, day)


class InstallmentPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        verbose_name='Usuário',
    )
    name = models.CharField('Nome', max_length=150)
    total_amount = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)
    installment_count = models.PositiveIntegerField(
        'Quantidade de Parcelas',
        validators=[MinValueValidator(2), MaxValueValidator(120)],
    )
    installment_amount = models.DecimalField(
        'Valor da Parcela',
        max_digits=10,
        decimal_places=2,
        editable=False,
    )
    start_date = models.DateField('Data da Primeira Parcela')
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='installment_plans',
        verbose_name='Categoria',
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='installment_plans',
        verbose_name='Conta',
    )
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Plano de Parcelamento'
        verbose_name_plural = 'Planos de Parcelamento'

    def __str__(self):
        return self.name

    @property
    def paid_count(self):
        return self.installments.filter(status=Installment.PAID).count()

    @property
    def remaining_count(self):
        return self.installment_count - self.paid_count

    @property
    def remaining_amount(self):
        return self.installment_amount * self.remaining_count

    @property
    def progress_percentage(self):
        if not self.installment_count:
            return 0
        return min((self.paid_count / self.installment_count) * 100, 100)

    @property
    def is_completed(self):
        return self.remaining_count == 0

    @property
    def next_installment(self):
        return self.installments.filter(status=Installment.PENDING).order_by('due_date').first()

    def save(self, *args, **kwargs):
        self.installment_amount = (
            Decimal(self.total_amount) / Decimal(self.installment_count)
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)


class Installment(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (PENDING, 'Pendente'),
        (PAID, 'Paga'),
        (OVERDUE, 'Atrasada'),
    ]

    plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name='Plano',
    )
    number = models.PositiveIntegerField('Número da Parcela')
    due_date = models.DateField('Data de Vencimento')
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    paid_date = models.DateField('Data de Pagamento', null=True, blank=True)
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        related_name='installments',
        null=True,
        blank=True,
        verbose_name='Transação',
    )

    class Meta:
        ordering = ['number']
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        unique_together = ['plan', 'number']

    def __str__(self):
        return f'{self.plan.name} - {self.number}/{self.plan.installment_count}'

    @property
    def is_overdue(self):
        return self.status == self.PENDING and self.due_date < date.today()
