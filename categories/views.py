import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CategoryForm
from .models import Category

logger = logging.getLogger(__name__)


class CategoryListView(LoginRequiredMixin, ListView):
    """List default categories and user's custom categories."""
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """Return default categories and user's custom categories."""
        return Category.objects.filter(
            Q(is_default=True, user=None) | Q(user=self.request.user),
            is_active=True
        ).order_by('name')

    def get_context_data(self, **kwargs):
        """Separate categories by type (income/expense) in context."""
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        context['income_categories'] = queryset.filter(
            category_type=Category.INCOME
        )
        context['expense_categories'] = queryset.filter(
            category_type=Category.EXPENSE
        )

        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create a new custom category for the logged user."""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:list')

    def get_form_kwargs(self):
        """Pass user to form for validation."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Associate category to logged user before saving."""
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao criar categoria para o usuário %s', self.request.user.email)
            messages.error(
                self.request,
                'Ocorreu um erro ao criar a categoria. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('categories:list'))
        messages.success(
            self.request,
            f'Categoria "{self.object.name}" criada com sucesso!'
        )
        return response


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing non-default category."""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:list')

    def get_form_kwargs(self):
        """Pass user to form for validation."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        """Return only non-default categories owned by the logged user."""
        return Category.objects.filter(
            user=self.request.user,
            is_default=False
        )

    def form_valid(self, form):
        """Add success message after update."""
        try:
            response = super().form_valid(form)
        except Exception:
            logger.exception('Erro ao atualizar categoria %s', self.object.pk)
            messages.error(
                self.request,
                'Ocorreu um erro ao atualizar a categoria. Tente novamente.'
            )
            return HttpResponseRedirect(reverse_lazy('categories:list'))
        messages.success(
            self.request,
            f'Categoria "{self.object.name}" atualizada com sucesso!'
        )
        return response


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Soft delete a non-default category (set is_active to False)."""
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('categories:list')

    def get_queryset(self):
        """Return only non-default categories owned by the logged user."""
        return Category.objects.filter(
            user=self.request.user,
            is_default=False
        )

    def form_valid(self, form):
        """Perform soft delete instead of actual deletion."""
        # Check if category is default (extra validation)
        if self.object.is_default:
            messages.error(
                self.request,
                'Categorias padrão não podem ser excluídas!'
            )
            return HttpResponseRedirect(self.success_url)

        # Check if category has transactions
        if self.object.transactions.exists():
            messages.error(
                self.request,
                f'A categoria "{self.object.name}" possui transações vinculadas e não pode ser excluída. '
                f'Remova ou reclassifique as transações antes de excluir.'
            )
            return HttpResponseRedirect(self.success_url)

        success_url = self.get_success_url()

        try:
            # Soft delete: set is_active to False
            self.object.is_active = False
            self.object.save()
        except Exception:
            logger.exception('Erro ao excluir categoria %s', self.object.pk)
            messages.error(
                self.request,
                'Ocorreu um erro ao excluir a categoria. Tente novamente.'
            )
            return HttpResponseRedirect(success_url)

        messages.success(
            self.request,
            f'Categoria "{self.object.name}" excluída com sucesso!'
        )

        return HttpResponseRedirect(success_url)
