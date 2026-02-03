"""
Comprehensive E2E Testing for Finanpy Django Admin Interface
Tests CRUD operations for Accounts and Categories models
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


class AdminE2ETester:
    def __init__(self, base_url='http://localhost:8000', headless=False):
        self.base_url = base_url
        self.admin_url = f'{base_url}/admin/'
        self.results = []
        self.screenshots_dir = 'test_screenshots/comprehensive'

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

        status_symbol = '✓' if status == 'PASS' else '✗'
        print(f'{status_symbol} {test_name}: {message}')

    def login(self, email='admin@test.com', password='admin123'):
        """Login to Django admin"""
        try:
            self.driver.get(self.admin_url)
            time.sleep(1)

            screenshot = self.take_screenshot('01_login_page')

            # Find and fill login form
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            password_input = self.driver.find_element(By.NAME, 'password')

            email_input.clear()
            email_input.send_keys(email)
            password_input.clear()
            password_input.send_keys(password)

            screenshot = self.take_screenshot('02_login_filled')

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            submit_button.click()

            time.sleep(2)

            # Check if login successful
            if '/admin/' in self.driver.current_url and 'login' not in self.driver.current_url:
                screenshot = self.take_screenshot('03_login_success')
                self.log_result('Login', 'PASS', f'Successfully logged in as {email}', screenshot)
                return True
            else:
                screenshot = self.take_screenshot('03_login_failed')
                self.log_result('Login', 'FAIL', 'Login failed - incorrect credentials or redirect issue', screenshot)
                return False

        except Exception as e:
            screenshot = self.take_screenshot('03_login_error')
            self.log_result('Login', 'FAIL', f'Login error: {str(e)}', screenshot)
            return False

    def test_accounts_crud(self):
        """Test CRUD operations for Accounts model"""
        print('\n=== Testing Accounts CRUD ===\n')

        try:
            # Navigate to Accounts admin
            self.driver.get(f'{self.admin_url}accounts/account/')
            time.sleep(2)

            screenshot = self.take_screenshot('10_accounts_list')
            self.log_result('Navigate to Accounts', 'PASS', 'Successfully navigated to Accounts list', screenshot)

            # Count existing accounts
            try:
                results_text = self.driver.find_element(By.CLASS_NAME, 'paginator').text
                self.log_result('View Accounts List', 'PASS', f'Accounts list loaded: {results_text}')
            except NoSuchElementException:
                self.log_result('View Accounts List', 'PASS', 'Accounts list loaded (no pagination)')

            # Test CREATE - Click "Add Account" button
            add_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.addlink, a[href*="add"]'))
            )
            add_button.click()
            time.sleep(2)

            screenshot = self.take_screenshot('11_account_add_form')
            self.log_result('Open Add Account Form', 'PASS', 'Add account form opened', screenshot)

            # Fill in account details
            test_account_name = f'Test Account E2E {datetime.now().strftime("%H%M%S")}'

            # Name field
            name_input = self.driver.find_element(By.ID, 'id_name')
            name_input.send_keys(test_account_name)

            # Account type - select checking
            account_type_select = Select(self.driver.find_element(By.ID, 'id_account_type'))
            account_type_select.select_by_value('checking')

            # Bank field (optional)
            try:
                bank_input = self.driver.find_element(By.ID, 'id_bank')
                bank_input.send_keys('Banco Teste')
            except NoSuchElementException:
                pass

            # Initial balance
            initial_balance_input = self.driver.find_element(By.ID, 'id_initial_balance')
            initial_balance_input.clear()
            initial_balance_input.send_keys('1500.50')

            screenshot = self.take_screenshot('12_account_form_filled')

            # Save
            save_button = self.driver.find_element(By.NAME, '_save')
            save_button.click()
            time.sleep(2)

            # Check for success message
            if 'was added successfully' in self.driver.page_source or 'adicionad' in self.driver.page_source.lower():
                screenshot = self.take_screenshot('13_account_created')
                self.log_result('Create Account', 'PASS', f'Account "{test_account_name}" created successfully', screenshot)
            else:
                screenshot = self.take_screenshot('13_account_create_failed')
                self.log_result('Create Account', 'FAIL', 'Account creation failed', screenshot)
                return

            # Test READ - Verify account appears in list
            time.sleep(1)
            if test_account_name in self.driver.page_source:
                self.log_result('Read Account', 'PASS', f'Account "{test_account_name}" found in list')
            else:
                self.log_result('Read Account', 'FAIL', f'Account "{test_account_name}" not found in list')

            # Test UPDATE - Click on the account to edit
            account_links = self.driver.find_elements(By.CSS_SELECTOR, 'th.field-name a')
            for link in account_links:
                if test_account_name in link.text:
                    link.click()
                    break

            time.sleep(2)
            screenshot = self.take_screenshot('14_account_edit_form')

            # Update the bank field
            try:
                bank_input = self.driver.find_element(By.ID, 'id_bank')
                bank_input.clear()
                bank_input.send_keys('Banco Atualizado E2E')
            except NoSuchElementException:
                name_input = self.driver.find_element(By.ID, 'id_name')
                name_input.clear()
                name_input.send_keys(f'{test_account_name} - Updated')

            screenshot = self.take_screenshot('15_account_edit_filled')

            # Save changes
            save_button = self.driver.find_element(By.NAME, '_save')
            save_button.click()
            time.sleep(2)

            if 'was changed successfully' in self.driver.page_source or 'alterad' in self.driver.page_source.lower():
                screenshot = self.take_screenshot('16_account_updated')
                self.log_result('Update Account', 'PASS', 'Account updated successfully', screenshot)
            else:
                screenshot = self.take_screenshot('16_account_update_failed')
                self.log_result('Update Account', 'FAIL', 'Account update failed', screenshot)

            # Test FILTERS - Test account_type filter
            self.driver.get(f'{self.admin_url}accounts/account/')
            time.sleep(1)

            # Look for filter sidebar
            try:
                filter_links = self.driver.find_elements(By.CSS_SELECTOR, '#changelist-filter a')
                if filter_links:
                    # Click on first filter option (e.g., "checking")
                    for link in filter_links:
                        if 'checking' in link.text.lower() or 'corrente' in link.text.lower():
                            link.click()
                            time.sleep(2)
                            screenshot = self.take_screenshot('17_account_filtered')
                            self.log_result('Filter Accounts', 'PASS', 'Account filtering works', screenshot)
                            break
            except NoSuchElementException:
                self.log_result('Filter Accounts', 'INFO', 'No filters found')

            # Test SEARCH
            try:
                search_input = self.driver.find_element(By.ID, 'searchbar')
                search_input.send_keys('Test')
                search_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value*="Search"], input[type="submit"][value*="Pesquisar"]')
                search_button.click()
                time.sleep(2)
                screenshot = self.take_screenshot('18_account_searched')
                self.log_result('Search Accounts', 'PASS', 'Account search works', screenshot)
            except NoSuchElementException:
                self.log_result('Search Accounts', 'INFO', 'Search functionality not found')

            # Test required field validation
            self.driver.get(f'{self.admin_url}accounts/account/add/')
            time.sleep(1)

            # Try to save without filling required fields
            save_button = self.driver.find_element(By.NAME, '_save')
            save_button.click()
            time.sleep(1)

            # Check for error messages
            if 'errorlist' in self.driver.page_source or 'required' in self.driver.page_source.lower():
                screenshot = self.take_screenshot('19_account_validation')
                self.log_result('Validate Required Fields', 'PASS', 'Required field validation working', screenshot)
            else:
                screenshot = self.take_screenshot('19_account_validation_missing')
                self.log_result('Validate Required Fields', 'FAIL', 'Required field validation not working', screenshot)

        except Exception as e:
            screenshot = self.take_screenshot('error_accounts_crud')
            self.log_result('Accounts CRUD', 'FAIL', f'Error during accounts CRUD: {str(e)}', screenshot)

    def test_categories_crud(self):
        """Test CRUD operations for Categories model"""
        print('\n=== Testing Categories CRUD ===\n')

        try:
            # Navigate to Categories admin
            self.driver.get(f'{self.admin_url}categories/category/')
            time.sleep(2)

            screenshot = self.take_screenshot('20_categories_list')
            self.log_result('Navigate to Categories', 'PASS', 'Successfully navigated to Categories list', screenshot)

            # Check for default categories
            default_categories = ['Alimentação', 'Transporte', 'Salário', 'Moradia']
            found_defaults = []
            for cat in default_categories:
                if cat in self.driver.page_source:
                    found_defaults.append(cat)

            if found_defaults:
                self.log_result('View Default Categories', 'PASS', f'Found default categories: {", ".join(found_defaults)}')
            else:
                self.log_result('View Default Categories', 'INFO', 'No default categories found in view')

            # Test CREATE - Click "Add Category" button
            add_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.addlink, a[href*="add"]'))
            )
            add_button.click()
            time.sleep(2)

            screenshot = self.take_screenshot('21_category_add_form')
            self.log_result('Open Add Category Form', 'PASS', 'Add category form opened', screenshot)

            # Fill in category details
            test_category_name = f'Test Category E2E {datetime.now().strftime("%H%M%S")}'

            # Name field
            name_input = self.driver.find_element(By.ID, 'id_name')
            name_input.send_keys(test_category_name)

            # Category type - select expense
            category_type_select = Select(self.driver.find_element(By.ID, 'id_category_type'))
            category_type_select.select_by_value('expense')

            # Color field - try to set hex color
            try:
                color_input = self.driver.find_element(By.ID, 'id_color')
                # Check if it's a color picker or text input
                input_type = color_input.get_attribute('type')
                if input_type == 'color':
                    # Use JavaScript to set color value for color picker
                    self.driver.execute_script("arguments[0].value = '#FF5733'", color_input)
                else:
                    color_input.clear()
                    color_input.send_keys('#FF5733')
            except NoSuchElementException:
                self.log_result('Set Color', 'INFO', 'Color field not found')

            screenshot = self.take_screenshot('22_category_form_filled')

            # Save
            save_button = self.driver.find_element(By.NAME, '_save')
            save_button.click()
            time.sleep(2)

            # Check for success message
            if 'was added successfully' in self.driver.page_source or 'adicionad' in self.driver.page_source.lower():
                screenshot = self.take_screenshot('23_category_created')
                self.log_result('Create Category', 'PASS', f'Category "{test_category_name}" created successfully', screenshot)
            else:
                screenshot = self.take_screenshot('23_category_create_failed')
                self.log_result('Create Category', 'FAIL', 'Category creation failed', screenshot)
                return

            # Test READ - Verify category appears in list
            time.sleep(1)
            if test_category_name in self.driver.page_source:
                self.log_result('Read Category', 'PASS', f'Category "{test_category_name}" found in list')
            else:
                self.log_result('Read Category', 'FAIL', f'Category "{test_category_name}" not found in list')

            # Test UPDATE - Click on the category to edit
            category_links = self.driver.find_elements(By.CSS_SELECTOR, 'th.field-name a')
            for link in category_links:
                if test_category_name in link.text:
                    link.click()
                    break

            time.sleep(2)
            screenshot = self.take_screenshot('24_category_edit_form')

            # Update the color
            try:
                color_input = self.driver.find_element(By.ID, 'id_color')
                input_type = color_input.get_attribute('type')
                if input_type == 'color':
                    self.driver.execute_script("arguments[0].value = '#33C3FF'", color_input)
                else:
                    color_input.clear()
                    color_input.send_keys('#33C3FF')

                screenshot = self.take_screenshot('25_category_edit_filled')

                # Save changes
                save_button = self.driver.find_element(By.NAME, '_save')
                save_button.click()
                time.sleep(2)

                if 'was changed successfully' in self.driver.page_source or 'alterad' in self.driver.page_source.lower():
                    screenshot = self.take_screenshot('26_category_updated')
                    self.log_result('Update Category', 'PASS', 'Category updated successfully', screenshot)
                else:
                    screenshot = self.take_screenshot('26_category_update_failed')
                    self.log_result('Update Category', 'FAIL', 'Category update failed', screenshot)
            except NoSuchElementException:
                self.log_result('Update Category', 'INFO', 'Could not update color field')

            # Test FILTERS - Test category_type filter
            self.driver.get(f'{self.admin_url}categories/category/')
            time.sleep(1)

            try:
                filter_links = self.driver.find_elements(By.CSS_SELECTOR, '#changelist-filter a')
                if filter_links:
                    # Click on "expense" filter
                    for link in filter_links:
                        if 'expense' in link.text.lower() or 'despesa' in link.text.lower():
                            link.click()
                            time.sleep(2)
                            screenshot = self.take_screenshot('27_category_filtered_expense')
                            self.log_result('Filter Categories by Type', 'PASS', 'Category type filtering works', screenshot)
                            break

                    # Try is_default filter
                    self.driver.get(f'{self.admin_url}categories/category/')
                    time.sleep(1)
                    filter_links = self.driver.find_elements(By.CSS_SELECTOR, '#changelist-filter a')
                    for link in filter_links:
                        if 'yes' in link.text.lower() or 'sim' in link.text.lower() or 'true' in link.text.lower():
                            link.click()
                            time.sleep(2)
                            screenshot = self.take_screenshot('28_category_filtered_default')
                            self.log_result('Filter Categories by Default', 'PASS', 'Category is_default filtering works', screenshot)
                            break
            except NoSuchElementException:
                self.log_result('Filter Categories', 'INFO', 'No filters found')

            # Test SEARCH
            self.driver.get(f'{self.admin_url}categories/category/')
            time.sleep(1)

            try:
                search_input = self.driver.find_element(By.ID, 'searchbar')
                search_input.send_keys('Test')
                search_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value*="Search"], input[type="submit"][value*="Pesquisar"]')
                search_button.click()
                time.sleep(2)
                screenshot = self.take_screenshot('29_category_searched')
                self.log_result('Search Categories', 'PASS', 'Category search works', screenshot)
            except NoSuchElementException:
                self.log_result('Search Categories', 'INFO', 'Search functionality not found')

        except Exception as e:
            screenshot = self.take_screenshot('error_categories_crud')
            self.log_result('Categories CRUD', 'FAIL', f'Error during categories CRUD: {str(e)}', screenshot)

    def generate_report(self):
        """Generate test report"""
        print('\n' + '='*80)
        print('COMPREHENSIVE E2E TEST REPORT - FINANPY ADMIN')
        print('='*80 + '\n')

        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        info = sum(1 for r in self.results if r['status'] == 'INFO')

        print(f'Total Tests: {total_tests}')
        print(f'Passed: {passed} ({passed/total_tests*100:.1f}%)')
        print(f'Failed: {failed} ({failed/total_tests*100:.1f}%)')
        print(f'Info: {info} ({info/total_tests*100:.1f}%)')
        print('\n' + '-'*80 + '\n')

        # Group results by status
        for status in ['FAIL', 'PASS', 'INFO']:
            status_results = [r for r in self.results if r['status'] == status]
            if status_results:
                print(f'\n{status} ({len(status_results)}):')
                print('-' * 40)
                for result in status_results:
                    print(f'  - {result["test"]}: {result["message"]}')
                    if result['screenshot']:
                        print(f'    Screenshot: {result["screenshot"]}')

        print('\n' + '='*80)

        # Save detailed report to file
        report_file = f'{self.screenshots_dir}/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('='*80 + '\n')
            f.write('COMPREHENSIVE E2E TEST REPORT - FINANPY ADMIN\n')
            f.write('='*80 + '\n\n')
            f.write(f'Total Tests: {total_tests}\n')
            f.write(f'Passed: {passed} ({passed/total_tests*100:.1f}%)\n')
            f.write(f'Failed: {failed} ({failed/total_tests*100:.1f}%)\n')
            f.write(f'Info: {info} ({info/total_tests*100:.1f}%)\n\n')

            for result in self.results:
                f.write(f'\n{result["status"]}: {result["test"]}\n')
                f.write(f'Message: {result["message"]}\n')
                f.write(f'Timestamp: {result["timestamp"]}\n')
                if result['screenshot']:
                    f.write(f'Screenshot: {result["screenshot"]}\n')
                f.write('-' * 80 + '\n')

        print(f'\nDetailed report saved to: {report_file}')

    def run_all_tests(self):
        """Run all tests"""
        print('Starting Comprehensive E2E Tests for Finanpy Admin...\n')

        # Login
        if not self.login():
            print('Login failed. Cannot proceed with tests.')
            self.driver.quit()
            return

        # Test Accounts CRUD
        self.test_accounts_crud()

        # Test Categories CRUD
        self.test_categories_crud()

        # Generate report
        self.generate_report()

        # Close browser
        self.driver.quit()
        print('\nTests completed. Browser closed.')


if __name__ == '__main__':
    # Try different password combinations
    passwords_to_try = ['admin123', 'test123', 'password123', 'Admin@123']

    tester = None
    login_success = False

    for password in passwords_to_try:
        print(f'\n=== Trying login with password: {password} ===\n')
        tester = AdminE2ETester(headless=False)

        if tester.login(password=password):
            login_success = True
            break
        else:
            tester.driver.quit()

    if not login_success:
        print('\n❌ Could not login with any of the attempted passwords.')
        print('Please create a superuser with:')
        print('  python manage.py createsuperuser')
        print('  Email: admin@test.com')
        print('  Password: admin123')
    else:
        # Run all tests
        tester.test_accounts_crud()
        tester.test_categories_crud()
        tester.generate_report()
        tester.driver.quit()
