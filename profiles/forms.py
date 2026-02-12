import re
from datetime import date, timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone', 'birth_date']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'phone': 'Telefone',
            'birth_date': 'Data de Nascimento',
        }
        help_texts = {
            'first_name': 'Digite seu primeiro nome',
            'last_name': 'Digite seu sobrenome completo',
            'phone': 'Formato: (11) 99999-9999 ou 11999999999',
            'birth_date': 'Você deve ter pelo menos 18 anos',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'João',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Silva',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': '(11) 99999-9999',
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'type': 'date',
            }),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if not birth_date:
            return birth_date

        # Check if date is in the past
        today = date.today()
        if birth_date >= today:
            raise ValidationError('A data de nascimento deve estar no passado.')

        # Calculate age
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

        # Check if user is at least 18 years old
        if age < 18:
            raise ValidationError('Você deve ter pelo menos 18 anos.')

        # Optional: Check for unreasonably old dates (e.g., over 120 years)
        if age > 120:
            raise ValidationError('Data de nascimento inválida.')

        return birth_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone:
            return phone

        # Remove all non-digit characters for validation
        phone_digits = re.sub(r'\D', '', phone)

        # Brazilian phone patterns:
        # - 11 digits: 11999999999 (with country code without +)
        # - 11 digits: 11999999999 (DDD + 9 + 8 digits)
        # - 10 digits: 1199999999 (DDD + 8 digits - old format)
        # - 13 digits: 5511999999999 (with country code 55)

        valid_lengths = [10, 11, 13]

        if len(phone_digits) not in valid_lengths:
            raise ValidationError(
                'Telefone inválido. Use o formato: (11) 99999-9999 ou 11999999999'
            )

        # If it has 13 digits, check if it starts with 55 (Brazil country code)
        if len(phone_digits) == 13:
            if not phone_digits.startswith('55'):
                raise ValidationError(
                    'Código de país inválido. Use +55 para números brasileiros.'
                )

        # If it has 11 digits, check if the third digit is 9 (mobile)
        if len(phone_digits) == 11:
            if phone_digits[2] != '9':
                raise ValidationError(
                    'Número de celular inválido. O terceiro dígito deve ser 9.'
                )

        # Return the original format (user can input as they prefer)
        return phone

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name:
            first_name = first_name.strip()

            if len(first_name) < 2:
                raise ValidationError('O nome deve ter pelo menos 2 caracteres.')

            if len(first_name) > 150:
                raise ValidationError('O nome não pode ter mais de 150 caracteres.')

            # Only allow letters, spaces, hyphens, and apostrophes
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', first_name):
                raise ValidationError('O nome deve conter apenas letras, espaços e hífens.')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name:
            last_name = last_name.strip()

            if len(last_name) < 2:
                raise ValidationError('O sobrenome deve ter pelo menos 2 caracteres.')

            if len(last_name) > 150:
                raise ValidationError('O sobrenome não pode ter mais de 150 caracteres.')

            # Only allow letters, spaces, hyphens, and apostrophes
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', last_name):
                raise ValidationError('O sobrenome deve conter apenas letras, espaços e hífens.')

        return last_name
