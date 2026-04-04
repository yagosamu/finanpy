from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import Account
from categories.models import Category
from profiles.models import Profile
from transactions.models import Transaction

User = get_user_model()


# ---------------------------------------------------------------------------
# Dados de seed
# ---------------------------------------------------------------------------

_USERS = [
    {
        'email': 'teste@finanpy.com',
        'password': 'senha123',
        'profile': {
            'first_name': 'Carlos',
            'last_name': 'Mendes',
            'phone': '(11) 98765-4321',
            'birth_date': date(1990, 4, 15),
        },
    },
    {
        'email': 'demo@finanpy.com',
        'password': 'senha123',
        'profile': {
            'first_name': 'Ana',
            'last_name': 'Souza',
            'phone': '(21) 99123-4567',
            'birth_date': date(1985, 8, 22),
        },
    },
]

_TESTE_ACCOUNTS = [
    {'name': 'Conta Corrente', 'account_type': Account.CHECKING, 'bank': 'Nubank'},
    {'name': 'Poupança',       'account_type': Account.SAVINGS,  'bank': 'Caixa Econômica Federal'},
    {'name': 'Carteira',       'account_type': Account.WALLET,   'bank': ''},
]

_DEMO_ACCOUNTS = [
    {'name': 'Conta Corrente', 'account_type': Account.CHECKING, 'bank': 'Bradesco'},
    {'name': 'Poupança',       'account_type': Account.SAVINGS,  'bank': 'Itaú'},
]


def _days_ago(n):
    return date.today() - timedelta(days=n)


# ~40 transações para teste@finanpy.com
# Tupla: (days_ago, category_name, category_type, amount, account_name, description)
_TESTE_TRANSACTIONS = [
    # --- Mês atual (~0-30 dias) ---
    (2,  'Salário',      'income',  5800.00, 'Conta Corrente', 'Salário março'),
    (3,  'Alimentação',  'expense',  320.50, 'Conta Corrente', 'Supermercado Extra'),
    (4,  'Transporte',   'expense',   89.90, 'Conta Corrente', 'Combustível posto Shell'),
    (5,  'Alimentação',  'expense',   42.80, 'Carteira',       'Almoço restaurante'),
    (7,  'Lazer',        'expense',  180.00, 'Conta Corrente', 'Cinema e jantar'),
    (8,  'Saúde',        'expense',  250.00, 'Conta Corrente', 'Plano de saúde'),
    (10, 'Moradia',      'expense', 1200.00, 'Conta Corrente', 'Aluguel'),
    (11, 'Alimentação',  'expense',   35.60, 'Carteira',       'Padaria'),
    (12, 'Transporte',   'expense',   28.50, 'Conta Corrente', 'Uber'),
    (14, 'Freelance',    'income',  1200.00, 'Conta Corrente', 'Projeto logo marca'),
    (15, 'Educação',     'expense',  350.00, 'Conta Corrente', 'Curso de Python online'),
    (17, 'Alimentação',  'expense',  198.40, 'Conta Corrente', 'iFood semana'),
    (18, 'Vestuário',    'expense',  279.90, 'Conta Corrente', 'Tênis Nike'),
    (20, 'Lazer',        'expense',   65.00, 'Carteira',       'Netflix e Spotify'),
    (21, 'Transporte',   'expense',  145.00, 'Conta Corrente', 'Gasolina'),
    (22, 'Saúde',        'expense',   89.00, 'Conta Corrente', 'Farmácia'),
    (24, 'Alimentação',  'expense',  412.30, 'Conta Corrente', 'Supermercado Carrefour'),
    (25, 'Outros',       'expense',   75.00, 'Conta Corrente', 'Presente aniversário'),
    (27, 'Investimentos', 'income',   500.00, 'Poupança',       'Depósito reserva de emergência'),
    (28, 'Investimentos','income',   180.00, 'Conta Corrente', 'Rendimento CDB'),

    # --- 2 meses atrás (~31-60 dias) ---
    (32, 'Salário',      'income',  5800.00, 'Conta Corrente', 'Salário fevereiro'),
    (33, 'Moradia',      'expense', 1200.00, 'Conta Corrente', 'Aluguel fevereiro'),
    (35, 'Alimentação',  'expense',  290.70, 'Conta Corrente', 'Supermercado'),
    (36, 'Saúde',        'expense',  250.00, 'Conta Corrente', 'Plano de saúde fevereiro'),
    (38, 'Transporte',   'expense',  110.00, 'Conta Corrente', 'Combustível'),
    (40, 'Lazer',        'expense',  220.00, 'Conta Corrente', 'Show de música'),
    (42, 'Alimentação',  'expense',   52.30, 'Carteira',       'Lanchonete'),
    (44, 'Freelance',    'income',   800.00, 'Conta Corrente', 'Consultoria design'),
    (45, 'Educação',     'expense',  350.00, 'Conta Corrente', 'Curso Python fevereiro'),
    (47, 'Vestuário',    'expense',  149.90, 'Conta Corrente', 'Camisa social'),
    (50, 'Alimentação',  'expense',  380.10, 'Conta Corrente', 'Supermercado quinzenal'),
    (52, 'Transporte',   'expense',   67.00, 'Conta Corrente', 'Táxi aeroporto'),
    (55, 'Outros',       'expense',  120.00, 'Conta Corrente', 'Conserto celular'),

    # --- 3 meses atrás (~61-90 dias) ---
    (62, 'Salário',      'income',  5800.00, 'Conta Corrente', 'Salário janeiro'),
    (63, 'Moradia',      'expense', 1200.00, 'Conta Corrente', 'Aluguel janeiro'),
    (65, 'Alimentação',  'expense',  310.00, 'Conta Corrente', 'Supermercado'),
    (67, 'Saúde',        'expense',  250.00, 'Conta Corrente', 'Plano de saúde janeiro'),
    (70, 'Lazer',        'expense',   98.00, 'Conta Corrente', 'Streaming e jogos'),
    (72, 'Transporte',   'expense',  130.00, 'Conta Corrente', 'Combustível janeiro'),
    (75, 'Investimentos','income',   150.00, 'Conta Corrente', 'Rendimento poupança'),
    (78, 'Alimentação',  'expense',  275.80, 'Conta Corrente', 'Supermercado quinzenal'),
    (80, 'Outros',       'expense',   45.00, 'Carteira',       'Barbearia'),
    (85, 'Freelance',    'income',   600.00, 'Conta Corrente', 'Identidade visual cliente'),
]

_DEMO_TRANSACTIONS = [
    (3,  'Salário',     'income',  4200.00, 'Conta Corrente', 'Salário mensal'),
    (5,  'Moradia',     'expense', 1100.00, 'Conta Corrente', 'Aluguel'),
    (7,  'Alimentação', 'expense',  280.00, 'Conta Corrente', 'Supermercado'),
    (10, 'Saúde',       'expense',  200.00, 'Conta Corrente', 'Plano de saúde'),
    (12, 'Transporte',  'expense',   95.00, 'Conta Corrente', 'Combustível'),
    (15, 'Lazer',       'expense',  120.00, 'Conta Corrente', 'Cinema e restaurante'),
    (18, 'Alimentação', 'expense',   58.40, 'Conta Corrente', 'iFood'),
    (20, 'Investimentos','income',   300.00, 'Poupança',       'Depósito poupança'),
    (35, 'Salário',     'income',  4200.00, 'Conta Corrente', 'Salário mês anterior'),
    (37, 'Moradia',     'expense', 1100.00, 'Conta Corrente', 'Aluguel anterior'),
    (40, 'Alimentação', 'expense',  320.00, 'Conta Corrente', 'Supermercado'),
    (42, 'Transporte',  'expense',   80.00, 'Conta Corrente', 'Transporte'),
    (45, 'Saúde',       'expense',  200.00, 'Conta Corrente', 'Plano de saúde'),
    (65, 'Salário',     'income',  4200.00, 'Conta Corrente', 'Salário há 2 meses'),
    (68, 'Moradia',     'expense', 1100.00, 'Conta Corrente', 'Aluguel há 2 meses'),
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados realistas de teste'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== seed_data ===\n'))

        # 1. Categorias padrão
        self._ensure_default_categories()

        # 2. Carregar categorias padrão em memória (user=None, is_default=True)
        categories = {
            (c.name, c.category_type): c
            for c in Category.objects.filter(user=None, is_default=True)
        }

        # 3. Criar/atualizar usuários
        users_created = {}
        for user_data in _USERS:
            user, created = self._get_or_create_user(user_data)
            users_created[user_data['email']] = (user, created)

        # 4. Contas — teste@finanpy.com
        teste_user, _ = users_created['teste@finanpy.com']
        teste_accounts = self._ensure_accounts(teste_user, _TESTE_ACCOUNTS)

        # 5. Contas — demo@finanpy.com
        demo_user, _ = users_created['demo@finanpy.com']
        demo_accounts = self._ensure_accounts(demo_user, _DEMO_ACCOUNTS)

        # 6. Transações
        teste_tx_count = self._ensure_transactions(
            teste_user, teste_accounts, categories, _TESTE_TRANSACTIONS
        )
        demo_tx_count = self._ensure_transactions(
            demo_user, demo_accounts, categories, _DEMO_TRANSACTIONS
        )

        # 7. Resumo
        self._print_summary(users_created, teste_accounts, demo_accounts, teste_tx_count, demo_tx_count)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_default_categories(self):
        self.stdout.write('Verificando categorias padrão...')
        existing = Category.objects.filter(user=None, is_default=True).count()
        if existing == 0:
            self.stdout.write('  Nenhuma encontrada — executando create_default_categories')
            call_command('create_default_categories', verbosity=0)
        else:
            self.stdout.write(self.style.SUCCESS(f'  {existing} categorias padrão já existem'))

    def _get_or_create_user(self, user_data):
        email = user_data['email']
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'is_active': True},
        )
        if created:
            user.set_password(user_data['password'])
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'  Usuário criado: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'  Usuário já existe: {email}'))

        # Atualizar perfil (criado automaticamente via signal)
        profile_data = user_data['profile']
        Profile.objects.filter(user=user).update(
            first_name=profile_data['first_name'],
            last_name=profile_data['last_name'],
            phone=profile_data['phone'],
            birth_date=profile_data['birth_date'],
        )
        return user, created

    def _ensure_accounts(self, user, accounts_spec):
        accounts = {}
        for spec in accounts_spec:
            account, created = Account.objects.get_or_create(
                user=user,
                name=spec['name'],
                defaults={
                    'account_type': spec['account_type'],
                    'bank': spec['bank'],
                    'initial_balance': 0,
                    'current_balance': 0,
                    'is_active': True,
                },
            )
            accounts[spec['name']] = account
            label = 'criada' if created else 'já existe'
            self.stdout.write(f'  Conta [{user.email}] "{account.name}" — {label}')
        return accounts

    def _ensure_transactions(self, user, accounts, categories, transactions_spec):
        created_count = 0
        skipped_count = 0

        for days_ago, cat_name, cat_type, amount, account_name, description in transactions_spec:
            account = accounts.get(account_name)
            if account is None:
                self.stdout.write(
                    self.style.WARNING(f'  Conta "{account_name}" não encontrada para {user.email} — pulando')
                )
                continue

            category = categories.get((cat_name, cat_type))
            if category is None:
                self.stdout.write(
                    self.style.WARNING(f'  Categoria "{cat_name}" ({cat_type}) não encontrada — pulando')
                )
                continue

            tx_date = _days_ago(days_ago)

            _, created = Transaction.objects.get_or_create(
                user=user,
                account=account,
                category=category,
                transaction_type=cat_type,
                amount=amount,
                date=tx_date,
                description=description,
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        return created_count, skipped_count

    def _print_summary(self, users_created, teste_accounts, demo_accounts, teste_tx, demo_tx):
        self.stdout.write('\n' + '=' * 55)
        self.stdout.write(self.style.SUCCESS('RESUMO DO SEED'))
        self.stdout.write('=' * 55)

        for email, (user, created) in users_created.items():
            status = 'NOVO' if created else 'existente'
            self.stdout.write(f'  Usuário [{status}]: {email}')

        self.stdout.write(f'\n  Contas teste@finanpy.com : {len(teste_accounts)}')
        self.stdout.write(f'  Contas demo@finanpy.com  : {len(demo_accounts)}')

        t_created, t_skipped = teste_tx
        d_created, d_skipped = demo_tx
        self.stdout.write(f'\n  Transações teste@ criadas : {t_created}  (já existiam: {t_skipped})')
        self.stdout.write(f'  Transações demo@  criadas : {d_created}  (já existiam: {d_skipped})')
        self.stdout.write('=' * 55 + '\n')
