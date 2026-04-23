import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.services import debit_account

from .forms import GoalDepositForm, GoalForm
from .models import Goal

logger = logging.getLogger(__name__)


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/goal_list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return Goal.objects.filter(
            user=self.request.user
        ).select_related('category').order_by('is_completed', 'deadline', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goals = self.get_queryset()
        context['total_goals'] = goals.count()
        context['active_goals'] = goals.filter(is_completed=False).count()
        context['completed_goals'] = goals.filter(is_completed=True).count()
        context['deposit_form'] = GoalDepositForm(user=self.request.user)
        context['today'] = date.today()
        return context


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'goals/goal_form.html'
    success_url = reverse_lazy('goals:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar meta para o usuário %s', self.request.user.email)
            messages.error(self.request, 'Ocorreu um erro ao criar a meta. Tente novamente.')
            return HttpResponseRedirect(reverse_lazy('goals:list'))
        messages.success(self.request, f'Meta "{self.object.name}" criada com sucesso!')
        return response


class GoalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = 'goals/goal_form.html'
    success_url = reverse_lazy('goals:list')

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao atualizar meta %s', self.object.pk)
            messages.error(self.request, 'Ocorreu um erro ao atualizar a meta. Tente novamente.')
            return HttpResponseRedirect(reverse_lazy('goals:list'))
        messages.success(self.request, f'Meta "{self.object.name}" atualizada com sucesso!')
        return response


class GoalDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Goal
    template_name = 'goals/goal_confirm_delete.html'
    success_url = reverse_lazy('goals:list')

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def form_valid(self, form):
        goal_name = self.object.name
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao excluir meta %s', self.object.pk)
            messages.error(self.request, 'Ocorreu um erro ao excluir a meta. Tente novamente.')
            return HttpResponseRedirect(reverse_lazy('goals:list'))
        messages.success(self.request, f'Meta "{goal_name}" excluída com sucesso!')
        return response


class GoalDepositView(LoginRequiredMixin, View):
    """POST-only view: adds amount to goal's current_amount."""

    http_method_names = ['post']

    def get_form_kwargs(self):
        return {
            'data': self.request.POST,
            'user': self.request.user,
        }

    def post(self, request, pk, *args, **kwargs):
        goal = Goal.objects.filter(user=request.user, pk=pk).first()
        if not goal:
            messages.error(request, 'Meta não encontrada.')
            return HttpResponseRedirect(reverse_lazy('goals:list'))

        form = GoalDepositForm(**self.get_form_kwargs())
        if form.is_valid():
            amount = form.cleaned_data['amount']
            source_account = form.cleaned_data['source_account']
            description = f'Depósito na meta "{goal.name}"'
            goal.current_amount += amount
            try:
                debit_account(source_account, amount, description)
                goal.save()
            except Exception:
                logger.exception('Erro ao depositar na meta %s', pk)
                messages.error(request, 'Ocorreu um erro ao registrar o depósito. Tente novamente.')
                return HttpResponseRedirect(reverse_lazy('goals:list'))

            source_account.refresh_from_db()
            if source_account.current_balance < 0:
                messages.warning(request, 'Atenção: sua conta ficou com saldo negativo.')

            if goal.is_completed:
                messages.success(
                    request,
                    f'Parabéns! Meta "{goal.name}" concluída! R$ {amount:,.2f} depositado.'
                )
            else:
                remaining = goal.target_amount - goal.current_amount
                messages.success(
                    request,
                    f'R$ {amount:,.2f} depositado em "{goal.name}". '
                    f'Faltam R$ {remaining:,.2f} para atingir a meta.'
                )
        else:
            messages.error(request, 'Valor inválido. Por favor, informe um valor positivo.')

        return HttpResponseRedirect(reverse_lazy('goals:list'))
