import calendar
import logging
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ai.services.analysis_service import analyze_all_active_users, analyze_user

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = 'Executa a análise financeira de IA para um usuário ou para todos os usuários ativos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            metavar='EMAIL',
            help='E-mail do usuário a ser analisado. Omita para analisar todos os usuários ativos.',
        )
        parser.add_argument(
            '--month',
            type=str,
            metavar='YYYY-MM',
            help='Mês de referência no formato YYYY-MM (ex: 2026-04). Padrão: mês atual.',
        )

    def _parse_month(self, month_str):
        '''Converte "YYYY-MM" em (period_start, period_end) como objetos date.

        Returns:
            Tupla (date, date) com o primeiro e último dia do mês.

        Raises:
            ValueError: se o formato for inválido.
        '''
        try:
            year_str, month_str_part = month_str.split('-')
            year = int(year_str)
            month = int(month_str_part)
            if not (1 <= month <= 12):
                raise ValueError('Mês fora do intervalo válido (1–12).')
            period_start = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            period_end = date(year, month, last_day)
            return period_start, period_end
        except (ValueError, AttributeError) as exc:
            raise ValueError(
                f'Formato de mês inválido: "{month_str}". Use YYYY-MM (ex: 2026-04).'
            ) from exc

    def handle(self, *args, **options):
        month_input = options.get('month')
        email = options.get('user')

        # --- Resolver período ---
        if month_input:
            try:
                period_start, period_end = self._parse_month(month_input)
            except ValueError as exc:
                self.stderr.write(self.style.ERROR(str(exc)))
                return
        else:
            today = date.today()
            period_start = today.replace(day=1)
            period_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        # --- Análise individual ---
        if email:
            self._handle_single_user(email, period_start, period_end)
        else:
            self._handle_all_users(period_start, period_end)

    def _handle_single_user(self, email, period_start, period_end):
        '''Busca o usuário pelo e-mail e executa a análise individual.'''
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f'Usuário não encontrado com o e-mail: {email}')
            )
            return

        self.stdout.write(
            f'Analisando usuário: {email} (período: {period_start} a {period_end})...'
        )

        try:
            analyze_user(user, period_start, period_end)
            self.stdout.write(self.style.SUCCESS(f'Análise concluída para {email}'))
        except Exception as exc:
            logger.error(
                'Falha ao analisar usuário via management command',
                extra={'user_email': email, 'error': str(exc)},
                exc_info=True,
            )
            self.stderr.write(
                self.style.ERROR(f'Erro ao analisar {email}: {exc}')
            )

    def _handle_all_users(self, period_start, period_end):
        '''Executa a análise em lote para todos os usuários ativos.'''
        total = User.objects.filter(is_active=True).count()

        self.stdout.write(
            f'Iniciando análise em lote para {total} usuário(s) '
            f'(período: {period_start} a {period_end})...'
        )

        try:
            result = analyze_all_active_users(period_start, period_end)
        except Exception as exc:
            logger.error(
                'Falha inesperada na análise em lote via management command',
                extra={'error': str(exc)},
                exc_info=True,
            )
            self.stderr.write(
                self.style.ERROR(f'Erro inesperado na análise em lote: {exc}')
            )
            return

        success = result['success']
        errors = result['errors']

        self.stdout.write(
            self.style.SUCCESS(
                f'{success} análise(s) gerada(s) com sucesso. {len(errors)} erro(s).'
            )
        )

        for entry in errors:
            self.stdout.write(
                self.style.WARNING(f'  {entry["user_email"]}: {entry["error"]}')
            )
