import json
import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Category


# Suggested colors for categories
SUGGESTED_COLORS = [
    '#EF4444',  # Red
    '#F97316',  # Orange
    '#F59E0B',  # Amber
    '#EAB308',  # Yellow
    '#84CC16',  # Lime
    '#22C55E',  # Green
    '#10B981',  # Emerald
    '#14B8A6',  # Teal
    '#06B6D4',  # Cyan
    '#0EA5E9',  # Sky
    '#3B82F6',  # Blue
    '#6366F1',  # Indigo
    '#8B5CF6',  # Violet
    '#A855F7',  # Purple
    '#D946EF',  # Fuchsia
    '#EC4899',  # Pink
    '#F43F5E',  # Rose
    '#64748B',  # Slate
]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'color']
        labels = {
            'name': 'Nome da Categoria',
            'category_type': 'Tipo',
            'color': 'Cor',
        }
        help_texts = {
            'name': 'Digite um nome descritivo para a categoria',
            'category_type': 'Selecione se é uma categoria de receita ou despesa',
            'color': 'Escolha uma cor para identificar visualmente a categoria',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Alimentação',
            }),
            'category_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'mt-1 h-10 w-20 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 cursor-pointer',
                'data-suggested-colors': json.dumps(SUGGESTED_COLORS),
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if name:
            name = name.strip()

            if len(name) < 2:
                raise ValidationError('O nome da categoria deve ter pelo menos 2 caracteres.')

            # Check for uniqueness among user's categories
            if self.user:
                # Get existing categories for this user (excluding current instance if updating)
                user_categories = Category.objects.filter(user=self.user, name__iexact=name)
                if self.instance and self.instance.pk:
                    user_categories = user_categories.exclude(pk=self.instance.pk)

                if user_categories.exists():
                    raise ValidationError('Você já possui uma categoria com este nome.')

            # Check if name conflicts with default categories
            default_categories = Category.objects.filter(is_default=True, name__iexact=name)
            if self.instance and self.instance.pk:
                default_categories = default_categories.exclude(pk=self.instance.pk)

            if default_categories.exists():
                raise ValidationError('Já existe uma categoria padrão com este nome.')

        return name

    def clean_color(self):
        color = self.cleaned_data.get('color')

        if color:
            color = color.strip().upper()

            # Validate hexadecimal color format (#RRGGBB)
            hex_pattern = re.compile(r'^#[0-9A-F]{6}$')
            if not hex_pattern.match(color):
                raise ValidationError('A cor deve estar no formato hexadecimal (#RRGGBB). Exemplo: #EF4444')

        return color

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category_type = cleaned_data.get('category_type')

        # Additional validation: check uniqueness considering category_type
        if name and category_type and self.user:
            # Check if a category with the same name and type already exists
            existing = Category.objects.filter(
                user=self.user,
                name__iexact=name,
                category_type=category_type
            )

            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError('Já existe uma categoria com este nome e tipo.')

        return cleaned_data
