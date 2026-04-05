from django.urls import path

from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.GoalListView.as_view(), name='list'),
    path('nova/', views.GoalCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.GoalUpdateView.as_view(), name='update'),
    path('<int:pk>/deletar/', views.GoalDeleteView.as_view(), name='delete'),
    path('<int:pk>/depositar/', views.GoalDepositView.as_view(), name='deposit'),
]
