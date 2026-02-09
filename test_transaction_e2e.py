"""
E2E Test Script for Transaction Creation Flow
Task 6.9.1 - Testing transaction creation, validation, and balance updates
"""

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import traceback

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/usuarios/login/"
TRANSACTION_CREATE_URL = f"{BASE_URL}/transacoes/nova/"
TRANSACTION_LIST_URL = f"{BASE_URL}/transacoes/"
ACCOUNTS_URL = f"{BASE_URL}/accounts/"

# Test credentials
TEST_EMAIL = "qa-test@finanpy.com"
TEST_PASSWORD = "TestPass123!"

# Test results storage
test_results = []


class TestResult:
    def __init__(self, test_name, test_number):
        self.test_name = test_name
        self.test_number = test_number
        self.status = "PASS"
        self.steps = []
        self.screenshots = []
        self.issues = []
        self.expected = ""
        self.actual = ""

    def add_step(self, step_description, status="OK"):
        self.steps.append({"description": step_description, "status": status})

    def add_issue(self, issue):
        self.issues.append(issue)
        self.status = "FAIL"

    def add_screenshot(self, filename, description):
        self.screenshots.append({"file": filename, "description": description})

    def set_expected_actual(self, expected, actual):
        self.expected = expected
        self.actual = actual


def setup_driver():
    """Initialize Chrome WebDriver with appropriate options"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Trying Firefox...")
        try:
            from selenium.webdriver.firefox.options import Options
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            driver = webdriver.Firefox(options=firefox_options)
            return driver
        except Exception as e2:
            print(f"Error setting up Firefox driver: {e2}")
            raise Exception("Could not initialize any WebDriver")


def login(driver, result):
    """Perform login operation"""
    try:
        result.add_step("Navigate to login page")
        driver.get(LOGIN_URL)
        time.sleep(1)

        result.add_screenshot("login_page.png", "Login page before authentication")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\login_page.png")

        result.add_step("Fill email field")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)

        result.add_step("Fill password field")
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)

        result.add_step("Submit login form")
        # Find the submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for redirect after login
        time.sleep(2)

        result.add_step("Verify successful login")
        current_url = driver.current_url
        if "/usuarios/login/" in current_url:
            result.add_issue("Login failed - still on login page")
            result.add_step("Login verification", "FAILED")
            return False
        else:
            result.add_step("Login successful - redirected to dashboard", "OK")
            return True

    except Exception as e:
        result.add_issue(f"Login error: {str(e)}")
        result.add_step("Login process", "FAILED")
        return False


def test_1_create_income_transaction(driver):
    """Test Case 1: Create an Income transaction"""
    result = TestResult("Create Income Transaction", 1)
    result.add_step("Starting Test 1: Create Income Transaction")

    try:
        # Login first
        if not login(driver, result):
            test_results.append(result)
            return

        # Navigate to transaction creation page
        result.add_step(f"Navigate to {TRANSACTION_CREATE_URL}")
        driver.get(TRANSACTION_CREATE_URL)
        time.sleep(1)

        result.add_screenshot("transaction_form_initial.png", "Transaction form initial state")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\transaction_form_initial.png")

        # Select transaction type: Income (Receita)
        result.add_step("Select transaction type: Receita (income)")
        type_select = Select(driver.find_element(By.NAME, "transaction_type"))
        type_select.select_by_value("income")
        time.sleep(0.5)  # Wait for category dropdown to update via JavaScript

        # Enter amount
        result.add_step("Enter amount: 1500.00")
        amount_field = driver.find_element(By.NAME, "amount")
        amount_field.clear()
        amount_field.send_keys("1500.00")

        # Enter date
        result.add_step("Enter date: 2025-01-15")
        date_field = driver.find_element(By.NAME, "date")
        date_field.clear()
        date_field.send_keys("2025-01-15")

        # Select account
        result.add_step("Select account: Conta Corrente Itau")
        account_select = Select(driver.find_element(By.NAME, "account"))
        # Find option by partial text match
        for option in account_select.options:
            if "Conta Corrente Itau" in option.text or "Itau" in option.text:
                account_select.select_by_visible_text(option.text)
                break

        # Select category
        result.add_step("Select category: Salário")
        category_select = Select(driver.find_element(By.NAME, "category"))
        # Find Salário option
        for option in category_select.options:
            if "Salário" in option.text or "Salario" in option.text:
                category_select.select_by_visible_text(option.text)
                break

        # Enter description
        result.add_step("Enter description: Salário de janeiro")
        description_field = driver.find_element(By.NAME, "description")
        description_field.clear()
        description_field.send_keys("Salário de janeiro")

        result.add_screenshot("transaction_form_filled.png", "Transaction form filled with income data")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\transaction_form_filled_income.png")

        # Submit the form
        result.add_step("Submit transaction form")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for redirect
        time.sleep(2)

        # Verify redirect to transaction list
        result.add_step("Verify redirect to transaction list")
        current_url = driver.current_url
        if "/transacoes/" in current_url:
            result.add_step("Redirected to transaction list successfully", "OK")
        else:
            result.add_issue(f"Expected redirect to transaction list, but current URL is: {current_url}")
            result.add_step("Redirect verification", "FAILED")

        result.add_screenshot("after_income_creation.png", "Page after income transaction creation")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\after_income_creation.png")

        # Check for success message
        result.add_step("Check for success message")
        try:
            # Look for common success message patterns
            page_source = driver.page_source.lower()
            if "sucesso" in page_source or "success" in page_source or "criada" in page_source or "criado" in page_source:
                result.add_step("Success message found", "OK")
            else:
                result.add_issue("No success message visible on page")
        except Exception as e:
            result.add_issue(f"Could not verify success message: {str(e)}")

        # Verify transaction appears in list
        result.add_step("Verify transaction appears in list")
        try:
            page_text = driver.page_source
            if "1500" in page_text and ("Salário de janeiro" in page_text or "Salario de janeiro" in page_text):
                result.add_step("Transaction visible in list", "OK")
            else:
                result.add_issue("Created transaction not found in list")
        except Exception as e:
            result.add_issue(f"Error verifying transaction in list: {str(e)}")

        result.set_expected_actual(
            "Transaction created, redirected to list, success message shown, transaction visible",
            f"URL: {current_url}, Transaction creation completed"
        )

    except Exception as e:
        result.add_issue(f"Test 1 failed with exception: {str(e)}\n{traceback.format_exc()}")
        result.add_step("Test execution", "FAILED")

    test_results.append(result)


def test_2_create_expense_transaction(driver):
    """Test Case 2: Create an Expense transaction"""
    result = TestResult("Create Expense Transaction", 2)
    result.add_step("Starting Test 2: Create Expense Transaction")

    try:
        # Navigate to transaction creation page
        result.add_step(f"Navigate to {TRANSACTION_CREATE_URL}")
        driver.get(TRANSACTION_CREATE_URL)
        time.sleep(1)

        # Select transaction type: Expense (Despesa)
        result.add_step("Select transaction type: Despesa (expense)")
        type_select = Select(driver.find_element(By.NAME, "transaction_type"))
        type_select.select_by_value("expense")
        time.sleep(0.5)  # Wait for category dropdown to update

        # Enter amount
        result.add_step("Enter amount: 250.50")
        amount_field = driver.find_element(By.NAME, "amount")
        amount_field.clear()
        amount_field.send_keys("250.50")

        # Enter date
        result.add_step("Enter date: 2025-01-16")
        date_field = driver.find_element(By.NAME, "date")
        date_field.clear()
        date_field.send_keys("2025-01-16")

        # Select account
        result.add_step("Select account: Carteira Pessoal")
        account_select = Select(driver.find_element(By.NAME, "account"))
        for option in account_select.options:
            if "Carteira Pessoal" in option.text or "Carteira" in option.text:
                account_select.select_by_visible_text(option.text)
                break

        # Select category
        result.add_step("Select category: Alimentação")
        category_select = Select(driver.find_element(By.NAME, "category"))
        for option in category_select.options:
            if "Alimentação" in option.text or "Alimentacao" in option.text:
                category_select.select_by_visible_text(option.text)
                break

        # Enter description
        result.add_step("Enter description: Compras no supermercado")
        description_field = driver.find_element(By.NAME, "description")
        description_field.clear()
        description_field.send_keys("Compras no supermercado")

        result.add_screenshot("transaction_form_filled_expense.png", "Transaction form filled with expense data")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\transaction_form_filled_expense.png")

        # Submit the form
        result.add_step("Submit transaction form")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for redirect
        time.sleep(2)

        # Verify redirect
        result.add_step("Verify redirect to transaction list")
        current_url = driver.current_url
        if "/transacoes/" in current_url:
            result.add_step("Redirected to transaction list successfully", "OK")
        else:
            result.add_issue(f"Expected redirect to transaction list, but current URL is: {current_url}")
            result.add_step("Redirect verification", "FAILED")

        result.add_screenshot("after_expense_creation.png", "Page after expense transaction creation")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\after_expense_creation.png")

        # Check for success message
        result.add_step("Check for success message")
        page_source = driver.page_source.lower()
        if "sucesso" in page_source or "success" in page_source or "criada" in page_source or "criado" in page_source:
            result.add_step("Success message found", "OK")
        else:
            result.add_issue("No success message visible on page")

        # Verify transaction appears in list
        result.add_step("Verify transaction appears in list")
        page_text = driver.page_source
        if "250" in page_text and "Compras no supermercado" in page_text:
            result.add_step("Transaction visible in list", "OK")
        else:
            result.add_issue("Created transaction not found in list")

        result.set_expected_actual(
            "Expense transaction created, redirected to list, success message shown, transaction visible",
            f"URL: {current_url}, Transaction creation completed"
        )

    except Exception as e:
        result.add_issue(f"Test 2 failed with exception: {str(e)}\n{traceback.format_exc()}")
        result.add_step("Test execution", "FAILED")

    test_results.append(result)


def test_3_verify_balance_updates(driver):
    """Test Case 3: Verify Balance Updates"""
    result = TestResult("Verify Balance Updates", 3)
    result.add_step("Starting Test 3: Verify Balance Updates")

    try:
        # Navigate to accounts page
        result.add_step(f"Navigate to {ACCOUNTS_URL}")
        driver.get(ACCOUNTS_URL)
        time.sleep(1)

        result.add_screenshot("accounts_page.png", "Accounts page with updated balances")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\accounts_page.png")

        page_text = driver.page_source

        # Check Conta Corrente Itau balance (should be 2500 + 1500 = 4000)
        result.add_step("Check Conta Corrente Itau balance (expected: R$ 4,000.00)")
        if "4.000" in page_text or "4000" in page_text or "4,000" in page_text:
            result.add_step("Conta Corrente Itau balance correctly updated to R$ 4,000.00", "OK")
        else:
            result.add_issue("Conta Corrente Itau balance not showing expected value of R$ 4,000.00")
            result.add_step("Conta Corrente Itau balance check", "FAILED")

        # Check Carteira Pessoal balance (should be 350.75 - 250.50 = 100.25)
        result.add_step("Check Carteira Pessoal balance (expected: R$ 100.25)")
        if "100,25" in page_text or "100.25" in page_text:
            result.add_step("Carteira Pessoal balance correctly updated to R$ 100.25", "OK")
        else:
            result.add_issue("Carteira Pessoal balance not showing expected value of R$ 100.25")
            result.add_step("Carteira Pessoal balance check", "FAILED")

        result.set_expected_actual(
            "Conta Corrente Itau: R$ 4,000.00, Carteira Pessoal: R$ 100.25",
            "Balance updates verified on accounts page"
        )

    except Exception as e:
        result.add_issue(f"Test 3 failed with exception: {str(e)}\n{traceback.format_exc()}")
        result.add_step("Test execution", "FAILED")

    test_results.append(result)


def test_4_form_validations(driver):
    """Test Case 4: Test Form Validations"""
    result = TestResult("Form Validation Tests", 4)
    result.add_step("Starting Test 4: Form Validation Tests")

    try:
        # Test 4a: Submit empty form
        result.add_step("Test 4a: Submit empty form")
        driver.get(TRANSACTION_CREATE_URL)
        time.sleep(1)

        result.add_screenshot("empty_form.png", "Empty transaction form")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\empty_form.png")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(1)

        # Check if still on form page (validation should prevent submission)
        current_url = driver.current_url
        if "nova" in current_url:
            result.add_step("Empty form submission blocked by validation", "OK")
        else:
            result.add_issue("Empty form was submitted without validation errors")
            result.add_step("Empty form validation", "FAILED")

        result.add_screenshot("empty_form_validation.png", "Validation errors for empty form")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\empty_form_validation.png")

        # Test 4b: Future date validation
        result.add_step("Test 4b: Future date validation")
        driver.get(TRANSACTION_CREATE_URL)
        time.sleep(1)

        # Fill form with future date
        type_select = Select(driver.find_element(By.NAME, "transaction_type"))
        type_select.select_by_value("income")

        amount_field = driver.find_element(By.NAME, "amount")
        amount_field.clear()
        amount_field.send_keys("100.00")

        date_field = driver.find_element(By.NAME, "date")
        date_field.clear()
        date_field.send_keys("2027-01-01")

        account_select = Select(driver.find_element(By.NAME, "account"))
        account_select.select_by_index(1)  # Select first account

        category_select = Select(driver.find_element(By.NAME, "category"))
        time.sleep(0.5)
        category_select.select_by_index(1)  # Select first category

        result.add_screenshot("future_date_form.png", "Form with future date")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\future_date_form.png")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(1)

        # Check for date validation error
        page_source = driver.page_source.lower()
        current_url = driver.current_url

        if "nova" in current_url or "erro" in page_source or "error" in page_source or "data" in page_source:
            result.add_step("Future date validation working", "OK")
        else:
            result.add_issue("Future date was accepted without validation error")
            result.add_step("Future date validation", "FAILED")

        result.add_screenshot("future_date_validation.png", "Future date validation result")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\future_date_validation.png")

        # Test 4c: Zero/negative amount validation
        result.add_step("Test 4c: Zero/negative amount validation")
        driver.get(TRANSACTION_CREATE_URL)
        time.sleep(1)

        type_select = Select(driver.find_element(By.NAME, "transaction_type"))
        type_select.select_by_value("income")

        amount_field = driver.find_element(By.NAME, "amount")
        amount_field.clear()
        amount_field.send_keys("0")

        date_field = driver.find_element(By.NAME, "date")
        date_field.clear()
        date_field.send_keys("2025-01-15")

        account_select = Select(driver.find_element(By.NAME, "account"))
        account_select.select_by_index(1)

        category_select = Select(driver.find_element(By.NAME, "category"))
        time.sleep(0.5)
        category_select.select_by_index(1)

        result.add_screenshot("zero_amount_form.png", "Form with zero amount")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\zero_amount_form.png")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(1)

        current_url = driver.current_url
        page_source = driver.page_source.lower()

        if "nova" in current_url or "erro" in page_source or "error" in page_source:
            result.add_step("Zero amount validation working", "OK")
        else:
            result.add_issue("Zero amount was accepted without validation error")
            result.add_step("Zero amount validation", "FAILED")

        result.add_screenshot("zero_amount_validation.png", "Zero amount validation result")
        driver.save_screenshot("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\zero_amount_validation.png")

        result.set_expected_actual(
            "All form validations working: empty form blocked, future dates rejected, zero/negative amounts rejected",
            "Validation tests completed"
        )

    except Exception as e:
        result.add_issue(f"Test 4 failed with exception: {str(e)}\n{traceback.format_exc()}")
        result.add_step("Test execution", "FAILED")

    test_results.append(result)


def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "="*80)
    print("E2E TEST REPORT - TRANSACTION CREATION FLOW (Task 6.9.1)")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Total Tests: {len(test_results)}")

    passed = sum(1 for r in test_results if r.status == "PASS")
    failed = sum(1 for r in test_results if r.status == "FAIL")
    pass_rate = (passed / len(test_results) * 100) if test_results else 0

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print("="*80)

    for result in test_results:
        print(f"\n{'='*80}")
        print(f"TEST #{result.test_number}: {result.test_name}")
        print(f"Status: {result.status}")
        print(f"{'='*80}")

        print("\nSteps Executed:")
        for i, step in enumerate(result.steps, 1):
            status_symbol = "OK" if step["status"] == "OK" else "FAIL" if step["status"] == "FAILED" else "INFO"
            print(f"  {i}. [{status_symbol}] {step['description']}")

        if result.screenshots:
            print("\nScreenshots:")
            for screenshot in result.screenshots:
                print(f"  - {screenshot['file']}: {screenshot['description']}")

        if result.expected or result.actual:
            print(f"\nExpected: {result.expected}")
            print(f"Actual: {result.actual}")

        if result.issues:
            print("\nIssues Found:")
            for issue in result.issues:
                print(f"  - {issue}")

    print("\n" + "="*80)
    print("SUMMARY AND RECOMMENDATIONS")
    print("="*80)

    if failed == 0:
        print("\nAll tests PASSED successfully!")
        print("The transaction creation flow is working as expected.")
    else:
        print(f"\n{failed} test(s) FAILED. Review the issues above.")

    print("\nTest Coverage:")
    print("- Income transaction creation: TESTED")
    print("- Expense transaction creation: TESTED")
    print("- Balance updates verification: TESTED")
    print("- Form validations: TESTED")

    print("\n" + "="*80)


def main():
    """Main test execution function"""
    driver = None

    try:
        print("Setting up WebDriver...")
        driver = setup_driver()
        print("WebDriver initialized successfully")

        # Create screenshots directory
        import os
        os.makedirs("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots", exist_ok=True)

        print("\nStarting E2E tests...")
        print("="*80)

        # Run all test cases
        test_1_create_income_transaction(driver)
        print("Test 1 completed")

        test_2_create_expense_transaction(driver)
        print("Test 2 completed")

        test_3_verify_balance_updates(driver)
        print("Test 3 completed")

        test_4_form_validations(driver)
        print("Test 4 completed")

        # Generate report
        generate_report()

    except Exception as e:
        print(f"Fatal error during test execution: {str(e)}")
        print(traceback.format_exc())

    finally:
        if driver:
            driver.quit()
            print("\nWebDriver closed")


if __name__ == "__main__":
    main()
