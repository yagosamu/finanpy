from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account, CreditCard
from budgets.models import Budget
from categories.models import Category

from .forms import TransactionForm
from .models import Transaction


class TransactionFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='transactions@example.com',
            password='secret123'
        )
        self.default_account = Account.objects.create(
            user=self.user,
            name='Conta Padrão',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('300.00'),
            is_default=True,
        )
        self.other_account = Account.objects.create(
            user=self.user,
            name='Conta Secundária',
            account_type=Account.SAVINGS,
            initial_balance=Decimal('100.00'),
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Salário',
            category_type=Category.INCOME,
            color='#22c55e'
        )

    def test_transaction_form_prefills_default_account(self):
        form = TransactionForm(user=self.user)

        self.assertEqual(form.fields['account'].initial, self.default_account)

    def test_transaction_form_keeps_submitted_account_selection(self):
        form = TransactionForm(
            data={
                'transaction_type': 'income',
                'amount': '25.00',
                'date': date.today().isoformat(),
                'description': 'Teste',
                'account': str(self.other_account.pk),
                'category': str(self.category.pk),
            },
            user=self.user,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['account'], self.other_account)

    def test_transaction_form_exposes_credit_card_field_filtered_by_user(self):
        active_card = CreditCard.objects.create(
            user=self.user,
            name='Cartao Ativo',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('5000.00'),
            closing_day=10,
            due_day=20,
        )
        inactive_card = CreditCard.objects.create(
            user=self.user,
            name='Cartao Inativo',
            bank_code=Account.ITAU,
            credit_limit=Decimal('2000.00'),
            closing_day=5,
            due_day=15,
            is_active=False,
        )
        other_user = get_user_model().objects.create_user(
            email='transactions-other@example.com',
            password='secret123'
        )
        CreditCard.objects.create(
            user=other_user,
            name='Cartao Alheio',
            bank_code=Account.C6,
            credit_limit=Decimal('7000.00'),
            closing_day=8,
            due_day=18,
        )

        form = TransactionForm(user=self.user)

        self.assertIn('credit_card', form.fields)
        self.assertEqual(form.fields['credit_card'].empty_label, 'Débito em conta (padrão)')
        self.assertQuerySetEqual(
            form.fields['credit_card'].queryset.order_by('pk'),
            [active_card],
            transform=lambda card: card,
        )
        self.assertEqual(
            form.fields['account'].widget.attrs['data-account-field'],
            'true',
        )
        self.assertEqual(
            form.fields['credit_card'].widget.attrs['data-credit-card-field'],
            'true',
        )


class TransactionCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='transaction-view@example.com',
            password='secret123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('30.00'),
            is_default=True,
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Mercado',
            category_type=Category.EXPENSE,
            color='#ef4444'
        )
        self.client.force_login(self.user)

    def test_create_expense_warns_when_balance_becomes_negative(self):
        response = self.client.post(
            reverse('transactions:create'),
            data={
                'transaction_type': Transaction.EXPENSE,
                'amount': '50.00',
                'date': date.today().isoformat(),
                'description': 'Compra',
                'account': str(self.account.pk),
                'category': str(self.category.pk),
            },
            follow=True,
        )

        self.account.refresh_from_db()

        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(self.account.current_balance, Decimal('-20.00'))
        self.assertContains(response, 'Transa')
        self.assertContains(response, 'saldo negativo')

    def test_create_expense_warns_when_budget_is_exceeded(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('40.00'),
            month=date.today().replace(day=1),
        )

        response = self.client.post(
            reverse('transactions:create'),
            data={
                'transaction_type': Transaction.EXPENSE,
                'amount': '50.00',
                'date': date.today().isoformat(),
                'description': 'Compra',
                'account': str(self.account.pk),
                'category': str(self.category.pk),
            },
            follow=True,
        )

        self.assertEqual(Transaction.objects.count(), 1)
        self.assertContains(response, 'ultrapassou o or')
        self.assertContains(response, 'Mercado')

    def test_transaction_form_page_renders_credit_card_selector(self):
        CreditCard.objects.create(
            user=self.user,
            name='Cartao Principal',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('5000.00'),
            closing_day=10,
            due_day=20,
        )

        response = self.client.get(reverse('transactions:create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cartão de Crédito')
        self.assertContains(response, 'Débito em conta (padrão)')
        self.assertContains(response, 'selectedCreditCardName')


class TransactionSignalTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='transaction-signals@example.com',
            password='secret123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
            is_default=True,
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Cartão',
            category_type=Category.EXPENSE,
            color='#ef4444'
        )
        self.credit_card = CreditCard.objects.create(
            user=self.user,
            name='Cartão Principal',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('5000.00'),
            closing_day=10,
            due_day=20,
        )

    def test_credit_card_transaction_does_not_change_account_balance(self):
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('250.00'),
            date=date.today(),
            description='Compra no cartão',
            credit_card=self.credit_card,
        )

        self.account.refresh_from_db()

        self.assertEqual(self.account.current_balance, Decimal('1000.00'))
