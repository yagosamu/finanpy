from django.urls import path

from .views import (
    InstallmentPayView,
    InstallmentPlanCreateView,
    InstallmentPlanDeleteView,
    InstallmentPlanDetailView,
    InstallmentPlanListView,
)

app_name = 'installments'

urlpatterns = [
    path('', InstallmentPlanListView.as_view(), name='list'),
    path('novo/', InstallmentPlanCreateView.as_view(), name='create'),
    path('<int:pk>/', InstallmentPlanDetailView.as_view(), name='detail'),
    path('<int:pk>/excluir/', InstallmentPlanDeleteView.as_view(), name='delete'),
    path('parcela/<int:pk>/pagar/', InstallmentPayView.as_view(), name='pay'),
]
