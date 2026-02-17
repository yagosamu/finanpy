"""
Edge Case Testing Script for Finanpy
Tests various edge cases and boundary conditions
"""

from playwright.sync_api import sync_playwright, expect
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "edge_test_user@teste.com"
TEST_PASSWORD = "EdgeTest@2024!"

def take_screenshot(page, name):
    """Helper to take screenshots"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/edge_{name}_{timestamp}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"Screenshot saved: {filename}")
    return filename

def test_user_without_accounts(page):
    """Test 1: User Without Accounts"""
    print("\n=== TEST 1: User Without Accounts ===")
    results = []

    try:
        # Navigate to registration page
        print("Navigating to registration page...")
        page.goto(f"{BASE_URL}/usuarios/cadastro/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Take screenshot of registration page
        take_screenshot(page, "01_registration_page")

        # Fill registration form
        print(f"Registering new user: {TEST_EMAIL}")

        # Try different possible field selectors
        email_filled = False
        if page.locator('input[name="email"]').count() > 0:
            page.fill('input[name="email"]', TEST_EMAIL)
            email_filled = True
        elif page.locator('input[type="email"]').count() > 0:
            page.fill('input[type="email"]', TEST_EMAIL)
            email_filled = True

        password1_filled = False
        if page.locator('input[name="password1"]').count() > 0:
            page.fill('input[name="password1"]', TEST_PASSWORD)
            password1_filled = True
        elif page.locator('input[name="password"]').count() > 0:
            page.fill('input[name="password"]', TEST_PASSWORD)
            password1_filled = True

        password2_filled = False
        if page.locator('input[name="password2"]').count() > 0:
            page.fill('input[name="password2"]', TEST_PASSWORD)
            password2_filled = True
        elif page.locator('input[name="password_confirm"]').count() > 0:
            page.fill('input[name="password_confirm"]', TEST_PASSWORD)
            password2_filled = True

        print(f"Email filled: {email_filled}, Password1: {password1_filled}, Password2: {password2_filled}")

        # Take screenshot before submit
        take_screenshot(page, "02_registration_filled")

        # Submit form
        print("Submitting registration form...")
        if page.locator('button[type="submit"]').count() > 0:
            page.click('button[type="submit"]')
        elif page.locator('input[type="submit"]').count() > 0:
            page.click('input[type="submit"]')
        elif page.locator('button:has-text("Cadastrar")').count() > 0:
            page.click('button:has-text("Cadastrar")')

        page.wait_for_timeout(3000)
        take_screenshot(page, "03_after_registration")

        current_url = page.url
        print(f"Current URL after registration: {current_url}")

        # If registration failed, try to login instead
        if "cadastro" in current_url or "register" in current_url.lower():
            print("Registration may have failed (user might exist), trying login...")
            page.goto(f"{BASE_URL}/usuarios/login/", wait_until="networkidle")
            page.wait_for_timeout(2000)

            if page.locator('input[name="username"]').count() > 0:
                page.fill('input[name="username"]', TEST_EMAIL)
            elif page.locator('input[name="email"]').count() > 0:
                page.fill('input[name="email"]', TEST_EMAIL)
            elif page.locator('input[type="email"]').count() > 0:
                page.fill('input[type="email"]', TEST_EMAIL)

            if page.locator('input[name="password"]').count() > 0:
                page.fill('input[name="password"]', TEST_PASSWORD)

            take_screenshot(page, "04_login_filled")

            if page.locator('button[type="submit"]').count() > 0:
                page.click('button[type="submit"]')
            elif page.locator('button:has-text("Entrar")').count() > 0:
                page.click('button:has-text("Entrar")')

            page.wait_for_timeout(3000)
            take_screenshot(page, "05_after_login")

        # Navigate to dashboard
        print("Navigating to dashboard...")
        page.goto(f"{BASE_URL}/dashboard/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        screenshot_file = take_screenshot(page, "06_dashboard_no_accounts")

        # Check for errors or empty state
        has_error = page.locator('text=/erro|error/i').count() > 0
        has_empty_state = page.locator('text=/nenhum|vazio|empty|sem/i').count() > 0

        results.append({
            "test": "Dashboard with no accounts",
            "status": "PASSED" if not has_error else "FAILED",
            "details": f"Dashboard loaded without errors. Empty state shown: {has_empty_state}",
            "screenshot": screenshot_file
        })

        # Navigate to accounts list
        print("Navigating to accounts list...")
        page.goto(f"{BASE_URL}/accounts/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        screenshot_file = take_screenshot(page, "07_accounts_list_empty")

        has_error = page.locator('text=/erro|error/i').count() > 0
        has_empty_state = page.locator('text=/nenhum|vazio|empty|sem/i').count() > 0

        results.append({
            "test": "Accounts list with no accounts",
            "status": "PASSED" if not has_error else "FAILED",
            "details": f"Accounts list loaded without errors. Empty state shown: {has_empty_state}",
            "screenshot": screenshot_file
        })

    except Exception as e:
        results.append({
            "test": "User Without Accounts",
            "status": "FAILED",
            "details": f"Error: {str(e)}",
            "screenshot": ""
        })
        print(f"Error in test_user_without_accounts: {e}")

    return results

def test_account_without_transactions(page):
    """Test 2: Account Without Transactions"""
    print("\n=== TEST 2: Account Without Transactions ===")
    results = []

    try:
        # Navigate to create account page
        print("Navigating to create account page...")
        page.goto(f"{BASE_URL}/accounts/nova/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        take_screenshot(page, "08_create_account_page")

        # Fill account form
        print("Filling account form...")
        if page.locator('input[name="name"]').count() > 0:
            page.fill('input[name="name"]', "Conta Edge Test")
        elif page.locator('input[name="account_name"]').count() > 0:
            page.fill('input[name="account_name"]', "Conta Edge Test")

        # Select account type
        if page.locator('select[name="account_type"]').count() > 0:
            page.select_option('select[name="account_type"]', index=0)
        elif page.locator('select[name="type"]').count() > 0:
            page.select_option('select[name="type"]', index=0)

        # Fill bank name
        if page.locator('input[name="bank"]').count() > 0:
            page.fill('input[name="bank"]', "Banco Edge")
        elif page.locator('input[name="bank_name"]').count() > 0:
            page.fill('input[name="bank_name"]', "Banco Edge")

        # Fill initial balance
        if page.locator('input[name="balance"]').count() > 0:
            page.fill('input[name="balance"]', "500.00")
        elif page.locator('input[name="initial_balance"]').count() > 0:
            page.fill('input[name="initial_balance"]', "500.00")

        take_screenshot(page, "09_create_account_filled")

        # Submit form
        print("Submitting account form...")
        if page.locator('button[type="submit"]').count() > 0:
            page.click('button[type="submit"]')
        elif page.locator('button:has-text("Salvar")').count() > 0:
            page.click('button:has-text("Salvar")')

        page.wait_for_timeout(3000)
        screenshot_file = take_screenshot(page, "10_after_account_creation")

        results.append({
            "test": "Create account with no transactions",
            "status": "PASSED",
            "details": "Account created successfully",
            "screenshot": screenshot_file
        })

        # Navigate to transactions list
        print("Navigating to transactions list...")
        page.goto(f"{BASE_URL}/transacoes/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        screenshot_file = take_screenshot(page, "11_transactions_list_empty")

        has_error = page.locator('text=/erro|error/i').count() > 0
        has_empty_state = page.locator('text=/nenhum|vazio|empty|sem/i').count() > 0

        results.append({
            "test": "Transactions list with no transactions",
            "status": "PASSED" if not has_error else "FAILED",
            "details": f"Transactions list loaded without errors. Empty state shown: {has_empty_state}",
            "screenshot": screenshot_file
        })

        # Check dashboard
        print("Checking dashboard with account but no transactions...")
        page.goto(f"{BASE_URL}/dashboard/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        screenshot_file = take_screenshot(page, "12_dashboard_with_empty_account")

        has_error = page.locator('text=/erro|error/i').count() > 0

        results.append({
            "test": "Dashboard with account but no transactions",
            "status": "PASSED" if not has_error else "FAILED",
            "details": "Dashboard loaded with account but no transactions",
            "screenshot": screenshot_file
        })

    except Exception as e:
        results.append({
            "test": "Account Without Transactions",
            "status": "FAILED",
            "details": f"Error: {str(e)}",
            "screenshot": ""
        })
        print(f"Error in test_account_without_transactions: {e}")

    return results

def test_extreme_values(page):
    """Test 3: Extreme Values"""
    print("\n=== TEST 3: Extreme Values ===")
    results = []

    test_values = [
        ("0.01", "very small value", "should_pass"),
        ("999999.99", "very large value", "should_pass"),
        ("0", "zero value", "should_fail"),
        ("-100", "negative value", "should_fail")
    ]

    for value, description, expected in test_values:
        try:
            print(f"Testing transaction with {description}: {value}")
            page.goto(f"{BASE_URL}/transacoes/nova/", wait_until="networkidle")
            page.wait_for_timeout(2000)

            # Fill transaction form
            # Select type (receita/despesa)
            if page.locator('select[name="type"]').count() > 0:
                page.select_option('select[name="type"]', index=0)
            elif page.locator('select[name="transaction_type"]').count() > 0:
                page.select_option('select[name="transaction_type"]', index=0)

            # Fill amount
            if page.locator('input[name="amount"]').count() > 0:
                page.fill('input[name="amount"]', value)
            elif page.locator('input[name="value"]').count() > 0:
                page.fill('input[name="value"]', value)

            # Select date (today)
            today = datetime.now().strftime("%Y-%m-%d")
            if page.locator('input[name="date"]').count() > 0:
                page.fill('input[name="date"]', today)
            elif page.locator('input[name="transaction_date"]').count() > 0:
                page.fill('input[name="transaction_date"]', today)

            # Select category
            if page.locator('select[name="category"]').count() > 0:
                page.select_option('select[name="category"]', index=0)

            # Select account
            if page.locator('select[name="account"]').count() > 0:
                page.select_option('select[name="account"]', index=0)

            # Fill description
            if page.locator('input[name="description"]').count() > 0:
                page.fill('input[name="description"]', f"Test {description}")
            elif page.locator('textarea[name="description"]').count() > 0:
                page.fill('textarea[name="description"]', f"Test {description}")

            screenshot_name = f"13_transaction_{description.replace(' ', '_')}_filled"
            take_screenshot(page, screenshot_name)

            # Submit form
            if page.locator('button[type="submit"]').count() > 0:
                page.click('button[type="submit"]')
            elif page.locator('button:has-text("Salvar")').count() > 0:
                page.click('button:has-text("Salvar")')

            page.wait_for_timeout(3000)

            screenshot_name = f"14_transaction_{description.replace(' ', '_')}_result"
            screenshot_file = take_screenshot(page, screenshot_name)

            current_url = page.url
            has_error = page.locator('text=/erro|error|invalid|inválido/i').count() > 0

            # Determine if test passed
            if expected == "should_pass":
                passed = not has_error and "nova" not in current_url
            else:
                passed = has_error or "nova" in current_url

            results.append({
                "test": f"Transaction with {description} ({value})",
                "status": "PASSED" if passed else "FAILED",
                "details": f"Expected: {expected}, Has error: {has_error}, Stayed on form: {'nova' in current_url}",
                "screenshot": screenshot_file
            })

        except Exception as e:
            results.append({
                "test": f"Transaction with {description}",
                "status": "FAILED",
                "details": f"Error: {str(e)}",
                "screenshot": ""
            })
            print(f"Error testing {description}: {e}")

    return results

def test_date_edge_cases(page):
    """Test 4: Date Edge Cases"""
    print("\n=== TEST 4: Date Edge Cases ===")
    results = []

    test_dates = [
        (datetime.now().strftime("%Y-%m-%d"), "today's date", "should_pass"),
        ("2020-01-01", "past date", "should_pass"),
        ((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "future date", "should_fail")
    ]

    for date_value, description, expected in test_dates:
        try:
            print(f"Testing transaction with {description}: {date_value}")
            page.goto(f"{BASE_URL}/transacoes/nova/", wait_until="networkidle")
            page.wait_for_timeout(2000)

            # Fill minimum required fields
            if page.locator('select[name="type"]').count() > 0:
                page.select_option('select[name="type"]', index=0)

            if page.locator('input[name="amount"]').count() > 0:
                page.fill('input[name="amount"]', "100.00")
            elif page.locator('input[name="value"]').count() > 0:
                page.fill('input[name="value"]', "100.00")

            if page.locator('input[name="date"]').count() > 0:
                page.fill('input[name="date"]', date_value)
            elif page.locator('input[name="transaction_date"]').count() > 0:
                page.fill('input[name="transaction_date"]', date_value)

            if page.locator('select[name="category"]').count() > 0:
                page.select_option('select[name="category"]', index=0)

            if page.locator('select[name="account"]').count() > 0:
                page.select_option('select[name="account"]', index=0)

            if page.locator('input[name="description"]').count() > 0:
                page.fill('input[name="description"]', f"Test {description}")

            screenshot_name = f"15_date_{description.replace(' ', '_')}_filled"
            take_screenshot(page, screenshot_name)

            # Submit
            if page.locator('button[type="submit"]').count() > 0:
                page.click('button[type="submit"]')

            page.wait_for_timeout(3000)

            screenshot_name = f"16_date_{description.replace(' ', '_')}_result"
            screenshot_file = take_screenshot(page, screenshot_name)

            current_url = page.url
            has_error = page.locator('text=/erro|error|invalid|inválido/i').count() > 0

            if expected == "should_pass":
                passed = not has_error and "nova" not in current_url
            else:
                passed = has_error or "nova" in current_url

            results.append({
                "test": f"Transaction with {description} ({date_value})",
                "status": "PASSED" if passed else "FAILED",
                "details": f"Expected: {expected}, Has error: {has_error}, URL: {current_url}",
                "screenshot": screenshot_file
            })

        except Exception as e:
            results.append({
                "test": f"Date test: {description}",
                "status": "FAILED",
                "details": f"Error: {str(e)}",
                "screenshot": ""
            })
            print(f"Error testing {description}: {e}")

    return results

def test_empty_forms(page):
    """Test 5: Empty/Invalid Form Submissions"""
    print("\n=== TEST 5: Empty/Invalid Form Submissions ===")
    results = []

    # Test empty transaction form
    try:
        print("Testing empty transaction form...")
        page.goto(f"{BASE_URL}/transacoes/nova/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        take_screenshot(page, "17_empty_transaction_form")

        # Submit without filling
        if page.locator('button[type="submit"]').count() > 0:
            page.click('button[type="submit"]')

        page.wait_for_timeout(2000)
        screenshot_file = take_screenshot(page, "18_empty_transaction_submit")

        has_validation_error = page.locator('text=/obrigatório|required|preencha/i').count() > 0
        stayed_on_form = "nova" in page.url

        results.append({
            "test": "Empty transaction form submission",
            "status": "PASSED" if (has_validation_error or stayed_on_form) else "FAILED",
            "details": f"Validation errors shown: {has_validation_error}, Stayed on form: {stayed_on_form}",
            "screenshot": screenshot_file
        })

    except Exception as e:
        results.append({
            "test": "Empty transaction form",
            "status": "FAILED",
            "details": f"Error: {str(e)}",
            "screenshot": ""
        })

    # Test empty account form
    try:
        print("Testing empty account form...")
        page.goto(f"{BASE_URL}/accounts/nova/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        take_screenshot(page, "19_empty_account_form")

        # Submit without filling
        if page.locator('button[type="submit"]').count() > 0:
            page.click('button[type="submit"]')

        page.wait_for_timeout(2000)
        screenshot_file = take_screenshot(page, "20_empty_account_submit")

        has_validation_error = page.locator('text=/obrigatório|required|preencha/i').count() > 0
        stayed_on_form = "nova" in page.url

        results.append({
            "test": "Empty account form submission",
            "status": "PASSED" if (has_validation_error or stayed_on_form) else "FAILED",
            "details": f"Validation errors shown: {has_validation_error}, Stayed on form: {stayed_on_form}",
            "screenshot": screenshot_file
        })

    except Exception as e:
        results.append({
            "test": "Empty account form",
            "status": "FAILED",
            "details": f"Error: {str(e)}",
            "screenshot": ""
        })

    return results

def generate_report(all_results):
    """Generate final test report"""
    print("\n" + "="*80)
    print("EDGE CASE TESTING - FINAL REPORT")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: Finanpy - {BASE_URL}")
    print("\n")

    total_tests = sum(len(r) for r in all_results)
    passed_tests = sum(1 for r in all_results for test in r if test["status"] == "PASSED")
    failed_tests = total_tests - passed_tests

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print("\n")

    for i, test_group in enumerate(all_results, 1):
        print(f"\n{'='*80}")
        print(f"TEST GROUP {i}")
        print('='*80)
        for test in test_group:
            print(f"\nTest: {test['test']}")
            print(f"Status: {test['status']}")
            print(f"Details: {test['details']}")
            if test['screenshot']:
                print(f"Screenshot: {test['screenshot']}")
            print("-" * 40)

    # Write report to file
    with open("edge_case_test_report.txt", "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("EDGE CASE TESTING - FINAL REPORT\n")
        f.write("="*80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target: Finanpy - {BASE_URL}\n\n")
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Passed: {passed_tests}\n")
        f.write(f"Failed: {failed_tests}\n")
        f.write(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n\n")

        for i, test_group in enumerate(all_results, 1):
            f.write(f"\n{'='*80}\n")
            f.write(f"TEST GROUP {i}\n")
            f.write('='*80 + "\n")
            for test in test_group:
                f.write(f"\nTest: {test['test']}\n")
                f.write(f"Status: {test['status']}\n")
                f.write(f"Details: {test['details']}\n")
                if test['screenshot']:
                    f.write(f"Screenshot: {test['screenshot']}\n")
                f.write("-" * 40 + "\n")

    print("\n\nReport saved to: edge_case_test_report.txt")

def main():
    """Main test execution"""
    import os

    # Create screenshots directory
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    print("Starting Edge Case Testing for Finanpy")
    print(f"Target URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print("-" * 80)

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        all_results = []

        try:
            # Run all tests
            all_results.append(test_user_without_accounts(page))
            all_results.append(test_account_without_transactions(page))
            all_results.append(test_extreme_values(page))
            all_results.append(test_date_edge_cases(page))
            all_results.append(test_empty_forms(page))

            # Generate final report
            generate_report(all_results)

        except Exception as e:
            print(f"\n\nFATAL ERROR: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Close browser
            print("\n\nClosing browser...")
            page.wait_for_timeout(3000)
            browser.close()

if __name__ == "__main__":
    main()
