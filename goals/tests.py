from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account
from goals.forms import GoalDepositForm
from goals.models import Goal
from transactions.models import Transaction


class GoalDepositFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='goals@example.com',
            password='secret123'
        )
        self.default_account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('50.00'),
            is_default=True,
        )
        self.goal = Goal.objects.create(
            user=self.user,
            name='Reserva',
            target_amount=Decimal('500.00'),
            current_amount=Decimal('100.00'),
        )

    def test_goal_deposit_form_prefills_default_source_account(self):
        form = GoalDepositForm(user=self.user)

        self.assertIn('source_account', form.fields)
        self.assertEqual(form.fields['source_account'].initial, self.default_account)

    def test_goal_deposit_creates_expense_transaction_and_warns_on_negative_balance(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('goals:deposit', args=[self.goal.pk]),
            data={
                'amount': '60.00',
                'source_account': str(self.default_account.pk),
            },
            follow=True,
        )

        self.goal.refresh_from_db()
        self.default_account.refresh_from_db()
        messages = [message.message for message in get_messages(response.wsgi_request)]

        self.assertEqual(self.goal.current_amount, Decimal('160.00'))
        self.assertEqual(self.default_account.current_balance, Decimal('-10.00'))
        self.assertTrue(Transaction.objects.filter(
            user=self.user,
            account=self.default_account,
            amount=Decimal('60.00'),
            transaction_type=Transaction.EXPENSE,
        ).exists())
        self.assertIn('Atenção: sua conta ficou com saldo negativo.', messages)
