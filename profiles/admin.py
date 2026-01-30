from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'first_name', 'last_name', 'phone', 'created_at']
    search_fields = ['user__email', 'first_name', 'last_name', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = [
        ('Usuário', {
            'fields': ['user']
        }),
        ('Informações Pessoais', {
            'fields': ['first_name', 'last_name', 'phone', 'birth_date']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
