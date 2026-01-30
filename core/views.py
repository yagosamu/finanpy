from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Landing page view."""
    template_name = 'home.html'
