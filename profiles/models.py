from django.conf import settings
from django.db import models


class Profile(models.Model):
    # OneToOne relationship with User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )

    # Personal information fields
    first_name = models.CharField(
        max_length=150,
        verbose_name='Nome'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Sobrenome'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Nascimento'
    )

    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.user.email
