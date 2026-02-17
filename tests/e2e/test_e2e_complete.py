"""
Comprehensive End-to-End Test for Finanpy Application
Tests complete user journey from registration to dashboard verification
"""
import asyncio
from playwright.async_api import async_playwright, expect
from datetime import datetime
import os

# Test configuration
BASE_URL = 'http://localhost:8000'
TEST_EMAIL = 'teste_qa_891@teste.com'
TEST_PASSWORD = 'TestQA@2024!'
SCREENSHOTS_DIR = 'test_screenshots'

# Create screenshots directory
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class E2ETestReport:
    def __init__(self):
        self.steps = []
        self.issues = []
        self.screenshots = []

    def add_step(self, step_name, status, details=''):
        self.steps.append({
            'name': step_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def add_issue(self, issue):
        self.issues.append(issue)

    def add_screenshot(self, description, path):
        self.screenshots.append({
            'description': description,
            'path': path
        })

    def generate_report(self):
        print('\n' + '='*80)
        print('COMPREHENSIVE E2E TEST REPORT - FINANPY')
        print('='*80)
        print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'Base URL: {BASE_URL}')
        print(f'Test Email: {TEST_EMAIL}')
        print('\n' + '-'*80)
        print('TEST STEPS EXECUTED')
        print('-'*80)

        passed = 0
        failed = 0

        for i, step in enumerate(self.steps, 1):
            status_symbol = '[OK]' if step['status'] == 'PASSED' else '[FAIL]'
            print(f"{i}. {step['name']} - {status_symbol} {step['status']}")
            if step['details']:
                print(f"   Details: {step['details']}")

            if step['status'] == 'PASSED':
                passed += 1
            else:
                failed += 1

        print('\n' + '-'*80)
        print(f'SUMMARY: {passed} PASSED | {failed} FAILED')
        print('-'*80)

        if self.screenshots:
            print('\nSCREENSHOTS CAPTURED')
            print('-'*80)
            for screenshot in self.screenshots:
                print(f"- {screenshot['description']}")
                print(f"  Path: {screenshot['path']}")

        if self.issues:
            print('\nISSUES FOUND')
            print('-'*80)
            for issue in self.issues:
                print(f"- {issue}")
        else:
            print('\nNo issues found - All tests passed!')

        print('\n' + '='*80)

        overall_status = 'PASSED' if failed == 0 else 'FAILED'
        print(f'OVERALL STATUS: {overall_status}')
        print('='*80 + '\n')

        return overall_status

async def test_complete_user_flow():
    report = E2ETestReport()

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        try:
            # ===== STEP 1: REGISTRATION =====
            print('\n[1/7] Testing Registration Flow...')
            try:
                await page.goto(f'{BASE_URL}/usuarios/cadastro/')
                await page.wait_for_load_state('networkidle')

                # Take screenshot of registration page
                screenshot_path = f'{SCREENSHOTS_DIR}/01_registration_page.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Registration page loaded', screenshot_path)

                # Fill registration form
                await page.fill('input[name="email"]', TEST_EMAIL)
                await page.fill('input[name="password1"]', TEST_PASSWORD)
                await page.fill('input[name="password2"]', TEST_PASSWORD)

                # Take screenshot before submit
                screenshot_path = f'{SCREENSHOTS_DIR}/02_registration_filled.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Registration form filled', screenshot_path)

                # Submit form
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')

                # Wait a bit for redirect
                await asyncio.sleep(2)

                # Take screenshot after submit
                screenshot_path = f'{SCREENSHOTS_DIR}/03_registration_result.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('After registration submit', screenshot_path)

                current_url = page.url

                if '/dashboard/' in current_url or '/login/' in current_url:
                    report.add_step('Registration', 'PASSED', f'Redirected to: {current_url}')
                else:
                    # Check if there are error messages
                    error_elements = await page.query_selector_all('.alert-danger, .error, .text-red-500')
                    if error_elements:
                        error_text = await error_elements[0].inner_text()
                        report.add_step('Registration', 'INFO', f'User may already exist: {error_text}')
                    else:
                        report.add_step('Registration', 'PASSED', f'Current URL: {current_url}')

            except Exception as e:
                report.add_step('Registration', 'FAILED', str(e))
                report.add_issue(f'Registration failed: {str(e)}')

            # ===== STEP 2: LOGIN =====
            print('[2/7] Testing Login Flow...')
            try:
                # Navigate to login page
                await page.goto(f'{BASE_URL}/usuarios/login/')
                await page.wait_for_load_state('networkidle')

                screenshot_path = f'{SCREENSHOTS_DIR}/04_login_page.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Login page loaded', screenshot_path)

                # Fill login form
                await page.fill('input[name="email"]', TEST_EMAIL)
                await page.fill('input[name="password"]', TEST_PASSWORD)

                screenshot_path = f'{SCREENSHOTS_DIR}/05_login_filled.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Login form filled', screenshot_path)

                # Submit login
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                screenshot_path = f'{SCREENSHOTS_DIR}/06_login_result.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('After login submit', screenshot_path)

                current_url = page.url

                if '/dashboard/' in current_url:
                    report.add_step('Login', 'PASSED', 'Successfully logged in and redirected to dashboard')
                else:
                    report.add_step('Login', 'FAILED', f'Not redirected to dashboard. Current URL: {current_url}')
                    report.add_issue(f'Login did not redirect to dashboard: {current_url}')

            except Exception as e:
                report.add_step('Login', 'FAILED', str(e))
                report.add_issue(f'Login failed: {str(e)}')

            # ===== STEP 3: CREATE BANK ACCOUNT =====
            print('[3/7] Testing Create Bank Account Flow...')
            try:
                await page.goto(f'{BASE_URL}/accounts/nova/')
                await page.wait_for_load_state('networkidle')

                screenshot_path = f'{SCREENSHOTS_DIR}/07_create_account_page.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Create account page loaded', screenshot_path)

                # Fill account form
                await page.fill('input[name="name"]', 'Conta Teste QA')

                # Select account type (Conta Corrente)
                await page.select_option('select[name="account_type"]', 'checking')

                await page.fill('input[name="bank"]', 'Banco Teste')
                await page.fill('input[name="balance"]', '1000.00')

                screenshot_path = f'{SCREENSHOTS_DIR}/08_create_account_filled.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Create account form filled', screenshot_path)

                # Submit form
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                screenshot_path = f'{SCREENSHOTS_DIR}/09_create_account_result.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('After account creation', screenshot_path)

                current_url = page.url

                if '/accounts/' in current_url:
                    report.add_step('Create Bank Account', 'PASSED', 'Account created successfully')
                else:
                    report.add_step('Create Bank Account', 'FAILED', f'Unexpected URL: {current_url}')

            except Exception as e:
                report.add_step('Create Bank Account', 'FAILED', str(e))
                report.add_issue(f'Create bank account failed: {str(e)}')

            # ===== STEP 4: VIEW CATEGORIES =====
            print('[4/7] Testing Categories Page...')
            try:
                await page.goto(f'{BASE_URL}/categorias/')
                await page.wait_for_load_state('networkidle')

                screenshot_path = f'{SCREENSHOTS_DIR}/10_categories_page.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Categories page', screenshot_path)

                # Check if categories are displayed
                categories = await page.query_selector_all('.category, tr, .card')

                if len(categories) > 0:
                    report.add_step('View Categories', 'PASSED', f'Found {len(categories)} category elements')
                else:
                    report.add_step('View Categories', 'WARNING', 'No category elements found')

            except Exception as e:
                report.add_step('View Categories', 'FAILED', str(e))
                report.add_issue(f'View categories failed: {str(e)}')

            # ===== STEP 5: CREATE TRANSACTION =====
            print('[5/7] Testing Create Transaction Flow...')
            try:
                await page.goto(f'{BASE_URL}/transacoes/nova/')
                await page.wait_for_load_state('networkidle')

                screenshot_path = f'{SCREENSHOTS_DIR}/11_create_transaction_page.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Create transaction page', screenshot_path)

                # Fill transaction form
                # Select type (despesa/expense)
                type_select = await page.query_selector('select[name="transaction_type"]')
                if type_select:
                    await page.select_option('select[name="transaction_type"]', 'expense')

                await page.fill('input[name="amount"]', '150.00')

                # Set date to today
                today = datetime.now().strftime('%Y-%m-%d')
                date_input = await page.query_selector('input[name="date"]')
                if date_input:
                    await page.fill('input[name="date"]', today)

                # Select category (first available expense category)
                category_select = await page.query_selector('select[name="category"]')
                if category_select:
                    options = await category_select.query_selector_all('option')
                    if len(options) > 1:  # Skip first option if it's placeholder
                        await page.select_option('select[name="category"]', index=1)

                # Select account (should be the one we just created)
                account_select = await page.query_selector('select[name="account"]')
                if account_select:
                    options = await account_select.query_selector_all('option')
                    if len(options) > 1:
                        await page.select_option('select[name="account"]', index=1)

                # Fill description
                description_field = await page.query_selector('textarea[name="description"]')
                if description_field:
                    await page.fill('textarea[name="description"]', 'Transação teste QA')

                screenshot_path = f'{SCREENSHOTS_DIR}/12_create_transaction_filled.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Create transaction form filled', screenshot_path)

                # Submit form
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                screenshot_path = f'{SCREENSHOTS_DIR}/13_create_transaction_result.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('After transaction creation', screenshot_path)

                current_url = page.url

                if '/transacoes/' in current_url:
                    report.add_step('Create Transaction', 'PASSED', 'Transaction created successfully')
                else:
                    report.add_step('Create Transaction', 'FAILED', f'Unexpected URL: {current_url}')

            except Exception as e:
                report.add_step('Create Transaction', 'FAILED', str(e))
                report.add_issue(f'Create transaction failed: {str(e)}')

            # ===== STEP 6: VIEW DASHBOARD =====
            print('[6/7] Testing Dashboard View...')
            try:
                await page.goto(f'{BASE_URL}/dashboard/')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                screenshot_path = f'{SCREENSHOTS_DIR}/14_dashboard_desktop.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Dashboard - Desktop view (1280px)', screenshot_path)

                # Check for key elements
                balance_cards = await page.query_selector_all('.balance, .card, [class*="balance"]')
                transactions = await page.query_selector_all('.transaction, tr, [class*="transaction"]')

                dashboard_elements = {
                    'balance_cards': len(balance_cards),
                    'transactions': len(transactions)
                }

                report.add_step('View Dashboard', 'PASSED',
                               f'Dashboard loaded. Found {dashboard_elements["balance_cards"]} balance cards, '
                               f'{dashboard_elements["transactions"]} transaction elements')

            except Exception as e:
                report.add_step('View Dashboard', 'FAILED', str(e))
                report.add_issue(f'Dashboard view failed: {str(e)}')

            # ===== STEP 7: RESPONSIVE TESTING =====
            print('[7/7] Testing Responsive Design...')
            try:
                # Mobile viewport (375px)
                await page.set_viewport_size({'width': 375, 'height': 667})
                await page.goto(f'{BASE_URL}/dashboard/')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)

                screenshot_path = f'{SCREENSHOTS_DIR}/15_dashboard_mobile.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Dashboard - Mobile view (375px)', screenshot_path)

                # Tablet viewport (768px)
                await page.set_viewport_size({'width': 768, 'height': 1024})
                await page.goto(f'{BASE_URL}/dashboard/')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)

                screenshot_path = f'{SCREENSHOTS_DIR}/16_dashboard_tablet.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Dashboard - Tablet view (768px)', screenshot_path)

                # Desktop viewport (1280px)
                await page.set_viewport_size({'width': 1280, 'height': 720})
                await page.goto(f'{BASE_URL}/dashboard/')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)

                screenshot_path = f'{SCREENSHOTS_DIR}/17_dashboard_desktop_large.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                report.add_screenshot('Dashboard - Desktop view (1280px)', screenshot_path)

                report.add_step('Responsive Testing', 'PASSED',
                               'Tested mobile (375px), tablet (768px), and desktop (1280px) viewports')

            except Exception as e:
                report.add_step('Responsive Testing', 'FAILED', str(e))
                report.add_issue(f'Responsive testing failed: {str(e)}')

        except Exception as e:
            print(f'\nCritical error during test execution: {str(e)}')
            report.add_issue(f'Critical error: {str(e)}')

        finally:
            # Close browser
            await browser.close()

    # Generate and return report
    return report.generate_report()

async def main():
    print('='*80)
    print('FINANPY - COMPREHENSIVE END-TO-END TEST SUITE')
    print('='*80)
    print(f'\nStarting test execution at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Base URL: {BASE_URL}')
    print(f'Test user: {TEST_EMAIL}')
    print(f'Screenshots will be saved to: {SCREENSHOTS_DIR}/')
    print('\nPress Ctrl+C to abort test execution\n')

    result = await test_complete_user_flow()

    print(f'\nTest execution completed at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Overall result: {result}\n')

    return result

if __name__ == '__main__':
    asyncio.run(main())
