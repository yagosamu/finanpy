from datetime import date, timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.test.client import RequestFactory
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

from .forms import RecurrenceForm
from .models import Recurrence
from .views import RecurrenceCreateView, RecurrenceUpdateView


class RecurrenceModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='recurrences@example.com',
            password='secret123',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Assinaturas',
            category_type=Category.EXPENSE,
            color='#eab308',
        )

    def test_is_due_this_month_is_true_when_not_generated_in_current_month(self):
        recurrence = Recurrence.objects.create(
            user=self.user,
            name='Netflix',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('39.90'),
            category=self.category,
            account=self.account,
            day_of_month=15,
            start_date=date.today().replace(day=1),
            last_generated_date=date.today() - timedelta(days=31),
        )

        self.assertTrue(recurrence.is_due_this_month)

    def test_is_due_this_month_is_false_when_already_generated_in_current_month(self):
        recurrence = Recurrence.objects.create(
            user=self.user,
            name='Internet',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('99.90'),
            category=self.category,
            account=self.account,
            day_of_month=10,
            start_date=date.today().replace(day=1),
            last_generated_date=date.today(),
        )

        self.assertFalse(recurrence.is_due_this_month)


class RecurrenceListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='recurrences-list@example.com',
            password='secret123',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
        )
        self.income_category = Category.objects.create(
            user=self.user,
            name='Salário',
            category_type=Category.INCOME,
            color='#22c55e',
        )
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Moradia',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )
        Recurrence.objects.create(
            user=self.user,
            name='Freela mensal',
            transaction_type=Transaction.INCOME,
            amount=Decimal('2500.00'),
            category=self.income_category,
            account=self.account,
            day_of_month=5,
            start_date=date.today().replace(day=1),
        )
        Recurrence.objects.create(
            user=self.user,
            name='Aluguel',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('1200.00'),
            category=self.expense_category,
            account=self.account,
            day_of_month=8,
            start_date=date.today().replace(day=1),
        )
        self.client.force_login(self.user)

    def test_list_view_renders_user_recurrences(self):
        response = self.client.get(reverse('recurrences:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receitas Fixas')
        self.assertContains(response, 'Despesas Fixas')
        self.assertContains(response, 'Freela mensal')
        self.assertContains(response, 'Aluguel')


class RecurrenceFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='recurrence-form@example.com',
            password='secret123',
        )
        self.other_user = get_user_model().objects.create_user(
            email='other-recurrence-form@example.com',
            password='secret123',
        )
        self.active_account = Account.objects.create(
            user=self.user,
            name='Conta Ativa',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
        )
        self.inactive_account = Account.objects.create(
            user=self.user,
            name='Conta Inativa',
            account_type=Account.SAVINGS,
            bank_code=Account.INTER,
            initial_balance=Decimal('500.00'),
            is_active=False,
        )
        self.other_user_account = Account.objects.create(
            user=self.other_user,
            name='Conta Terceiro',
            account_type=Account.CHECKING,
            bank_code=Account.NUBANK,
            initial_balance=Decimal('700.00'),
        )
        self.default_category = Category.objects.create(
            user=None,
            name='Categoria Padrão',
            category_type=Category.EXPENSE,
            color='#22c55e',
            is_default=True,
        )
        self.custom_category = Category.objects.create(
            user=self.user,
            name='Categoria Customizada',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )
        self.inactive_category = Category.objects.create(
            user=self.user,
            name='Categoria Inativa',
            category_type=Category.EXPENSE,
            color='#eab308',
            is_active=False,
        )
        self.other_user_category = Category.objects.create(
            user=self.other_user,
            name='Categoria Terceiro',
            category_type=Category.EXPENSE,
            color='#3b82f6',
        )

    def get_valid_form_data(self):
        return {
            'name': 'Academia',
            'transaction_type': Transaction.EXPENSE,
            'amount': '89.90',
            'category': self.custom_category.pk,
            'account': self.active_account.pk,
            'day_of_month': 12,
            'start_date': '2026-04-01',
            'end_date': '2026-06-01',
        }

    def test_form_filters_categories_and_active_accounts_by_user(self):
        form = RecurrenceForm(user=self.user)

        self.assertQuerySetEqual(
            form.fields['category'].queryset.order_by('name'),
            [self.custom_category, self.default_category],
            transform=lambda category: category,
        )
        self.assertQuerySetEqual(
            form.fields['account'].queryset.order_by('name'),
            [self.active_account],
            transform=lambda account: account,
        )

    def test_form_rejects_day_of_month_above_28(self):
        form = RecurrenceForm(
            data={**self.get_valid_form_data(), 'day_of_month': 29},
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('day_of_month', form.errors)

    def test_form_rejects_end_date_not_after_start_date(self):
        form = RecurrenceForm(
            data={**self.get_valid_form_data(), 'end_date': '2026-04-01'},
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)


class RecurrenceViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='recurrence-view@example.com',
            password='secret123',
        )
        self.factory = RequestFactory()

    def test_create_view_passes_request_user_to_form(self):
        request = self.factory.get('/recorrencias/nova/')
        request.user = self.user
        view = RecurrenceCreateView()
        view.setup(request)

        form_kwargs = view.get_form_kwargs()

        self.assertEqual(form_kwargs['user'], self.user)

    def test_update_view_passes_request_user_to_form(self):
        request = self.factory.get('/recorrencias/1/editar/')
        request.user = self.user
        view = RecurrenceUpdateView()
        view.setup(request)
        view.object = None

        form_kwargs = view.get_form_kwargs()

        self.assertEqual(form_kwargs['user'], self.user)


class GenerateRecurrencesCommandTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='recurrence-command@example.com',
            password='secret123',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Contas Fixas',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )

    def create_recurrence(self, **overrides):
        today = timezone.localdate()
        defaults = {
            'user': self.user,
            'name': 'Aluguel',
            'transaction_type': Transaction.EXPENSE,
            'amount': Decimal('1200.00'),
            'category': self.category,
            'account': self.account,
            'day_of_month': 8,
            'start_date': today.replace(day=1),
        }
        defaults.update(overrides)
        return Recurrence.objects.create(**defaults)

    def test_command_generates_due_recurrences_only_once_for_current_month(self):
        recurrence = self.create_recurrence()
        stdout = StringIO()

        call_command('generate_recurrences', stdout=stdout)
        first_run_output = stdout.getvalue()

        self.assertIn('1 recorrências geradas, 0 com erro', first_run_output)
        self.assertEqual(Transaction.objects.filter(description='Aluguel').count(), 1)

        stdout = StringIO()
        call_command('generate_recurrences', stdout=stdout)

        self.assertIn('0 recorrências geradas, 0 com erro', stdout.getvalue())
        self.assertEqual(Transaction.objects.filter(description='Aluguel').count(), 1)
        recurrence.refresh_from_db()
        self.assertEqual(
            recurrence.last_generated_date.month,
            timezone.localdate().month,
        )

    def test_command_accepts_month_argument_and_generates_for_target_month(self):
        recurrence = self.create_recurrence(
            name='Internet',
            day_of_month=15,
            start_date=date(2026, 4, 1),
        )
        stdout = StringIO()

        call_command('generate_recurrences', '--month', '2026-04', stdout=stdout)

        self.assertIn('1 recorrências geradas, 0 com erro', stdout.getvalue())
        transaction = Transaction.objects.get(description='Internet')
        self.assertEqual(transaction.date, date(2026, 4, 15))
        recurrence.refresh_from_db()
        self.assertEqual(recurrence.last_generated_date, date(2026, 4, 15))


class RecurrenceTemplateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='recurrence-template@example.com',
            password='secret123',
            first_name='Yago',
        )
        self.factory = RequestFactory()
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
        )
        self.income_category = Category.objects.create(
            user=self.user,
            name='Salário',
            category_type=Category.INCOME,
            color='#22c55e',
        )
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Aluguel',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )

    def get_request(self, path):
        request = self.factory.get(path)
        request.user = self.user
        request.session = self.client.session
        return request

    def test_recurrence_form_template_renders_preview_and_filter_script(self):
        form = RecurrenceForm(user=self.user)
        request = self.get_request('/recorrencias/nova/')

        html = render_to_string(
            'recurrences/recurrence_form.html',
            {'form': form, 'object': None},
            request=request,
        )

        self.assertIn('Dashboard', html)
        self.assertIn('Recorrências', html)
        self.assertIn('Nova', html)
        self.assertIn('Será lançado todo dia', html)
        self.assertIn('data-category-type=', html)
        self.assertIn('transactionTypeField', html)
        self.assertIn('categoryField', html)
        self.assertIn('previewText', html)
        self.assertIn('data-nav="recorrencias"', html)

    def test_recurrence_confirm_delete_template_renders_warning(self):
        recurrence = Recurrence.objects.create(
            user=self.user,
            name='Academia',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('99.90'),
            category=self.expense_category,
            account=self.account,
            day_of_month=10,
            start_date=date(2026, 4, 1),
        )
        request = self.get_request('/recorrencias/1/excluir/')

        html = render_to_string(
            'recurrences/recurrence_confirm_delete.html',
            {'object': recurrence},
            request=request,
        )

        self.assertIn('Confirmar desativação', html)
        self.assertIn('A recorrência será desativada e não gerará novos lançamentos.', html)
        self.assertIn('Academia', html)
        self.assertIn('R$', html)
