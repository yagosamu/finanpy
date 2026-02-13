from django import forms
from django.core.exceptions import ValidationError

from .models import Account


class AccountUpdateForm(forms.ModelForm):
    """Form for updating an account (excludes initial_balance)."""

    class Meta:
        model = Account
        fields = ['name', 'account_type', 'bank']
        labels = {
            'name': 'Nome da Conta',
            'account_type': 'Tipo de Conta',
            'bank': 'Banco',
        }
        help_texts = {
            'name': 'Digite um nome descritivo para identificar esta conta',
            'account_type': 'Selecione o tipo de conta bancária',
            'bank': 'Nome do banco ou instituição financeira (opcional)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Minha Conta Corrente',
            }),
            'account_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'bank': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Banco do Brasil',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if name:
            name = name.strip()

            if len(name) < 2:
                raise ValidationError('O nome da conta deve ter pelo menos 2 caracteres.')

            if len(name) > 100:
                raise ValidationError('O nome da conta não pode ter mais de 100 caracteres.')

            # Check uniqueness per user
            if self.user:
                existing = Account.objects.filter(
                    user=self.user,
                    name__iexact=name,
                    is_active=True
                )
                if self.instance and self.instance.pk:
                    existing = existing.exclude(pk=self.instance.pk)
                if existing.exists():
                    raise ValidationError('Você já possui uma conta com este nome.')

        return name

    def clean_bank(self):
        bank = self.cleaned_data.get('bank')

        if bank:
            bank = bank.strip()
            if len(bank) > 100:
                raise ValidationError('O nome do banco não pode ter mais de 100 caracteres.')

        return bank


class AccountForm(forms.ModelForm):
    """Form for creating an account with initial balance."""

    class Meta:
        model = Account
        fields = ['name', 'account_type', 'bank', 'initial_balance']
        labels = {
            'name': 'Nome da Conta',
            'account_type': 'Tipo de Conta',
            'bank': 'Banco',
            'initial_balance': 'Saldo Inicial',
        }
        help_texts = {
            'name': 'Digite um nome descritivo para identificar esta conta',
            'account_type': 'Selecione o tipo de conta bancária',
            'bank': 'Nome do banco ou instituição financeira (opcional)',
            'initial_balance': 'Saldo inicial da conta (pode ser positivo ou negativo)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Minha Conta Corrente',
            }),
            'account_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'bank': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Banco do Brasil',
            }),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0.00',
                'step': '0.01',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if name:
            name = name.strip()

            if len(name) < 2:
                raise ValidationError('O nome da conta deve ter pelo menos 2 caracteres.')

            if len(name) > 100:
                raise ValidationError('O nome da conta não pode ter mais de 100 caracteres.')

            # Check uniqueness per user
            if self.user:
                existing = Account.objects.filter(
                    user=self.user,
                    name__iexact=name,
                    is_active=True
                )
                if self.instance and self.instance.pk:
                    existing = existing.exclude(pk=self.instance.pk)
                if existing.exists():
                    raise ValidationError('Você já possui uma conta com este nome.')

        return name

    def clean_initial_balance(self):
        initial_balance = self.cleaned_data.get('initial_balance')

        if initial_balance is None:
            raise ValidationError('O saldo inicial é obrigatório.')

        if initial_balance > 99999999.99:
            raise ValidationError('O saldo inicial não pode ser maior que R$ 99.999.999,99.')

        if initial_balance < -99999999.99:
            raise ValidationError('O saldo inicial não pode ser menor que -R$ 99.999.999,99.')

        return initial_balance

    def clean_bank(self):
        bank = self.cleaned_data.get('bank')

        if bank:
            bank = bank.strip()
            if len(bank) > 100:
                raise ValidationError('O nome do banco não pode ter mais de 100 caracteres.')

        return bank
