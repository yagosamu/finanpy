import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import AccountForm, AccountUpdateForm
from .models import Account

logger = logging.getLogger(__name__)


class AccountListView(LoginRequiredMixin, ListView):
    """List all active accounts for the logged user."""
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        """Return only active accounts for the logged user."""
        return Account.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('name')

    def get_context_data(self, **kwargs):
        """Add total balance to context."""
        context = super().get_context_data(**kwargs)
        total = self.get_queryset().aggregate(
            total=Sum('current_balance')
        )['total']
        context['total_balance'] = total or 0
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    """Create a new account for the logged user."""
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:list')

    def get_form_kwargs(self):
        """Pass user to form for validation."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Associate account to logged user before saving."""
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar conta para o usuário %s', self.request.user.email)
            messages.error(
                self.request,
                'Ocorreu um erro ao criar a conta. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('accounts:list'))
        messages.success(
            self.request,
            f'Conta "{self.object.name}" criada com sucesso!'
        )
        return response


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing account."""
    model = Account
    form_class = AccountUpdateForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:list')

    def get_queryset(self):
        """Return only accounts owned by the logged user."""
        return Account.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        """Pass user to form for validation."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Add success message after update."""
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao atualizar conta %s', self.object.pk)
            messages.error(
                self.request,
                'Ocorreu um erro ao atualizar a conta. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('accounts:list'))
        messages.success(
            self.request,
            f'Conta "{self.object.name}" atualizada com sucesso!'
        )
        return response


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """Soft delete an account (set is_active to False)."""
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:list')

    def get_queryset(self):
        """Return only accounts owned by the logged user."""
        return Account.objects.filter(user=self.request.user)

    def form_valid(self, form):
        """Perform soft delete instead of actual deletion."""
        # Check if account has transactions
        if self.object.transactions.exists():
            messages.error(
                self.request,
                f'A conta "{self.object.name}" possui transações vinculadas e não pode ser excluída. '
                f'Remova as transações antes de excluir a conta.'
            )
            return HttpResponseRedirect(self.get_success_url())

        success_url = self.get_success_url()

        try:
            # Soft delete: set is_active to False
            self.object.is_active = False
            self.object.save()
        except Exception:
            logger.exception('Erro ao excluir conta %s', self.object.pk)
            messages.error(
                self.request,
                'Ocorreu um erro ao excluir a conta. Tente novamente.'
            )
            return HttpResponseRedirect(success_url)

        messages.success(
            self.request,
            f'Conta "{self.object.name}" excluída com sucesso!'
        )

        return HttpResponseRedirect(success_url)


class AccountDetailView(LoginRequiredMixin, DetailView):
    """Show detailed information about an account."""
    model = Account
    template_name = 'accounts/account_detail.html'
    context_object_name = 'account'

    def get_queryset(self):
        """Return only accounts owned by the logged user."""
        return Account.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Add recent transactions to context."""
        context = super().get_context_data(**kwargs)

        # Get last 10 transactions for this account with related data
        context['recent_transactions'] = self.object.transactions.select_related(
            'category'
        ).order_by('-date', '-created_at')[:10]

        return context
