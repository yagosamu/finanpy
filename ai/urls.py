from django.urls import path

from ai.views import RunAnalysisView

app_name = 'ai'

urlpatterns = [
    path('analisar/', RunAnalysisView.as_view(), name='run_analysis'),
]
