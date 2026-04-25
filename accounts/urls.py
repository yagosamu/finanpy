from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='list'),
    path('nova/', views.AccountCreateView.as_view(), name='create'),
    path('transferir/', views.TransferView.as_view(), name='transfer'),
    path('cartoes/', views.CardListView.as_view(), name='card_list'),
    path('cartoes/novo/', views.CardCreateView.as_view(), name='card_create'),
    path('cartoes/<int:pk>/', views.CardDetailView.as_view(), name='card_detail'),
    path('cartoes/<int:pk>/editar/', views.CardUpdateView.as_view(), name='card_update'),
    path('cartoes/<int:pk>/excluir/', views.CardDeleteView.as_view(), name='card_delete'),
    path('cartoes/<int:pk>/pagar/', views.CardBillPayView.as_view(), name='card_bill_pay'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.AccountUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.AccountDeleteView.as_view(), name='delete'),
]
