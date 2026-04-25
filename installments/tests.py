from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

from .forms import InstallmentPlanForm
from .models import Installment, InstallmentPlan
from .views import (
    InstallmentPlanCreateView,
    InstallmentPlanDeleteView,
    InstallmentPlanDetailView,
    InstallmentPlanListView,
)


class InstallmentPlanModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='installments-model@example.com',
            password='secret123',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('5000.00'),
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Eletrônicos',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )

    def test_plan_save_calculates_installment_amount_and_generates_installments(self):
        plan = InstallmentPlan.objects.create(
            user=self.user,
            name='iPhone 15 Pro - Magazine Luiza',
            total_amount=Decimal('3000.00'),
            installment_count=3,
            start_date=date(2026, 4, 10),
            category=self.category,
            account=self.account,
        )

        installments = list(plan.installments.order_by('number'))

        self.assertEqual(plan.installment_amount, Decimal('1000.00'))
        self.assertEqual(len(installments), 3)
        self.assertEqual(installments[0].due_date, date(2026, 4, 10))
        self.assertEqual(installments[1].due_date, date(2026, 5, 10))
        self.assertEqual(installments[2].due_date, date(2026, 6, 10))
        self.assertTrue(all(installment.status == Installment.PENDING for installment in installments))

    def test_plan_properties_reflect_paid_and_remaining_installments(self):
        plan = InstallmentPlan.objects.create(
            user=self.user,
            name='Notebook',
            total_amount=Decimal('1200.00'),
            installment_count=4,
            start_date=date(2026, 4, 5),
            category=self.category,
            account=self.account,
        )
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            amount=Decimal('300.00'),
            date=date(2026, 4, 5),
            description='Parcela 1/4 - Notebook',
        )
        first_installment = plan.installments.get(number=1)
        first_installment.status = Installment.PAID
        first_installment.paid_date = date(2026, 4, 5)
        first_installment.transaction = transaction
        first_installment.save()

        self.assertEqual(plan.paid_count, 1)
        self.assertEqual(plan.remaining_count, 3)
        self.assertEqual(plan.remaining_amount, Decimal('900.00'))
        self.assertEqual(plan.progress_percentage, 25)
        self.assertFalse(plan.is_completed)
        self.assertEqual(plan.next_installment.number, 2)

    def test_installment_is_overdue_when_pending_and_due_date_in_past(self):
        plan = InstallmentPlan.objects.create(
            user=self.user,
            name='TV',
            total_amount=Decimal('900.00'),
            installment_count=3,
            start_date=timezone.localdate() - timedelta(days=90),
            category=self.category,
            account=self.account,
        )
        installment = plan.installments.get(number=1)
        installment.due_date = timezone.localdate() - timedelta(days=1)
        installment.save(update_fields=['due_date'])

        self.assertTrue(installment.is_overdue)


class InstallmentPlanFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='installments-form@example.com',
            password='secret123',
        )
        self.other_user = get_user_model().objects.create_user(
            email='installments-form-other@example.com',
            password='secret123',
        )
        self.active_account = Account.objects.create(
            user=self.user,
            name='Conta Ativa',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('1000.00'),
        )
        Account.objects.create(
            user=self.user,
            name='Conta Inativa',
            account_type=Account.SAVINGS,
            bank_code=Account.INTER,
            initial_balance=Decimal('500.00'),
            is_active=False,
        )
        self.default_category = Category.objects.create(
            user=None,
            name='Compras',
            category_type=Category.EXPENSE,
            color='#22c55e',
            is_default=True,
        )
        self.custom_category = Category.objects.create(
            user=self.user,
            name='Tecnologia',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )
        Category.objects.create(
            user=self.other_user,
            name='Outro Usuário',
            category_type=Category.EXPENSE,
            color='#3b82f6',
        )

    def valid_data(self):
        return {
            'name': 'Notebook Gamer',
            'total_amount': '4500.00',
            'installment_count': 10,
            'start_date': '2026-04-10',
            'category': self.custom_category.pk,
            'account': self.active_account.pk,
            'notes': 'Compra parcelada',
        }

    def test_form_filters_categories_and_active_accounts_by_user(self):
        form = InstallmentPlanForm(user=self.user)

        self.assertQuerySetEqual(
            form.fields['category'].queryset.order_by('name'),
            [self.default_category, self.custom_category],
            transform=lambda category: category,
        )
        self.assertQuerySetEqual(
            form.fields['account'].queryset.order_by('name'),
            [self.active_account],
            transform=lambda account: account,
        )

    def test_form_rejects_invalid_installment_count(self):
        form = InstallmentPlanForm(
            data={**self.valid_data(), 'installment_count': 1},
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('installment_count', form.errors)

    def test_form_rejects_non_positive_total_amount(self):
        form = InstallmentPlanForm(
            data={**self.valid_data(), 'total_amount': '0.00'},
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('total_amount', form.errors)


class InstallmentViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            email='installments-view@example.com',
            password='secret123',
        )
        self.other_user = get_user_model().objects.create_user(
            email='installments-view-other@example.com',
            password='secret123',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('3000.00'),
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Eletrônicos',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )
        self.plan = InstallmentPlan.objects.create(
            user=self.user,
            name='Notebook',
            total_amount=Decimal('1200.00'),
            installment_count=4,
            start_date=timezone.localdate().replace(day=10),
            category=self.category,
            account=self.account,
        )
        self.completed_plan = InstallmentPlan.objects.create(
            user=self.user,
            name='Fone',
            total_amount=Decimal('200.00'),
            installment_count=2,
            start_date=timezone.localdate().replace(day=5),
            category=self.category,
            account=self.account,
        )
        for installment in self.completed_plan.installments.all():
            installment.status = Installment.PAID
            installment.paid_date = timezone.localdate()
            installment.save(update_fields=['status', 'paid_date'])

    def test_list_view_separates_active_and_completed_and_sums_debt(self):
        request = self.factory.get('/parcelamentos/')
        request.user = self.user
        view = InstallmentPlanListView()
        view.setup(request)

        with patch('installments.views.timezone.localdate', return_value=timezone.localdate()):
            queryset = list(view.get_queryset())
            context = view.get_context_data(object_list=queryset)

        self.assertEqual([plan.pk for plan in context['active_plans']], [self.plan.pk])
        self.assertEqual([plan.pk for plan in context['completed_plans']], [self.completed_plan.pk])
        self.assertEqual(context['total_debt'], self.plan.remaining_amount)
        self.assertEqual(context['installments_due_this_month'].count(), 1)

    def test_create_view_passes_request_user_to_form(self):
        request = self.factory.get('/parcelamentos/novo/')
        request.user = self.user
        view = InstallmentPlanCreateView()
        view.setup(request)

        self.assertEqual(view.get_form_kwargs()['user'], self.user)

    def test_detail_view_raises_404_for_non_owner(self):
        request = self.factory.get(f'/parcelamentos/{self.plan.pk}/')
        request.user = self.other_user
        view = InstallmentPlanDetailView()
        view.setup(request, pk=self.plan.pk)

        with self.assertRaises(Http404):
            view.get_object()

    def test_delete_view_is_user_scoped_and_cascades_installments(self):
        self.client.force_login(self.user)
        installment_ids = list(self.plan.installments.values_list('pk', flat=True))

        response = self.client.post(reverse('installments:delete', args=[self.plan.pk]))

        self.assertRedirects(response, reverse('installments:list'), fetch_redirect_response=False)
        self.assertFalse(InstallmentPlan.objects.filter(pk=self.plan.pk).exists())
        self.assertFalse(Installment.objects.filter(pk__in=installment_ids).exists())

    def test_pay_view_creates_expense_transaction_marks_installment_paid_and_updates_balance(self):
        self.client.force_login(self.user)
        installment = self.plan.installments.get(number=1)
        initial_balance = self.account.current_balance

        response = self.client.post(reverse('installments:pay', args=[installment.pk]))

        installment.refresh_from_db()
        self.account.refresh_from_db()

        self.assertRedirects(
            response,
            reverse('installments:detail', args=[self.plan.pk]),
            fetch_redirect_response=False,
        )
        self.assertEqual(installment.status, Installment.PAID)
        self.assertEqual(installment.paid_date, timezone.localdate())
        self.assertIsNotNone(installment.transaction)
        self.assertEqual(installment.transaction.transaction_type, Transaction.EXPENSE)
        self.assertEqual(
            installment.transaction.description,
            f'Parcela {installment.number}/{self.plan.installment_count} - {self.plan.name}',
        )
        self.assertEqual(
            self.account.current_balance,
            initial_balance - installment.amount,
        )


class InstallmentTemplateTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            email='installments-template@example.com',
            password='secret123',
            first_name='Yago',
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Conta Principal',
            account_type=Account.CHECKING,
            bank_code=Account.ITAU,
            initial_balance=Decimal('3000.00'),
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Eletrônicos',
            category_type=Category.EXPENSE,
            color='#ef4444',
        )
        self.plan = InstallmentPlan.objects.create(
            user=self.user,
            name='Notebook',
            total_amount=Decimal('1200.00'),
            installment_count=4,
            start_date=date(2026, 4, 10),
            category=self.category,
            account=self.account,
        )

    def get_request(self, path):
        request = self.factory.get(path)
        request.user = self.user
        request.session = self.client.session
        return request

    def test_view_template_names_use_short_plan_files(self):
        self.assertEqual(InstallmentPlanListView.template_name, 'installments/plan_list.html')
        self.assertEqual(InstallmentPlanCreateView.template_name, 'installments/plan_form.html')
        self.assertEqual(InstallmentPlanDetailView.template_name, 'installments/plan_detail.html')
        self.assertEqual(InstallmentPlanDeleteView.template_name, 'installments/plan_confirm_delete.html')

    def test_plan_list_template_renders_summary_and_collapse_script(self):
        request = self.get_request('/parcelamentos/')
        html = render_to_string(
            'installments/plan_list.html',
            {
                'active_plans': [self.plan],
                'completed_plans': [],
                'total_debt': self.plan.remaining_amount,
                'installments_due_this_month': self.plan.installments.filter(number=1),
            },
            request=request,
        )

        self.assertIn('Parcelamentos', html)
        self.assertIn('Novo Parcelamento', html)
        self.assertIn('Total de dívida ativa', html)
        self.assertIn('completedPlansSection', html)
        self.assertIn('toggleCompletedPlans', html)

    def test_plan_detail_template_renders_installments_table_and_pay_action(self):
        request = self.get_request(f'/parcelamentos/{self.plan.pk}/')
        html = render_to_string(
            'installments/plan_detail.html',
            {
                'plan': self.plan,
                'object': self.plan,
                'installments': self.plan.installments.all(),
            },
            request=request,
        )

        self.assertIn('Dashboard', html)
        self.assertIn('Valor total restante', html)
        self.assertIn('Marcar como paga', html)
        self.assertIn('Parcela', html)

    def test_plan_form_template_renders_preview_script(self):
        request = self.get_request('/parcelamentos/novo/')
        form = InstallmentPlanForm(user=self.user)
        html = render_to_string(
            'installments/plan_form.html',
            {'form': form},
            request=request,
        )

        self.assertIn('Valor por parcela:', html)
        self.assertIn('firstDueDatesPreview', html)
        self.assertIn('installmentAmountPreview', html)
        self.assertIn('Parcelamentos', html)

    def test_plan_confirm_delete_template_renders_warning(self):
        request = self.get_request(f'/parcelamentos/{self.plan.pk}/excluir/')
        html = render_to_string(
            'installments/plan_confirm_delete.html',
            {'object': self.plan},
            request=request,
        )

        self.assertIn('Todas as parcelas serão excluídas. Transações já pagas não serão afetadas.', html)
        self.assertIn('Confirmar exclusão', html)
        self.assertIn('Parcelas restantes', html)
