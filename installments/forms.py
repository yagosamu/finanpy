from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from categories.models import Category

from .models import InstallmentPlan


class InstallmentPlanForm(forms.ModelForm):
    class Meta:
        model = InstallmentPlan
        fields = [
            'name',
            'total_amount',
            'installment_count',
            'start_date',
            'category',
            'account',
            'notes',
        ]
        labels = {
            'name': 'Nome',
            'total_amount': 'Valor Total',
            'installment_count': 'Quantidade de Parcelas',
            'start_date': 'Data da Primeira Parcela',
            'category': 'Categoria',
            'account': 'Conta',
            'notes': 'Observações',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Ex.: iPhone 15 Pro - Magazine Luiza',
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0.01',
            }),
            'installment_count': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'min': '2',
                'max': '120',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'date',
            }),
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'account': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Observações opcionais',
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
                category_type=Category.EXPENSE,
            ).order_by('name')
            self.fields['account'].queryset = self.user.accounts.filter(is_active=True).order_by('name')

    def clean_installment_count(self):
        installment_count = self.cleaned_data.get('installment_count')
        if installment_count is None:
            raise ValidationError('A quantidade de parcelas é obrigatória.')
        if not 2 <= installment_count <= 120:
            raise ValidationError('A quantidade de parcelas deve estar entre 2 e 120.')
        return installment_count

    def clean_total_amount(self):
        total_amount = self.cleaned_data.get('total_amount')
        if total_amount is None:
            raise ValidationError('O valor total é obrigatório.')
        if total_amount <= 0:
            raise ValidationError('O valor total deve ser maior que zero.')
        return total_amount
