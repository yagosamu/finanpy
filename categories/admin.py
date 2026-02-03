from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Category


class CategoryAdminForm(forms.ModelForm):
    """Form customizado para usar widget HTML5 color picker."""

    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
        help_texts = {
            'name': 'Nome da categoria (máximo 50 caracteres)',
            'category_type': 'Selecione se é uma categoria de Receita ou Despesa',
            'color': 'Escolha uma cor para identificar visualmente a categoria',
            'is_default': 'Categorias padrão são criadas automaticamente para novos usuários',
            'is_active': 'Desmarque para desativar a categoria sem excluí-la',
            'user': 'Deixe em branco para criar uma categoria padrão do sistema',
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Category."""

    form = CategoryAdminForm

    list_display = [
        'color_preview',
        'name',
        'category_type',
        'is_default',
        'is_active',
        'get_user_display',
    ]

    list_filter = [
        'category_type',
        'is_default',
        'is_active',
    ]

    search_fields = [
        'name',
    ]

    ordering = ['category_type', 'name']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'name', 'category_type')
        }),
        ('Aparência', {
            'fields': ('color',),
            'description': 'Configure a cor que representa visualmente esta categoria'
        }),
        ('Configurações', {
            'fields': ('is_default', 'is_active'),
            'description': 'Controle o comportamento e disponibilidade da categoria'
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Informações de auditoria'
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def color_preview(self, obj):
        """
        Exibe um quadrado colorido mostrando a cor da categoria.

        Args:
            obj: Instância do modelo Category

        Returns:
            HTML string com preview da cor
        """
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; '
                'border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'

    color_preview.short_description = 'Cor'

    def get_user_display(self, obj):
        """
        Exibe o usuário ou 'Sistema' para categorias padrão.

        Args:
            obj: Instância do modelo Category

        Returns:
            String com o nome do usuário ou 'Sistema'
        """
        if obj.is_default or obj.user is None:
            return format_html('<strong>Sistema</strong>')
        return obj.user.email if hasattr(obj.user, 'email') else str(obj.user)

    get_user_display.short_description = 'Usuário'
    get_user_display.admin_order_field = 'user'

    def get_queryset(self, request):
        """
        Otimiza queryset com select_related para evitar N+1 queries.

        Args:
            request: HttpRequest object

        Returns:
            QuerySet otimizado
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')
