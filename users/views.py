from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomAuthenticationForm, SignUpForm


class SignUpView(CreateView):
    """
    View for user registration.
    After successful signup, automatically logs the user in.
    """
    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """
        If the form is valid, save the user and log them in.
        """
        response = super().form_valid(form)
        # Automatically log the user in after successful signup
        login(self.request, self.object)
        messages.success(
            self.request,
            f'Bem-vindo(a), {self.object.email}! Sua conta foi criada com sucesso.'
        )
        return response

    def form_invalid(self, form):
        """
        If the form is invalid, show an error message.
        """
        messages.error(
            self.request,
            'Ocorreu um erro ao criar sua conta. Por favor, verifique os dados e tente novamente.'
        )
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """
    Custom login view that uses email instead of username.
    """
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Redirect to dashboard after successful login.
        """
        return reverse_lazy('dashboard')

    def form_valid(self, form):
        """
        If the form is valid, log the user in and show a success message.
        """
        messages.success(
            self.request,
            f'Bem-vindo(a) de volta, {form.get_user().email}!'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, show an error message.
        """
        messages.error(
            self.request,
            'Email ou senha incorretos. Por favor, tente novamente.'
        )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Custom logout view with success message.
    """
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        """
        Add a success message when the user logs out.
        """
        if request.user.is_authenticated:
            messages.success(
                request,
                'Você saiu da sua conta com sucesso. Até logo!'
            )
        return super().dispatch(request, *args, **kwargs)
