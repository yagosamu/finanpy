import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import Account
from categories.models import Category

from .forms import TransactionForm
from .models import Transaction

logger = logging.getLogger(__name__)


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            user=self.request.user
        ).select_related('account', 'category')

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Filter by transaction type
        transaction_type = self.request.GET.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        # Filter by account
        account = self.request.GET.get('account')
        if account:
            queryset = queryset.filter(account_id=account)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate totals from filtered queryset
        queryset = self.get_queryset()

        total_income = queryset.filter(
            transaction_type=Transaction.INCOME
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = queryset.filter(
            transaction_type=Transaction.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['total_income'] = total_income
        context['total_expense'] = total_expense
        context['balance'] = total_income - total_expense

        # Pass filter values back to template
        context['filter_date_from'] = self.request.GET.get('date_from', '')
        context['filter_date_to'] = self.request.GET.get('date_to', '')
        context['filter_category'] = self.request.GET.get('category', '')
        context['filter_transaction_type'] = self.request.GET.get('transaction_type', '')
        context['filter_account'] = self.request.GET.get('account', '')

        # Pass available accounts and categories for filter dropdowns
        context['available_accounts'] = Account.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('name')

        context['available_categories'] = Category.objects.filter(
            Q(user=self.request.user) | Q(is_default=True),
            is_active=True
        ).order_by('name')

        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar transação para o usuário %s', self.request.user.email)
            messages.error(
                self.request,
                'Ocorreu um erro ao criar a transação. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('transactions:list'))
        messages.success(self.request, 'Transação criada com sucesso!')
        return response


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('account', 'category')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao atualizar transação %s', self.object.pk)
            messages.error(
                self.request,
                'Ocorreu um erro ao atualizar a transação. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('transactions:list'))
        messages.success(self.request, 'Transação atualizada com sucesso!')
        return response


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:list')

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('account', 'category')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao excluir transação %s', self.object.pk)
            messages.error(
                self.request,
                'Ocorreu um erro ao excluir a transação. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('transactions:list'))
        messages.success(self.request, 'Transação excluída com sucesso!')
        return response
