from decimal import Decimal
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic import CreateView, UpdateView

from transactions.models import Transaction

from .forms import RecurrenceForm
from .models import Recurrence
from .services import get_pending_recurrences_count

logger = logging.getLogger(__name__)


class RecurrenceListView(LoginRequiredMixin, ListView):
    model = Recurrence
    template_name = 'recurrences/recurrence_list.html'
    context_object_name = 'recurrences'

    def get_queryset(self):
        return Recurrence.objects.filter(
            user=self.request.user,
            is_active=True,
        ).select_related('category', 'account').order_by('transaction_type', 'day_of_month', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recurrences = list(context['recurrences'])
        context['income_recurrences'] = [
            recurrence for recurrence in recurrences
            if recurrence.transaction_type == Transaction.INCOME
        ]
        context['expense_recurrences'] = [
            recurrence for recurrence in recurrences
            if recurrence.transaction_type == Transaction.EXPENSE
        ]
        context['fixed_income_total'] = sum(
            (recurrence.amount for recurrence in context['income_recurrences']),
            Decimal('0.00'),
        )
        context['fixed_expense_total'] = sum(
            (recurrence.amount for recurrence in context['expense_recurrences']),
            Decimal('0.00'),
        )
        context['pending_recurrences_count'] = get_pending_recurrences_count(self.request.user)
        return context


class RecurrenceCreateView(LoginRequiredMixin, CreateView):
    model = Recurrence
    form_class = RecurrenceForm
    template_name = 'recurrences/recurrence_form.html'
    success_url = reverse_lazy('recurrences:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar recorrência para o usuário %s', self.request.user.email)
            messages.error(self.request, 'Ocorreu um erro ao criar a recorrência. Tente novamente.')
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, f'Recorrência "{self.object.name}" criada com sucesso!')
        return response


class RecurrenceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recurrence
    form_class = RecurrenceForm
    template_name = 'recurrences/recurrence_form.html'
    success_url = reverse_lazy('recurrences:list')

    def get_queryset(self):
        return Recurrence.objects.filter(user=self.request.user).select_related('category', 'account')

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
            logger.exception('Erro ao atualizar recorrência %s', self.object.pk)
            messages.error(self.request, 'Ocorreu um erro ao atualizar a recorrência. Tente novamente.')
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, f'Recorrência "{self.object.name}" atualizada com sucesso!')
        return response
