"""
Load Test Performance Measurement Script
Measures page load times with 150+ transactions
"""

import time
from playwright.sync_api import sync_playwright

# Test configuration
BASE_URL = 'http://127.0.0.1:8000'
TEST_EMAIL = 'loadtest@teste.com'
TEST_PASSWORD = 'LoadTest@2024!'

# Results storage
results = {
    'login': 0,
    'dashboard': 0,
    'transactions_list': 0,
    'transactions_filtered': 0,
    'accounts_list': 0,
    'categories_list': 0
}

screenshots_dir = 'load_test_screenshots'

print('=' * 70)
print('FINANPY LOAD TEST - PERFORMANCE MEASUREMENT')
print('=' * 70)
print(f'\nBase URL: {BASE_URL}')
print(f'Test User: {TEST_EMAIL}')
print(f'Expected Transactions: 150+')
print('\n' + '-' * 70)

with sync_playwright() as p:
    # Launch browser in headless mode
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()

    print('\n[1/6] Testing Login Page')
    try:
        start = time.time()
        page.goto(f'{BASE_URL}/usuarios/login/')
        page.wait_for_load_state('networkidle')

        # Take screenshot
        page.screenshot(path='load_test_login.png')

        # Fill login form (Django auth uses 'username' field for email)
        page.fill('input[type="email"]', TEST_EMAIL)
        page.fill('input[type="password"]', TEST_PASSWORD)

        # Click login button and measure
        login_start = time.time()
        page.click('button[type="submit"]')
        page.wait_for_url('**/dashboard/', timeout=10000)
        page.wait_for_load_state('networkidle')
        login_time = time.time() - login_start

        results['login'] = login_time
        print(f'  [OK] Login successful: {login_time:.2f}s')

    except Exception as e:
        print(f'  [FAIL] Login failed: {e}')
        browser.close()
        exit(1)

    print('\n[2/6] Testing Dashboard Page')
    try:
        start = time.time()
        page.goto(f'{BASE_URL}/dashboard/')
        page.wait_for_load_state('networkidle')
        dashboard_time = time.time() - start

        results['dashboard'] = dashboard_time

        # Take screenshot
        page.screenshot(path='load_test_dashboard.png', full_page=True)

        # Verify dashboard elements
        has_balance = page.locator('text=Saldo Total').count() > 0
        has_chart = page.locator('canvas').count() > 0
        has_recent = page.locator('text=Transações Recentes').count() > 0

        print(f'  [OK] Dashboard loaded: {dashboard_time:.2f}s')
        print(f'  - Balance card: {"Yes" if has_balance else "No"}')
        print(f'  - Chart: {"Yes" if has_chart else "No"}')
        print(f'  - Recent transactions: {"Yes" if has_recent else "No"}')

    except Exception as e:
        print(f'  [FAIL] Dashboard failed: {e}')

    print('\n[3/6] Testing Transactions List (All)')
    try:
        start = time.time()
        page.goto(f'{BASE_URL}/transacoes/')
        page.wait_for_load_state('networkidle')
        transactions_time = time.time() - start

        results['transactions_list'] = transactions_time

        # Take screenshot
        page.screenshot(path='load_test_transactions.png', full_page=True)

        # Check pagination
        has_pagination = page.locator('.pagination').count() > 0
        transaction_count = page.locator('tbody tr').count()

        print(f'  [OK] Transactions list loaded: {transactions_time:.2f}s')
        print(f'  - Pagination: {"Yes" if has_pagination else "No"}')
        print(f'  - Transactions on page: {transaction_count}')

    except Exception as e:
        print(f'  [FAIL] Transactions list failed: {e}')

    print('\n[4/6] Testing Filtered Transactions')
    try:
        # Apply filter
        start = time.time()

        # Click on expense filter if available
        expense_filter = page.locator('text=Despesa').first
        if expense_filter.count() > 0:
            expense_filter.click()
            page.wait_for_load_state('networkidle')

        filtered_time = time.time() - start
        results['transactions_filtered'] = filtered_time

        # Take screenshot
        page.screenshot(path='load_test_transactions_filtered.png', full_page=True)

        filtered_count = page.locator('tbody tr').count()

        print(f'  [OK] Filtered transactions loaded: {filtered_time:.2f}s')
        print(f'  - Filtered transactions shown: {filtered_count}')

    except Exception as e:
        print(f'  [FAIL] Filtered transactions failed: {e}')

    print('\n[5/6] Testing Accounts List')
    try:
        start = time.time()
        page.goto(f'{BASE_URL}/accounts/')
        page.wait_for_load_state('networkidle')
        accounts_time = time.time() - start

        results['accounts_list'] = accounts_time

        # Take screenshot
        page.screenshot(path='load_test_accounts.png', full_page=True)

        account_count = page.locator('.card').count()

        print(f'  [OK] Accounts list loaded: {accounts_time:.2f}s')
        print(f'  - Accounts shown: {account_count}')

    except Exception as e:
        print(f'  [FAIL] Accounts list failed: {e}')

    print('\n[6/6] Testing Categories List')
    try:
        start = time.time()
        page.goto(f'{BASE_URL}/categorias/')
        page.wait_for_load_state('networkidle')
        categories_time = time.time() - start

        results['categories_list'] = categories_time

        # Take screenshot
        page.screenshot(path='load_test_categories.png', full_page=True)

        category_count = page.locator('tbody tr').count()

        print(f'  [OK] Categories list loaded: {categories_time:.2f}s')
        print(f'  - Categories shown: {category_count}')

    except Exception as e:
        print(f'  [FAIL] Categories list failed: {e}')

    # Close browser
    browser.close()

# Display summary
print('\n' + '=' * 70)
print('PERFORMANCE SUMMARY')
print('=' * 70)
print('\nPage Load Times:')
print(f'  - Login & Redirect:        {results["login"]:.3f}s')
print(f'  - Dashboard:               {results["dashboard"]:.3f}s')
print(f'  - Transactions List (All): {results["transactions_list"]:.3f}s')
print(f'  - Transactions Filtered:   {results["transactions_filtered"]:.3f}s')
print(f'  - Accounts List:           {results["accounts_list"]:.3f}s')
print(f'  - Categories List:         {results["categories_list"]:.3f}s')

# Calculate average
avg_time = sum(results.values()) / len(results)
print(f'\nAverage Load Time: {avg_time:.3f}s')

# Performance rating
if avg_time < 1.0:
    rating = 'EXCELLENT'
elif avg_time < 2.0:
    rating = 'GOOD'
elif avg_time < 3.0:
    rating = 'ACCEPTABLE'
else:
    rating = 'NEEDS IMPROVEMENT'

print(f'Performance Rating: {rating}')

print('\nScreenshots saved:')
print('  - load_test_login.png')
print('  - load_test_dashboard.png')
print('  - load_test_transactions.png')
print('  - load_test_transactions_filtered.png')
print('  - load_test_accounts.png')
print('  - load_test_categories.png')

print('\n' + '=' * 70)
print('LOAD TEST COMPLETED!')
print('=' * 70)
