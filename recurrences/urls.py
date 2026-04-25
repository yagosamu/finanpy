from django.urls import path

from .views import RecurrenceListView

app_name = 'recurrences'

urlpatterns = [
    path('', RecurrenceListView.as_view(), name='list'),
]
