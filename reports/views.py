import calendar
from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import Account
from transactions.models import Transaction


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/report.html'
    PERIOD_THIS_MONTH = 'this_month'
    PERIOD_LAST_MONTH = 'last_month'
    PERIOD_LAST_3_MONTHS = 'last_3_months'
    PERIOD_LAST_6_MONTHS = 'last_6_months'
    PERIOD_THIS_YEAR = 'this_year'
    VALID_PERIODS = {
        PERIOD_THIS_MONTH,
        PERIOD_LAST_MONTH,
        PERIOD_LAST_3_MONTHS,
        PERIOD_LAST_6_MONTHS,
        PERIOD_THIS_YEAR,
    }

    def get_period(self):
        period = self.request.GET.get('period', self.PERIOD_THIS_MONTH)
        if period not in self.VALID_PERIODS:
            return self.PERIOD_THIS_MONTH
        return period

    def get_date_range(self, period):
        today = timezone.localdate()

        if period == self.PERIOD_THIS_YEAR:
            return date(today.year, 1, 1), date(today.year, 12, 31)

        if period == self.PERIOD_THIS_MONTH:
            target_year = today.year
            target_month = today.month
        elif period == self.PERIOD_LAST_MONTH:
            if today.month == 1:
                target_year = today.year - 1
                target_month = 12
            else:
                target_year = today.year
                target_month = today.month - 1
        elif period == self.PERIOD_LAST_3_MONTHS:
            target_year, target_month = self._shift_month(today.year, today.month, -2)
            return date(target_year, target_month, 1), self._last_day_of_month(today.year, today.month)
        else:
            target_year, target_month = self._shift_month(today.year, today.month, -5)
            return date(target_year, target_month, 1), self._last_day_of_month(today.year, today.month)

        return date(target_year, target_month, 1), self._last_day_of_month(target_year, target_month)

    def _shift_month(self, year, month, delta):
        shifted_month = month + delta
        shifted_year = year

        while shifted_month <= 0:
            shifted_month += 12
            shifted_year -= 1

        while shifted_month > 12:
            shifted_month -= 12
            shifted_year += 1

        return shifted_year, shifted_month

    def _last_day_of_month(self, year, month):
        return date(year, month, calendar.monthrange(year, month)[1])

    def get_selected_account(self, accounts):
        account_id = self.request.GET.get('account')
        if not account_id:
            return None
        return accounts.filter(pk=account_id).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = self.get_period()
        date_start, date_end = self.get_date_range(period)
        period_days = Decimal((date_end - date_start).days + 1)

        accounts = Account.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('name')
        selected_account = self.get_selected_account(accounts)

        transaction_filters = Q(
            user=self.request.user,
            date__range=(date_start, date_end)
        )
        if selected_account:
            transaction_filters &= Q(account=selected_account)

        transactions = Transaction.objects.filter(transaction_filters)
        transactions_with_related = transactions.select_related('account', 'category')

        totals = transactions.aggregate(
            total_income=Coalesce(
                Sum('amount', filter=Q(transaction_type=Transaction.INCOME)),
                Decimal('0.00')
            ),
            total_expense=Coalesce(
                Sum('amount', filter=Q(transaction_type=Transaction.EXPENSE)),
                Decimal('0.00')
            ),
        )
        total_income = totals['total_income']
        total_expense = totals['total_expense']
        net_balance = total_income - total_expense
        avg_daily_expense = (
            (total_expense / period_days).quantize(Decimal('0.01'))
            if period_days > 0 else Decimal('0.00')
        )

        expense_by_category = self._get_category_totals(
            transactions,
            Transaction.EXPENSE,
            total_expense,
        )
        income_by_category = self._get_category_totals(
            transactions,
            Transaction.INCOME,
            total_income,
        )

        daily_evolution_queryset = transactions.values('date').annotate(
            income=Coalesce(
                Sum('amount', filter=Q(transaction_type=Transaction.INCOME)),
                Decimal('0.00')
            ),
            expense=Coalesce(
                Sum('amount', filter=Q(transaction_type=Transaction.EXPENSE)),
                Decimal('0.00')
            ),
        ).order_by('date')
        daily_evolution = [
            {
                'date': item['date'].isoformat(),
                'income': f"{item['income']:.2f}",
                'expense': f"{item['expense']:.2f}",
            }
            for item in daily_evolution_queryset
        ]

        account_transaction_filter = Q(
            transactions__user=self.request.user,
            transactions__date__range=(date_start, date_end),
        )
        if selected_account:
            account_transaction_filter &= Q(transactions__account=selected_account)

        by_account_queryset = accounts.annotate(
            period_income=Coalesce(
                Sum(
                    'transactions__amount',
                    filter=account_transaction_filter & Q(
                        transactions__transaction_type=Transaction.INCOME
                    )
                ),
                Decimal('0.00')
            ),
            period_expense=Coalesce(
                Sum(
                    'transactions__amount',
                    filter=account_transaction_filter & Q(
                        transactions__transaction_type=Transaction.EXPENSE
                    )
                ),
                Decimal('0.00')
            ),
        )
        by_account = list(by_account_queryset.values(
            'name',
            'account_type',
            'current_balance',
            'period_income',
            'period_expense',
        ))

        context.update({
            'period': period,
            'date_start': date_start,
            'date_end': date_end,
            'selected_account': selected_account,
            'accounts': accounts,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'avg_daily_expense': avg_daily_expense,
            'biggest_income': transactions_with_related.filter(
                transaction_type=Transaction.INCOME
            ).order_by('-amount', '-date').first(),
            'biggest_expense': transactions_with_related.filter(
                transaction_type=Transaction.EXPENSE
            ).order_by('-amount', '-date').first(),
            'expense_by_category': expense_by_category,
            'income_by_category': income_by_category,
            'daily_evolution': daily_evolution,
            'by_account': by_account,
            'top_expenses': list(
                transactions_with_related.filter(
                    transaction_type=Transaction.EXPENSE
                ).order_by('-amount', '-date')[:5]
            ),
            'top_incomes': list(
                transactions_with_related.filter(
                    transaction_type=Transaction.INCOME
                ).order_by('-amount', '-date')[:5]
            ),
        })
        return context

    def _get_category_totals(self, transactions, transaction_type, total_amount):
        queryset = transactions.filter(
            transaction_type=transaction_type
        ).values(
            name=F('category__name'),
            color=F('category__color'),
        ).annotate(
            total=Coalesce(Sum('amount'), Decimal('0.00')),
            count=Count('id'),
        ).order_by('-total', 'name')
        category_totals = list(queryset)

        for item in category_totals:
            if total_amount > 0:
                item['percentage'] = (
                    item['total'] * Decimal('100.00') / total_amount
                ).quantize(Decimal('0.01'))
            else:
                item['percentage'] = Decimal('0.00')

        return category_totals

# Create your views here.
