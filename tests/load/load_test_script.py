"""
Load Test Script for Finanpy
Creates test user with 150+ transactions across multiple accounts and categories
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

User = get_user_model()

# Configuration
TEST_EMAIL = 'loadtest@teste.com'
TEST_PASSWORD = 'LoadTest@2024!'
NUM_TRANSACTIONS = 150

print('=' * 60)
print('FINANPY LOAD TEST - DATA GENERATION')
print('=' * 60)

# Step 1: Create or get test user
print(f'\n[1/5] Creating test user: {TEST_EMAIL}')
user, created = User.objects.get_or_create(
    email=TEST_EMAIL,
    defaults={'is_active': True}
)
if created:
    user.set_password(TEST_PASSWORD)
    user.save()
    print(f'✓ User created: {TEST_EMAIL}')
else:
    print(f'✓ User already exists: {TEST_EMAIL}')

# Step 2: Create test accounts
print('\n[2/5] Creating test accounts...')
accounts_data = [
    {
        'name': 'Conta Corrente Principal',
        'account_type': Account.CHECKING,
        'bank': 'Banco do Brasil',
        'initial_balance': Decimal('5000.00')
    },
    {
        'name': 'Poupança',
        'account_type': Account.SAVINGS,
        'bank': 'Itaú',
        'initial_balance': Decimal('10000.00')
    },
    {
        'name': 'Carteira',
        'account_type': Account.WALLET,
        'bank': '',
        'initial_balance': Decimal('500.00')
    }
]

accounts = []
for acc_data in accounts_data:
    account, created = Account.objects.get_or_create(
        user=user,
        name=acc_data['name'],
        defaults=acc_data
    )
    accounts.append(account)
    status = 'created' if created else 'exists'
    print(f'  ✓ {acc_data["name"]} ({status})')

print(f'✓ Total accounts: {len(accounts)}')

# Step 3: Get or create categories
print('\n[3/5] Setting up categories...')

# Get default income categories
income_categories = list(Category.objects.filter(
    category_type=Category.INCOME,
    is_default=True,
    is_active=True
))

# Get default expense categories
expense_categories = list(Category.objects.filter(
    category_type=Category.EXPENSE,
    is_default=True,
    is_active=True
))

# Create some custom categories if needed
custom_categories_data = [
    {'name': 'Freelance', 'category_type': Category.INCOME, 'color': '#10B981'},
    {'name': 'Projetos', 'category_type': Category.INCOME, 'color': '#3B82F6'},
    {'name': 'Cursos Online', 'category_type': Category.EXPENSE, 'color': '#8B5CF6'},
    {'name': 'Assinaturas', 'category_type': Category.EXPENSE, 'color': '#EF4444'},
]

for cat_data in custom_categories_data:
    category, created = Category.objects.get_or_create(
        user=user,
        name=cat_data['name'],
        defaults=cat_data
    )
    if cat_data['category_type'] == Category.INCOME:
        income_categories.append(category)
    else:
        expense_categories.append(category)
    status = 'created' if created else 'exists'
    print(f'  ✓ {cat_data["name"]} ({status})')

print(f'✓ Income categories: {len(income_categories)}')
print(f'✓ Expense categories: {len(expense_categories)}')

# Step 4: Create transactions
print(f'\n[4/5] Creating {NUM_TRANSACTIONS} transactions...')

# Delete existing transactions for this user to start fresh
existing_count = Transaction.objects.filter(user=user).count()
if existing_count > 0:
    Transaction.objects.filter(user=user).delete()
    print(f'  Deleted {existing_count} existing transactions')

# Reset account balances to initial
for account in accounts:
    account.current_balance = account.initial_balance
    account.save()

# Income amounts range (higher values)
income_amounts = [
    Decimal('1500.00'), Decimal('2000.00'), Decimal('2500.00'),
    Decimal('3000.00'), Decimal('3500.00'), Decimal('4000.00'),
    Decimal('5000.00'), Decimal('800.00'), Decimal('1200.00')
]

# Expense amounts range (various values)
expense_amounts = [
    Decimal('50.00'), Decimal('75.00'), Decimal('100.00'),
    Decimal('150.00'), Decimal('200.00'), Decimal('250.00'),
    Decimal('300.00'), Decimal('400.00'), Decimal('500.00'),
    Decimal('800.00'), Decimal('1000.00'), Decimal('1500.00')
]

# Descriptions
income_descriptions = [
    'Salário mensal',
    'Pagamento de projeto freelance',
    'Bonificação',
    'Rendimentos de investimento',
    'Trabalho extra',
    'Consultoria',
    'Venda de produto',
    ''
]

expense_descriptions = [
    'Compra no supermercado',
    'Pagamento de conta',
    'Restaurante',
    'Combustível',
    'Farmácia',
    'Cinema',
    'Compras online',
    'Manutenção',
    'Presente',
    'Academia',
    ''
]

# Generate dates for the last 6 months
end_date = datetime.now().date()
start_date = end_date - timedelta(days=180)

transactions_created = 0
batch_size = 50

for i in range(NUM_TRANSACTIONS):
    # Randomize transaction type (60% expense, 40% income)
    is_income = random.random() < 0.4

    if is_income:
        transaction_type = Transaction.INCOME
        amount = random.choice(income_amounts)
        category = random.choice(income_categories)
        description = random.choice(income_descriptions)
    else:
        transaction_type = Transaction.EXPENSE
        amount = random.choice(expense_amounts)
        category = random.choice(expense_categories)
        description = random.choice(expense_descriptions)

    # Random date within the last 6 months
    days_offset = random.randint(0, 180)
    transaction_date = start_date + timedelta(days=days_offset)

    # Random account
    account = random.choice(accounts)

    # Create transaction
    Transaction.objects.create(
        user=user,
        account=account,
        category=category,
        transaction_type=transaction_type,
        amount=amount,
        date=transaction_date,
        description=description
    )

    transactions_created += 1

    # Progress indicator
    if (i + 1) % batch_size == 0:
        print(f'  Progress: {i + 1}/{NUM_TRANSACTIONS} transactions created...')

print(f'✓ Created {transactions_created} transactions')

# Step 5: Display final statistics
print('\n[5/5] Final Statistics')
print('-' * 60)

total_income = Transaction.objects.filter(
    user=user,
    transaction_type=Transaction.INCOME
).count()

total_expense = Transaction.objects.filter(
    user=user,
    transaction_type=Transaction.EXPENSE
).count()

print(f'User: {user.email}')
print(f'Accounts: {Account.objects.filter(user=user).count()}')
print(f'Transactions:')
print(f'  - Income: {total_income}')
print(f'  - Expense: {total_expense}')
print(f'  - Total: {total_income + total_expense}')

# Account balances
print(f'\nAccount Balances:')
for account in Account.objects.filter(user=user):
    account.refresh_from_db()
    print(f'  - {account.name}: R$ {account.current_balance:,.2f}')

print('\n' + '=' * 60)
print('LOAD TEST DATA GENERATION COMPLETED!')
print('=' * 60)
print(f'\nCredentials:')
print(f'  Email: {TEST_EMAIL}')
print(f'  Password: {TEST_PASSWORD}')
print('\nYou can now test the application at http://localhost:8000')
print('=' * 60)
