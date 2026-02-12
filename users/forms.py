from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class SignUpForm(UserCreationForm):
    """
    Form for user registration with email-based authentication.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
        }),
        label='Email',
        help_text='Digite um endereço de email válido.'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'autocomplete': 'new-password',
        }),
        label='Senha',
        help_text='Sua senha deve conter pelo menos 8 caracteres.'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha',
            'autocomplete': 'new-password',
        }),
        label='Confirmação de senha',
        help_text='Digite a mesma senha novamente para confirmação.'
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        """
        Validate that the email is unique and properly formatted.
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()

            if len(email) > 254:
                raise ValidationError('O email não pode ter mais de 254 caracteres.')

            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    'Este email já está cadastrado. Por favor, utilize outro email ou faça login.'
                )
        return email

    def save(self, commit=True):
        """
        Save the user with the email as the username.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that uses email instead of username.
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
            'autofocus': True,
        }),
        label='Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'autocomplete': 'current-password',
        }),
        label='Senha',
    )

    error_messages = {
        'invalid_login': 'Por favor, digite um email e senha corretos. '
                        'Note que ambos os campos podem ser sensíveis a maiúsculas.',
        'inactive': 'Esta conta está inativa.',
    }
