import json
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import Account
from transactions.models import Transaction
from categories.models import Category


class HomeView(TemplateView):
    """Landing page view."""
    template_name = 'home.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for authenticated users."""
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get current month date range
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month_start = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month_start = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # Month names in Portuguese
        month_names = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        # 7.1.1 - Basic data
        # Calculate total balance from all active accounts
        total_balance = Account.objects.filter(
            user=user,
            is_active=True
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0.00')

        # Count active accounts
        active_accounts_count = Account.objects.filter(
            user=user,
            is_active=True
        ).count()

        # Get last 5 transactions with select_related
        recent_transactions = Transaction.objects.filter(
            user=user
        ).select_related('account', 'category').order_by('-date', '-created_at')[:5]

        # Get category distribution (all transactions)
        category_distribution = Transaction.objects.filter(
            user=user
        ).values('category__name', 'transaction_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        # 7.1.2 - Statistical calculations
        # Total income of current month
        total_income = Transaction.objects.filter(
            user=user,
            transaction_type=Transaction.INCOME,
            date__gte=current_month_start.date(),
            date__lt=next_month_start.date()
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Total expenses of current month
        total_expenses = Transaction.objects.filter(
            user=user,
            transaction_type=Transaction.EXPENSE,
            date__gte=current_month_start.date(),
            date__lt=next_month_start.date()
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Balance (income - expenses)
        monthly_balance = total_income - total_expenses

        # Current month name in Portuguese
        current_month_name = month_names[now.month - 1]

        # 7.1.3 - Chart data
        # Aggregate expenses by category for current month
        expense_by_category = Transaction.objects.filter(
            user=user,
            transaction_type=Transaction.EXPENSE,
            date__gte=current_month_start.date(),
            date__lt=next_month_start.date()
        ).values(
            'category__name',
            'category__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]

        # Calculate percentage and prepare chart data
        chart_data = []
        if total_expenses > 0:
            for item in expense_by_category:
                percentage = (item['total'] / total_expenses) * 100
                chart_data.append({
                    'category': item['category__name'],
                    'color': item['category__color'],
                    'amount': float(item['total']),
                    'percentage': round(float(percentage), 2)
                })

        # Serialize chart data as JSON for JavaScript consumption
        chart_data_json = json.dumps(chart_data)

        # Add all data to context
        context.update({
            # Basic data
            'total_balance': total_balance,
            'active_accounts_count': active_accounts_count,
            'recent_transactions': recent_transactions,
            'category_distribution': category_distribution,

            # Statistical calculations
            'total_income': total_income,
            'total_expenses': total_expenses,
            'monthly_balance': monthly_balance,
            'current_month_name': current_month_name,
            'current_year': now.year,

            # Chart data
            'expense_by_category': expense_by_category,
            'chart_data_json': chart_data_json,
        })

        return context
