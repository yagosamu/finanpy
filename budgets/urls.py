from django.urls import path

from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.BudgetListView.as_view(), name='list'),
    path('novo/', views.BudgetCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.BudgetUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.BudgetDeleteView.as_view(), name='delete'),
    path('api/', views.BudgetAPIView.as_view(), name='api'),
]
