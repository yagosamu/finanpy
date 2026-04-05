from django.conf import settings
from django.db import models


class Goal(models.Model):
    """
    Financial goal with progress tracking.

    Progress is tracked via current_amount vs target_amount.
    is_completed is set automatically when current_amount >= target_amount.
    """

    # Color choices
    GREEN = '#22c55e'
    BLUE = '#3b82f6'
    PURPLE = '#a855f7'
    ORANGE = '#f97316'
    YELLOW = '#eab308'
    RED = '#ef4444'
    PINK = '#ec4899'
    TEAL = '#14b8a6'

    COLOR_CHOICES = [
        (GREEN, 'Verde'),
        (BLUE, 'Azul'),
        (PURPLE, 'Roxo'),
        (ORANGE, 'Laranja'),
        (YELLOW, 'Amarelo'),
        (RED, 'Vermelho'),
        (PINK, 'Rosa'),
        (TEAL, 'Turquesa'),
    ]

    # ForeignKey fields first
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name='Usuário'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        related_name='goals',
        verbose_name='Categoria',
        null=True,
        blank=True
    )

    # Regular fields
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    target_amount = models.DecimalField(
        'Valor Alvo',
        max_digits=12,
        decimal_places=2
    )
    current_amount = models.DecimalField(
        'Valor Acumulado',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    deadline = models.DateField('Prazo', null=True, blank=True)
    color = models.CharField(
        'Cor',
        max_length=7,
        choices=COLOR_CHOICES,
        default=GREEN
    )
    icon = models.CharField('Ícone', max_length=50, blank=True)
    is_completed = models.BooleanField('Concluída', default=False)

    # Timestamp fields last
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    updated_at = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        ordering = ['deadline', 'name']
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['user', 'deadline']),
        ]

    def __str__(self):
        return f'{self.name}'

    @property
    def progress_percentage(self):
        """Return progress as a percentage, capped at 100."""
        if not self.target_amount:
            return 0
        percentage = (self.current_amount / self.target_amount) * 100
        return min(float(percentage), 100)

    @property
    def remaining_amount(self):
        """Return how much is still needed to reach the goal."""
        remaining = self.target_amount - self.current_amount
        return max(remaining, 0)

    def save(self, *args, **kwargs):
        """Auto-set is_completed when current_amount reaches target_amount."""
        if self.current_amount >= self.target_amount:
            self.is_completed = True
        else:
            self.is_completed = False
        super().save(*args, **kwargs)
