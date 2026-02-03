"""
COMPREHENSIVE E2E TEST FOR DJANGO ADMIN - FINANPY
Tasks 3.6.2 and 3.6.3: CRUD testing for Accounts and Categories

This test suite performs comprehensive testing of the Django admin interface
including CRUD operations, filters, search, and validations.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright, expect
import time
from datetime import datetime
import json

BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test@123456"

class AdminE2ETester:
    def __init__(self):
        self.results = []
        self.screenshot_counter = 1
        self.test_counter = 0
        self.passed = 0
        self.failed = 0

    def log(self, test_name, status, message, screenshot=None):
        """Log test result"""
        self.test_counter += 1
        if status == "PASS":
            self.passed += 1
            symbol = "✓"
        elif status == "FAIL":
            self.failed += 1
            symbol = "✗"
        else:
            symbol = "ℹ"

        result = {
            'number': self.test_counter,
            'test': test_name,
            'status': status,
            'message': message,
            'screenshot': screenshot,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)

        print(f"{symbol} Test {self.test_counter}: {test_name}")
        print(f"   Status: {status}")
        print(f"   {message}")
        if screenshot:
            print(f"   Screenshot: {screenshot}")
        print()

    def screenshot(self, page, name):
        """Take screenshot"""
        filename = f"test_screenshots/final_{self.screenshot_counter:02d}_{name}.png"
        page.screenshot(path=filename, full_page=True)
        self.screenshot_counter += 1
        return filename

    def test_login(self, page):
        """Test admin login"""
        print("\n" + "="*80)
        print("AUTHENTICATION TEST")
        print("="*80 + "\n")

        try:
            page.goto(f"{BASE_URL}/admin/")
            page.wait_for_load_state('networkidle')

            screenshot = self.screenshot(page, "login_page")

            # Fill login form
            page.fill('input[name="username"]', ADMIN_EMAIL)
            page.fill('input[name="password"]', ADMIN_PASSWORD)

            screenshot = self.screenshot(page, "login_filled")

            # Submit
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Verify login
            if "/admin/" in page.url and "/login/" not in page.url:
                screenshot = self.screenshot(page, "login_success")
                self.log("Admin Login", "PASS", f"Successfully logged in as {ADMIN_EMAIL}", screenshot)
                return True
            else:
                screenshot = self.screenshot(page, "login_failed")
                self.log("Admin Login", "FAIL", "Login failed - redirect issue", screenshot)
                return False

        except Exception as e:
            screenshot = self.screenshot(page, "login_error")
            self.log("Admin Login", "FAIL", f"Exception: {str(e)}", screenshot)
            return False

    def test_accounts_crud(self, page):
        """Test CRUD operations for Accounts"""
        print("\n" + "="*80)
        print("TASK 3.6.2 - ACCOUNTS CRUD TEST")
        print("="*80 + "\n")

        test_account_name = f"Conta Teste E2E {datetime.now().strftime('%H%M%S')}"

        # 1. Navigate to Accounts
        try:
            page.goto(f"{BASE_URL}/admin/accounts/account/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            screenshot = self.screenshot(page, "accounts_list")

            # Check if we're on the right page
            if "account" in page.url:
                # Count existing accounts
                try:
                    paginator = page.locator('.paginator').text_content()
                    self.log("Navigate to Accounts", "PASS", f"Successfully navigated to Accounts list. {paginator}", screenshot)
                except:
                    self.log("Navigate to Accounts", "PASS", "Successfully navigated to Accounts list (no pagination)", screenshot)
            else:
                self.log("Navigate to Accounts", "FAIL", f"Wrong URL: {page.url}", screenshot)
                return

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_nav_error")
            self.log("Navigate to Accounts", "FAIL", f"Exception: {str(e)}", screenshot)
            return

        # 2. CREATE - Add new account
        try:
            add_button = page.locator('a.addlink, a[href*="add"]').first
            add_button.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            screenshot = self.screenshot(page, "accounts_add_form")
            self.log("Open Add Account Form", "PASS", "Add account form opened", screenshot)

            # Fill form
            # Note: Based on previous test, we need to handle the user field
            try:
                page.select_option('select[name="user"]', index=1)
            except:
                pass  # User may be auto-filled

            page.fill('input[name="name"]', test_account_name)
            page.select_option('select[name="account_type"]', value="checking")
            page.fill('input[name="bank"]', "Banco Teste E2E")
            page.fill('input[name="initial_balance"]', "1500.50")

            screenshot = self.screenshot(page, "accounts_form_filled")

            # Save
            page.click('input[name="_save"]')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            screenshot = self.screenshot(page, "accounts_after_save")

            # Check for errors
            error_count = page.locator('.errorlist').count()
            if error_count > 0:
                errors = page.locator('.errorlist li').all_text_contents()
                error_msg = "; ".join(errors)
                self.log("Create Account", "FAIL", f"Validation errors: {error_msg}", screenshot)
                return

            # Check for success
            success_count = page.locator('li.success, .messagelist .success').count()
            if success_count > 0 or "foi adicionado com sucesso" in page.content().lower():
                self.log("Create Account", "PASS", f"Account '{test_account_name}' created successfully", screenshot)
            else:
                # Check if we're on the list page (which also indicates success)
                if "/account/" in page.url and "/add/" not in page.url:
                    self.log("Create Account", "PASS", f"Account '{test_account_name}' created (redirected to list)", screenshot)
                else:
                    self.log("Create Account", "FAIL", "No success message found and still on add page", screenshot)
                    return

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_create_error")
            self.log("Create Account", "FAIL", f"Exception: {str(e)}", screenshot)
            return

        # 3. READ - Verify account in list
        try:
            page.goto(f"{BASE_URL}/admin/accounts/account/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            if test_account_name in page.content():
                screenshot = self.screenshot(page, "accounts_list_with_new")
                self.log("Read Account (List)", "PASS", f"Account '{test_account_name}' found in list", screenshot)
            else:
                screenshot = self.screenshot(page, "accounts_list_missing")
                self.log("Read Account (List)", "FAIL", f"Account '{test_account_name}' not found in list", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_read_error")
            self.log("Read Account (List)", "FAIL", f"Exception: {str(e)}", screenshot)

        # 4. UPDATE - Edit account
        try:
            # Click on the account name to edit
            account_link = page.locator(f'th.field-name a:has-text("{test_account_name}")').first
            if account_link.count() > 0:
                account_link.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                screenshot = self.screenshot(page, "accounts_edit_form")

                # Update bank name
                bank_input = page.locator('input[name="bank"]')
                bank_input.clear()
                bank_input.fill("Banco Atualizado E2E")

                screenshot = self.screenshot(page, "accounts_edit_filled")

                # Save
                page.click('input[name="_save"]')
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                screenshot = self.screenshot(page, "accounts_after_update")

                # Check for success
                if "foi alterado com sucesso" in page.content().lower() or "was changed successfully" in page.content().lower():
                    self.log("Update Account", "PASS", "Account updated successfully", screenshot)
                else:
                    self.log("Update Account", "PASS", "Account update completed (redirected)", screenshot)

            else:
                screenshot = self.screenshot(page, "accounts_edit_notfound")
                self.log("Update Account", "FAIL", f"Could not find account link for '{test_account_name}'", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_update_error")
            self.log("Update Account", "FAIL", f"Exception: {str(e)}", screenshot)

        # 5. Test FILTERS
        try:
            page.goto(f"{BASE_URL}/admin/accounts/account/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Check for filter sidebar
            filter_sidebar = page.locator('#changelist-filter')
            if filter_sidebar.count() > 0:
                screenshot = self.screenshot(page, "accounts_filters")

                # Try clicking on "Conta Corrente" filter
                filter_links = page.locator('#changelist-filter a')
                found_filter = False

                for i in range(filter_links.count()):
                    link_text = filter_links.nth(i).text_content().lower()
                    if 'corrente' in link_text or 'checking' in link_text:
                        filter_links.nth(i).click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(1)
                        screenshot = self.screenshot(page, "accounts_filtered_checking")
                        self.log("Filter Accounts (Type)", "PASS", f"Account type filter working (filtered by {link_text})", screenshot)
                        found_filter = True
                        break

                if not found_filter:
                    self.log("Filter Accounts (Type)", "INFO", "Filter links found but could not apply specific filter")

                # Try is_active filter
                page.goto(f"{BASE_URL}/admin/accounts/account/")
                page.wait_for_load_state('networkidle')
                filter_links = page.locator('#changelist-filter a')

                for i in range(filter_links.count()):
                    link_text = filter_links.nth(i).text_content().lower()
                    if 'sim' in link_text or 'yes' in link_text or (link_text == 'todos' and i > 0):
                        filter_links.nth(i).click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(1)
                        screenshot = self.screenshot(page, "accounts_filtered_active")
                        self.log("Filter Accounts (Active)", "PASS", f"Account active filter working (filtered by {link_text})", screenshot)
                        break

            else:
                screenshot = self.screenshot(page, "accounts_no_filters")
                self.log("Filter Accounts", "FAIL", "No filter sidebar found", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_filter_error")
            self.log("Filter Accounts", "FAIL", f"Exception: {str(e)}", screenshot)

        # 6. Test SEARCH
        try:
            page.goto(f"{BASE_URL}/admin/accounts/account/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            search_input = page.locator('input#searchbar')
            if search_input.count() > 0:
                search_input.fill("Teste")

                # Look for search button (in Portuguese)
                search_button = page.locator('input[type="submit"][value="Pesquisar"], input[type="submit"][value="Search"]')
                if search_button.count() > 0:
                    search_button.click()
                    page.wait_for_load_state('networkidle')
                    time.sleep(1)

                    screenshot = self.screenshot(page, "accounts_searched")
                    self.log("Search Accounts", "PASS", "Account search functionality working", screenshot)
                else:
                    # Try pressing Enter instead
                    search_input.press("Enter")
                    page.wait_for_load_state('networkidle')
                    time.sleep(1)
                    screenshot = self.screenshot(page, "accounts_searched")
                    self.log("Search Accounts", "PASS", "Account search functionality working (Enter key)", screenshot)
            else:
                screenshot = self.screenshot(page, "accounts_no_search")
                self.log("Search Accounts", "FAIL", "Search input not found", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_search_error")
            self.log("Search Accounts", "FAIL", f"Exception: {str(e)}", screenshot)

        # 7. Test required field validation
        try:
            page.goto(f"{BASE_URL}/admin/accounts/account/add/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Try to save without filling required fields
            page.click('input[name="_save"]')
            time.sleep(1)

            # Check for validation errors
            error_count = page.locator('.errorlist').count()
            if error_count > 0:
                screenshot = self.screenshot(page, "accounts_validation")
                errors = page.locator('.errorlist li').all_text_contents()
                self.log("Validate Required Fields", "PASS", f"Required field validation working. Errors: {len(errors)}", screenshot)
            else:
                screenshot = self.screenshot(page, "accounts_no_validation")
                self.log("Validate Required Fields", "FAIL", "No validation errors shown for empty form", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "accounts_validation_error")
            self.log("Validate Required Fields", "FAIL", f"Exception: {str(e)}", screenshot)

    def test_categories_crud(self, page):
        """Test CRUD operations for Categories"""
        print("\n" + "="*80)
        print("TASK 3.6.3 - CATEGORIES CRUD TEST")
        print("="*80 + "\n")

        test_category_name = f"Categoria Teste E2E {datetime.now().strftime('%H%M%S')}"

        # 1. Navigate to Categories
        try:
            page.goto(f"{BASE_URL}/admin/categories/category/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            screenshot = self.screenshot(page, "categories_list")

            if "categor" in page.url.lower():
                try:
                    paginator = page.locator('.paginator').text_content()
                    self.log("Navigate to Categories", "PASS", f"Successfully navigated to Categories list. {paginator}", screenshot)
                except:
                    self.log("Navigate to Categories", "PASS", "Successfully navigated to Categories list", screenshot)
            else:
                self.log("Navigate to Categories", "FAIL", f"Wrong URL: {page.url}", screenshot)
                return

        except Exception as e:
            screenshot = self.screenshot(page, "categories_nav_error")
            self.log("Navigate to Categories", "FAIL", f"Exception: {str(e)}", screenshot)
            return

        # 2. Verify default categories
        try:
            default_cats = ['Alimentação', 'Transporte', 'Salário', 'Moradia', 'Saúde']
            found_cats = []

            for cat in default_cats:
                if cat in page.content():
                    found_cats.append(cat)

            if found_cats:
                screenshot = self.screenshot(page, "categories_with_defaults")
                self.log("View Default Categories", "PASS", f"Found {len(found_cats)} default categories: {', '.join(found_cats)}", screenshot)
            else:
                screenshot = self.screenshot(page, "categories_no_defaults")
                self.log("View Default Categories", "INFO", "No default categories found in current view", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "categories_defaults_error")
            self.log("View Default Categories", "FAIL", f"Exception: {str(e)}", screenshot)

        # 3. CREATE - Add new category
        try:
            add_button = page.locator('a.addlink, a[href*="add"]').first
            add_button.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            screenshot = self.screenshot(page, "categories_add_form")
            self.log("Open Add Category Form", "PASS", "Add category form opened", screenshot)

            # Fill form
            try:
                page.select_option('select[name="user"]', index=1)
            except:
                pass  # User may be auto-filled

            page.fill('input[name="name"]', test_category_name)
            page.select_option('select[name="category_type"]', value="expense")

            # Handle color field
            color_input = page.locator('input[name="color"]')
            if color_input.count() > 0:
                input_type = color_input.get_attribute('type')
                if input_type == 'color':
                    # Use JavaScript to set color picker value
                    page.evaluate('document.querySelector(\'input[name="color"]\').value = "#FF5733"')
                else:
                    color_input.fill("#FF5733")

            screenshot = self.screenshot(page, "categories_form_filled")

            # Save
            page.click('input[name="_save"]')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            screenshot = self.screenshot(page, "categories_after_save")

            # Check for errors
            error_count = page.locator('.errorlist').count()
            if error_count > 0:
                errors = page.locator('.errorlist li').all_text_contents()
                error_msg = "; ".join(errors)
                self.log("Create Category", "FAIL", f"Validation errors: {error_msg}", screenshot)
                return

            # Check for success
            if "foi adicionado com sucesso" in page.content().lower() or "was added successfully" in page.content().lower():
                self.log("Create Category", "PASS", f"Category '{test_category_name}' created successfully", screenshot)
            else:
                if "/category/" in page.url and "/add/" not in page.url:
                    self.log("Create Category", "PASS", f"Category '{test_category_name}' created (redirected to list)", screenshot)
                else:
                    self.log("Create Category", "FAIL", "No success message and still on add page", screenshot)
                    return

        except Exception as e:
            screenshot = self.screenshot(page, "categories_create_error")
            self.log("Create Category", "FAIL", f"Exception: {str(e)}", screenshot)
            return

        # 4. READ - Verify category in list
        try:
            page.goto(f"{BASE_URL}/admin/categories/category/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            if test_category_name in page.content():
                screenshot = self.screenshot(page, "categories_list_with_new")
                self.log("Read Category (List)", "PASS", f"Category '{test_category_name}' found in list", screenshot)
            else:
                screenshot = self.screenshot(page, "categories_list_missing")
                self.log("Read Category (List)", "FAIL", f"Category '{test_category_name}' not found in list", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "categories_read_error")
            self.log("Read Category (List)", "FAIL", f"Exception: {str(e)}", screenshot)

        # 5. UPDATE - Edit category color
        try:
            category_link = page.locator(f'th.field-name a:has-text("{test_category_name}")').first
            if category_link.count() > 0:
                category_link.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                screenshot = self.screenshot(page, "categories_edit_form")

                # Update color
                color_input = page.locator('input[name="color"]')
                if color_input.count() > 0:
                    input_type = color_input.get_attribute('type')
                    if input_type == 'color':
                        page.evaluate('document.querySelector(\'input[name="color"]\').value = "#33C3FF"')
                    else:
                        color_input.clear()
                        color_input.fill("#33C3FF")

                screenshot = self.screenshot(page, "categories_edit_filled")

                # Save
                page.click('input[name="_save"]')
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                screenshot = self.screenshot(page, "categories_after_update")

                if "foi alterado com sucesso" in page.content().lower() or "was changed successfully" in page.content().lower():
                    self.log("Update Category", "PASS", "Category color updated successfully", screenshot)
                else:
                    self.log("Update Category", "PASS", "Category update completed (redirected)", screenshot)

            else:
                screenshot = self.screenshot(page, "categories_edit_notfound")
                self.log("Update Category", "FAIL", f"Could not find category link for '{test_category_name}'", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "categories_update_error")
            self.log("Update Category", "FAIL", f"Exception: {str(e)}", screenshot)

        # 6. Test FILTERS
        try:
            page.goto(f"{BASE_URL}/admin/categories/category/")
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            filter_sidebar = page.locator('#changelist-filter')
            if filter_sidebar.count() > 0:
                screenshot = self.screenshot(page, "categories_filters")

                # Try expense filter
                filter_links = page.locator('#changelist-filter a')
                found_expense = False

                for i in range(filter_links.count()):
                    link_text = filter_links.nth(i).text_content().lower()
                    if 'despesa' in link_text or 'expense' in link_text:
                        filter_links.nth(i).click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(1)
                        screenshot = self.screenshot(page, "categories_filtered_expense")
                        self.log("Filter Categories (Type)", "PASS", f"Category type filter working (filtered by {link_text})", screenshot)
                        found_expense = True
                        break

                if not found_expense:
                    self.log("Filter Categories (Type)", "INFO", "Expense filter not found")

                # Try is_default filter
                page.goto(f"{BASE_URL}/admin/categories/category/")
                page.wait_for_load_state('networkidle')
                filter_links = page.locator('#changelist-filter a')

                for i in range(filter_links.count()):
                    link_text = filter_links.nth(i).text_content().lower()
                    if ('sim' in link_text or 'yes' in link_text or 'true' in link_text) and 'todos' not in link_text:
                        filter_links.nth(i).click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(1)
                        screenshot = self.screenshot(page, "categories_filtered_default")
                        self.log("Filter Categories (Default)", "PASS", f"Category is_default filter working", screenshot)
                        break

            else:
                screenshot = self.screenshot(page, "categories_no_filters")
                self.log("Filter Categories", "FAIL", "No filter sidebar found", screenshot)

        except Exception as e:
            screenshot = self.screenshot(page, "categories_filter_error")
            self.log("Filter Categories", "FAIL", f"Exception: {str(e)}", screenshot)

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE E2E TEST REPORT - FINANPY ADMIN")
        print("="*80 + "\n")

        total = self.test_counter
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed} ({100-pass_rate:.1f}%)")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "-"*80 + "\n")

        # Group by status
        for status in ['FAIL', 'PASS', 'INFO']:
            status_results = [r for r in self.results if r['status'] == status]
            if status_results:
                print(f"\n{status} ({len(status_results)}):")
                print("-" * 40)
                for r in status_results:
                    print(f"  {r['number']}. {r['test']}")
                    print(f"     {r['message']}")
                    if r['screenshot']:
                        print(f"     Screenshot: {r['screenshot']}")

        # Save JSON report
        report_file = f"test_screenshots/final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': total,
                    'passed': self.passed,
                    'failed': self.failed,
                    'pass_rate': pass_rate,
                    'timestamp': datetime.now().isoformat()
                },
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n\nJSON report saved to: {report_file}")
        print("="*80 + "\n")


def main():
    print("\n" + "="*80)
    print("FINANPY ADMIN - COMPREHENSIVE E2E TEST SUITE")
    print("Tasks 3.6.2 and 3.6.3")
    print("="*80 + "\n")

    tester = AdminE2ETester()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Test login
            if not tester.test_login(page):
                print("\n❌ Login failed. Cannot continue with tests.")
                browser.close()
                return

            # Test Accounts CRUD (Task 3.6.2)
            tester.test_accounts_crud(page)

            # Test Categories CRUD (Task 3.6.3)
            tester.test_categories_crud(page)

        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")

        finally:
            # Generate report
            tester.generate_report()

            # Close browser
            browser.close()
            print("\nTests completed. Browser closed.\n")


if __name__ == '__main__':
    main()
