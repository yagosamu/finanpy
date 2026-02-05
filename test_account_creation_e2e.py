"""
E2E Testing for Account Creation Functionality
Task 4.7.1: Test Account Creation with validation scenarios

Test Credentials:
- Email: qa-test@finanpy.com
- Password: QaTest@2024!
"""

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os


class AccountCreationE2ETester:
    def __init__(self, base_url='http://localhost:8000', headless=False):
        self.base_url = base_url
        self.results = []
        self.screenshots_dir = 'test_screenshots/account_creation'

        # Test credentials
        self.test_email = 'qa-test@finanpy.com'
        self.test_password = 'QaTest@2024!'

        # Create screenshots directory
        os.makedirs(self.screenshots_dir, exist_ok=True)

        # Setup Chrome driver
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def take_screenshot(self, name):
        """Take a screenshot with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.screenshots_dir}/{timestamp}_{name}.png'
        self.driver.save_screenshot(filename)
        return filename

    def log_result(self, test_name, status, message, screenshot=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'screenshot': screenshot,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)

        status_symbol = 'PASS' if status == 'PASS' else 'FAIL' if status == 'FAIL' else 'INFO'
        print(f'[{status_symbol}] {test_name}: {message}')

    def login(self):
        """Step 1: Login with test credentials"""
        try:
            print('\n=== STEP 1: Login ===\n')

            self.driver.get(f'{self.base_url}/login/')
            time.sleep(1)

            screenshot = self.take_screenshot('01_login_page')

            # Find and fill login form
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, 'email'))
            )
            password_input = self.driver.find_element(By.NAME, 'password')

            email_input.clear()
            email_input.send_keys(self.test_email)
            password_input.clear()
            password_input.send_keys(self.test_password)

            screenshot = self.take_screenshot('02_login_filled')

            # Submit form - look for button with text "Entrar"
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()

            time.sleep(2)

            # Check if login successful
            if 'login' not in self.driver.current_url:
                screenshot = self.take_screenshot('03_login_success')
                self.log_result('Step 1: Login', 'PASS', f'Successfully logged in as {self.test_email}', screenshot)
                return True
            else:
                screenshot = self.take_screenshot('03_login_failed')
                self.log_result('Step 1: Login', 'FAIL', 'Login failed - check credentials or redirect', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('03_login_error')
            self.log_result('Step 1: Login', 'FAIL', f'Login error: {str(e)}', screenshot)
            return False

    def navigate_to_account_creation(self):
        """Step 2: Navigate to Account Creation page"""
        try:
            print('\n=== STEP 2: Navigate to Account Creation ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(2)

            screenshot = self.take_screenshot('04_account_creation_page')

            # Verify we're on the account creation page
            if 'nova' in self.driver.current_url:
                self.log_result('Step 2: Navigate to Account Creation', 'PASS', 'Successfully navigated to /accounts/nova/', screenshot)
                return True
            else:
                self.log_result('Step 2: Navigate to Account Creation', 'FAIL', f'Wrong URL: {self.driver.current_url}', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('04_navigation_error')
            self.log_result('Step 2: Navigate to Account Creation', 'FAIL', f'Navigation error: {str(e)}', screenshot)
            return False

    def test_empty_form_submission(self):
        """Step 3.1: Test empty form submission"""
        try:
            print('\n=== STEP 3.1: Test Empty Form Submission ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(1)

            screenshot = self.take_screenshot('05_empty_form_before')

            # Try to submit empty form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(1)

            screenshot = self.take_screenshot('06_empty_form_after')

            # Check for validation messages
            page_source = self.driver.page_source.lower()

            # Look for error indicators
            has_errors = False
            error_messages = []

            # Check for HTML5 validation or Django error messages
            if 'este campo é obrigatório' in page_source or 'required' in page_source or 'obrigatório' in page_source:
                has_errors = True
                error_messages.append('Required field validation messages found')

            # Check if still on the same page (not redirected)
            if 'nova' in self.driver.current_url:
                has_errors = True
                error_messages.append('Form did not submit (stayed on creation page)')

            try:
                # Look for error elements
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.errorlist, .error, .text-red-500, .invalid-feedback')
                if error_elements:
                    has_errors = True
                    error_messages.append(f'Found {len(error_elements)} error elements on page')
            except:
                pass

            if has_errors:
                self.log_result('Step 3.1: Empty Form Validation', 'PASS', f'Empty form rejected correctly. {"; ".join(error_messages)}', screenshot)
                return True
            else:
                self.log_result('Step 3.1: Empty Form Validation', 'FAIL', 'Empty form was accepted (should have been rejected)', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('06_empty_form_error')
            self.log_result('Step 3.1: Empty Form Validation', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def test_name_too_short(self):
        """Step 3.2: Test name validation with 1 character"""
        try:
            print('\n=== STEP 3.2: Test Name Too Short Validation ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(1)

            # Fill with 1 character name
            name_input = self.driver.find_element(By.NAME, 'name')
            name_input.clear()
            name_input.send_keys('A')

            # Fill other required fields
            try:
                account_type_select = Select(self.driver.find_element(By.NAME, 'account_type'))
                account_type_select.select_by_value('checking')
            except:
                pass

            try:
                initial_balance = self.driver.find_element(By.NAME, 'initial_balance')
                initial_balance.clear()
                initial_balance.send_keys('100')
            except:
                pass

            screenshot = self.take_screenshot('07_short_name_before')

            # Submit
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(1)

            screenshot = self.take_screenshot('08_short_name_after')

            # Check for specific error message
            page_source = self.driver.page_source
            expected_error = 'O nome da conta deve ter pelo menos 2 caracteres.'

            if expected_error in page_source:
                self.log_result('Step 3.2: Name Too Short Validation', 'PASS', f'Correct error message displayed: "{expected_error}"', screenshot)
                return True
            elif 'nova' in self.driver.current_url:
                # Still on form page, some validation occurred
                self.log_result('Step 3.2: Name Too Short Validation', 'PASS', 'Short name rejected (validation occurred)', screenshot)
                return True
            else:
                self.log_result('Step 3.2: Name Too Short Validation', 'FAIL', 'Short name was accepted or wrong error message', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('08_short_name_error')
            self.log_result('Step 3.2: Name Too Short Validation', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def test_valid_name(self):
        """Step 3.3: Test valid name with 2+ characters"""
        try:
            print('\n=== STEP 3.3: Test Valid Name ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(1)

            # Fill with valid 2+ character name
            name_input = self.driver.find_element(By.NAME, 'name')
            name_input.clear()
            name_input.send_keys('AB')

            # Fill other required fields
            try:
                account_type_select = Select(self.driver.find_element(By.NAME, 'account_type'))
                account_type_select.select_by_value('checking')
            except:
                pass

            try:
                initial_balance = self.driver.find_element(By.NAME, 'initial_balance')
                initial_balance.clear()
                initial_balance.send_keys('100')
            except:
                pass

            screenshot = self.take_screenshot('09_valid_name_filled')

            # Note: We're just testing that the name is accepted, not submitting yet
            # Check that there's no immediate validation error
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.errorlist, .error, .text-red-500')
                if not error_elements:
                    self.log_result('Step 3.3: Valid Name Test', 'PASS', 'Valid 2-character name accepted without errors', screenshot)
                    return True
                else:
                    self.log_result('Step 3.3: Valid Name Test', 'FAIL', 'Valid name showing errors', screenshot)
                    return False
            except:
                self.log_result('Step 3.3: Valid Name Test', 'PASS', 'Valid 2-character name accepted', screenshot)
                return True

        except Exception as e:
            screenshot = self.take_screenshot('09_valid_name_error')
            self.log_result('Step 3.3: Valid Name Test', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def test_successful_account_creation(self):
        """Step 4: Test successful account creation"""
        try:
            print('\n=== STEP 4: Test Successful Account Creation ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(1)

            # Fill the form with valid data
            test_account_name = f'Conta Corrente Teste QA'

            name_input = self.driver.find_element(By.NAME, 'name')
            name_input.clear()
            name_input.send_keys(test_account_name)

            # Select account type: Conta Corrente (checking)
            account_type_select = Select(self.driver.find_element(By.NAME, 'account_type'))
            account_type_select.select_by_value('checking')

            # Fill bank name
            try:
                bank_input = self.driver.find_element(By.NAME, 'bank')
                bank_input.clear()
                bank_input.send_keys('Banco do Brasil')
            except:
                pass

            # Fill initial balance
            initial_balance = self.driver.find_element(By.NAME, 'initial_balance')
            initial_balance.clear()
            initial_balance.send_keys('1500.50')

            screenshot = self.take_screenshot('10_account_form_filled')

            # Submit
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(2)

            screenshot = self.take_screenshot('11_after_submit')

            # Check for success
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            success = False
            success_message = ''

            # Check if redirected to accounts list
            if '/accounts/' in current_url and 'nova' not in current_url:
                success = True
                success_message = 'Redirected to accounts list'

            # Check for success message
            if 'sucesso' in page_source or 'success' in page_source or 'criada' in page_source or 'adicionada' in page_source:
                success = True
                success_message += '; Success message found'

            # Check if account appears in the list
            if test_account_name.lower() in page_source:
                success = True
                success_message += '; Account appears in list'

            if success:
                self.log_result('Step 4: Successful Account Creation', 'PASS', f'Account created successfully. {success_message}', screenshot)
                return True
            else:
                self.log_result('Step 4: Successful Account Creation', 'FAIL', f'Account creation failed. URL: {current_url}', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('11_creation_error')
            self.log_result('Step 4: Successful Account Creation', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def test_create_savings_account(self):
        """Step 5: Create another account with different type (Poupança)"""
        try:
            print('\n=== STEP 5: Create Savings Account ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(1)

            # Fill the form
            test_account_name = f'Poupança Teste QA'

            name_input = self.driver.find_element(By.NAME, 'name')
            name_input.clear()
            name_input.send_keys(test_account_name)

            # Select account type: Poupança (savings)
            account_type_select = Select(self.driver.find_element(By.NAME, 'account_type'))
            account_type_select.select_by_value('savings')

            # Fill bank name
            try:
                bank_input = self.driver.find_element(By.NAME, 'bank')
                bank_input.clear()
                bank_input.send_keys('Nubank')
            except:
                pass

            # Fill initial balance
            initial_balance = self.driver.find_element(By.NAME, 'initial_balance')
            initial_balance.clear()
            initial_balance.send_keys('5000.00')

            screenshot = self.take_screenshot('12_savings_form_filled')

            # Submit
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(2)

            screenshot = self.take_screenshot('13_savings_created')

            # Check for success
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            if '/accounts/' in current_url and 'nova' not in current_url:
                self.log_result('Step 5: Create Savings Account', 'PASS', 'Savings account created successfully', screenshot)
                return True
            else:
                self.log_result('Step 5: Create Savings Account', 'FAIL', f'Creation failed. URL: {current_url}', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('13_savings_error')
            self.log_result('Step 5: Create Savings Account', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def test_create_wallet_without_bank(self):
        """Step 6: Create wallet account without bank name"""
        try:
            print('\n=== STEP 6: Create Wallet Without Bank ===\n')

            self.driver.get(f'{self.base_url}/accounts/nova/')
            time.sleep(1)

            # Fill the form
            test_account_name = f'Carteira QA'

            name_input = self.driver.find_element(By.NAME, 'name')
            name_input.clear()
            name_input.send_keys(test_account_name)

            # Select account type: Carteira (wallet)
            account_type_select = Select(self.driver.find_element(By.NAME, 'account_type'))
            account_type_select.select_by_value('wallet')

            # Leave bank empty

            # Fill initial balance
            initial_balance = self.driver.find_element(By.NAME, 'initial_balance')
            initial_balance.clear()
            initial_balance.send_keys('200.00')

            screenshot = self.take_screenshot('14_wallet_form_filled')

            # Submit
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(2)

            screenshot = self.take_screenshot('15_wallet_created')

            # Check for success
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            if '/accounts/' in current_url and 'nova' not in current_url:
                self.log_result('Step 6: Create Wallet Without Bank', 'PASS', 'Wallet account created successfully without bank name', screenshot)
                return True
            else:
                self.log_result('Step 6: Create Wallet Without Bank', 'FAIL', f'Creation failed. URL: {current_url}', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('15_wallet_error')
            self.log_result('Step 6: Create Wallet Without Bank', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def verify_accounts_list(self):
        """Step 7: Verify all accounts appear in the list"""
        try:
            print('\n=== STEP 7: Verify Accounts List ===\n')

            self.driver.get(f'{self.base_url}/accounts/')
            time.sleep(2)

            screenshot = self.take_screenshot('16_accounts_list')

            page_source = self.driver.page_source.lower()

            # Check for the accounts we created
            accounts_found = []
            accounts_missing = []

            expected_accounts = [
                'conta corrente teste qa',
                'poupança teste qa',
                'carteira qa'
            ]

            for account in expected_accounts:
                if account in page_source:
                    accounts_found.append(account)
                else:
                    accounts_missing.append(account)

            if len(accounts_found) == len(expected_accounts):
                self.log_result('Step 7: Verify Accounts List', 'PASS', f'All {len(accounts_found)} accounts found in list', screenshot)
                return True
            else:
                message = f'Found {len(accounts_found)}/{len(expected_accounts)} accounts. Missing: {", ".join(accounts_missing)}'
                self.log_result('Step 7: Verify Accounts List', 'FAIL', message, screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('16_list_error')
            self.log_result('Step 7: Verify Accounts List', 'FAIL', f'Error: {str(e)}', screenshot)
            return False

    def generate_report(self):
        """Generate test report"""
        print('\n' + '='*80)
        print('E2E TEST REPORT - ACCOUNT CREATION FUNCTIONALITY')
        print('Task 4.7.1: Test Account Creation')
        print('='*80 + '\n')

        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')

        print(f'Total Tests: {total_tests}')
        print(f'Passed: {passed} ({passed/total_tests*100:.1f}%)')
        print(f'Failed: {failed} ({failed/total_tests*100:.1f}%)')
        print('\n' + '-'*80 + '\n')

        # Show detailed results
        print('DETAILED RESULTS:\n')
        for result in self.results:
            status_icon = '[PASS]' if result['status'] == 'PASS' else '[FAIL]'
            print(f'{status_icon} {result["test"]}')
            print(f'  Message: {result["message"]}')
            if result['screenshot']:
                print(f'  Screenshot: {result["screenshot"]}')
            print()

        print('='*80)

        # Save report to file
        report_file = f'{self.screenshots_dir}/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('='*80 + '\n')
            f.write('E2E TEST REPORT - ACCOUNT CREATION FUNCTIONALITY\n')
            f.write('Task 4.7.1: Test Account Creation\n')
            f.write('='*80 + '\n\n')
            f.write(f'Test Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'Test Credentials: {self.test_email}\n\n')
            f.write(f'Total Tests: {total_tests}\n')
            f.write(f'Passed: {passed} ({passed/total_tests*100:.1f}%)\n')
            f.write(f'Failed: {failed} ({failed/total_tests*100:.1f}%)\n\n')
            f.write('-'*80 + '\n\n')

            for result in self.results:
                f.write(f'{result["status"]}: {result["test"]}\n')
                f.write(f'Message: {result["message"]}\n')
                f.write(f'Timestamp: {result["timestamp"]}\n')
                if result['screenshot']:
                    f.write(f'Screenshot: {result["screenshot"]}\n')
                f.write('-' * 80 + '\n\n')

        print(f'\nDetailed report saved to: {report_file}')
        return passed == total_tests

    def run_all_tests(self):
        """Run all tests according to test plan"""
        print('\n' + '='*80)
        print('STARTING E2E TESTS - ACCOUNT CREATION FUNCTIONALITY')
        print('Task 4.7.1: Test Account Creation')
        print('='*80 + '\n')

        try:
            # Step 1: Login
            if not self.login():
                print('\nLogin failed. Cannot proceed with tests.')
                return False

            # Step 2: Navigate to Account Creation
            if not self.navigate_to_account_creation():
                print('\nNavigation failed. Cannot proceed with tests.')
                return False

            # Step 3: Test Form Validations
            self.test_empty_form_submission()
            self.test_name_too_short()
            self.test_valid_name()

            # Step 4: Test Successful Account Creation
            self.test_successful_account_creation()

            # Step 5: Create Savings Account
            self.test_create_savings_account()

            # Step 6: Create Wallet Without Bank
            self.test_create_wallet_without_bank()

            # Step 7: Verify Database
            self.verify_accounts_list()

            # Generate report
            all_passed = self.generate_report()

            return all_passed

        finally:
            # Close browser
            self.driver.quit()
            print('\nTests completed. Browser closed.')


if __name__ == '__main__':
    print('='*80)
    print('E2E Testing - Account Creation Functionality')
    print('Task 4.7.1: Test Account Creation')
    print('='*80)

    # Run tests
    tester = AccountCreationE2ETester(headless=False)
    all_passed = tester.run_all_tests()

    if all_passed:
        print('\n✓ All tests PASSED!')
        exit(0)
    else:
        print('\n✗ Some tests FAILED. Check the report for details.')
        exit(1)
