from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from ai.services.analysis_service import analyze_user


class RunAnalysisView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not settings.OPENAI_API_KEY:
            messages.error(
                request,
                'A análise com IA não está configurada. '
                'Adicione OPENAI_API_KEY ao arquivo .env e reinicie o servidor.',
            )
            return redirect('dashboard')

        try:
            analyze_user(request.user)
            messages.success(request, 'Análise financeira gerada com sucesso!')
        except Exception:
            messages.error(
                request,
                'Não foi possível gerar a análise no momento. Tente novamente em instantes.',
            )

        return redirect('dashboard')
