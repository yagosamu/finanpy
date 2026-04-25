from calendar import monthrange
from datetime import date, timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def add_months(base_date, months):
    total_months = base_date.month - 1 + months
    year = base_date.year + total_months // 12
    month = total_months % 12 + 1
    day = min(base_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def get_day_in_month(year, month, day):
    return date(year, month, min(day, monthrange(year, month)[1]))


class Account(models.Model):
    """
    Bank account with automatic balance tracking.

    Balance is set from initial_balance on creation and updated
    atomically via signals when transactions are created/edited/deleted.
    """

    # Constants for choices at the top
    CHECKING = 'checking'
    SAVINGS = 'savings'
    WALLET = 'wallet'
    INVESTMENT = 'investment'
    NUBANK = 'nubank'
    ITAU = 'itau'
    BRADESCO = 'bradesco'
    SANTANDER = 'santander'
    BB = 'bb'
    CAIXA = 'caixa'
    INTER = 'inter'
    C6 = 'c6'
    OTHER = 'other'

    ACCOUNT_TYPE_CHOICES = [
        (CHECKING, 'Conta Corrente'),
        (SAVINGS, 'Poupança'),
        (WALLET, 'Carteira'),
        (INVESTMENT, 'Investimentos'),
    ]
    BANK_CODE_CHOICES = [
        (NUBANK, 'Nubank'),
        (ITAU, 'Itaú'),
        (BRADESCO, 'Bradesco'),
        (SANTANDER, 'Santander'),
        (BB, 'Banco do Brasil'),
        (CAIXA, 'Caixa'),
        (INTER, 'Inter'),
        (C6, 'C6 Bank'),
        (OTHER, 'Outro'),
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
    bank_code = models.CharField(
        'Código do Banco',
        max_length=20,
        choices=BANK_CODE_CHOICES,
        null=True,
        blank=True
    )
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
    is_default = models.BooleanField('Conta Padrão', default=False)
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
        """Set current_balance on creation and enforce a single default account."""
        if not self.pk:
            self.current_balance = self.initial_balance

        if self.is_default and self.user_id:
            Account.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)


class CreditCard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_cards',
        verbose_name='Usuário'
    )
    name = models.CharField('Nome', max_length=100)
    bank_code = models.CharField(
        'Código do Banco',
        max_length=20,
        choices=Account.BANK_CODE_CHOICES
    )
    credit_limit = models.DecimalField(
        'Limite de Crédito',
        max_digits=10,
        decimal_places=2
    )
    closing_day = models.PositiveIntegerField(
        'Dia de Fechamento',
        validators=[MinValueValidator(1), MaxValueValidator(28)]
    )
    due_day = models.PositiveIntegerField(
        'Dia de Vencimento',
        validators=[MinValueValidator(1), MaxValueValidator(28)]
    )
    is_active = models.BooleanField('Ativo', default=True)
    color = models.CharField('Cor', max_length=7, default='#22c55e')
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cartão de Crédito'
        verbose_name_plural = 'Cartões de Crédito'

    def __str__(self):
        return self.name

    @property
    def current_billing_start(self):
        today = date.today()
        if today.day <= self.closing_day:
            previous_month = add_months(today.replace(day=1), -1)
            closing_date = get_day_in_month(
                previous_month.year,
                previous_month.month,
                self.closing_day
            )
            return closing_date + timedelta(days=1)

        closing_date = get_day_in_month(today.year, today.month, self.closing_day)
        return closing_date + timedelta(days=1)

    @property
    def current_billing_end(self):
        today = date.today()
        if today.day <= self.closing_day:
            return get_day_in_month(today.year, today.month, self.closing_day)

        next_month = add_months(today.replace(day=1), 1)
        return get_day_in_month(next_month.year, next_month.month, self.closing_day)

    @property
    def current_bill_amount(self):
        from transactions.models import Transaction

        return (
            Transaction.objects.filter(
                credit_card=self,
                date__gte=self.current_billing_start,
                date__lte=self.current_billing_end,
            ).aggregate(total=models.Sum('amount'))['total']
            or 0
        )

    @property
    def available_limit(self):
        return self.credit_limit - self.current_bill_amount

    @property
    def next_due_date(self):
        today = date.today()
        if today.day <= self.due_day:
            return get_day_in_month(today.year, today.month, self.due_day)

        next_month = add_months(today.replace(day=1), 1)
        return get_day_in_month(next_month.year, next_month.month, self.due_day)

    def pay_bill(self, account):
        bill = self.bills.filter(
            status__in=[CardBill.OPEN, CardBill.CLOSED]
        ).order_by('-reference_month').first()

        if bill is None:
            reference_month = self.current_billing_end.replace(day=1)
            bill, _ = CardBill.objects.get_or_create(
                credit_card=self,
                reference_month=reference_month,
                defaults={
                    'closing_date': self.current_billing_end,
                    'due_date': self.next_due_date,
                    'total_amount': self.current_bill_amount,
                    'status': CardBill.CLOSED,
                },
            )

        if bill.total_amount != self.current_bill_amount and self.current_bill_amount > 0:
            bill.total_amount = self.current_bill_amount
            bill.closing_date = self.current_billing_end
            bill.due_date = self.next_due_date
            if bill.status == CardBill.OPEN:
                bill.status = CardBill.CLOSED
            bill.save(update_fields=['total_amount', 'closing_date', 'due_date', 'status'])

        return bill.pay_bill(account)


class CardBill(models.Model):
    OPEN = 'open'
    CLOSED = 'closed'
    PAID = 'paid'
    STATUS_CHOICES = [
        (OPEN, 'Aberta'),
        (CLOSED, 'Fechada'),
        (PAID, 'Paga'),
    ]

    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.CASCADE,
        related_name='bills',
        verbose_name='Cartão de Crédito'
    )
    reference_month = models.DateField('Mês de Referência')
    closing_date = models.DateField('Data de Fechamento')
    due_date = models.DateField('Data de Vencimento')
    total_amount = models.DecimalField(
        'Valor Total',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default=OPEN
    )
    payment_date = models.DateField('Data de Pagamento', null=True, blank=True)
    payment_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        related_name='paid_card_bills',
        null=True,
        blank=True,
        verbose_name='Conta de Pagamento'
    )

    class Meta:
        ordering = ['-reference_month']
        unique_together = ['credit_card', 'reference_month']
        verbose_name = 'Fatura do Cartão'
        verbose_name_plural = 'Faturas do Cartão'

    def __str__(self):
        return f'{self.credit_card.name} - {self.reference_month:%m/%Y}'

    def pay_bill(self, account):
        from categories.models import Category
        from transactions.models import Transaction

        category, _ = Category.objects.get_or_create(
            user=self.credit_card.user,
            name='Pagamento de Fatura',
            defaults={
                'category_type': Category.EXPENSE,
                'color': '#ef4444',
            }
        )
        payment_transaction = Transaction.objects.create(
            user=self.credit_card.user,
            account=account,
            category=category,
            transaction_type=Transaction.EXPENSE,
            amount=self.total_amount,
            date=date.today(),
            description=(
                f'Pagamento da fatura {self.credit_card.name} '
                f'- {self.reference_month:%m/%Y}'
            ),
        )
        self.status = self.PAID
        self.payment_date = date.today()
        self.payment_account = account
        self.save(update_fields=['status', 'payment_date', 'payment_account'])
        return payment_transaction
