from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Landing page view."""
    template_name = 'home.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for authenticated users."""
    template_name = 'dashboard.html'
