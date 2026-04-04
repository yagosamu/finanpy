from django.conf import settings
from django.db import models
from django.db.models import CASCADE


class AIAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='ai_analyses',
        verbose_name='usuário',
    )
    content = models.TextField(verbose_name='análise completa')
    summary = models.CharField(max_length=500, verbose_name='resumo')
    period_start = models.DateField(verbose_name='início do período')
    period_end = models.DateField(verbose_name='fim do período')
    tokens_used = models.IntegerField(default=0, verbose_name='tokens utilizados')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Análise de IA'
        verbose_name_plural = 'Análises de IA'

    def __str__(self):
        return f'Análise de {self.user} — {self.period_start} a {self.period_end}'
