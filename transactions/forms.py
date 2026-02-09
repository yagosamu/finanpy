import json
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'date', 'description', 'account', 'category']
        labels = {
            'transaction_type': 'Tipo de Transação',
            'amount': 'Valor',
            'date': 'Data',
            'description': 'Descrição',
            'account': 'Conta',
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
            }),
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Filter accounts: only user's active accounts
            self.fields['account'].queryset = self.user.accounts.filter(is_active=True)

            # Filter categories: user's categories + default categories, active only
            from categories.models import Category
            categories = Category.objects.filter(
                is_active=True
            ).filter(
                Q(user=self.user) | Q(is_default=True)
            ).select_related('user')

            self.fields['category'].queryset = categories

            # Store categories data as JSON for JS filtering
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
        if amount is not None and amount <= 0:
            raise ValidationError('O valor deve ser maior que zero.')
        return amount

    def clean_date(self):
        transaction_date = self.cleaned_data.get('date')
        if transaction_date and transaction_date > date.today():
            raise ValidationError('A data da transação não pode ser no futuro.')
        return transaction_date

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')

        # Validate category type matches transaction type
        if transaction_type and category:
            if transaction_type != category.category_type:
                raise ValidationError({
                    'category': 'O tipo da categoria deve corresponder ao tipo da transação.'
                })

        return cleaned_data
