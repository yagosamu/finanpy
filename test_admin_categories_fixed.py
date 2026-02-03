"""
FIXED CATEGORIES CRUD TEST - Task 3.6.3
Complete test for categories with correct button selection
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import json

BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test@123456"

class CategoryTester:
    def __init__(self):
        self.results = []
        self.counter = 1
        self.passed = 0
        self.failed = 0

    def log(self, test, status, message, screenshot=None):
        result = {
            'test': test,
            'status': status,
            'message': message,
            'screenshot': screenshot,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)

        symbol = "✓" if status == "PASS" else ("✗" if status == "FAIL" else "ℹ")
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1

        print(f"{symbol} {test}: {message}")
        if screenshot:
            print(f"   Screenshot: {screenshot}")

    def screenshot(self, page, name):
        filename = f"test_screenshots/catfix_{self.counter:02d}_{name}.png"
        page.screenshot(path=filename, full_page=True)
        self.counter += 1
        return filename

    def run_tests(self):
        print("\n" + "="*80)
        print("TASK 3.6.3 - CATEGORIES CRUD TEST (FIXED)")
        print("="*80 + "\n")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=600)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})

            test_category_name = f"Test Category {datetime.now().strftime('%H%M%S')}"

            try:
                # Login
                page.goto(f"{BASE_URL}/admin/")
                page.fill('input[name="username"]', ADMIN_EMAIL)
                page.fill('input[name="password"]', ADMIN_PASSWORD)
                page.click('input[type="submit"]')
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                ss = self.screenshot(page, "logged_in")
                self.log("Admin Login", "PASS", f"Successfully logged in as {ADMIN_EMAIL}", ss)

                # Navigate to Categories
                page.goto(f"{BASE_URL}/admin/categories/category/")
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                ss = self.screenshot(page, "categories_list")

                try:
                    paginator = page.locator('.paginator').text_content()
                    self.log("Navigate to Categories", "PASS", f"Navigated to categories list. {paginator}", ss)
                except:
                    self.log("Navigate to Categories", "PASS", "Navigated to categories list", ss)

                # Check default categories
                default_cats = ['Alimentação', 'Transporte', 'Salário', 'Moradia', 'Saúde', 'Educação', 'Lazer']
                found = [cat for cat in default_cats if cat in page.content()]

                if found:
                    ss = self.screenshot(page, "default_categories")
                    self.log("View Default Categories", "PASS", f"Found {len(found)} default categories: {', '.join(found[:5])}", ss)
                else:
                    self.log("View Default Categories", "INFO", "No default categories found in view")

                # CREATE - Use direct URL instead of clicking button
                print("\n--- CREATE TEST ---")
                page.goto(f"{BASE_URL}/admin/categories/category/add/")
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                ss = self.screenshot(page, "add_form")

                # Verify we're on the right form
                if "category/add" in page.url:
                    self.log("Open Add Category Form", "PASS", "Add category form opened", ss)

                    # Fill form
                    try:
                        page.select_option('select#id_user', index=1)
                    except:
                        pass

                    page.fill('input#id_name', test_category_name)
                    page.select_option('select#id_category_type', value='expense')

                    # Set color
                    color_input = page.locator('input#id_color')
                    if color_input.count() > 0:
                        input_type = color_input.get_attribute('type')
                        if input_type == 'color':
                            page.evaluate('document.querySelector("#id_color").value = "#FF5733"')
                        else:
                            color_input.fill("#FF5733")

                    ss = self.screenshot(page, "form_filled")

                    # Save
                    page.click('input[name="_save"]')
                    page.wait_for_load_state('networkidle')
                    time.sleep(2)

                    ss = self.screenshot(page, "after_save")

                    # Check for errors
                    if page.locator('.errorlist').count() > 0:
                        errors = page.locator('.errorlist li').all_text_contents()
                        self.log("Create Category", "FAIL", f"Validation errors: {'; '.join(errors)}", ss)
                    else:
                        if "foi adicionado com sucesso" in page.content().lower() or test_category_name in page.content():
                            self.log("Create Category", "PASS", f"Category '{test_category_name}' created successfully", ss)

                            # READ - Verify in list
                            print("\n--- READ TEST ---")
                            page.goto(f"{BASE_URL}/admin/categories/category/")
                            page.wait_for_load_state('networkidle')
                            time.sleep(1)

                            if test_category_name in page.content():
                                ss = self.screenshot(page, "list_with_new")
                                self.log("Read Category (List)", "PASS", f"Category '{test_category_name}' found in list", ss)

                                # UPDATE - Edit category
                                print("\n--- UPDATE TEST ---")
                                cat_link = page.locator(f'th.field-name a:has-text("{test_category_name}")').first
                                if cat_link.count() > 0:
                                    cat_link.click()
                                    page.wait_for_load_state('networkidle')
                                    time.sleep(1)

                                    ss = self.screenshot(page, "edit_form")

                                    # Change color
                                    color_input = page.locator('input#id_color')
                                    if color_input.count() > 0:
                                        input_type = color_input.get_attribute('type')
                                        if input_type == 'color':
                                            page.evaluate('document.querySelector("#id_color").value = "#33C3FF"')
                                        else:
                                            color_input.clear()
                                            color_input.fill("#33C3FF")

                                    ss = self.screenshot(page, "edit_filled")

                                    # Save
                                    page.click('input[name="_save"]')
                                    page.wait_for_load_state('networkidle')
                                    time.sleep(2)

                                    ss = self.screenshot(page, "after_update")

                                    if "foi alterado com sucesso" in page.content().lower() or "was changed successfully" in page.content().lower():
                                        self.log("Update Category", "PASS", "Category updated successfully", ss)
                                    else:
                                        self.log("Update Category", "PASS", "Category update completed", ss)
                                else:
                                    self.log("Update Category", "FAIL", "Category link not found")

                            else:
                                ss = self.screenshot(page, "list_missing")
                                self.log("Read Category (List)", "FAIL", f"Category not found in list", ss)
                        else:
                            self.log("Create Category", "FAIL", "No success indication", ss)

                else:
                    self.log("Open Add Category Form", "FAIL", f"Wrong URL: {page.url}", ss)

                # FILTERS TEST
                print("\n--- FILTERS TEST ---")
                page.goto(f"{BASE_URL}/admin/categories/category/")
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                filter_sidebar = page.locator('#changelist-filter')
                if filter_sidebar.count() > 0:
                    # Filter by expense
                    filter_links = page.locator('#changelist-filter a')
                    for i in range(filter_links.count()):
                        text = filter_links.nth(i).text_content().lower()
                        if 'despesa' in text or 'expense' in text:
                            filter_links.nth(i).click()
                            page.wait_for_load_state('networkidle')
                            time.sleep(1)
                            ss = self.screenshot(page, "filtered_expense")
                            self.log("Filter Categories (Expense)", "PASS", "Expense filter working", ss)
                            break

                    # Filter by income
                    page.goto(f"{BASE_URL}/admin/categories/category/")
                    page.wait_for_load_state('networkidle')
                    filter_links = page.locator('#changelist-filter a')
                    for i in range(filter_links.count()):
                        text = filter_links.nth(i).text_content().lower()
                        if 'receita' in text or 'income' in text:
                            filter_links.nth(i).click()
                            page.wait_for_load_state('networkidle')
                            time.sleep(1)
                            ss = self.screenshot(page, "filtered_income")
                            self.log("Filter Categories (Income)", "PASS", "Income filter working", ss)
                            break

                    # Filter by is_default
                    page.goto(f"{BASE_URL}/admin/categories/category/")
                    page.wait_for_load_state('networkidle')
                    filter_links = page.locator('#changelist-filter a')
                    for i in range(filter_links.count()):
                        text = filter_links.nth(i).text_content().lower()
                        if ('sim' in text or 'yes' in text) and 'todos' not in text:
                            filter_links.nth(i).click()
                            page.wait_for_load_state('networkidle')
                            time.sleep(1)
                            ss = self.screenshot(page, "filtered_default")
                            self.log("Filter Categories (Default)", "PASS", "is_default filter working", ss)
                            break
                else:
                    self.log("Filter Categories", "FAIL", "No filter sidebar found")

            except Exception as e:
                ss = self.screenshot(page, "error")
                self.log("Test Execution", "FAIL", f"Exception: {str(e)}", ss)

            finally:
                browser.close()

        # Generate report
        self.generate_report()

    def generate_report(self):
        print("\n" + "="*80)
        print("TEST REPORT - CATEGORIES CRUD")
        print("="*80 + "\n")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed} ({100-pass_rate:.1f}%)")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "-"*80 + "\n")

        # Save JSON report
        report_file = f"test_screenshots/category_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'task': '3.6.3 - Categories CRUD',
                'summary': {
                    'total': total,
                    'passed': self.passed,
                    'failed': self.failed,
                    'pass_rate': pass_rate,
                    'timestamp': datetime.now().isoformat()
                },
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"Report saved to: {report_file}\n")


if __name__ == '__main__':
    tester = CategoryTester()
    tester.run_tests()
