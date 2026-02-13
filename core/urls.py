"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from core.views import DashboardView, HomeView

handler403 = 'core.views.custom_403'
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('users.urls')),
    path('', include('profiles.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('categorias/', include('categories.urls', namespace='categories')),
    path('transacoes/', include('transactions.urls', namespace='transactions')),
]

# Debug-only routes
if settings.DEBUG:
    urlpatterns += [
        path('test-tailwind/', TemplateView.as_view(template_name='test_tailwind.html'), name='test_tailwind'),
    ]
