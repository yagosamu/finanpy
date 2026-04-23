from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import AccountForm, AccountUpdateForm, TransferForm
from .models import Account
from .services import debit_account, get_default_account
from .templatetags.account_tags import get_bank_icon_path
from transactions.models import Transaction


class AccountModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='accounts@example.com',
            password='secret123'
        )

    def test_setting_default_account_unsets_other_default_accounts_for_same_user(self):
        first_account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank='Banco A',
            bank_code=Account.ITAU,
            initial_balance=Decimal('100.00'),
            is_default=True,
        )
        second_account = Account.objects.create(
            user=self.user,
            name='Conta Reserva',
            account_type=Account.SAVINGS,
            bank='Banco B',
            bank_code=Account.NUBANK,
            initial_balance=Decimal('50.00'),
            is_default=True,
        )

        first_account.refresh_from_db()
        second_account.refresh_from_db()

        self.assertFalse(first_account.is_default)
        self.assertTrue(second_account.is_default)
        self.assertEqual(second_account.bank_code, Account.NUBANK)

    def test_account_defaults_to_not_default_and_allows_empty_bank_code(self):
        account = Account.objects.create(
            user=self.user,
            name='Carteira',
            account_type=Account.WALLET,
            initial_balance=Decimal('0.00'),
        )

        self.assertFalse(account.is_default)
        self.assertIsNone(account.bank_code)


class AccountFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='account-forms@example.com',
            password='secret123'
        )

    def test_checking_account_requires_bank_code(self):
        form = AccountForm(
            data={
                'name': 'Conta Corrente',
                'account_type': Account.CHECKING,
                'bank': 'Banco Exemplo',
                'initial_balance': '150.00',
                'is_default': 'on',
            },
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('bank_code', form.errors)

    def test_non_checking_account_allows_empty_bank_code(self):
        form = AccountForm(
            data={
                'name': 'Carteira Fisica',
                'account_type': Account.WALLET,
                'bank': '',
                'bank_code': '',
                'initial_balance': '30.00',
            },
            user=self.user,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_update_form_exposes_bank_code_and_is_default_fields(self):
        form = AccountUpdateForm(user=self.user)

        self.assertIn('bank_code', form.fields)
        self.assertIn('is_default', form.fields)

    def test_transfer_form_rejects_same_origin_and_destination(self):
        account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('100.00'),
            is_default=True,
        )

        form = TransferForm(
            data={
                'from_account': str(account.pk),
                'to_account': str(account.pk),
                'amount': '10.00',
                'description': 'Teste',
                'date': date.today().isoformat(),
            },
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_transfer_form_prefills_default_origin_account(self):
        default_account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('100.00'),
            is_default=True,
        )
        Account.objects.create(
            user=self.user,
            name='Conta Reserva',
            account_type=Account.SAVINGS,
            initial_balance=Decimal('50.00'),
        )

        form = TransferForm(user=self.user)

        self.assertEqual(form.fields['from_account'].initial, default_account)


class AccountTemplateTagTests(TestCase):
    def test_bank_icon_returns_expected_svg_path(self):
        self.assertEqual(get_bank_icon_path(Account.NUBANK), 'images/banks/nubank.svg')
        self.assertEqual(get_bank_icon_path(Account.OTHER), 'images/banks/other.svg')
        self.assertEqual(get_bank_icon_path(None), 'images/banks/other.svg')


class AccountTemplateRenderTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='account-templates@example.com',
            password='secret123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Nubank',
            account_type=Account.CHECKING,
            bank='Nubank',
            bank_code=Account.NUBANK,
            initial_balance=Decimal('250.00'),
            is_default=True,
        )
        self.client.force_login(self.user)

    def test_account_pages_render_bank_icon_and_default_badge(self):
        create_response = self.client.get(reverse('accounts:create'))
        update_response = self.client.get(reverse('accounts:update', args=[self.account.pk]))
        detail_response = self.client.get(reverse('accounts:detail', args=[self.account.pk]))
        list_response = self.client.get(reverse('accounts:list'))

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(list_response.status_code, 200)

        self.assertContains(create_response, 'id="bank-icon-preview"')
        self.assertContains(update_response, 'Usar como conta')
        self.assertContains(detail_response, '/static/images/banks/nubank.svg')
        self.assertContains(list_response, '/static/images/banks/nubank.svg')


class AccountServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='account-services@example.com',
            password='secret123'
        )

    def test_get_default_account_returns_user_default_account(self):
        Account.objects.create(
            user=self.user,
            name='Conta Secundaria',
            account_type=Account.SAVINGS,
            initial_balance=Decimal('100.00'),
        )
        default_account = Account.objects.create(
            user=self.user,
            name='Conta Padrao',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('250.00'),
            is_default=True,
        )

        self.assertEqual(get_default_account(self.user), default_account)

    def test_debit_account_creates_expense_transaction_and_updates_balance(self):
        account = Account.objects.create(
            user=self.user,
            name='Conta Debito',
            account_type=Account.CHECKING,
            bank_code=Account.NUBANK,
            initial_balance=Decimal('200.00'),
        )

        transaction = debit_account(
            account=account,
            amount=Decimal('35.50'),
            description='Deposito em meta'
        )

        account.refresh_from_db()

        self.assertEqual(transaction.transaction_type, Transaction.EXPENSE)
        self.assertEqual(transaction.account, account)
        self.assertEqual(transaction.user, self.user)
        self.assertIn('Transfer', transaction.category.name)
        self.assertTrue(transaction.category.is_default)
        self.assertEqual(account.current_balance, Decimal('164.50'))


class AccountTransferViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='account-transfer@example.com',
            password='secret123'
        )
        self.from_account = Account.objects.create(
            user=self.user,
            name='Conta Origem',
            account_type=Account.CHECKING,
            bank_code=Account.NUBANK,
            initial_balance=Decimal('80.00'),
            is_default=True,
        )
        self.to_account = Account.objects.create(
            user=self.user,
            name='Conta Destino',
            account_type=Account.SAVINGS,
            initial_balance=Decimal('20.00'),
        )
        self.client.force_login(self.user)

    def test_transfer_page_renders_and_exposes_balance_preview_markup(self):
        response = self.client.get(reverse('accounts:transfer'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saldo atual da conta de origem')
        self.assertContains(response, 'data-balance=')

    def test_transfer_view_creates_both_transactions_and_warns_on_negative_balance(self):
        response = self.client.post(
            reverse('accounts:transfer'),
            data={
                'from_account': str(self.from_account.pk),
                'to_account': str(self.to_account.pk),
                'amount': '100.00',
                'description': 'Reserva mensal',
                'date': date.today().isoformat(),
            },
            follow=True,
        )

        self.from_account.refresh_from_db()
        self.to_account.refresh_from_db()
        transactions = Transaction.objects.filter(user=self.user)

        self.assertRedirects(response, reverse('accounts:list'))
        self.assertEqual(transactions.count(), 2)
        self.assertEqual(self.from_account.current_balance, Decimal('-20.00'))
        self.assertEqual(self.to_account.current_balance, Decimal('120.00'))
        self.assertEqual(transactions.filter(transaction_type=Transaction.EXPENSE).count(), 1)
        self.assertEqual(transactions.filter(transaction_type=Transaction.INCOME).count(), 1)
        self.assertContains(response, 'Transfer')
        self.assertContains(response, 'saldo negativo')

    def test_account_list_and_dashboard_show_transfer_shortcuts(self):
        list_response = self.client.get(reverse('accounts:list'))
        dashboard_response = self.client.get(reverse('dashboard'))

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(list_response, reverse('accounts:transfer'))
        self.assertContains(dashboard_response, reverse('accounts:transfer'))
