# Padroes de Codigo

## Estilo Python

O codigo deve seguir PEP 8 com as seguintes especificacoes:

### Aspas

Usar **aspas simples** para strings:

```python
# Correto
name = 'Finanpy'
message = 'Transacao criada com sucesso'

# Incorreto
name = "Finanpy"
```

### Idioma

- **Codigo em ingles** (variaveis, funcoes, classes)
- **Interface em portugues** (textos exibidos ao usuario)

```python
# Correto
class Transaction(models.Model):
    description = models.CharField(verbose_name='Descricao')

# Incorreto
class Transacao(models.Model):
    descricao = models.CharField(verbose_name='Description')
```

### Imports

Organizar imports na seguinte ordem:

1. Biblioteca padrao Python
2. Bibliotecas de terceiros
3. Imports locais do Django
4. Imports do projeto

```python
import datetime
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model

from accounts.models import Account
```

### Models

```python
class Transaction(models.Model):
    # Choices como constantes de classe
    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [
        (INCOME, 'Receita'),
        (EXPENSE, 'Despesa'),
    ]

    # Campos
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transacao'
        verbose_name_plural = 'Transacoes'

    def __str__(self):
        return f'{self.description} - R$ {self.amount}'
```

### Views

Usar Class-Based Views com mixins:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
```

### Forms

```python
from django import forms

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'account', 'description', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0,00'
            }),
        }
```

## Convencoes de Nomenclatura

| Tipo | Convencao | Exemplo |
|------|-----------|---------|
| Classes | PascalCase | `TransactionForm` |
| Funcoes/Metodos | snake_case | `get_balance()` |
| Variaveis | snake_case | `total_amount` |
| Constantes | UPPER_SNAKE_CASE | `MAX_AMOUNT` |
| Templates | snake_case | `transaction_list.html` |
| URLs | kebab-case | `/transacoes/nova/` |

## Boas Praticas

### Queries

Usar `select_related` e `prefetch_related` para otimizar queries:

```python
# Correto
transactions = Transaction.objects.select_related('account', 'category').filter(user=user)

# Evitar N+1 queries
for t in transactions:
    print(t.account.name)  # Nao faz query adicional
```

### Validacoes

Validar dados em multiplas camadas:

1. Frontend (JavaScript)
2. Forms Django
3. Models (validators)

```python
from django.core.validators import MinValueValidator

class Transaction(models.Model):
    amount = models.DecimalField(
        validators=[MinValueValidator(Decimal('0.01'))]
    )
```

### Seguranca

- Sempre verificar ownership antes de update/delete
- Usar `LoginRequiredMixin` em views protegidas
- Nunca expor dados de outros usuarios

```python
def get_queryset(self):
    # Sempre filtrar por usuario
    return self.model.objects.filter(user=self.request.user)
```
