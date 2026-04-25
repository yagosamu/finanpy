from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from .forms import (
    AccountForm,
    AccountUpdateForm,
    CardBillPayForm,
    CreditCardForm,
    TransferForm,
)
from .models import Account, CardBill, CreditCard
from .services import debit_account, get_default_account
from .templatetags.account_tags import get_bank_icon_path
from .views import CardDetailView, CardListView
from categories.models import Category
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


class CreditCardModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='credit-card@example.com',
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
        self.card = CreditCard.objects.create(
            user=self.user,
            name='Nubank Roxinho',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('5000.00'),
            closing_day=10,
            due_day=20,
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Cartão',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )

    def test_credit_card_current_bill_amount_and_available_limit_use_current_cycle(self):
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('300.00'),
            date=self.card.current_billing_start,
            description='Compra parcelada',
            credit_card=self.card,
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('120.00'),
            date=self.card.current_billing_end,
            description='Compra dentro da fatura',
            credit_card=self.card,
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('999.99'),
            date=self.card.current_billing_start.replace(day=1),
            description='Compra fora da fatura',
            credit_card=self.card,
        )

        self.assertEqual(self.card.current_bill_amount, Decimal('420.00'))
        self.assertEqual(self.card.available_limit, Decimal('4580.00'))
        self.assertLessEqual(self.card.current_billing_start, self.card.current_billing_end)
        self.assertGreaterEqual(self.card.next_due_date, date.today())

    def test_card_bill_pay_bill_creates_expense_transaction_and_marks_bill_paid(self):
        bill = CardBill.objects.create(
            credit_card=self.card,
            reference_month=date.today().replace(day=1),
            closing_date=self.card.current_billing_end,
            due_date=self.card.next_due_date,
            total_amount=Decimal('450.00'),
            status=CardBill.CLOSED,
        )

        bill.pay_bill(self.account)
        bill.refresh_from_db()
        self.account.refresh_from_db()

        self.assertEqual(bill.status, CardBill.PAID)
        self.assertEqual(bill.payment_date, date.today())
        self.assertEqual(bill.payment_account, self.account)
        payment_transaction = Transaction.objects.get(
            user=self.user,
            account=self.account,
            amount=Decimal('450.00'),
            transaction_type=Transaction.EXPENSE,
        )
        self.assertIn(self.card.name, payment_transaction.description)
        self.assertEqual(self.account.current_balance, Decimal('550.00'))


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


class CreditCardFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='credit-card-forms@example.com',
            password='secret123'
        )
        self.active_account = Account.objects.create(
            user=self.user,
            name='Conta Ativa',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('100.00'),
        )
        self.inactive_account = Account.objects.create(
            user=self.user,
            name='Conta Inativa',
            account_type=Account.SAVINGS,
            initial_balance=Decimal('50.00'),
            is_active=False,
        )

    def test_credit_card_form_uses_color_input_and_validates_day_range(self):
        form = CreditCardForm(
            data={
                'name': 'Cartao Teste',
                'bank_code': Account.NUBANK,
                'credit_limit': '3000.00',
                'closing_day': '0',
                'due_day': '29',
                'color': '#22c55e',
            }
        )

        self.assertEqual(form.fields['color'].widget.input_type, 'color')
        self.assertFalse(form.is_valid())
        self.assertIn('closing_day', form.errors)
        self.assertIn('due_day', form.errors)

    def test_card_bill_pay_form_filters_only_active_user_accounts(self):
        other_user = get_user_model().objects.create_user(
            email='other-bill@example.com',
            password='secret123'
        )
        Account.objects.create(
            user=other_user,
            name='Conta Alheia',
            account_type=Account.CHECKING,
            bank_code=Account.NUBANK,
            initial_balance=Decimal('10.00'),
        )

        form = CardBillPayForm(user=self.user)

        self.assertQuerySetEqual(
            form.fields['payment_account'].queryset.order_by('pk'),
            [self.active_account],
            transform=lambda account: account,
        )


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


class CreditCardViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='credit-card-views@example.com',
            password='secret123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='credit-card-views-other@example.com',
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
        self.card = CreditCard.objects.create(
            user=self.user,
            name='Cartao Principal',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('4000.00'),
            closing_day=10,
            due_day=20,
        )
        self.bill = CardBill.objects.create(
            credit_card=self.card,
            reference_month=date.today().replace(day=1),
            closing_date=self.card.current_billing_end,
            due_date=self.card.next_due_date,
            total_amount=Decimal('250.00'),
            status=CardBill.CLOSED,
        )
        self.client.force_login(self.user)
        self.factory = RequestFactory()

    def test_card_create_view_creates_card_for_logged_user(self):
        response = self.client.post(
            reverse('accounts:card_create'),
            data={
                'name': 'Cartao Backup',
                'bank_code': Account.ITAU,
                'credit_limit': '5000.00',
                'closing_day': '12',
                'due_day': '22',
                'color': '#16a34a',
            },
        )

        self.assertRedirects(
            response,
            reverse('accounts:card_list'),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            CreditCard.objects.filter(
                user=self.user,
                name='Cartao Backup',
                is_active=True,
            ).exists()
        )

    def test_card_update_view_denies_access_to_other_user(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse('accounts:card_update', args=[self.card.pk]),
            data={
                'name': 'Nao Pode',
                'bank_code': Account.ITAU,
                'credit_limit': '5000.00',
                'closing_day': '12',
                'due_day': '22',
                'color': '#16a34a',
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_card_delete_view_soft_deletes_card(self):
        response = self.client.post(reverse('accounts:card_delete', args=[self.card.pk]))

        self.assertRedirects(
            response,
            reverse('accounts:card_list'),
            fetch_redirect_response=False,
        )
        self.card.refresh_from_db()
        self.assertFalse(self.card.is_active)

    def test_card_bill_pay_view_pays_bill_and_redirects_to_detail(self):
        response = self.client.post(
            reverse('accounts:card_bill_pay', args=[self.card.pk]),
            data={'payment_account': str(self.account.pk)},
        )

        self.bill.refresh_from_db()
        self.account.refresh_from_db()

        self.assertRedirects(
            response,
            reverse('accounts:card_detail', args=[self.card.pk]),
            fetch_redirect_response=False,
        )
        self.assertEqual(self.bill.status, CardBill.PAID)
        self.assertEqual(self.bill.payment_account, self.account)
        self.assertEqual(self.account.current_balance, Decimal('750.00'))

    def test_card_detail_view_raises_404_for_non_owner(self):
        request = self.factory.get(reverse('accounts:card_detail', args=[self.card.pk]))
        request.user = self.other_user
        view = CardDetailView()
        view.request = request
        view.kwargs = {'pk': self.card.pk}

        with self.assertRaises(Http404):
            view.get_object()

    def test_card_list_view_context_includes_active_cards_and_total_debt(self):
        inactive_card = CreditCard.objects.create(
            user=self.user,
            name='Cartao Inativo',
            bank_code=Account.C6,
            credit_limit=Decimal('2000.00'),
            closing_day=5,
            due_day=15,
            is_active=False,
        )
        CardBill.objects.create(
            credit_card=inactive_card,
            reference_month=date.today().replace(day=1),
            closing_date=inactive_card.current_billing_end,
            due_date=inactive_card.next_due_date,
            total_amount=Decimal('900.00'),
            status=CardBill.OPEN,
        )
        request = self.factory.get(reverse('accounts:card_list'))
        request.user = self.user
        view = CardListView()
        view.request = request
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(list(context['cards']), [self.card])
        self.assertEqual(context['total_card_debt'], Decimal('250.00'))

    def test_card_pages_render_expected_credit_card_sections(self):
        list_response = self.client.get(reverse('accounts:card_list'))
        detail_response = self.client.get(reverse('accounts:card_detail', args=[self.card.pk]))
        create_response = self.client.get(reverse('accounts:card_create'))
        update_response = self.client.get(reverse('accounts:card_update', args=[self.card.pk]))

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)

        self.assertContains(list_response, 'Cartões de Crédito')
        self.assertContains(list_response, reverse('accounts:card_create'))
        self.assertContains(detail_response, 'Pagar fatura')
        self.assertContains(detail_response, 'Histórico de faturas')
        self.assertContains(create_response, 'Sua fatura fecha todo dia')
        self.assertContains(update_response, 'Sua fatura fecha todo dia')
