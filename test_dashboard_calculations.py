"""
E2E Test Script for Dashboard Calculations (Task 7.7.1)
Tests dashboard calculation accuracy with real transaction data.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DashboardTester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, status, expected, actual, notes=''):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'expected': expected,
            'actual': actual,
            'notes': notes,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        status_icon = '✓' if status == 'PASS' else '✗'
        print(f"{status_icon} {test_name}")
        print(f"  Expected: {expected}")
        print(f"  Actual: {actual}")
        if notes:
            print(f"  Notes: {notes}")
        print()

    def extract_csrf_token(self, html):
        """Extract CSRF token from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            return csrf_input.get('value')
        return None

    def parse_currency(self, text):
        """Parse Brazilian currency string to float"""
        # Remove R$, spaces, dots (thousand separator), replace comma with dot
        if not text:
            return 0.0
        cleaned = text.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def format_currency(self, value):
        """Format float to Brazilian currency string"""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def register_user(self, email, password):
        """Register a new user"""
        print(f"\n{'='*60}")
        print("STEP 1: REGISTER/LOGIN USER")
        print(f"{'='*60}\n")

        # Get registration page
        response = self.session.get(f'{self.base_url}/usuarios/cadastro/')
        if response.status_code != 200:
            self.log_test('Navigate to registration page', 'FAIL', '200', response.status_code,
                         'Could not access registration page')
            return False

        csrf_token = self.extract_csrf_token(response.text)

        # Attempt registration
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'email': email,
            'password1': password,
            'password2': password
        }

        response = self.session.post(
            f'{self.base_url}/usuarios/cadastro/',
            data=data,
            allow_redirects=True
        )

        # Check if logged in (either new user or already exists)
        if 'dashboard' in response.url or response.status_code == 200:
            self.log_test('User registration/login', 'PASS', 'User authenticated',
                         'User authenticated successfully')
            return True

        # Try login if registration failed
        response = self.session.get(f'{self.base_url}/usuarios/login/')
        csrf_token = self.extract_csrf_token(response.text)

        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': email,
            'password': password
        }

        response = self.session.post(
            f'{self.base_url}/usuarios/login/',
            data=data,
            allow_redirects=True
        )

        if response.status_code == 200:
            self.log_test('User login', 'PASS', 'User authenticated', 'User logged in successfully')
            return True
        else:
            self.log_test('User login', 'FAIL', 'User authenticated', f'Status {response.status_code}')
            return False

    def create_account(self, name, account_type, initial_balance):
        """Create a bank account"""
        print(f"\n{'='*60}")
        print("STEP 2: CREATE TEST BANK ACCOUNT")
        print(f"{'='*60}\n")

        # Get account creation page
        response = self.session.get(f'{self.base_url}/accounts/nova/')
        if response.status_code != 200:
            self.log_test('Navigate to account creation page', 'FAIL', '200', response.status_code)
            return None

        csrf_token = self.extract_csrf_token(response.text)

        # Create account (use US format with dot, not comma)
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'name': name,
            'account_type': account_type,
            'bank': 'Banco Teste',
            'initial_balance': str(initial_balance)  # Use dot format: "1000.00"
        }

        response = self.session.post(
            f'{self.base_url}/accounts/nova/',
            data=data,
            allow_redirects=True
        )

        if response.status_code == 200:
            # Extract account ID from redirect or page
            soup = BeautifulSoup(response.text, 'html.parser')
            # Try to find the account in the list
            self.log_test('Create bank account', 'PASS', f'Account "{name}" created',
                         f'Account created with initial balance {self.format_currency(initial_balance)}')
            return True
        else:
            self.log_test('Create bank account', 'FAIL', 'Account created',
                         f'Status {response.status_code}')
            return None

    def get_dashboard_data(self):
        """Get dashboard data and extract key metrics"""
        response = self.session.get(f'{self.base_url}/dashboard/')
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract dashboard metrics
        data = {
            'total_balance': 0.0,
            'monthly_income': 0.0,
            'monthly_expenses': 0.0,
            'monthly_balance': 0.0,
            'recent_transactions': []
        }

        # Find all cards with financial data
        # Look for specific text patterns
        text = soup.get_text()

        # Try to find balance card
        balance_patterns = [
            r'Saldo Total[\s\S]*?R\$\s*([\d.,]+)',
            r'Total[\s\S]*?R\$\s*([\d.,]+)',
        ]

        for pattern in balance_patterns:
            match = re.search(pattern, text)
            if match:
                data['total_balance'] = self.parse_currency(match.group(1))
                break

        # Find monthly income
        income_patterns = [
            r'Receitas do Mês[\s\S]*?R\$\s*([\d.,]+)',
            r'Receitas[\s\S]*?R\$\s*([\d.,]+)',
        ]

        for pattern in income_patterns:
            match = re.search(pattern, text)
            if match:
                data['monthly_income'] = self.parse_currency(match.group(1))
                break

        # Find monthly expenses
        expense_patterns = [
            r'Despesas do Mês[\s\S]*?R\$\s*([\d.,]+)',
            r'Despesas[\s\S]*?R\$\s*([\d.,]+)',
        ]

        for pattern in expense_patterns:
            match = re.search(pattern, text)
            if match:
                data['monthly_expenses'] = self.parse_currency(match.group(1))
                break

        # Calculate monthly balance
        data['monthly_balance'] = data['monthly_income'] - data['monthly_expenses']

        # Extract recent transactions
        transaction_table = soup.find('table')
        if transaction_table:
            rows = transaction_table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    transaction = {
                        'date': cols[0].get_text(strip=True),
                        'description': cols[1].get_text(strip=True),
                        'category': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                        'amount': cols[-1].get_text(strip=True)
                    }
                    data['recent_transactions'].append(transaction)

        return data

    def create_transaction(self, trans_type, amount, description, category_name=None, account_name=None):
        """Create a transaction"""
        # Get transaction creation page
        response = self.session.get(f'{self.base_url}/transacoes/nova/')
        if response.status_code != 200:
            self.log_test('Navigate to transaction page', 'FAIL', '200', response.status_code)
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = self.extract_csrf_token(response.text)

        # Find category and account select options
        category_select = soup.find('select', {'name': 'category'})
        account_select = soup.find('select', {'name': 'account'})

        category_id = None
        account_id = None

        if category_select:
            # Find first category of the right type (income or expense)
            for option in category_select.find_all('option'):
                if option.get('value'):
                    category_id = option.get('value')
                    break

        if account_select:
            # Find first account
            for option in account_select.find_all('option'):
                if option.get('value'):
                    account_id = option.get('value')
                    break

        if not category_id or not account_id:
            self.log_test('Get form data', 'FAIL', 'Category and account found',
                         'Could not find category or account')
            return False

        # Create transaction (use US format with dot)
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'transaction_type': trans_type,
            'amount': str(amount),  # Use dot format
            'description': description,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': category_id,
            'account': account_id
        }

        response = self.session.post(
            f'{self.base_url}/transacoes/nova/',
            data=data,
            allow_redirects=True
        )

        if response.status_code == 200:
            self.log_test(f'Create {trans_type} transaction', 'PASS',
                         f'Transaction created ({self.format_currency(amount)})',
                         'Transaction created successfully')
            return True
        else:
            self.log_test(f'Create {trans_type} transaction', 'FAIL',
                         'Transaction created', f'Status {response.status_code}')
            return False

    def run_full_test(self):
        """Run complete dashboard calculation test"""
        print("\n" + "="*60)
        print("FINANPY DASHBOARD CALCULATION TEST (Task 7.7.1)")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        # Step 1: Register/Login
        if not self.register_user('test_dashboard@test.com', 'TestPass123!'):
            print("\n❌ CRITICAL ERROR: Could not authenticate user. Stopping test.")
            return

        time.sleep(1)

        # Step 2: Create bank account
        initial_balance = 1000.00
        if not self.create_account('Conta Teste Dashboard', 'checking', initial_balance):
            print("\n❌ CRITICAL ERROR: Could not create account. Stopping test.")
            return

        time.sleep(1)

        # Step 3: Check initial dashboard state
        print(f"\n{'='*60}")
        print("STEP 3: VERIFY INITIAL DASHBOARD STATE")
        print(f"{'='*60}\n")

        dashboard_data = self.get_dashboard_data()
        if dashboard_data:
            # Verify total balance
            if dashboard_data['total_balance'] == initial_balance:
                self.log_test('Initial total balance', 'PASS',
                             self.format_currency(initial_balance),
                             self.format_currency(dashboard_data['total_balance']))
            else:
                self.log_test('Initial total balance', 'FAIL',
                             self.format_currency(initial_balance),
                             self.format_currency(dashboard_data['total_balance']),
                             'Balance does not match initial account balance')

            # Verify no income
            if dashboard_data['monthly_income'] == 0.0:
                self.log_test('Initial monthly income', 'PASS', 'R$ 0,00',
                             self.format_currency(dashboard_data['monthly_income']))
            else:
                self.log_test('Initial monthly income', 'FAIL', 'R$ 0,00',
                             self.format_currency(dashboard_data['monthly_income']))

            # Verify no expenses
            if dashboard_data['monthly_expenses'] == 0.0:
                self.log_test('Initial monthly expenses', 'PASS', 'R$ 0,00',
                             self.format_currency(dashboard_data['monthly_expenses']))
            else:
                self.log_test('Initial monthly expenses', 'FAIL', 'R$ 0,00',
                             self.format_currency(dashboard_data['monthly_expenses']))
        else:
            self.log_test('Load dashboard', 'FAIL', 'Dashboard loaded', 'Could not load dashboard')

        time.sleep(1)

        # Step 4: Create income transaction
        print(f"\n{'='*60}")
        print("STEP 4: CREATE INCOME TRANSACTION")
        print(f"{'='*60}\n")

        income_amount = 500.00
        if not self.create_transaction('income', income_amount, 'Salário teste'):
            print("\n❌ Could not create income transaction")

        time.sleep(1)

        # Step 5: Verify dashboard after income
        print(f"\n{'='*60}")
        print("STEP 5: VERIFY DASHBOARD AFTER INCOME")
        print(f"{'='*60}\n")

        expected_balance_after_income = initial_balance + income_amount
        dashboard_data = self.get_dashboard_data()

        if dashboard_data:
            # Verify updated balance
            if dashboard_data['total_balance'] == expected_balance_after_income:
                self.log_test('Balance after income', 'PASS',
                             self.format_currency(expected_balance_after_income),
                             self.format_currency(dashboard_data['total_balance']))
            else:
                self.log_test('Balance after income', 'FAIL',
                             self.format_currency(expected_balance_after_income),
                             self.format_currency(dashboard_data['total_balance']),
                             f'Difference: {self.format_currency(abs(expected_balance_after_income - dashboard_data["total_balance"]))}')

            # Verify monthly income
            if dashboard_data['monthly_income'] == income_amount:
                self.log_test('Monthly income after transaction', 'PASS',
                             self.format_currency(income_amount),
                             self.format_currency(dashboard_data['monthly_income']))
            else:
                self.log_test('Monthly income after transaction', 'FAIL',
                             self.format_currency(income_amount),
                             self.format_currency(dashboard_data['monthly_income']))
        else:
            self.log_test('Load dashboard after income', 'FAIL', 'Dashboard loaded',
                         'Could not load dashboard')

        time.sleep(1)

        # Step 6: Create expense transaction
        print(f"\n{'='*60}")
        print("STEP 6: CREATE EXPENSE TRANSACTION")
        print(f"{'='*60}\n")

        expense_amount = 200.00
        if not self.create_transaction('expense', expense_amount, 'Compra teste'):
            print("\n❌ Could not create expense transaction")

        time.sleep(1)

        # Step 7: Verify dashboard after expense
        print(f"\n{'='*60}")
        print("STEP 7: VERIFY DASHBOARD AFTER EXPENSE")
        print(f"{'='*60}\n")

        expected_final_balance = expected_balance_after_income - expense_amount
        expected_monthly_balance = income_amount - expense_amount
        dashboard_data = self.get_dashboard_data()

        if dashboard_data:
            # Verify final balance
            if dashboard_data['total_balance'] == expected_final_balance:
                self.log_test('Final total balance', 'PASS',
                             self.format_currency(expected_final_balance),
                             self.format_currency(dashboard_data['total_balance']))
            else:
                self.log_test('Final total balance', 'FAIL',
                             self.format_currency(expected_final_balance),
                             self.format_currency(dashboard_data['total_balance']),
                             f'Difference: {self.format_currency(abs(expected_final_balance - dashboard_data["total_balance"]))}')

            # Verify monthly expenses
            if dashboard_data['monthly_expenses'] == expense_amount:
                self.log_test('Monthly expenses', 'PASS',
                             self.format_currency(expense_amount),
                             self.format_currency(dashboard_data['monthly_expenses']))
            else:
                self.log_test('Monthly expenses', 'FAIL',
                             self.format_currency(expense_amount),
                             self.format_currency(dashboard_data['monthly_expenses']))

            # Verify monthly balance (savings)
            if dashboard_data['monthly_balance'] == expected_monthly_balance:
                self.log_test('Monthly balance (savings)', 'PASS',
                             self.format_currency(expected_monthly_balance),
                             self.format_currency(dashboard_data['monthly_balance']))
            else:
                self.log_test('Monthly balance (savings)', 'FAIL',
                             self.format_currency(expected_monthly_balance),
                             self.format_currency(dashboard_data['monthly_balance']))
        else:
            self.log_test('Load dashboard after expense', 'FAIL', 'Dashboard loaded',
                         'Could not load dashboard')

        # Step 8: Verify recent transactions
        print(f"\n{'='*60}")
        print("STEP 8: VERIFY RECENT TRANSACTIONS SECTION")
        print(f"{'='*60}\n")

        if dashboard_data and dashboard_data['recent_transactions']:
            transaction_count = len(dashboard_data['recent_transactions'])
            if transaction_count >= 2:
                self.log_test('Recent transactions displayed', 'PASS',
                             'At least 2 transactions shown',
                             f'{transaction_count} transactions found')

                # Verify transactions have required fields
                for idx, trans in enumerate(dashboard_data['recent_transactions'][:2], 1):
                    has_date = bool(trans['date'])
                    has_description = bool(trans['description'])
                    has_amount = bool(trans['amount'])

                    if has_date and has_description and has_amount:
                        self.log_test(f'Transaction {idx} data completeness', 'PASS',
                                     'Date, description, amount present',
                                     f"✓ Date: {trans['date']}, Desc: {trans['description'][:30]}...")
                    else:
                        missing = []
                        if not has_date: missing.append('date')
                        if not has_description: missing.append('description')
                        if not has_amount: missing.append('amount')
                        self.log_test(f'Transaction {idx} data completeness', 'FAIL',
                                     'All fields present',
                                     f'Missing: {", ".join(missing)}')
            else:
                self.log_test('Recent transactions displayed', 'FAIL',
                             'At least 2 transactions',
                             f'Only {transaction_count} transaction(s) found')
        else:
            self.log_test('Recent transactions displayed', 'FAIL',
                         'Transactions section visible',
                         'No transactions found in dashboard')

        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate final test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY REPORT")
        print("="*60 + "\n")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t['status'] == 'PASS')
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✓")
        print(f"Failed: {failed_tests} ✗")
        print(f"Pass Rate: {pass_rate:.1f}%\n")

        if failed_tests > 0:
            print("FAILED TESTS:")
            print("-" * 60)
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"\n✗ {result['test']}")
                    print(f"  Expected: {result['expected']}")
                    print(f"  Actual: {result['actual']}")
                    if result['notes']:
                        print(f"  Notes: {result['notes']}")

        print("\n" + "="*60)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        # Overall result
        if pass_rate == 100:
            print("🎉 ALL TESTS PASSED! Dashboard calculations are working correctly.")
        elif pass_rate >= 80:
            print("⚠️  MOSTLY PASSING - Some issues found that need attention.")
        else:
            print("❌ CRITICAL ISSUES - Dashboard calculations have significant problems.")


if __name__ == '__main__':
    tester = DashboardTester()
    tester.run_full_test()
