import re
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account, CreditCard
from budgets.models import Budget
from categories.models import Category
from installments.models import InstallmentPlan
from recurrences.models import Recurrence
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

    def test_dashboard_shows_pending_recurrence_alert_and_sidebar_badge(self):
        due_recurrence = Recurrence.objects.create(
            user=self.user,
            name='Netflix',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('39.90'),
            category=self.food,
            account=self.account,
            day_of_month=15,
            start_date=date.today().replace(day=1),
        )
        Recurrence.objects.create(
            user=self.user,
            name='Spotify',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('21.90'),
            category=self.transport,
            account=self.account,
            day_of_month=20,
            start_date=date.today().replace(day=1),
            last_generated_date=date.today(),
        )

        response = self.client.get(reverse('dashboard'))

        self.assertTrue(due_recurrence.is_due_this_month)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lançar agora')
        self.assertContains(response, reverse('recurrences:list'))
        self.assertContains(response, 'data-nav="recorrencias"')
        self.assertContains(response, 'Recorrências')
        self.assertContains(response, 'background:rgba(234,179,8,0.12)')
        self.assertRegex(
            response.content.decode(),
            re.compile(r'<span class="ml-auto inline-flex min-w-5.*?>\s*1\s*</span>', re.S),
        )

    def test_sidebar_recurrence_badge_is_available_outside_dashboard(self):
        Recurrence.objects.create(
            user=self.user,
            name='Internet',
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('99.90'),
            category=self.food,
            account=self.account,
            day_of_month=10,
            start_date=date.today().replace(day=1),
        )

        response = self.client.get(reverse('budgets:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-nav="recorrencias"')
        self.assertContains(response, reverse('recurrences:list'))
        self.assertRegex(
            response.content.decode(),
            re.compile(r'<span class="ml-auto inline-flex min-w-5.*?>\s*1\s*</span>', re.S),
        )

    def test_dashboard_shows_installments_month_card_with_upcoming_installments(self):
        plan = InstallmentPlan.objects.create(
            user=self.user,
            name='Notebook Gamer',
            total_amount=Decimal('1200.00'),
            installment_count=4,
            start_date=date.today().replace(day=5),
            category=self.food,
            account=self.account,
        )
        later_plan = InstallmentPlan.objects.create(
            user=self.user,
            name='TV 4K',
            total_amount=Decimal('900.00'),
            installment_count=3,
            start_date=date.today().replace(day=20),
            category=self.transport,
            account=self.account,
        )
        later_plan.installments.filter(number=1).update(amount=Decimal('300.00'))
        plan.installments.filter(number=1).update(amount=Decimal('300.00'))

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Parcelas do Mês')
        self.assertContains(response, 'Notebook Gamer')
        self.assertContains(response, 'TV 4K')
        self.assertContains(response, reverse('installments:list'))
        self.assertContains(response, 'Ver todos os parcelamentos')

    def test_dashboard_shows_installments_empty_state_when_no_due_installments(self):
        next_month = date.today().replace(day=1)
        if next_month.month == 12:
            next_month = next_month.replace(year=next_month.year + 1, month=1)
        else:
            next_month = next_month.replace(month=next_month.month + 1)

        InstallmentPlan.objects.create(
            user=self.user,
            name='Celular',
            total_amount=Decimal('800.00'),
            installment_count=4,
            start_date=next_month.replace(day=5),
            category=self.food,
            account=self.account,
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma parcela vencendo neste mês.')

    def test_dashboard_shows_credit_cards_summary_card(self):
        main_card = CreditCard.objects.create(
            user=self.user,
            name='Nubank Roxinho',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('5000.00'),
            closing_day=10,
            due_day=20,
        )
        secondary_card = CreditCard.objects.create(
            user=self.user,
            name='Cartao Viagem',
            bank_code=Account.ITAU,
            credit_limit=Decimal('3000.00'),
            closing_day=12,
            due_day=25,
        )
        card_category = Category.objects.create(
            user=self.user,
            name='Compras no Cartao',
            category_type=Category.EXPENSE,
            color='#8b5cf6',
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=card_category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('420.00'),
            date=main_card.current_billing_start,
            description='Notebook',
            credit_card=main_card,
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=card_category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('180.00'),
            date=secondary_card.current_billing_start,
            description='Hotel',
            credit_card=secondary_card,
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cartões de Crédito')
        self.assertContains(response, 'Nubank Roxinho')
        self.assertContains(response, 'Cartao Viagem')
        self.assertContains(response, reverse('accounts:card_list'))
        self.assertContains(response, 'Ver cartões')

    def test_dashboard_shows_credit_cards_empty_state_when_no_open_bills(self):
        CreditCard.objects.create(
            user=self.user,
            name='Cartao Sem Uso',
            bank_code=Account.NUBANK,
            credit_limit=Decimal('2500.00'),
            closing_day=8,
            due_day=18,
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum cartão com fatura aberta no momento.')

    def test_sidebar_positions_credit_cards_below_accounts(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode()

        self.assertContains(response, 'data-nav="cartoes"')
        self.assertContains(response, reverse('accounts:card_list'))
        self.assertLess(
            content.index('data-nav="accounts"'),
            content.index('data-nav="cartoes"'),
        )
