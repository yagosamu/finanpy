import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from categories.models import Category
from transactions.models import Transaction

from .forms import (
    AccountForm,
    AccountUpdateForm,
    CardBillPayForm,
    CreditCardForm,
    TransferForm,
)
from .models import Account, CardBill, CreditCard
from .services import debit_account

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


class TransferView(LoginRequiredMixin, FormView):
    """Transfer balance between two user accounts."""

    template_name = 'accounts/transfer.html'
    form_class = TransferForm
    success_url = reverse_lazy('accounts:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        from_account = form.cleaned_data['from_account']
        to_account = form.cleaned_data['to_account']
        amount = form.cleaned_data['amount']
        description = (form.cleaned_data.get('description') or '').strip()
        transfer_date = form.cleaned_data['date']
        message_description = (
            f'Transferencia: {description}' if description else 'Transferencia'
        )
        transfer_category, _ = Category.objects.get_or_create(
            user=None,
            name='Transferência',
            defaults={
                'category_type': Category.EXPENSE,
                'color': '#525252',
                'is_default': True,
                'is_active': True,
            },
        )

        try:
            debit_account(
                from_account,
                amount,
                message_description,
                category=transfer_category,
                date=transfer_date,
            )
            Transaction.objects.create(
                user=self.request.user,
                account=to_account,
                category=transfer_category,
                transaction_type=Transaction.INCOME,
                amount=amount,
                date=transfer_date,
                description=message_description,
            )
        except Exception:
            logger.exception(
                'Erro ao transferir saldo entre contas para o usuario %s',
                self.request.user.email,
            )
            messages.error(
                self.request,
                'Ocorreu um erro ao realizar a transferencia. Tente novamente.',
            )
            return HttpResponseRedirect(self.get_success_url())

        from_account.refresh_from_db()
        if from_account.current_balance < 0:
            messages.warning(self.request, 'Atenção: sua conta ficou com saldo negativo.')

        messages.success(self.request, 'Transferência realizada com sucesso!')
        return super().form_valid(form)


class CardListView(LoginRequiredMixin, ListView):
    model = CreditCard
    template_name = 'accounts/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return CreditCard.objects.filter(
            user=self.request.user,
            is_active=True,
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_card_debt = CardBill.objects.filter(
            credit_card__user=self.request.user,
            credit_card__is_active=True,
            status__in=[CardBill.OPEN, CardBill.CLOSED],
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        context['total_card_debt'] = total_card_debt
        return context


class CardCreateView(LoginRequiredMixin, CreateView):
    model = CreditCard
    form_class = CreditCardForm
    template_name = 'accounts/card_form.html'
    success_url = reverse_lazy('accounts:card_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Cartão "{self.object.name}" criado com sucesso!')
        return response


class CardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CreditCard
    form_class = CreditCardForm
    template_name = 'accounts/card_form.html'
    success_url = reverse_lazy('accounts:card_list')
    context_object_name = 'card'

    def get_queryset(self):
        return CreditCard.objects.all()

    def test_func(self):
        card = self.get_object()
        return card.user == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cartão "{self.object.name}" atualizado com sucesso!')
        return response


class CardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CreditCard
    template_name = 'accounts/card_confirm_delete.html'
    success_url = reverse_lazy('accounts:card_list')
    context_object_name = 'card'

    def get_queryset(self):
        return CreditCard.objects.all()

    def test_func(self):
        card = self.get_object()
        return card.user == self.request.user

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save(update_fields=['is_active'])
        messages.success(self.request, f'Cartão "{self.object.name}" excluído com sucesso!')
        return HttpResponseRedirect(self.get_success_url())


class CardDetailView(LoginRequiredMixin, DetailView):
    model = CreditCard
    template_name = 'accounts/card_detail.html'
    context_object_name = 'card'

    def get_queryset(self):
        return CreditCard.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        try:
            return queryset.get(pk=self.kwargs['pk'])
        except CreditCard.DoesNotExist as exc:
            raise Http404 from exc

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_bill_transactions'] = self.object.transactions.filter(
            date__gte=self.object.current_billing_start,
            date__lte=self.object.current_billing_end,
        ).select_related('category', 'account').order_by('-date', '-created_at')
        context['bill_history'] = self.object.bills.select_related('payment_account')[:6]
        context['payment_form'] = CardBillPayForm(user=self.request.user)
        return context


class CardBillPayView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            card = CreditCard.objects.get(pk=kwargs['pk'], user=request.user)
        except CreditCard.DoesNotExist:
            raise Http404

        form = CardBillPayForm(request.POST, user=request.user)
        if not form.is_valid():
            messages.error(request, 'Selecione uma conta válida para pagar a fatura.')
            return HttpResponseRedirect(reverse_lazy('accounts:card_detail', kwargs={'pk': card.pk}))

        payment_account = form.cleaned_data['payment_account']
        try:
            card.pay_bill(payment_account)
        except Exception:
            logger.exception('Erro ao pagar fatura do cartão %s', card.pk)
            messages.error(request, 'Ocorreu um erro ao pagar a fatura. Tente novamente.')
            return HttpResponseRedirect(reverse_lazy('accounts:card_detail', kwargs={'pk': card.pk}))

        messages.success(request, f'Fatura do cartão "{card.name}" paga com sucesso!')
        return HttpResponseRedirect(reverse_lazy('accounts:card_detail', kwargs={'pk': card.pk}))
