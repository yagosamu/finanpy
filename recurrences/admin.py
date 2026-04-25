from django.contrib import admin

from .models import Recurrence


@admin.register(Recurrence)
class RecurrenceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'transaction_type',
        'amount',
        'day_of_month',
        'is_active',
        'last_generated_date',
    )
    list_filter = ('transaction_type', 'is_active')
    search_fields = ('name', 'user__email')
