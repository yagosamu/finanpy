from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from categories.models import Category

from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month']
        labels = {
            'category': 'Categoria',
            'amount': 'Limite Mensal',
            'month': 'Mês',
        }
        widgets = {
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'month': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'month',
            }, format='%Y-%m'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['month'].input_formats = ['%Y-%m']
        self.fields['category'].queryset = Category.objects.none()

        if self.user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=self.user) | Q(is_default=True),
                category_type=Category.EXPENSE,
                is_active=True,
            ).order_by('name')

        if self.instance.pk and self.instance.month:
            self.initial['month'] = self.instance.month.strftime('%Y-%m')
        elif not self.is_bound:
            self.initial['month'] = date.today().strftime('%Y-%m')

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise ValidationError('O limite mensal deve ser maior que zero.')
        return amount

    def clean_month(self):
        month = self.cleaned_data.get('month')
        if not month:
            raise ValidationError('O mês é obrigatório.')
        return month.replace(day=1)
