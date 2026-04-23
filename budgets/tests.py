from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

from .forms import BudgetForm
from .models import Budget
from .views import BudgetListView


class BudgetModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='budgets-model@example.com',
            password='secret123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00')
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Moradia',
            category_type=Category.EXPENSE,
            color='#ef4444'
        )
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('800.00'),
            month=date(2026, 4, 1),
        )

    def test_budget_properties_are_calculated_from_month_transactions(self):
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('300.00'),
            date=date(2026, 4, 5),
            description='Aluguel'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('250.00'),
            date=date(2026, 4, 20),
            description='Condominio'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.INCOME,
            amount=Decimal('999.00'),
            date=date(2026, 4, 10),
            description='Nao entra'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('111.00'),
            date=date(2026, 5, 1),
            description='Nao entra'
        )

        self.assertEqual(self.budget.spent_amount, Decimal('550.00'))
        self.assertEqual(self.budget.remaining_amount, Decimal('250.00'))
        self.assertEqual(self.budget.usage_percentage, Decimal('68.75'))
        self.assertFalse(self.budget.is_exceeded)


class BudgetFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='budgets-form@example.com',
            password='secret123'
        )
        self.default_expense = Category.objects.create(
            user=None,
            name='Transporte',
            category_type=Category.EXPENSE,
            color='#f59e0b',
            is_default=True,
        )
        self.user_expense = Category.objects.create(
            user=self.user,
            name='Mercado',
            category_type=Category.EXPENSE,
            color='#ef4444'
        )
        Category.objects.create(
            user=self.user,
            name='Salario',
            category_type=Category.INCOME,
            color='#22c55e'
        )

    def test_form_filters_only_expense_categories_and_converts_month_input(self):
        form = BudgetForm(
            data={
                'category': str(self.user_expense.pk),
                'amount': '500.00',
                'month': '2026-04',
            },
            user=self.user,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(list(form.fields['category'].queryset), [self.user_expense, self.default_expense])
        self.assertEqual(form.cleaned_data['month'], date(2026, 4, 1))

    def test_form_rejects_non_positive_amount(self):
        form = BudgetForm(
            data={
                'category': str(self.user_expense.pk),
                'amount': '0.00',
                'month': '2026-04',
            },
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)


class BudgetViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            email='budgets-view@example.com',
            password='secret123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='budgets-other@example.com',
            password='secret123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1200.00')
        )
        self.food = Category.objects.create(
            user=self.user,
            name='Alimentacao',
            category_type=Category.EXPENSE,
            color='#ef4444'
        )
        self.transport = Category.objects.create(
            user=self.user,
            name='Transporte',
            category_type=Category.EXPENSE,
            color='#f59e0b'
        )
        self.other_category = Category.objects.create(
            user=self.other_user,
            name='Outra',
            category_type=Category.EXPENSE,
            color='#3b82f6'
        )
        self.food_budget = Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal('600.00'),
            month=date(2026, 4, 1),
        )
        self.transport_budget = Budget.objects.create(
            user=self.user,
            category=self.transport,
            amount=Decimal('300.00'),
            month=date(2026, 4, 1),
        )
        Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal('999.00'),
            month=date(2026, 4, 1),
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.food,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('450.00'),
            date=date(2026, 4, 10),
            description='Mercado'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.transport,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('120.00'),
            date=date(2026, 4, 12),
            description='Uber'
        )
        self.client.force_login(self.user)

    def test_budget_list_view_filters_selected_month_and_orders_by_usage(self):
        request = self.factory.get('/orcamentos/?month=2026-04')
        request.user = self.user

        view = BudgetListView()
        view.setup(request)

        with patch('budgets.views.timezone.localdate', return_value=date(2026, 4, 23)):
            queryset = list(view.get_queryset())
            context = view.get_context_data(object_list=queryset)

        self.assertEqual([budget.pk for budget in queryset], [self.food_budget.pk, self.transport_budget.pk])
        self.assertEqual(context['current_month'], '2026-04')
        self.assertEqual(context['prev_month'], '2026-03')
        self.assertEqual(context['next_month'], '2026-05')
        self.assertEqual(queryset[0].spent, Decimal('450.00'))
        self.assertEqual(queryset[1].spent, Decimal('120.00'))

    def test_crud_and_api_are_user_scoped(self):
        create_response = self.client.post(
            reverse('budgets:create'),
            data={
                'category': str(self.food.pk),
                'amount': '700.00',
                'month': '2026-05',
            },
        )
        created_budget = Budget.objects.get(
            user=self.user,
            category=self.food,
            month=date(2026, 5, 1),
        )

        update_response = self.client.post(
            reverse('budgets:update', args=[created_budget.pk]),
            data={
                'category': str(self.food.pk),
                'amount': '900.00',
                'month': '2026-05',
            },
        )
        created_budget.refresh_from_db()

        delete_response = self.client.post(
            reverse('budgets:delete', args=[created_budget.pk]),
        )

        api_response = self.client.get(reverse('budgets:api'))
        self.client.force_login(self.other_user)
        forbidden_update = self.client.get(reverse('budgets:update', args=[self.food_budget.pk]))
        forbidden_delete = self.client.get(reverse('budgets:delete', args=[self.food_budget.pk]))

        self.assertRedirects(create_response, reverse('budgets:list'), fetch_redirect_response=False)
        self.assertRedirects(update_response, reverse('budgets:list'), fetch_redirect_response=False)
        self.assertEqual(created_budget.amount, Decimal('900.00'))
        self.assertRedirects(delete_response, reverse('budgets:list'), fetch_redirect_response=False)
        self.assertFalse(Budget.objects.filter(pk=created_budget.pk).exists())

        self.assertEqual(api_response.status_code, 200)
        payload = api_response.json()
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]['category_name'], 'Alimentacao')
        self.assertEqual(payload[0]['spent'], 450.0)
        self.assertEqual(payload[0]['remaining'], 150.0)
        self.assertEqual(payload[0]['percentage'], 75.0)

        self.assertEqual(forbidden_update.status_code, 404)
        self.assertEqual(forbidden_delete.status_code, 404)
