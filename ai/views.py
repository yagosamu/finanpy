import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from openai import AuthenticationError, RateLimitError

from ai.services.analysis_service import analyze_user

logger = logging.getLogger(__name__)


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
        except AuthenticationError:
            messages.error(
                request,
                'Chave de API OpenAI inválida ou expirada. '
                'Verifique a OPENAI_API_KEY no arquivo .env e reinicie o servidor.',
            )
        except RateLimitError:
            messages.error(
                request,
                'Limite de requisições da OpenAI atingido. Tente novamente em alguns minutos.',
            )
        except Exception:
            logger.exception('Erro inesperado ao gerar análise para user_id=%s', request.user.id)
            messages.error(
                request,
                'Não foi possível gerar a análise no momento. Tente novamente em instantes.',
            )

        return redirect('dashboard')
