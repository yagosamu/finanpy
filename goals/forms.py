from django import forms
from django.core.exceptions import ValidationError

from .models import Goal


INPUT_STYLE = (
    'w-full px-4 py-2.5 rounded-lg text-sm transition-all duration-150 '
    'bg-[#0a0a0a] border border-[#262626] text-[#f5f5f5] '
    'focus:outline-none focus:border-[#22c55e]'
)

SELECT_STYLE = INPUT_STYLE + ' appearance-none'

TEXTAREA_STYLE = (
    'w-full px-4 py-2.5 rounded-lg text-sm transition-all duration-150 resize-none '
    'bg-[#0a0a0a] border border-[#262626] text-[#f5f5f5] '
    'focus:outline-none focus:border-[#22c55e]'
)


class GoalForm(forms.ModelForm):
    """Form for creating and editing a Goal."""

    class Meta:
        model = Goal
        fields = ['name', 'description', 'target_amount', 'current_amount',
                  'deadline', 'category', 'color', 'icon']
        labels = {
            'name': 'Nome da Meta',
            'description': 'Descrição',
            'target_amount': 'Valor Alvo',
            'current_amount': 'Valor Já Acumulado',
            'deadline': 'Prazo',
            'category': 'Categoria (opcional)',
            'color': 'Cor',
            'icon': 'Ícone (opcional)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Ex: Reserva de emergência',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_STYLE,
                'rows': 3,
                'placeholder': 'Descreva sua meta (opcional)',
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'current_amount': forms.NumberInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'deadline': forms.DateInput(attrs={
                'class': INPUT_STYLE,
                'type': 'date',
            }),
            'category': forms.Select(attrs={
                'class': SELECT_STYLE,
            }),
            'color': forms.Select(attrs={
                'class': SELECT_STYLE,
            }),
            'icon': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Ex: star, home, car (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter category to user's own categories + defaults
        from categories.models import Category
        from django.db.models import Q
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=self.user) | Q(is_default=True),
                is_active=True
            ).order_by('name')
        # Make category not required
        self.fields['category'].required = False
        self.fields['category'].empty_label = 'Nenhuma categoria'

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError('O nome da meta deve ter pelo menos 2 caracteres.')
        if len(name) > 100:
            raise ValidationError('O nome da meta não pode ter mais de 100 caracteres.')
        return name

    def clean_target_amount(self):
        amount = self.cleaned_data.get('target_amount')
        if amount is None:
            raise ValidationError('O valor alvo é obrigatório.')
        if amount <= 0:
            raise ValidationError('O valor alvo deve ser maior que zero.')
        if amount > 99999999.99:
            raise ValidationError('O valor alvo não pode ser maior que R$ 99.999.999,99.')
        return amount

    def clean_current_amount(self):
        amount = self.cleaned_data.get('current_amount')
        if amount is None:
            return 0
        if amount < 0:
            raise ValidationError('O valor acumulado não pode ser negativo.')
        if amount > 99999999.99:
            raise ValidationError('O valor acumulado não pode ser maior que R$ 99.999.999,99.')
        return amount

    def clean(self):
        cleaned_data = super().clean()
        target = cleaned_data.get('target_amount')
        current = cleaned_data.get('current_amount')
        if target and current and current > target:
            raise ValidationError(
                'O valor já acumulado não pode ser maior que o valor alvo.'
            )
        return cleaned_data


class GoalDepositForm(forms.Form):
    """Form for depositing an amount into a goal."""

    amount = forms.DecimalField(
        label='Valor a depositar',
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': INPUT_STYLE,
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01',
        })
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError('O valor do depósito deve ser maior que zero.')
        if amount > 99999999.99:
            raise ValidationError('O valor não pode ser maior que R$ 99.999.999,99.')
        return amount
