from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'date',
        'get_transaction_type_display',
        'formatted_amount',
        'category',
        'account',
        'user',
        'created_at'
    ]
    list_filter = ['transaction_type', 'category', 'account', 'date']
    search_fields = ['description']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'account', 'category', 'transaction_type'),
            'description': 'Dados principais da transação'
        }),
        ('Valores', {
            'fields': ('amount', 'date', 'description'),
            'description': 'Valor e detalhes da transação'
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Informações de auditoria'
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related for FK relationships."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'account', 'category')

    def formatted_amount(self, obj):
        """Format amount as Brazilian currency with color based on transaction type."""
        value = obj.amount

        # Green for income, red for expense
        if obj.transaction_type == Transaction.INCOME:
            color = 'green'
        else:
            color = 'red'

        # Format as Brazilian currency: R$ 1.234,56
        formatted = f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            formatted
        )
    formatted_amount.short_description = 'Valor'
    formatted_amount.admin_order_field = 'amount'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Add help text for foreign key fields."""
        if db_field.name == 'account':
            kwargs['help_text'] = 'Selecione a conta bancária associada a esta transação'
        elif db_field.name == 'category':
            kwargs['help_text'] = 'Selecione a categoria que melhor descreve esta transação'
        elif db_field.name == 'user':
            kwargs['help_text'] = 'Usuário responsável por esta transação'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
