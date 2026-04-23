import re
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account
from budgets.models import Budget
from categories.models import Category
from transactions.models import Transaction


class DashboardBudgetIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='dashboard-budgets@example.com',
            password='secret123',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('2000.00'),
        )
        self.food = Category.objects.create(
            user=self.user,
            name='Alimentacao',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )
        self.transport = Category.objects.create(
            user=self.user,
            name='Transporte',
            category_type=Category.EXPENSE,
            color='#f59e0b',
        )
        self.safe = Category.objects.create(
            user=self.user,
            name='Lazer',
            category_type=Category.EXPENSE,
            color='#3b82f6',
        )
        current_month = date.today().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal('100.00'),
            month=current_month,
        )
        Budget.objects.create(
            user=self.user,
            category=self.transport,
            amount=Decimal('200.00'),
            month=current_month,
        )
        Budget.objects.create(
            user=self.user,
            category=self.safe,
            amount=Decimal('500.00'),
            month=current_month,
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.food,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('120.00'),
            date=date.today(),
            description='Mercado',
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.transport,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('170.00'),
            date=date.today(),
            description='Uber',
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.safe,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('100.00'),
            date=date.today(),
            description='Cinema',
        )
        self.client.force_login(self.user)

    def test_dashboard_shows_budget_alerts_card_and_sidebar_link(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orçamentos')
        self.assertContains(response, 'Ver todos os orçamentos')
        self.assertContains(response, 'Alimentacao')
        self.assertContains(response, 'Transporte')
        self.assertContains(response, reverse('budgets:list'))
        self.assertContains(response, 'data-nav="orcamentos"')
        self.assertContains(response, 'ml-auto inline-flex min-w-5')
        self.assertRegex(
            response.content.decode(),
            re.compile(r'<span class="ml-auto inline-flex min-w-5.*?>\s*1\s*</span>', re.S),
        )

    def test_dashboard_shows_budget_empty_state_when_no_budgets(self):
        Budget.objects.filter(user=self.user).delete()

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum orçamento cadastrado')
        self.assertNotContains(response, 'ml-auto inline-flex min-w-5')
