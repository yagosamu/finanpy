from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from .forms import ProfileForm
from .models import Profile


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """Display the current user's profile."""

    model = Profile
    template_name = 'profiles/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Edit the current user's profile."""

    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_edit.html'
    success_url = reverse_lazy('profiles:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)
