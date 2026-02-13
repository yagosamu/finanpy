from django.conf import settings
from django.db import models


class Category(models.Model):
    # Constants for choices at the top
    INCOME = 'income'
    EXPENSE = 'expense'
    CATEGORY_TYPE_CHOICES = [
        (INCOME, 'Receita'),
        (EXPENSE, 'Despesa'),
    ]

    # ForeignKey fields first
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Usuário',
        null=True,
        blank=True
    )

    # Regular fields
    name = models.CharField('Nome', max_length=50)
    category_type = models.CharField(
        'Tipo',
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES
    )
    color = models.CharField('Cor', max_length=7)
    is_default = models.BooleanField('Padrão', default=False)
    is_active = models.BooleanField('Ativa', default=True)

    # Timestamp fields last
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_default', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name}'
