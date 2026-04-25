import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from transactions.models import Transaction

from .forms import InstallmentPlanForm
from .models import Installment, InstallmentPlan

logger = logging.getLogger(__name__)


class InstallmentPlanListView(LoginRequiredMixin, ListView):
    model = InstallmentPlan
    template_name = 'installments/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return InstallmentPlan.objects.filter(
            user=self.request.user,
        ).select_related('account', 'category').prefetch_related('installments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = list(context['plans'])
        active_plans = [plan for plan in plans if not plan.is_completed]
        completed_plans = [plan for plan in plans if plan.is_completed]
        today = timezone.localdate()

        context['active_plans'] = active_plans
        context['completed_plans'] = completed_plans
        context['total_debt'] = sum(
            (plan.remaining_amount for plan in active_plans),
            Decimal('0.00'),
        )
        context['installments_due_this_month'] = Installment.objects.filter(
            plan__user=self.request.user,
            status=Installment.PENDING,
            due_date__year=today.year,
            due_date__month=today.month,
        ).select_related('plan').order_by('due_date', 'number')
        return context


class InstallmentPlanCreateView(LoginRequiredMixin, CreateView):
    model = InstallmentPlan
    form_class = InstallmentPlanForm
    template_name = 'installments/plan_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('installments:detail', args=[self.object.pk])

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar parcelamento para o usuário %s', self.request.user.email)
            messages.error(self.request, 'Ocorreu um erro ao criar o parcelamento. Tente novamente.')
            return HttpResponseRedirect(reverse_lazy('installments:list'))
        messages.success(self.request, f'Parcelamento "{self.object.name}" criado com sucesso!')
        return response


class InstallmentPlanDetailView(LoginRequiredMixin, DetailView):
    model = InstallmentPlan
    template_name = 'installments/plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return InstallmentPlan.objects.select_related('account', 'category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404('Parcelamento não encontrado.')
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['installments'] = self.object.installments.select_related('transaction').order_by('number')
        return context


class InstallmentPlanDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = InstallmentPlan
    template_name = 'installments/plan_confirm_delete.html'
    success_url = reverse_lazy('installments:list')

    def get_queryset(self):
        return InstallmentPlan.objects.filter(user=self.request.user)

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        plan_name = self.object.name
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao excluir parcelamento %s', self.object.pk)
            messages.error(self.request, 'Ocorreu um erro ao excluir o parcelamento. Tente novamente.')
            return HttpResponseRedirect(self.success_url)
        messages.success(self.request, f'Parcelamento "{plan_name}" excluído com sucesso!')
        return response


class InstallmentPayView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        installment = get_object_or_404(
            Installment.objects.select_related('plan', 'plan__account', 'plan__category'),
            pk=pk,
            plan__user=request.user,
        )

        if installment.status != Installment.PENDING:
            messages.error(request, 'Esta parcela não está pendente.')
            return HttpResponseRedirect(reverse('installments:detail', args=[installment.plan.pk]))

        transaction = Transaction.objects.create(
            user=request.user,
            account=installment.plan.account,
            category=installment.plan.category,
            transaction_type=Transaction.EXPENSE,
            amount=installment.amount,
            date=timezone.localdate(),
            description=(
                f'Parcela {installment.number}/{installment.plan.installment_count} - '
                f'{installment.plan.name}'
            ),
        )
        installment.status = Installment.PAID
        installment.paid_date = timezone.localdate()
        installment.transaction = transaction
        installment.save(update_fields=['status', 'paid_date', 'transaction'])

        messages.success(request, 'Parcela registrada com sucesso.')
        return HttpResponseRedirect(reverse('installments:detail', args=[installment.plan.pk]))
