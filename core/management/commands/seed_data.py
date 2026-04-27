from calendar import monthrange
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import Account, CreditCard
from budgets.models import Budget
from categories.models import Category
from goals.models import Goal
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


# ---------------------------------------------------------------------------
# Dados de seed — Aurum Finance demo (Parte 1)
# ---------------------------------------------------------------------------

_AURUM_DEMO = {
    'email': 'demo@aurumfinance.com',
    'password': 'demo1234',
    'profile': {
        'first_name': 'Maria',
        'last_name': 'Silva',
        'phone': '(11) 99999-0001',
        'birth_date': date(1995, 3, 15),
    },
}

_AURUM_ACCOUNTS = [
    {
        'name': 'Nubank',
        'account_type': Account.CHECKING,
        'bank_code': Account.NUBANK,
        'bank': 'Nubank',
        'is_default': True,
    },
    {
        'name': 'Itaú Poupança',
        'account_type': Account.SAVINGS,
        'bank_code': Account.ITAU,
        'bank': 'Itaú',
        'is_default': False,
    },
    {
        'name': 'Carteira',
        'account_type': Account.WALLET,
        'bank_code': None,
        'bank': '',
        'is_default': False,
    },
]

_AURUM_CARDS = [
    {
        'name': 'Nubank Roxinho',
        'bank_code': Account.NUBANK,
        'credit_limit': 5000,
        'closing_day': 5,
        'due_day': 15,
        'color': '#820ad1',
    },
    {
        'name': 'Itaú Platinum',
        'bank_code': Account.ITAU,
        'credit_limit': 8000,
        'closing_day': 10,
        'due_day': 20,
        'color': '#EC7000',
    },
]

_AURUM_CUSTOM_CATEGORIES = [
    {'name': 'Pets',      'category_type': Category.EXPENSE, 'color': '#F59E0B'},
    {'name': 'Freelance', 'category_type': Category.INCOME,  'color': '#06B6D4'},
]

# Format: (days_ago, category_name, transaction_type, amount, description, is_card)
# is_card=True  → account=Nubank + credit_card=Nubank Roxinho (saldo NÃO alterado pelo signal)
# is_card=False → account=Nubank + credit_card=None           (saldo atualizado pelo signal)
# Distribuição: 18 receitas (30%) + 42 despesas (70%)
#               24 no cartão (40%) + 18 despesas conta (30%) + 18 receitas conta (30%)
_AURUM_TRANSACTIONS = [

    # ── Mês 1 (dias 1–30) ─────────────────────────────────────────────────

    # Receitas — conta
    (2,  'Salário',       'income',  7500.00, 'Salário março 2026',            False),
    (14, 'Freelance',     'income',  1800.00, 'Projeto identidade visual',     False),
    (22, 'Investimentos', 'income',   290.00, 'Rendimento CDB',                False),
    (28, 'Outros',        'income',   350.00, 'Reembolso despesas empresa',    False),

    # Despesas — conta
    (4,  'Alimentação',   'expense',  345.80, 'Supermercado Extra',            False),
    (7,  'Transporte',    'expense',   95.40, 'Combustível posto Shell',       False),
    (12, 'Alimentação',   'expense',   42.00, 'Almoço restaurante centro',     False),
    (19, 'Transporte',    'expense',   22.50, 'Uber viagem ao aeroporto',      False),
    (25, 'Pets',          'expense',  120.00, 'Pet shop banho e tosa',         False),

    # Despesas — cartão
    (5,  'Lazer',         'expense',   39.90, 'Netflix mensal',                True),
    (6,  'Lazer',         'expense',   21.90, 'Spotify mensal',                True),
    (8,  'Alimentação',   'expense',   67.50, 'iFood pedido marmita',          True),
    (11, 'Lazer',         'expense',  145.00, 'Amazon compra livros',          True),
    (13, 'Alimentação',   'expense',  138.00, 'Restaurante jantar casal',      True),
    (17, 'Lazer',         'expense',   55.00, 'Cinema ingresso duplo',         True),

    # ── Mês 2 (dias 31–60) ────────────────────────────────────────────────

    # Receitas — conta
    (32, 'Salário',       'income',  7500.00, 'Salário fevereiro 2026',        False),
    (44, 'Freelance',     'income',  2400.00, 'Consultoria UI redesign',       False),
    (52, 'Investimentos', 'income',   185.00, 'Rendimento poupança',           False),
    (58, 'Outros',        'income',   180.00, 'Venda de equipamento usado',    False),

    # Despesas — conta
    (33, 'Alimentação',   'expense',  298.60, 'Supermercado Carrefour',        False),
    (36, 'Transporte',    'expense',  108.00, 'Combustível posto BP',          False),
    (39, 'Alimentação',   'expense',   52.00, 'Almoço restaurante italiano',   False),
    (43, 'Saúde',         'expense',   55.00, 'Farmácia São Paulo',            False),
    (47, 'Pets',          'expense',   95.00, 'Pet shop ração premium',        False),

    # Despesas — cartão
    (34, 'Lazer',         'expense',   39.90, 'Netflix mensal',                True),
    (35, 'Lazer',         'expense',   21.90, 'Spotify mensal',                True),
    (38, 'Alimentação',   'expense',   79.90, 'iFood pedido pizza',            True),
    (41, 'Lazer',         'expense',   98.00, 'Amazon Prime compras',          True),
    (45, 'Alimentação',   'expense',  165.00, 'Restaurante aniversário',       True),
    (50, 'Lazer',         'expense',   72.00, 'Cinema filme estreia',          True),

    # ── Mês 3 (dias 61–90) ────────────────────────────────────────────────

    # Receitas — conta
    (62, 'Salário',       'income',  7500.00, 'Salário janeiro 2026',          False),
    (70, 'Freelance',     'income',  1200.00, 'Projeto logo startup',          False),
    (77, 'Freelance',     'income',   900.00, 'Revisão materiais gráficos',    False),
    (82, 'Investimentos', 'income',   240.00, 'Rendimento renda fixa',         False),
    (88, 'Outros',        'income',   120.00, 'Cashback cartão de crédito',    False),

    # Despesas — conta
    (63, 'Alimentação',   'expense',  412.30, 'Supermercado Extra quinzenal',  False),
    (66, 'Transporte',    'expense',   87.50, 'Combustível posto BR',          False),
    (72, 'Alimentação',   'expense',   47.50, 'Almoço sushi restaurante',      False),
    (78, 'Saúde',         'expense',   84.00, 'Farmácia Pague Menos',          False),

    # Despesas — cartão
    (64, 'Lazer',         'expense',   39.90, 'Netflix mensal',                True),
    (65, 'Lazer',         'expense',   21.90, 'Spotify mensal',                True),
    (68, 'Alimentação',   'expense',   58.90, 'iFood pedido hambúrguer',       True),
    (71, 'Lazer',         'expense',  189.00, 'Amazon Smart TV acessório',     True),
    (73, 'Alimentação',   'expense',  112.00, 'Restaurante rodízio japonês',   True),
    (79, 'Lazer',         'expense',   48.00, 'Cinema sessão matinê',          True),

    # ── Mês 4 (dias 91–120) ───────────────────────────────────────────────

    # Receitas — conta
    (92,  'Salário',       'income',  7500.00, 'Salário dezembro 2025',        False),
    (100, 'Freelance',     'income',   950.00, 'Identidade visual startup',    False),
    (108, 'Investimentos', 'income',   195.00, 'Rendimento fundo DI',          False),
    (114, 'Outros',        'income',   220.00, 'Reembolso médico plano saúde', False),
    (119, 'Freelance',     'income',   820.00, 'Criação banner marketing',     False),

    # Despesas — conta
    (93,  'Alimentação',   'expense',  375.00, 'Supermercado Extra mensal',    False),
    (96,  'Transporte',    'expense',  112.00, 'Combustível posto Shell',      False),
    (104, 'Educação',      'expense',  189.90, 'Curso Python Django Udemy',    False),
    (110, 'Pets',          'expense',  145.00, 'Pet shop vacina anual',        False),

    # Despesas — cartão
    (94,  'Lazer',         'expense',   39.90, 'Netflix mensal',               True),
    (95,  'Lazer',         'expense',   21.90, 'Spotify mensal',               True),
    (97,  'Alimentação',   'expense',   84.50, 'iFood pedido japonês',         True),
    (101, 'Lazer',         'expense',   65.00, 'Amazon livros técnicos',       True),
    (103, 'Alimentação',   'expense',  155.00, 'Restaurante familiar',         True),
    (107, 'Lazer',         'expense',   40.00, 'Cinema com amigos',            True),
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

        # 8. Aurum Finance demo (Parte 1) — usuário, contas, cartões, categorias
        self._seed_aurum_demo()

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

    def _seed_aurum_demo(self):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n=== Aurum Finance — demo@aurumfinance.com (Parte 1) ===\n'
        ))

        # Usuário
        user, created = User.objects.get_or_create(
            email=_AURUM_DEMO['email'],
            defaults={'is_active': True, 'is_staff': False},
        )
        if created:
            user.set_password(_AURUM_DEMO['password'])
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'  [NOVO] Usuário: {user.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'  [existe] Usuário: {user.email}'))

        # Perfil (auto-criado via signal; apenas atualiza campos)
        p = _AURUM_DEMO['profile']
        Profile.objects.filter(user=user).update(
            first_name=p['first_name'],
            last_name=p['last_name'],
            phone=p['phone'],
            birth_date=p['birth_date'],
        )
        self.stdout.write(f'  Perfil: {p["first_name"]} {p["last_name"]}')

        # Contas
        self.stdout.write('\n  Contas:')
        for spec in _AURUM_ACCOUNTS:
            account, created = Account.objects.get_or_create(
                user=user,
                name=spec['name'],
                defaults={
                    'account_type': spec['account_type'],
                    'bank_code': spec['bank_code'],
                    'bank': spec['bank'],
                    'initial_balance': 0,
                    'current_balance': 0,
                    'is_default': spec['is_default'],
                    'is_active': True,
                },
            )
            label = 'NOVA' if created else 'existe'
            self.stdout.write(f'    [{label}] {account.name} ({account.account_type})')

        # Cartões de crédito
        self.stdout.write('\n  Cartões de crédito:')
        for spec in _AURUM_CARDS:
            card, created = CreditCard.objects.get_or_create(
                user=user,
                name=spec['name'],
                defaults={
                    'bank_code': spec['bank_code'],
                    'credit_limit': spec['credit_limit'],
                    'closing_day': spec['closing_day'],
                    'due_day': spec['due_day'],
                    'color': spec['color'],
                    'is_active': True,
                },
            )
            label = 'NOVO' if created else 'existe'
            self.stdout.write(
                f'    [{label}] {card.name} — limite R$ {card.credit_limit}'
            )

        # Categorias personalizadas
        self.stdout.write('\n  Categorias personalizadas:')
        for spec in _AURUM_CUSTOM_CATEGORIES:
            cat, created = Category.objects.get_or_create(
                user=user,
                name=spec['name'],
                defaults={
                    'category_type': spec['category_type'],
                    'color': spec['color'],
                    'is_default': False,
                    'is_active': True,
                },
            )
            label = 'NOVA' if created else 'existe'
            self.stdout.write(f'    [{label}] {cat.name} ({cat.category_type})')

        # Metas e Orçamentos (Parte 3)
        self._seed_aurum_goals_budgets(user)

        # Transações (Parte 2)
        self._seed_aurum_transactions(user)

        self.stdout.write(self.style.SUCCESS('\n  Aurum seed concluído.\n'))

    def _seed_aurum_transactions(self, user):
        self.stdout.write(self.style.MIGRATE_HEADING('\n  Transações (Parte 2):'))

        # Buscar conta e cartão criados na Parte 1
        try:
            account = Account.objects.get(user=user, name='Nubank')
            card = CreditCard.objects.get(user=user, name='Nubank Roxinho')
        except (Account.DoesNotExist, CreditCard.DoesNotExist) as exc:
            self.stdout.write(self.style.ERROR(f'    Conta/cartão não encontrado: {exc}'))
            return

        # Mapa de categorias: default primeiro, user-specific sobrepõe
        # (garante que 'Freelance' use a categoria personalizada do usuário)
        cat_map = {c.name: c for c in Category.objects.filter(user=None, is_default=True)}
        cat_map.update({c.name: c for c in Category.objects.filter(user=user)})

        created_count = 0
        skipped_count = 0
        missing_cats = set()

        for days_ago, cat_name, tx_type, amount, description, is_card in _AURUM_TRANSACTIONS:
            category = cat_map.get(cat_name)
            if category is None:
                missing_cats.add(cat_name)
                continue

            tx_date = date.today() - timedelta(days=days_ago)

            _, created = Transaction.objects.get_or_create(
                user=user,
                account=account,
                credit_card=card if is_card else None,
                category=category,
                transaction_type=tx_type,
                amount=amount,
                date=tx_date,
                description=description,
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        if missing_cats:
            self.stdout.write(self.style.WARNING(
                f'    Categorias não encontradas: {", ".join(missing_cats)}'
            ))

        total = created_count + skipped_count
        self.stdout.write(self.style.SUCCESS(
            f'    {created_count} criadas  |  {skipped_count} já existiam  |  {total} total'
        ))

    def _seed_aurum_goals_budgets(self, user):
        self.stdout.write(self.style.MIGRATE_HEADING('\n  Metas e Orçamentos (Parte 3):'))

        # Helper: retorna uma data N meses à frente de hoje
        def months_ahead(n):
            today = date.today()
            total = today.month - 1 + n
            year = today.year + total // 12
            month = total % 12 + 1
            day = min(today.day, monthrange(year, month)[1])
            return date(year, month, day)

        # ── Metas ──────────────────────────────────────────────────────────
        self.stdout.write('\n  Metas:')
        goals_spec = [
            {
                'name': 'Viagem para Europa',
                'target_amount': 15000,
                'current_amount': 6900,
                'deadline': months_ahead(6),
                'color': '#22c55e',
            },
            {
                'name': 'Reserva de Emergência',
                'target_amount': 20000,
                'current_amount': 14600,
                'deadline': months_ahead(12),
                'color': '#a78bfa',
            },
            {
                'name': 'Novo Notebook',
                'target_amount': 6500,
                'current_amount': 1200,
                'deadline': months_ahead(3),
                'color': '#f59e0b',
            },
        ]

        for spec in goals_spec:
            goal, created = Goal.objects.get_or_create(
                user=user,
                name=spec['name'],
                defaults={
                    'target_amount': spec['target_amount'],
                    'current_amount': spec['current_amount'],
                    'deadline': spec['deadline'],
                    'color': spec['color'],
                },
            )
            label = 'NOVA' if created else 'existe'
            self.stdout.write(
                f'    [{label}] {goal.name} — {goal.progress_percentage:.0f}% concluída'
            )

        # ── Orçamentos ─────────────────────────────────────────────────────
        self.stdout.write('\n  Orçamentos:')
        current_month = date.today().replace(day=1)

        # Mapa de categorias: default primeiro, user-specific sobrepõe
        cat_map = {c.name: c for c in Category.objects.filter(user=None, is_default=True)}
        cat_map.update({c.name: c for c in Category.objects.filter(user=user)})

        # "Assinaturas" não é categoria padrão — garantir que existe para o usuário
        assinaturas, cat_created = Category.objects.get_or_create(
            user=user,
            name='Assinaturas',
            defaults={
                'category_type': Category.EXPENSE,
                'color': '#06b6d4',
                'is_default': False,
                'is_active': True,
            },
        )
        if cat_created:
            self.stdout.write(self.style.SUCCESS('    [NOVA] Categoria "Assinaturas" criada'))
        cat_map['Assinaturas'] = assinaturas

        budgets_spec = [
            ('Alimentação', 800),
            ('Transporte',  400),
            ('Lazer',       300),
            ('Saúde',       250),
            ('Assinaturas', 150),
        ]

        for cat_name, amount in budgets_spec:
            category = cat_map.get(cat_name)
            if category is None:
                self.stdout.write(
                    self.style.WARNING(f'    Categoria "{cat_name}" não encontrada — pulando')
                )
                continue

            budget, created = Budget.objects.get_or_create(
                user=user,
                category=category,
                month=current_month,
                defaults={'amount': amount},
            )
            label = 'NOVO' if created else 'existe'
            self.stdout.write(
                f'    [{label}] {cat_name} — R$ {budget.amount}'
            )
