from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('perfil/', views.ProfileDetailView.as_view(), name='profile'),
    path('perfil/editar/', views.ProfileUpdateView.as_view(), name='profile_edit'),
]
