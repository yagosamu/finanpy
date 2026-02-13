from django.contrib import admin
from django.utils.html import format_html
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'get_account_type_display',
        'bank',
        'formatted_current_balance',
        'is_active',
        'created_at'
    ]
    list_filter = ['account_type', 'is_active']
    search_fields = ['name', 'bank']
    readonly_fields = ['current_balance', 'created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'name', 'account_type', 'bank'),
            'description': 'Dados principais da conta bancária'
        }),
        ('Saldos', {
            'fields': ('initial_balance', 'current_balance'),
            'description': 'O saldo atual é calculado automaticamente com base nas transações'
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Contas inativas não aparecem para o usuário'
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_accounts', 'deactivate_accounts']

    def get_queryset(self, request):
        """Optimize admin list with select_related."""
        return super().get_queryset(request).select_related('user')

    def formatted_current_balance(self, obj):
        """Format current balance as Brazilian currency."""
        value = obj.current_balance
        if value >= 0:
            color = 'green'
        else:
            color = 'red'
        formatted = f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            formatted
        )
    formatted_current_balance.short_description = 'Saldo Atual'
    formatted_current_balance.admin_order_field = 'current_balance'

    @admin.action(description='Ativar contas selecionadas')
    def activate_accounts(self, request, queryset):
        """Activate selected accounts."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} conta(s) ativada(s) com sucesso.'
        )

    @admin.action(description='Desativar contas selecionadas')
    def deactivate_accounts(self, request, queryset):
        """Deactivate selected accounts."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} conta(s) desativada(s) com sucesso.'
        )

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with help texts."""
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['name'].help_text = 'Nome identificador da conta (ex: Nubank, Carteira Principal)'
        form.base_fields['account_type'].help_text = 'Tipo de conta bancária'
        form.base_fields['bank'].help_text = 'Nome do banco (opcional para carteiras e investimentos)'
        form.base_fields['initial_balance'].help_text = 'Saldo inicial ao cadastrar a conta'
        form.base_fields['is_active'].help_text = 'Desmarque para ocultar esta conta do usuário'

        return form
