import json
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from accounts.services import get_default_account
from accounts.models import CreditCard

from .models import Transaction


class TransactionForm(forms.ModelForm):
    """
    Form for creating/editing transactions.

    Filters accounts and categories by user. Serializes category data
    to JSON (data_categories attribute) for client-side type filtering.
    Validates category type matches transaction type.
    """

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'date', 'description', 'account', 'credit_card', 'category']
        labels = {
            'transaction_type': 'Tipo de Transação',
            'amount': 'Valor',
            'date': 'Data',
            'description': 'Descrição',
            'account': 'Conta',
            'credit_card': 'Cartão de Crédito',
            'category': 'Categoria',
        }
        help_texts = {
            'amount': 'Valor da transação em reais',
            'description': 'Informações adicionais sobre a transação (opcional)',
        }
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0.01',
            }),
            'date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'date',
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Descrição da transação (opcional)',
                'rows': 3,
            }),
            'account': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'data-account-field': 'true',
            }),
            'credit_card': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'data-credit-card-field': 'true',
            }),
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with user-scoped querysets and category JSON data."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['account'].queryset = self.user.accounts.filter(is_active=True)
            if not self.is_bound and not getattr(self.instance, 'pk', None):
                self.fields['account'].initial = get_default_account(self.user)
            self.fields['credit_card'].queryset = CreditCard.objects.filter(
                user=self.user,
                is_active=True,
            ).order_by('name')
            self.fields['credit_card'].required = False
            self.fields['credit_card'].empty_label = 'Débito em conta (padrão)'

            from categories.models import Category
            categories = Category.objects.filter(
                is_active=True
            ).filter(
                Q(user=self.user) | Q(is_default=True)
            ).select_related('user')

            self.fields['category'].queryset = categories

            categories_data = []
            for category in categories:
                categories_data.append({
                    'id': category.id,
                    'name': category.name,
                    'type': category.category_type,
                    'color': category.color,
                })

            self.fields['category'].widget.attrs['data_categories'] = json.dumps(categories_data)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError('O valor é obrigatório.')
        if amount <= 0:
            raise ValidationError('O valor deve ser maior que zero.')
        if amount > 99999999.99:
            raise ValidationError('O valor não pode ser maior que R$ 99.999.999,99.')
        return amount

    def clean_date(self):
        transaction_date = self.cleaned_data.get('date')
        if not transaction_date:
            raise ValidationError('A data é obrigatória.')
        if transaction_date > date.today():
            raise ValidationError('A data da transação não pode ser no futuro.')
        min_date = date.today().replace(year=date.today().year - 10)
        if transaction_date < min_date:
            raise ValidationError('A data não pode ser anterior a 10 anos atrás.')
        return transaction_date

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            if len(description) > 500:
                raise ValidationError('A descrição não pode ter mais de 500 caracteres.')
        return description or ''

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        account = cleaned_data.get('account')
        credit_card = cleaned_data.get('credit_card')

        if transaction_type and category:
            if transaction_type != category.category_type:
                raise ValidationError({
                    'category': 'O tipo da categoria deve corresponder ao tipo da transação.'
                })

        if account and self.user and account.user != self.user:
            raise ValidationError({
                'account': 'Conta inválida.'
            })

        if category and self.user:
            if category.user is not None and category.user != self.user:
                raise ValidationError({
                    'category': 'Categoria inválida.'
                })

        if credit_card and self.user and credit_card.user != self.user:
            raise ValidationError({
                'credit_card': 'Cartão inválido.'
            })

        return cleaned_data
