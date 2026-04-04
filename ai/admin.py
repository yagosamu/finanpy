from django.contrib import admin

from .models import AIAnalysis


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'summary', 'period_start', 'period_end', 'tokens_used', 'created_at']
    list_filter = ['period_start', 'created_at']
    search_fields = ['user__email', 'content', 'summary']
    readonly_fields = ['created_at', 'tokens_used']
