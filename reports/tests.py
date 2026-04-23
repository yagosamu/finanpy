from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import RequestFactory, TestCase

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

from .views import ReportView


class ReportViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            email='reports@example.com',
            password='secret123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='secret123'
        )

        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank='Banco A',
            initial_balance=Decimal('1000.00'),
            current_balance=Decimal('1000.00')
        )
        self.second_account = Account.objects.create(
            user=self.user,
            name='Reserva',
            account_type=Account.SAVINGS,
            bank='Banco B',
            initial_balance=Decimal('500.00'),
            current_balance=Decimal('500.00')
        )
        self.other_account = Account.objects.create(
            user=self.other_user,
            name='Conta Externa',
            account_type=Account.CHECKING,
            bank='Banco C',
            initial_balance=Decimal('300.00'),
            current_balance=Decimal('300.00')
        )

        self.salary_category = Category.objects.create(
            user=self.user,
            name='Salario',
            category_type=Category.INCOME,
            color='#22c55e'
        )
        self.freelance_category = Category.objects.create(
            user=self.user,
            name='Freela',
            category_type=Category.INCOME,
            color='#16a34a'
        )
        self.food_category = Category.objects.create(
            user=self.user,
            name='Alimentacao',
            category_type=Category.EXPENSE,
            color='#ef4444'
        )
        self.housing_category = Category.objects.create(
            user=self.user,
            name='Moradia',
            category_type=Category.EXPENSE,
            color='#f59e0b'
        )
        self.other_category = Category.objects.create(
            user=self.other_user,
            name='Outra',
            category_type=Category.EXPENSE,
            color='#3b82f6'
        )

        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.salary_category,
            transaction_type=Transaction.INCOME,
            amount=Decimal('3000.00'),
            date=date(2026, 4, 5),
            description='Salario abril'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.food_category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('500.00'),
            date=date(2026, 4, 6),
            description='Mercado'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.housing_category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('900.00'),
            date=date(2026, 4, 10),
            description='Aluguel'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.second_account,
            category=self.freelance_category,
            transaction_type=Transaction.INCOME,
            amount=Decimal('1200.00'),
            date=date(2026, 4, 15),
            description='Projeto'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.second_account,
            category=self.food_category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('300.00'),
            date=date(2026, 4, 15),
            description='Restaurante'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.salary_category,
            transaction_type=Transaction.INCOME,
            amount=Decimal('2800.00'),
            date=date(2026, 3, 15),
            description='Salario marco'
        )
        Transaction.objects.create(
            user=self.other_user,
            account=self.other_account,
            category=self.other_category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('999.00'),
            date=date(2026, 4, 12),
            description='Nao deve entrar'
        )

    def _get_context(self, query_string=''):
        request = self.factory.get(f'/relatorios/{query_string}')
        request.user = self.user

        view = ReportView()
        view.setup(request)
        with patch('reports.views.timezone.localdate', return_value=date(2026, 4, 23)):
            return view.get_context_data()

    def test_report_view_builds_context_for_selected_account_and_period(self):
        context = self._get_context('?period=this_month&account=%s' % self.account.pk)

        self.assertEqual(context['period'], 'this_month')
        self.assertEqual(context['date_start'], date(2026, 4, 1))
        self.assertEqual(context['date_end'], date(2026, 4, 30))
        self.assertEqual(context['selected_account'], self.account)
        self.assertEqual(list(context['accounts']), [self.account, self.second_account])

        self.assertEqual(context['total_income'], Decimal('3000.00'))
        self.assertEqual(context['total_expense'], Decimal('1400.00'))
        self.assertEqual(context['net_balance'], Decimal('1600.00'))
        self.assertEqual(context['avg_daily_expense'], Decimal('46.67'))

        self.assertEqual(context['biggest_income'].description, 'Salario abril')
        self.assertEqual(context['biggest_expense'].description, 'Aluguel')

        self.assertEqual(len(context['expense_by_category']), 2)
        self.assertEqual(context['expense_by_category'][0]['name'], 'Moradia')
        self.assertEqual(context['expense_by_category'][0]['total'], Decimal('900.00'))
        self.assertEqual(context['expense_by_category'][0]['percentage'], Decimal('64.29'))
        self.assertEqual(context['expense_by_category'][0]['count'], 1)

        self.assertEqual(len(context['income_by_category']), 1)
        self.assertEqual(context['income_by_category'][0]['name'], 'Salario')
        self.assertEqual(context['income_by_category'][0]['percentage'], Decimal('100.00'))

        self.assertEqual(
            context['daily_evolution'],
            [
                {'date': '2026-04-05', 'income': '3000.00', 'expense': '0.00'},
                {'date': '2026-04-06', 'income': '0.00', 'expense': '500.00'},
                {'date': '2026-04-10', 'income': '0.00', 'expense': '900.00'},
            ]
        )

        self.assertEqual(len(context['by_account']), 2)
        self.assertEqual(context['by_account'][0]['name'], 'Conta Principal')
        self.assertEqual(context['by_account'][0]['period_income'], Decimal('3000.00'))
        self.assertEqual(context['by_account'][0]['period_expense'], Decimal('1400.00'))
        self.assertEqual(context['by_account'][1]['period_income'], Decimal('0.00'))
        self.assertEqual(context['by_account'][1]['period_expense'], Decimal('0.00'))

        self.assertEqual(len(context['top_expenses']), 2)
        self.assertEqual(len(context['top_incomes']), 1)
        self.assertTrue(hasattr(context['top_expenses'][0], 'account'))
        self.assertTrue(hasattr(context['top_expenses'][0], 'category'))

    def test_report_view_returns_safe_empty_state(self):
        empty_user = get_user_model().objects.create_user(
            email='empty@example.com',
            password='secret123'
        )
        request = self.factory.get('/relatorios/')
        request.user = empty_user

        view = ReportView()
        view.setup(request)
        with patch('reports.views.timezone.localdate', return_value=date(2026, 4, 23)):
            context = view.get_context_data()

        self.assertEqual(context['period'], 'this_month')
        self.assertIsNone(context['selected_account'])
        self.assertEqual(list(context['accounts']), [])
        self.assertEqual(context['total_income'], Decimal('0.00'))
        self.assertEqual(context['total_expense'], Decimal('0.00'))
        self.assertEqual(context['net_balance'], Decimal('0.00'))
        self.assertEqual(context['avg_daily_expense'], Decimal('0.00'))
        self.assertIsNone(context['biggest_income'])
        self.assertIsNone(context['biggest_expense'])
        self.assertEqual(context['expense_by_category'], [])
        self.assertEqual(context['income_by_category'], [])
        self.assertEqual(context['daily_evolution'], [])
        self.assertEqual(context['by_account'], [])
        self.assertEqual(list(context['top_expenses']), [])
        self.assertEqual(list(context['top_incomes']), [])

    def test_report_page_renders_chart_hook_and_enabled_sidebar_link(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('reports:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="daily-evolution-data"')
        self.assertContains(response, "document.getElementById('daily-evolution-data').textContent")
        self.assertContains(response, 'id="dailyEvolutionChart"')
        self.assertContains(response, f'href="{reverse("reports:index")}"', html=False)
        self.assertContains(response, 'data-nav="relatorios"')
        self.assertNotContains(response, 'aria-disabled="true"')
        self.assertNotContains(response, 'cursor-not-allowed')
        self.assertNotContains(response, 'Em breve')
