from calendar import monthrange
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from recurrences.models import Recurrence
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Gera transações das recorrências pendentes para o mês informado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Mês alvo no formato YYYY-MM.',
        )

    def handle(self, *args, **options):
        target_month = self.parse_target_month(options.get('month'))
        generated_count = 0
        error_count = 0

        for recurrence in self.get_due_recurrences(target_month):
            transaction_date = self.get_transaction_date(recurrence, target_month)
            if transaction_date is None:
                continue

            if self.transaction_exists(recurrence, transaction_date):
                continue

            try:
                recurrence.generate_transaction(target_date=transaction_date)
                generated_count += 1
            except Exception:
                error_count += 1

        self.stdout.write(f'{generated_count} recorrências geradas, {error_count} com erro')

    def parse_target_month(self, month_option):
        if not month_option:
            today = timezone.localdate()
            return date(today.year, today.month, 1)

        try:
            return date.fromisoformat(f'{month_option}-01')
        except ValueError as exc:
            raise CommandError('Informe um mês válido no formato YYYY-MM.') from exc

    def get_due_recurrences(self, target_month):
        month_end = date(
            target_month.year,
            target_month.month,
            monthrange(target_month.year, target_month.month)[1],
        )
        recurrences = Recurrence.objects.filter(
            is_active=True,
            start_date__lte=month_end,
        ).select_related('account', 'category', 'user')

        return [
            recurrence for recurrence in recurrences
            if self.is_due_for_month(recurrence, target_month)
        ]

    def is_due_for_month(self, recurrence, target_month):
        if recurrence.end_date and recurrence.end_date < target_month:
            return False
        if recurrence.last_generated_date:
            if (
                recurrence.last_generated_date.year == target_month.year
                and recurrence.last_generated_date.month == target_month.month
            ):
                return False
        if target_month == timezone.localdate().replace(day=1):
            return recurrence.is_due_this_month
        return True

    def get_transaction_date(self, recurrence, target_month):
        month_last_day = monthrange(target_month.year, target_month.month)[1]
        transaction_date = date(
            target_month.year,
            target_month.month,
            min(recurrence.day_of_month, month_last_day),
        )

        if recurrence.start_date > transaction_date:
            if (
                recurrence.start_date.year == target_month.year
                and recurrence.start_date.month == target_month.month
            ):
                transaction_date = recurrence.start_date
            else:
                return None

        if recurrence.end_date and recurrence.end_date < transaction_date:
            return None

        return transaction_date

    def transaction_exists(self, recurrence, transaction_date):
        return Transaction.objects.filter(
            user=recurrence.user,
            account=recurrence.account,
            category=recurrence.category,
            transaction_type=recurrence.transaction_type,
            amount=recurrence.amount,
            date=transaction_date,
            description=recurrence.name,
        ).exists()
