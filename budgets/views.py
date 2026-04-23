import logging
from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Case, DecimalField, ExpressionWrapper, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from transactions.models import Transaction

from .forms import BudgetForm
from .models import Budget

logger = logging.getLogger(__name__)


def get_month_start(month_value):
    return month_value.replace(day=1)


def get_month_end(month_value):
    return month_value.replace(day=monthrange(month_value.year, month_value.month)[1])


def parse_month_param(month_param, fallback):
    if not month_param:
        return get_month_start(fallback)

    try:
        parsed = date.fromisoformat(f'{month_param}-01')
    except ValueError:
        return get_month_start(fallback)

    return get_month_start(parsed)


def shift_month(month_value, offset):
    total_months = month_value.year * 12 + month_value.month - 1 + offset
    year = total_months // 12
    month = total_months % 12 + 1
    return date(year, month, 1)


def get_budget_queryset(user, month_value):
    month_start = get_month_start(month_value)
    month_end = get_month_end(month_value)
    spent_annotation = Coalesce(
        Sum(
            'category__transactions__amount',
            filter=Q(
                category__transactions__user=user,
                category__transactions__transaction_type=Transaction.EXPENSE,
                category__transactions__date__gte=month_start,
                category__transactions__date__lte=month_end,
            )
        ),
        Value(Decimal('0.00')),
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )
    percentage_base = ExpressionWrapper(
        F('spent') * Value(100) / F('amount'),
        output_field=DecimalField(max_digits=7, decimal_places=2),
    )

    return Budget.objects.filter(
        user=user,
        month=month_start,
    ).select_related('category').annotate(
        spent=spent_annotation,
    ).annotate(
        usage_percentage_value=Case(
            When(amount__lte=0, then=Value(Decimal('0.00'))),
            When(spent__gte=F('amount'), then=Value(Decimal('100.00'))),
            default=percentage_base,
            output_field=DecimalField(max_digits=7, decimal_places=2),
        )
    ).order_by('-usage_percentage_value', 'category__name')


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'

    def get_selected_month(self):
        return parse_month_param(
            self.request.GET.get('month'),
            timezone.localdate(),
        )

    def get_queryset(self):
        return get_budget_queryset(self.request.user, self.get_selected_month())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month_date = self.get_selected_month()
        budgets = context['budgets']
        total_budgeted = sum((budget.amount for budget in budgets), Decimal('0.00'))
        total_spent = sum((budget.spent for budget in budgets), Decimal('0.00'))
        if total_budgeted > 0:
            overall_percentage = min(
                ((total_spent / total_budgeted) * Decimal('100')).quantize(Decimal('0.01')),
                Decimal('100.00')
            )
        else:
            overall_percentage = Decimal('0.00')

        context['current_month'] = current_month_date.strftime('%Y-%m')
        context['current_month_date'] = current_month_date
        context['prev_month'] = shift_month(current_month_date, -1).strftime('%Y-%m')
        context['next_month'] = shift_month(current_month_date, 1).strftime('%Y-%m')
        context['total_budgeted'] = total_budgeted
        context['total_spent'] = total_spent
        context['overall_percentage'] = overall_percentage
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar orçamento para o usuário %s', self.request.user.email)
            messages.error(self.request, 'Ocorreu um erro ao criar o orçamento. Tente novamente.')
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, 'Orçamento criado com sucesso!')
        return response


class BudgetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao atualizar orçamento %s', self.object.pk)
            messages.error(self.request, 'Ocorreu um erro ao atualizar o orçamento. Tente novamente.')
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, 'Orçamento atualizado com sucesso!')
        return response


class BudgetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Budget
    template_name = 'budgets/budget_confirm_delete.html'
    success_url = reverse_lazy('budgets:list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao excluir orçamento %s', self.object.pk)
            messages.error(self.request, 'Ocorreu um erro ao excluir o orçamento. Tente novamente.')
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, 'Orçamento excluído com sucesso!')
        return response


class BudgetAPIView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        current_month = get_month_start(timezone.localdate())
        budgets = get_budget_queryset(request.user, current_month)
        payload = [
            {
                'category_name': budget.category.name,
                'color': budget.category.color,
                'amount': float(budget.amount),
                'spent': float(budget.spent),
                'remaining': float(budget.amount - budget.spent),
                'percentage': float(budget.usage_percentage_value),
            }
            for budget in budgets
        ]
        return JsonResponse(payload, safe=False)
