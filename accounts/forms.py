from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .services import get_default_account
from .models import Account, CreditCard


class AccountUpdateForm(forms.ModelForm):
    """Form for updating an account (excludes initial_balance)."""

    class Meta:
        model = Account
        fields = ['name', 'account_type', 'bank', 'bank_code', 'is_default']
        labels = {
            'name': 'Nome da Conta',
            'account_type': 'Tipo de Conta',
            'bank': 'Banco',
            'bank_code': 'Banco Vinculado',
            'is_default': 'Usar como conta padrão',
        }
        help_texts = {
            'name': 'Digite um nome descritivo para identificar esta conta',
            'account_type': 'Selecione o tipo de conta bancária',
            'bank': 'Nome do banco ou instituição financeira (opcional)',
            'bank_code': 'Selecione o banco principal desta conta',
            'is_default': 'Esta conta será usada como padrão no sistema',
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
            'bank_code': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['bank_code'].required = False
        self.fields['is_default'].required = False

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

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        bank_code = cleaned_data.get('bank_code')

        if account_type == Account.CHECKING and not bank_code:
            self.add_error('bank_code', 'Selecione o banco para contas correntes.')

        return cleaned_data


class AccountForm(forms.ModelForm):
    """Form for creating an account with initial balance."""

    class Meta:
        model = Account
        fields = ['name', 'account_type', 'bank', 'bank_code', 'initial_balance', 'is_default']
        labels = {
            'name': 'Nome da Conta',
            'account_type': 'Tipo de Conta',
            'bank': 'Banco',
            'bank_code': 'Banco Vinculado',
            'initial_balance': 'Saldo Inicial',
            'is_default': 'Usar como conta padrão',
        }
        help_texts = {
            'name': 'Digite um nome descritivo para identificar esta conta',
            'account_type': 'Selecione o tipo de conta bancária',
            'bank': 'Nome do banco ou instituição financeira (opcional)',
            'bank_code': 'Selecione o banco principal desta conta',
            'initial_balance': 'Saldo inicial da conta (pode ser positivo ou negativo)',
            'is_default': 'Esta conta será usada como padrão no sistema',
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
            'bank_code': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['bank_code'].required = False
        self.fields['is_default'].required = False

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

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        bank_code = cleaned_data.get('bank_code')

        if account_type == Account.CHECKING and not bank_code:
            self.add_error('bank_code', 'Selecione o banco para contas correntes.')

        return cleaned_data


class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(
        label='Conta de origem',
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
    )
    to_account = forms.ModelChoiceField(
        label='Conta de destino',
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
    )
    amount = forms.DecimalField(
        label='Valor',
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01',
        }),
    )
    description = forms.CharField(
        label='Descricao',
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Ex: Reserva mensal',
        }),
    )
    date = forms.DateField(
        label='Data',
        initial=date.today,
        widget=forms.DateInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'type': 'date',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            accounts = Account.objects.filter(
                user=self.user,
                is_active=True
            ).order_by('name')
            self.fields['from_account'].queryset = accounts
            self.fields['to_account'].queryset = accounts
            if not self.is_bound:
                self.fields['from_account'].initial = get_default_account(self.user)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise ValidationError('O valor da transferencia deve ser maior que zero.')
        return amount

    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')

        if from_account and to_account and from_account == to_account:
            raise ValidationError('Selecione contas diferentes para a transferencia.')

        return cleaned_data


class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['name', 'bank_code', 'credit_limit', 'closing_day', 'due_day', 'color']
        labels = {
            'name': 'Nome do Cartão',
            'bank_code': 'Banco',
            'credit_limit': 'Limite de Crédito',
            'closing_day': 'Dia de Fechamento',
            'due_day': 'Dia de Vencimento',
            'color': 'Cor',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Nubank Roxinho',
            }),
            'bank_code': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'closing_day': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'min': '1',
                'max': '28',
            }),
            'due_day': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'min': '1',
                'max': '28',
            }),
            'color': forms.TextInput(attrs={
                'class': 'mt-1 block h-11 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'color',
            }),
        }
    def clean_closing_day(self):
        closing_day = self.cleaned_data.get('closing_day')
        if closing_day is None or not 1 <= closing_day <= 28:
            raise ValidationError('O dia de fechamento deve estar entre 1 e 28.')
        return closing_day

    def clean_due_day(self):
        due_day = self.cleaned_data.get('due_day')
        if due_day is None or not 1 <= due_day <= 28:
            raise ValidationError('O dia de vencimento deve estar entre 1 e 28.')
        return due_day


class CardBillPayForm(forms.Form):
    payment_account = forms.ModelChoiceField(
        label='Conta de Pagamento',
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['payment_account'].queryset = Account.objects.filter(
                user=self.user,
                is_active=True,
            ).order_by('name')
