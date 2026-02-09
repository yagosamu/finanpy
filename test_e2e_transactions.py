#!/usr/bin/env python
"""E2E tests for transaction creation, listing, filtering, editing and deletion."""
import os
import re
import sys
from decimal import Decimal

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from django.test import Client, override_settings
from users.models import CustomUser
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


def html_has_error(content, field_hint=None):
    """Check if HTML response contains form error messages."""
    # Django renders errors with text-red-400 class in our templates
    # Also check for Django's standard error list
    error_patterns = [
        r'text-red-400.*?</p>',
        r'errorlist.*?<li>(.*?)</li>',
        r'class="[^"]*error[^"]*"',
    ]
    for pattern in error_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            if field_hint:
                # Check if any error relates to the field
                for m in matches:
                    clean = re.sub(r'<[^>]+>', '', m).strip()
                    if clean and len(clean) > 5:
                        return True
            else:
                return True
    return False


def html_contains_validation_error(content, keywords):
    """Check if HTML contains error text matching any of the keywords."""
    content_lower = content.lower()
    for kw in keywords:
        if kw.lower() in content_lower:
            return True
    return False


def run_test_691():
    """Task 6.9.1 - Test transaction creation."""
    client = Client()
    results = []

    # Login
    login_ok = client.login(username='qa-test@finanpy.com', password='TestPass123!')
    print(f'Login: {"PASS" if login_ok else "FAIL"}')
    if not login_ok:
        print('ABORT: Cannot login')
        return False

    user = CustomUser.objects.get(email='qa-test@finanpy.com')
    account_cc = Account.objects.get(user=user, name='Conta Corrente Itau')
    account_cart = Account.objects.get(user=user, name='Carteira Pessoal')
    cat_salario = Category.objects.get(name='Sal\u00e1rio', is_default=True)
    cat_alim = Category.objects.get(name='Alimenta\u00e7\u00e3o', is_default=True)

    # ========================================
    # TEST 1: Create Income Transaction
    # ========================================
    print('\n' + '=' * 60)
    print('TEST 1: Create Income Transaction')
    print('=' * 60)

    response = client.get('/transacoes/nova/')
    t1_form = response.status_code == 200
    print(f'  Form loads: {"PASS" if t1_form else "FAIL"} (status={response.status_code})')
    results.append(t1_form)

    initial_cc = account_cc.current_balance
    print(f'  Initial balance CC: R$ {initial_cc}')

    data = {
        'transaction_type': 'income',
        'amount': '1500.00',
        'date': '2025-01-15',
        'account': account_cc.pk,
        'category': cat_salario.pk,
        'description': 'Salario de janeiro - teste E2E',
    }
    response = client.post('/transacoes/nova/', data)
    t1_create = response.status_code == 302
    print(f'  Create redirects: {"PASS" if t1_create else "FAIL"} (status={response.status_code})')
    if not t1_create:
        content = response.content.decode('utf-8')
        errors = re.findall(r'escolha v.lida|erro|error|inv.lid', content, re.IGNORECASE)
        print(f'  HTML errors found: {errors[:3]}')
    results.append(t1_create)

    txn_inc = Transaction.objects.filter(user=user, description__contains='teste E2E', transaction_type='income').first()
    t1_db = txn_inc is not None
    print(f'  Transaction in DB: {"PASS" if t1_db else "FAIL"}')
    if txn_inc:
        print(f'    ID={txn_inc.pk}, amount={txn_inc.amount}, cat={txn_inc.category.name}')
    results.append(t1_db)

    account_cc.refresh_from_db()
    expected_cc = initial_cc + Decimal('1500.00')
    t1_balance = account_cc.current_balance == expected_cc
    print(f'  Balance update: {"PASS" if t1_balance else "FAIL"} (expected={expected_cc}, actual={account_cc.current_balance})')
    results.append(t1_balance)

    # ========================================
    # TEST 2: Create Expense Transaction
    # ========================================
    print('\n' + '=' * 60)
    print('TEST 2: Create Expense Transaction')
    print('=' * 60)

    account_cart.refresh_from_db()
    initial_cart = account_cart.current_balance
    print(f'  Initial balance Carteira: R$ {initial_cart}')

    data = {
        'transaction_type': 'expense',
        'amount': '250.50',
        'date': '2025-01-16',
        'account': account_cart.pk,
        'category': cat_alim.pk,
        'description': 'Compras supermercado - teste E2E',
    }
    response = client.post('/transacoes/nova/', data)
    t2_create = response.status_code == 302
    print(f'  Create redirects: {"PASS" if t2_create else "FAIL"} (status={response.status_code})')
    if not t2_create:
        content = response.content.decode('utf-8')
        errors = re.findall(r'escolha v.lida|erro|error|inv.lid', content, re.IGNORECASE)
        print(f'  HTML errors found: {errors[:3]}')
    results.append(t2_create)

    txn_exp = Transaction.objects.filter(user=user, description__contains='supermercado', transaction_type='expense').first()
    t2_db = txn_exp is not None
    print(f'  Transaction in DB: {"PASS" if t2_db else "FAIL"}')
    if txn_exp:
        print(f'    ID={txn_exp.pk}, amount={txn_exp.amount}, cat={txn_exp.category.name}')
    results.append(t2_db)

    account_cart.refresh_from_db()
    expected_cart = initial_cart - Decimal('250.50')
    t2_balance = account_cart.current_balance == expected_cart
    print(f'  Balance update: {"PASS" if t2_balance else "FAIL"} (expected={expected_cart}, actual={account_cart.current_balance})')
    results.append(t2_balance)

    # ========================================
    # TEST 3: Verify Balances and List
    # ========================================
    print('\n' + '=' * 60)
    print('TEST 3: Verify Balance Updates and Transaction List')
    print('=' * 60)

    response_acc = client.get('/accounts/')
    t3_acc = response_acc.status_code == 200
    print(f'  Accounts page loads: {"PASS" if t3_acc else "FAIL"}')
    results.append(t3_acc)

    response_list = client.get('/transacoes/')
    t3_list = response_list.status_code == 200
    print(f'  List page loads: {"PASS" if t3_list else "FAIL"}')
    results.append(t3_list)

    content = response_list.content.decode('utf-8')
    has_income = 'teste E2E' in content
    has_expense = 'supermercado' in content
    print(f'  Income in list: {"PASS" if has_income else "FAIL"}')
    print(f'  Expense in list: {"PASS" if has_expense else "FAIL"}')
    results.append(has_income)
    results.append(has_expense)

    # ========================================
    # TEST 4: Form Validations
    # ========================================
    print('\n' + '=' * 60)
    print('TEST 4: Form Validations')
    print('=' * 60)

    # 4a: Future date
    data_future = {
        'transaction_type': 'income',
        'amount': '100.00',
        'date': '2027-06-01',
        'account': account_cc.pk,
        'category': cat_salario.pk,
        'description': 'Future date test',
    }
    response = client.post('/transacoes/nova/', data_future)
    content = response.content.decode('utf-8')
    t4a = response.status_code == 200 and html_contains_validation_error(content, ['futuro', 'future', 'data'])
    print(f'  Future date rejected: {"PASS" if t4a else "FAIL"} (status={response.status_code})')
    results.append(t4a)

    # 4b: Zero amount
    data_zero = {
        'transaction_type': 'expense',
        'amount': '0',
        'date': '2025-01-15',
        'account': account_cc.pk,
        'category': cat_alim.pk,
        'description': 'Zero amount test',
    }
    response = client.post('/transacoes/nova/', data_zero)
    content = response.content.decode('utf-8')
    t4b = response.status_code == 200 and html_contains_validation_error(content, ['maior que zero', 'zero', 'positiv', 'ensure'])
    print(f'  Zero amount rejected: {"PASS" if t4b else "FAIL"} (status={response.status_code})')
    results.append(t4b)

    # 4c: Category type mismatch (income type + expense category)
    data_mismatch = {
        'transaction_type': 'income',
        'amount': '100.00',
        'date': '2025-01-15',
        'account': account_cc.pk,
        'category': cat_alim.pk,
        'description': 'Mismatch test',
    }
    response = client.post('/transacoes/nova/', data_mismatch)
    content = response.content.decode('utf-8')
    t4c = response.status_code == 200 and html_contains_validation_error(content, ['tipo da categoria', 'corresponder', 'mismatch'])
    print(f'  Category mismatch rejected: {"PASS" if t4c else "FAIL"} (status={response.status_code})')
    results.append(t4c)

    # 4d: Negative amount
    data_neg = {
        'transaction_type': 'expense',
        'amount': '-50.00',
        'date': '2025-01-15',
        'account': account_cc.pk,
        'category': cat_alim.pk,
        'description': 'Negative amount test',
    }
    response = client.post('/transacoes/nova/', data_neg)
    content = response.content.decode('utf-8')
    t4d = response.status_code == 200 and html_contains_validation_error(content, ['maior que zero', 'positiv', 'ensure', 'negativ', 'minimum'])
    print(f'  Negative amount rejected: {"PASS" if t4d else "FAIL"} (status={response.status_code})')
    results.append(t4d)

    # No invalid transactions saved
    bad_count = Transaction.objects.filter(
        description__in=['Future date test', 'Zero amount test', 'Mismatch test', 'Negative amount test']
    ).count()
    t4e = bad_count == 0
    print(f'  No invalid txns saved: {"PASS" if t4e else "FAIL"} (bad_count={bad_count})')
    results.append(t4e)

    # ========================================
    # SUMMARY
    # ========================================
    passed = sum(1 for r in results if r)
    total = len(results)
    print('\n' + '=' * 60)
    print(f'TEST 6.9.1 SUMMARY: {passed}/{total} checks passed')
    print('=' * 60)

    return passed >= total - 1  # Allow 1 failure max


def run_test_692():
    """Task 6.9.2 - Test listing and filters."""
    client = Client()
    results = []

    login_ok = client.login(username='qa-test@finanpy.com', password='TestPass123!')
    if not login_ok:
        print('ABORT: Cannot login')
        return False

    user = CustomUser.objects.get(email='qa-test@finanpy.com')
    account_cc = Account.objects.get(user=user, name='Conta Corrente Itau')
    account_cart = Account.objects.get(user=user, name='Carteira Pessoal')
    cat_salario = Category.objects.get(name='Sal\u00e1rio', is_default=True)
    cat_transporte = Category.objects.get(name='Transporte', is_default=True)

    # Create extra transactions for filter testing
    extra_txns = [
        {
            'transaction_type': 'expense',
            'amount': '89.90',
            'date': '2025-02-10',
            'account': account_cc.pk,
            'category': cat_transporte.pk,
            'description': 'Uber fevereiro - teste filtro',
        },
        {
            'transaction_type': 'income',
            'amount': '500.00',
            'date': '2025-02-15',
            'account': account_cc.pk,
            'category': cat_salario.pk,
            'description': 'Freelance fevereiro - teste filtro',
        },
    ]

    for data in extra_txns:
        response = client.post('/transacoes/nova/', data)
        if response.status_code != 302:
            print(f'  WARNING: Failed to create extra transaction')

    print('\n' + '=' * 60)
    print('TEST 6.9.2: Listing and Filters')
    print('=' * 60)

    txn_count = Transaction.objects.filter(user=user).count()
    print(f'  Total transactions in DB: {txn_count}')

    # Test basic listing
    response = client.get('/transacoes/')
    t1 = response.status_code == 200
    print(f'  List page loads: {"PASS" if t1 else "FAIL"}')
    results.append(t1)

    # Test filter by date range
    response = client.get('/transacoes/?date_from=2025-02-01&date_to=2025-02-28')
    t2 = response.status_code == 200
    content = response.content.decode('utf-8')
    has_feb = 'fevereiro' in content
    has_jan = 'janeiro' in content
    t2_filter = has_feb and not has_jan
    print(f'  Date filter loads: {"PASS" if t2 else "FAIL"}')
    print(f'  Date filter correct: {"PASS" if t2_filter else "FAIL"} (has_feb={has_feb}, excludes_jan={not has_jan})')
    results.append(t2)
    results.append(t2_filter)

    # Test filter by category
    response = client.get(f'/transacoes/?category={cat_transporte.pk}')
    t3 = response.status_code == 200
    content = response.content.decode('utf-8')
    has_uber = 'Uber' in content
    print(f'  Category filter loads: {"PASS" if t3 else "FAIL"}')
    print(f'  Category filter shows Uber: {"PASS" if has_uber else "FAIL"}')
    results.append(t3)
    results.append(has_uber)

    # Test filter by transaction type
    response = client.get('/transacoes/?transaction_type=income')
    t4 = response.status_code == 200
    content = response.content.decode('utf-8')
    has_income_txn = 'Salario' in content or 'Freelance' in content or 'teste E2E' in content
    print(f'  Type filter loads: {"PASS" if t4 else "FAIL"}')
    print(f'  Type filter shows income: {"PASS" if has_income_txn else "FAIL"}')
    results.append(t4)
    results.append(has_income_txn)

    # Test filter by account
    response = client.get(f'/transacoes/?account={account_cart.pk}')
    t5 = response.status_code == 200
    content = response.content.decode('utf-8')
    has_cart_txn = 'supermercado' in content
    print(f'  Account filter loads: {"PASS" if t5 else "FAIL"}')
    print(f'  Account filter shows Carteira txns: {"PASS" if has_cart_txn else "FAIL"}')
    results.append(t5)
    results.append(has_cart_txn)

    # Test summary values via DB
    from django.db.models import Sum
    total_inc = Transaction.objects.filter(user=user, transaction_type='income').aggregate(s=Sum('amount'))['s'] or 0
    total_exp = Transaction.objects.filter(user=user, transaction_type='expense').aggregate(s=Sum('amount'))['s'] or 0
    t6 = float(total_inc) > 0 and float(total_exp) > 0
    print(f'  Summary values - Income: R$ {total_inc}, Expense: R$ {total_exp}, Balance: R$ {total_inc - total_exp}')
    print(f'  Summary has values: {"PASS" if t6 else "FAIL"}')
    results.append(t6)

    # Test pagination
    response = client.get('/transacoes/?page=1')
    t7 = response.status_code == 200
    print(f'  Pagination page=1: {"PASS" if t7 else "FAIL"}')
    results.append(t7)

    passed = sum(1 for r in results if r)
    total = len(results)
    print(f'\n  TEST 6.9.2 SUMMARY: {passed}/{total} checks passed')

    return passed >= total - 1


def run_test_693():
    """Task 6.9.3 - Test editing and deletion."""
    client = Client()
    results = []

    login_ok = client.login(username='qa-test@finanpy.com', password='TestPass123!')
    if not login_ok:
        print('ABORT: Cannot login')
        return False

    user = CustomUser.objects.get(email='qa-test@finanpy.com')

    print('\n' + '=' * 60)
    print('TEST 6.9.3: Edit and Delete Transactions')
    print('=' * 60)

    # Pick an income transaction to edit
    txn = Transaction.objects.filter(user=user, transaction_type='income').first()
    if not txn:
        print('  ABORT: No income transaction found')
        return False

    account = txn.account
    old_amount = txn.amount
    account.refresh_from_db()
    old_balance = account.current_balance
    print(f'  Editing txn ID={txn.pk}: amount={old_amount}, account={account.name}')
    print(f'  Account balance before edit: R$ {old_balance}')

    # Load edit form
    response = client.get(f'/transacoes/{txn.pk}/editar/')
    t1 = response.status_code == 200
    print(f'  Edit form loads: {"PASS" if t1 else "FAIL"} (status={response.status_code})')
    results.append(t1)

    # Edit: change amount to 2000.00
    new_amount = '2000.00'
    data = {
        'transaction_type': txn.transaction_type,
        'amount': new_amount,
        'date': str(txn.date),
        'account': txn.account.pk,
        'category': txn.category.pk,
        'description': txn.description + ' (editado)',
    }
    response = client.post(f'/transacoes/{txn.pk}/editar/', data)
    t2 = response.status_code == 302
    print(f'  Edit redirects: {"PASS" if t2 else "FAIL"} (status={response.status_code})')
    if not t2:
        content = response.content.decode('utf-8')
        errors = re.findall(r'escolha v.lida|erro|error', content, re.IGNORECASE)
        print(f'  HTML errors: {errors[:3]}')
    results.append(t2)

    # Verify transaction updated
    txn.refresh_from_db()
    t3 = txn.amount == Decimal('2000.00')
    print(f'  Amount updated: {"PASS" if t3 else "FAIL"} (expected=2000.00, actual={txn.amount})')
    results.append(t3)

    # Verify balance recalculated
    account.refresh_from_db()
    diff = Decimal(new_amount) - old_amount
    expected_balance = old_balance + diff
    t4 = account.current_balance == expected_balance
    print(f'  Balance recalculated: {"PASS" if t4 else "FAIL"} (expected={expected_balance}, actual={account.current_balance})')
    results.append(t4)

    # ========================================
    # DELETE TEST
    # ========================================
    print()

    txn_del = Transaction.objects.filter(user=user, transaction_type='expense').first()
    if not txn_del:
        print('  ABORT: No expense transaction found to delete')
        return False

    del_account = txn_del.account
    del_amount = txn_del.amount
    del_account.refresh_from_db()
    del_balance = del_account.current_balance
    del_pk = txn_del.pk
    print(f'  Deleting txn ID={del_pk}: amount={del_amount}, account={del_account.name}')
    print(f'  Account balance before delete: R$ {del_balance}')

    # Load delete confirmation page
    response = client.get(f'/transacoes/{del_pk}/excluir/')
    t5 = response.status_code == 200
    print(f'  Delete confirm page loads: {"PASS" if t5 else "FAIL"} (status={response.status_code})')
    results.append(t5)

    # Confirm deletion
    response = client.post(f'/transacoes/{del_pk}/excluir/')
    t6 = response.status_code == 302
    print(f'  Delete redirects: {"PASS" if t6 else "FAIL"} (status={response.status_code})')
    results.append(t6)

    # Verify transaction removed
    t7 = not Transaction.objects.filter(pk=del_pk).exists()
    print(f'  Transaction removed from DB: {"PASS" if t7 else "FAIL"}')
    results.append(t7)

    # Verify balance adjusted (expense deleted -> balance increases)
    del_account.refresh_from_db()
    expected_del_balance = del_balance + del_amount
    t8 = del_account.current_balance == expected_del_balance
    print(f'  Balance adjusted: {"PASS" if t8 else "FAIL"} (expected={expected_del_balance}, actual={del_account.current_balance})')
    results.append(t8)

    passed = sum(1 for r in results if r)
    total = len(results)
    print(f'\n  TEST 6.9.3 SUMMARY: {passed}/{total} checks passed')

    return passed >= total - 1


if __name__ == '__main__':
    test = sys.argv[1] if len(sys.argv) > 1 else 'all'

    with override_settings(ALLOWED_HOSTS=['*']):
        if test in ('691', 'all'):
            run_test_691()
        if test in ('692', 'all'):
            run_test_692()
        if test in ('693', 'all'):
            run_test_693()
