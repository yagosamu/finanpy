from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from categories.models import Category

from .models import Recurrence


class RecurrenceForm(forms.ModelForm):
    class Meta:
        model = Recurrence
        fields = [
            'name',
            'transaction_type',
            'amount',
            'category',
            'account',
            'day_of_month',
            'start_date',
            'end_date',
        ]
        labels = {
            'name': 'Nome',
            'transaction_type': 'Tipo de Transação',
            'amount': 'Valor',
            'category': 'Categoria',
            'account': 'Conta',
            'day_of_month': 'Dia do Mês',
            'start_date': 'Data de Início',
            'end_date': 'Data de Término',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Ex.: Aluguel',
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0.01',
            }),
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'account': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'day_of_month': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'min': '1',
                'max': '28',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.none()
        self.fields['account'].queryset = self._meta.model.account.field.remote_field.model.objects.none()

        if self.user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=self.user) | Q(is_default=True),
                is_active=True,
            ).order_by('name')
            self.fields['account'].queryset = self.user.accounts.filter(
                is_active=True,
            ).order_by('name')

    def clean_day_of_month(self):
        day_of_month = self.cleaned_data.get('day_of_month')
        if day_of_month is None:
            raise ValidationError('O dia do mês é obrigatório.')
        if not 1 <= day_of_month <= 28:
            raise ValidationError('O dia do mês deve estar entre 1 e 28.')
        return day_of_month

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date and end_date <= start_date:
            self.add_error('end_date', 'A data de término deve ser maior que a data de início.')

        return cleaned_data
