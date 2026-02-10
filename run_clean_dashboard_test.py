"""
Clean Dashboard Test - Fresh user for accurate results
"""

# Import the test class first (it sets up stdout)
from test_dashboard_calculations import DashboardTester
import random
import string

# Generate random email to ensure fresh start
random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
test_email = f'dashboard_test_{random_suffix}@test.com'
test_password = 'TestPass123!'

print(f"\nRunning dashboard test with fresh user: {test_email}\n")

tester = DashboardTester()
tester.test_email = test_email
tester.test_password = test_password

# Modify the run to use this email
original_run = tester.run_full_test

def modified_run():
    print("\n" + "="*60)
    print("FINANPY DASHBOARD CALCULATION TEST (Task 7.7.1)")
    print("="*60)
    print(f"Test user: {test_email}")
    print(f"Started at: {tester.test_results[0]['timestamp'] if tester.test_results else 'now'}")
    print("="*60 + "\n")

    # Run with our email
    from datetime import datetime
    import time

    # Step 1: Register/Login
    if not tester.register_user(test_email, test_password):
        print("\n❌ CRITICAL ERROR: Could not authenticate user. Stopping test.")
        return

    time.sleep(1)

    # Step 2: Create bank account
    initial_balance = 1000.00
    if not tester.create_account('Conta Teste Dashboard', 'checking', initial_balance):
        print("\n❌ CRITICAL ERROR: Could not create account. Stopping test.")
        return

    time.sleep(1)

    # Step 3: Check initial dashboard state
    print(f"\n{'='*60}")
    print("STEP 3: VERIFY INITIAL DASHBOARD STATE")
    print(f"{'='*60}\n")

    dashboard_data = tester.get_dashboard_data()
    if dashboard_data:
        # Verify total balance
        if dashboard_data['total_balance'] == initial_balance:
            tester.log_test('Initial total balance', 'PASS',
                         tester.format_currency(initial_balance),
                         tester.format_currency(dashboard_data['total_balance']))
        else:
            tester.log_test('Initial total balance', 'FAIL',
                         tester.format_currency(initial_balance),
                         tester.format_currency(dashboard_data['total_balance']),
                         'Balance does not match initial account balance')

        # Verify no income
        if dashboard_data['monthly_income'] == 0.0:
            tester.log_test('Initial monthly income', 'PASS', 'R$ 0,00',
                         tester.format_currency(dashboard_data['monthly_income']))
        else:
            tester.log_test('Initial monthly income', 'FAIL', 'R$ 0,00',
                         tester.format_currency(dashboard_data['monthly_income']))

        # Verify no expenses
        if dashboard_data['monthly_expenses'] == 0.0:
            tester.log_test('Initial monthly expenses', 'PASS', 'R$ 0,00',
                         tester.format_currency(dashboard_data['monthly_expenses']))
        else:
            tester.log_test('Initial monthly expenses', 'FAIL', 'R$ 0,00',
                         tester.format_currency(dashboard_data['monthly_expenses']))
    else:
        tester.log_test('Load dashboard', 'FAIL', 'Dashboard loaded', 'Could not load dashboard')

    time.sleep(1)

    # Step 4: Create income transaction
    print(f"\n{'='*60}")
    print("STEP 4: CREATE INCOME TRANSACTION")
    print(f"{'='*60}\n")

    income_amount = 500.00
    if not tester.create_transaction('income', income_amount, 'Salário teste'):
        print("\n❌ Could not create income transaction")

    time.sleep(1)

    # Step 5: Verify dashboard after income
    print(f"\n{'='*60}")
    print("STEP 5: VERIFY DASHBOARD AFTER INCOME")
    print(f"{'='*60}\n")

    expected_balance_after_income = initial_balance + income_amount
    dashboard_data = tester.get_dashboard_data()

    if dashboard_data:
        # Verify updated balance
        if dashboard_data['total_balance'] == expected_balance_after_income:
            tester.log_test('Balance after income', 'PASS',
                         tester.format_currency(expected_balance_after_income),
                         tester.format_currency(dashboard_data['total_balance']))
        else:
            tester.log_test('Balance after income', 'FAIL',
                         tester.format_currency(expected_balance_after_income),
                         tester.format_currency(dashboard_data['total_balance']),
                         f'Difference: {tester.format_currency(abs(expected_balance_after_income - dashboard_data["total_balance"]))}')

        # Verify monthly income
        if dashboard_data['monthly_income'] == income_amount:
            tester.log_test('Monthly income after transaction', 'PASS',
                         tester.format_currency(income_amount),
                         tester.format_currency(dashboard_data['monthly_income']))
        else:
            tester.log_test('Monthly income after transaction', 'FAIL',
                         tester.format_currency(income_amount),
                         tester.format_currency(dashboard_data['monthly_income']))
    else:
        tester.log_test('Load dashboard after income', 'FAIL', 'Dashboard loaded',
                     'Could not load dashboard')

    time.sleep(1)

    # Step 6: Create expense transaction
    print(f"\n{'='*60}")
    print("STEP 6: CREATE EXPENSE TRANSACTION")
    print(f"{'='*60}\n")

    expense_amount = 200.00
    if not tester.create_transaction('expense', expense_amount, 'Compra teste'):
        print("\n❌ Could not create expense transaction")

    time.sleep(1)

    # Step 7: Verify dashboard after expense
    print(f"\n{'='*60}")
    print("STEP 7: VERIFY DASHBOARD AFTER EXPENSE")
    print(f"{'='*60}\n")

    expected_final_balance = expected_balance_after_income - expense_amount
    expected_monthly_balance = income_amount - expense_amount
    dashboard_data = tester.get_dashboard_data()

    if dashboard_data:
        # Verify final balance
        if dashboard_data['total_balance'] == expected_final_balance:
            tester.log_test('Final total balance', 'PASS',
                         tester.format_currency(expected_final_balance),
                         tester.format_currency(dashboard_data['total_balance']))
        else:
            tester.log_test('Final total balance', 'FAIL',
                         tester.format_currency(expected_final_balance),
                         tester.format_currency(dashboard_data['total_balance']),
                         f'Difference: {tester.format_currency(abs(expected_final_balance - dashboard_data["total_balance"]))}')

        # Verify monthly expenses
        if dashboard_data['monthly_expenses'] == expense_amount:
            tester.log_test('Monthly expenses', 'PASS',
                         tester.format_currency(expense_amount),
                         tester.format_currency(dashboard_data['monthly_expenses']))
        else:
            tester.log_test('Monthly expenses', 'FAIL',
                         tester.format_currency(expense_amount),
                         tester.format_currency(dashboard_data['monthly_expenses']))

        # Verify monthly balance (savings)
        if dashboard_data['monthly_balance'] == expected_monthly_balance:
            tester.log_test('Monthly balance (savings)', 'PASS',
                         tester.format_currency(expected_monthly_balance),
                         tester.format_currency(dashboard_data['monthly_balance']))
        else:
            tester.log_test('Monthly balance (savings)', 'FAIL',
                         tester.format_currency(expected_monthly_balance),
                         tester.format_currency(dashboard_data['monthly_balance']))
    else:
        tester.log_test('Load dashboard after expense', 'FAIL', 'Dashboard loaded',
                     'Could not load dashboard')

    # Step 8: Verify recent transactions
    print(f"\n{'='*60}")
    print("STEP 8: VERIFY RECENT TRANSACTIONS SECTION")
    print(f"{'='*60}\n")

    if dashboard_data and dashboard_data['recent_transactions']:
        transaction_count = len(dashboard_data['recent_transactions'])
        if transaction_count >= 2:
            tester.log_test('Recent transactions displayed', 'PASS',
                         'At least 2 transactions shown',
                         f'{transaction_count} transactions found')

            # Verify transactions have required fields
            for idx, trans in enumerate(dashboard_data['recent_transactions'][:2], 1):
                has_date = bool(trans['date'])
                has_description = bool(trans['description'])
                has_amount = bool(trans['amount'])

                if has_date and has_description and has_amount:
                    tester.log_test(f'Transaction {idx} data completeness', 'PASS',
                                 'Date, description, amount present',
                                 f"Date: {trans['date']}, Desc: {trans['description'][:30]}...")
                else:
                    missing = []
                    if not has_date: missing.append('date')
                    if not has_description: missing.append('description')
                    if not has_amount: missing.append('amount')
                    tester.log_test(f'Transaction {idx} data completeness', 'FAIL',
                                 'All fields present',
                                 f'Missing: {", ".join(missing)}')
        else:
            tester.log_test('Recent transactions displayed', 'FAIL',
                         'At least 2 transactions',
                         f'Only {transaction_count} transaction(s) found')
    else:
        tester.log_test('Recent transactions displayed', 'FAIL',
                     'Transactions section visible',
                     'No transactions found in dashboard')

    # Generate summary report
    tester.generate_summary_report()

modified_run()
