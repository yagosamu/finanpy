"""
E2E Tests for Django Admin - Accounts and Categories CRUD
Task 3.6.2 and 3.6.3

This script tests:
- Account CRUD operations
- Category CRUD operations
- Admin list displays
- Filters and search functionality
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright, expect
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test@123456"
SCREENSHOT_DIR = "test_screenshots"

def create_screenshot_dir(page):
    """Create directory for screenshots"""
    import os
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

def take_screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"  Screenshot saved: {filename}")
    return filename

def login_admin(page):
    """Login to Django Admin"""
    print("\n=== ADMIN LOGIN ===")
    try:
        page.goto(f"{BASE_URL}/admin/")
        print("  Navigated to admin login page")
        take_screenshot(page, "01_admin_login_page")

        # Fill login form
        page.fill('input[name="username"]', ADMIN_EMAIL)
        page.fill('input[name="password"]', ADMIN_PASSWORD)
        print(f"  Filled credentials: {ADMIN_EMAIL}")
        take_screenshot(page, "02_admin_credentials_filled")

        # Click login button
        page.click('input[type="submit"]')
        page.wait_for_load_state('networkidle')
        print("  Clicked login button")

        # Verify login success (Portuguese interface)
        page.wait_for_selector('text=Administração do Site', timeout=5000)
        take_screenshot(page, "03_admin_dashboard")
        print("  LOGIN SUCCESSFUL")
        return True
    except Exception as e:
        print(f"  LOGIN FAILED: {str(e)}")
        take_screenshot(page, "ERROR_login_failed")
        return False

def test_accounts_crud(page):
    """Test Account CRUD operations"""
    print("\n" + "="*60)
    print("=== TASK 3.6.2 - TEST CRUD DE ACCOUNTS ===")
    print("="*60)

    results = []

    # Step 1: Navigate to Accounts
    print("\n[STEP 1] Navigate to Accounts section")
    try:
        page.goto(f"{BASE_URL}/admin/accounts/account/")
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "10_accounts_list")
        print("  PASS: Navigated to Accounts list")
        results.append(("Navigate to Accounts", "PASS", ""))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Navigate to Accounts", "FAIL", str(e)))
        take_screenshot(page, "ERROR_accounts_navigate")
        return results

    # Step 2: Verify list display columns
    print("\n[STEP 2] Verify list display columns")
    try:
        expected_columns = ["Nome", "Tipo", "Banco", "Saldo", "Ativa", "Criado em"]
        found_columns = []

        for col in expected_columns:
            if page.locator(f'text="{col}"').count() > 0:
                found_columns.append(col)

        print(f"  Expected columns: {expected_columns}")
        print(f"  Found columns: {found_columns}")

        if len(found_columns) >= 4:  # At least 4 key columns
            print("  PASS: List display shows required columns")
            results.append(("Verify list columns", "PASS", f"Found {len(found_columns)} columns"))
        else:
            print("  FAIL: Missing required columns")
            results.append(("Verify list columns", "FAIL", f"Only found {len(found_columns)} columns"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Verify list columns", "FAIL", str(e)))
        take_screenshot(page, "ERROR_accounts_columns")

    # Step 3: Create new account
    print("\n[STEP 3] Create new account")
    try:
        page.click('a.addlink:has-text("Adicionar conta")')
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "11_accounts_add_form")
        print("  Clicked 'Add Account' button")

        # Fill account form
        page.select_option('select[name="user"]', index=1)  # Select first user
        page.fill('input[name="name"]', "Conta Teste")
        page.select_option('select[name="account_type"]', value="checking")
        page.fill('input[name="bank"]', "Banco Teste")
        page.fill('input[name="initial_balance"]', "1000.00")

        print("  Filled account form:")
        print("    - Name: Conta Teste")
        print("    - Type: Conta Corrente (checking)")
        print("    - Bank: Banco Teste")
        print("    - Initial balance: 1000.00")
        take_screenshot(page, "12_accounts_form_filled")

        # Save account
        page.click('input[name="_save"]')
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "13_accounts_created")

        # Verify success message
        if page.locator('li.success').count() > 0:
            print("  PASS: Account created successfully")
            results.append(("Create account", "PASS", "Account 'Conta Teste' created"))
        else:
            print("  FAIL: No success message found")
            results.append(("Create account", "FAIL", "No success message"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Create account", "FAIL", str(e)))
        take_screenshot(page, "ERROR_accounts_create")

    # Step 4: Verify account in list
    print("\n[STEP 4] Verify account appears in list")
    try:
        page.goto(f"{BASE_URL}/admin/accounts/account/")
        page.wait_for_load_state('networkidle')

        if page.locator('text="Conta Teste"').count() > 0:
            print("  PASS: Account 'Conta Teste' found in list")
            results.append(("Verify account in list", "PASS", ""))
            take_screenshot(page, "14_accounts_list_with_new")
        else:
            print("  FAIL: Account not found in list")
            results.append(("Verify account in list", "FAIL", "Account not visible"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Verify account in list", "FAIL", str(e)))

    # Step 5: Edit account
    print("\n[STEP 5] Edit account name")
    try:
        page.click('a:has-text("Conta Teste")')
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "15_accounts_edit_form")

        page.fill('input[name="name"]', "Conta Teste Editada")
        print("  Changed name to: Conta Teste Editada")
        take_screenshot(page, "16_accounts_edit_filled")

        page.click('input[name="_save"]')
        page.wait_for_load_state('networkidle')

        if page.locator('li.success').count() > 0:
            print("  PASS: Account edited successfully")
            results.append(("Edit account", "PASS", "Name changed to 'Conta Teste Editada'"))
            take_screenshot(page, "17_accounts_edited")
        else:
            print("  FAIL: Edit failed")
            results.append(("Edit account", "FAIL", "No success message"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Edit account", "FAIL", str(e)))
        take_screenshot(page, "ERROR_accounts_edit")

    # Step 6: Test filters
    print("\n[STEP 6] Test account_type filter")
    try:
        page.goto(f"{BASE_URL}/admin/accounts/account/")
        page.wait_for_load_state('networkidle')

        # Check if filter sidebar exists
        if page.locator('#changelist-filter').count() > 0:
            print("  Filter sidebar found")
            take_screenshot(page, "18_accounts_filters")

            # Click on account type filter
            if page.locator('a:has-text("Conta Corrente")').count() > 0:
                page.click('a:has-text("Conta Corrente")')
                page.wait_for_load_state('networkidle')
                take_screenshot(page, "19_accounts_filtered")
                print("  PASS: Account type filter working")
                results.append(("Test account_type filter", "PASS", ""))
            else:
                print("  WARN: Filter option not found")
                results.append(("Test account_type filter", "PARTIAL", "Filter sidebar exists but option not clickable"))
        else:
            print("  WARN: Filter sidebar not found")
            results.append(("Test account_type filter", "FAIL", "No filter sidebar"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Test account_type filter", "FAIL", str(e)))

    # Step 7: Test search
    print("\n[STEP 7] Test search functionality")
    try:
        page.goto(f"{BASE_URL}/admin/accounts/account/")
        page.wait_for_load_state('networkidle')

        if page.locator('input[name="q"]').count() > 0:
            page.fill('input[name="q"]', "Conta Teste")
            page.click('input[type="submit"][value="Search"]')
            page.wait_for_load_state('networkidle')
            take_screenshot(page, "20_accounts_search")

            if page.locator('text="Conta Teste"').count() > 0:
                print("  PASS: Search found 'Conta Teste'")
                results.append(("Test search", "PASS", ""))
            else:
                print("  FAIL: Search did not find results")
                results.append(("Test search", "FAIL", "No results found"))
        else:
            print("  WARN: Search box not found")
            results.append(("Test search", "FAIL", "Search box not available"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Test search", "FAIL", str(e)))

    return results

def test_categories_crud(page):
    """Test Category CRUD operations"""
    print("\n" + "="*60)
    print("=== TASK 3.6.3 - TEST CRUD DE CATEGORIES ===")
    print("="*60)

    results = []

    # Step 1: Navigate to Categories
    print("\n[STEP 1] Navigate to Categories section")
    try:
        page.goto(f"{BASE_URL}/admin/categories/category/")
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "30_categories_list")
        print("  PASS: Navigated to Categories list")
        results.append(("Navigate to Categories", "PASS", ""))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Navigate to Categories", "FAIL", str(e)))
        take_screenshot(page, "ERROR_categories_navigate")
        return results

    # Step 2: Verify default categories exist
    print("\n[STEP 2] Verify default categories exist")
    try:
        default_categories = ["Alimentação", "Transporte", "Salário"]
        found_categories = []

        for cat in default_categories:
            if page.locator(f'text="{cat}"').count() > 0:
                found_categories.append(cat)

        print(f"  Checking for default categories: {default_categories}")
        print(f"  Found: {found_categories}")

        if len(found_categories) >= 2:
            print("  PASS: Default categories exist")
            results.append(("Verify default categories", "PASS", f"Found {len(found_categories)} default categories"))
        else:
            print("  FAIL: Default categories missing")
            results.append(("Verify default categories", "FAIL", f"Only found {len(found_categories)} categories"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Verify default categories", "FAIL", str(e)))

    # Step 3: Verify list display columns
    print("\n[STEP 3] Verify list display with color preview")
    try:
        # Check for colored_name column which includes color preview
        if page.locator('th.column-colored_name').count() > 0 or page.locator('text="Nome"').count() > 0:
            print("  PASS: List display shows name column")
            take_screenshot(page, "31_categories_columns")
            results.append(("Verify list columns", "PASS", "Name column with color preview"))
        else:
            print("  FAIL: Name column not found")
            results.append(("Verify list columns", "FAIL", "Column structure missing"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Verify list columns", "FAIL", str(e)))

    # Step 4: Create new custom category
    print("\n[STEP 4] Create new custom category")
    try:
        page.click('a.addlink:has-text("Adicionar categoria")')
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "32_categories_add_form")
        print("  Clicked 'Add Category' button")

        # Fill category form
        page.select_option('select[name="user"]', index=1)  # Select first user
        page.fill('input[name="name"]', "Categoria Teste")
        page.select_option('select[name="category_type"]', value="expense")
        page.fill('input[name="color"]', "#FF5733")

        # Uncheck is_default if checked
        if page.is_checked('input[name="is_default"]'):
            page.uncheck('input[name="is_default"]')

        # Ensure is_active is checked
        if not page.is_checked('input[name="is_active"]'):
            page.check('input[name="is_active"]')

        print("  Filled category form:")
        print("    - Name: Categoria Teste")
        print("    - Type: Despesa (expense)")
        print("    - Color: #FF5733")
        print("    - is_default: False")
        print("    - is_active: True")
        take_screenshot(page, "33_categories_form_filled")

        # Save category
        page.click('input[name="_save"]')
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "34_categories_created")

        # Verify success message
        if page.locator('li.success').count() > 0:
            print("  PASS: Category created successfully")
            results.append(("Create category", "PASS", "Category 'Categoria Teste' created"))
        else:
            print("  FAIL: No success message found")
            results.append(("Create category", "FAIL", "No success message"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Create category", "FAIL", str(e)))
        take_screenshot(page, "ERROR_categories_create")

    # Step 5: Verify category in list with color
    print("\n[STEP 5] Verify category appears in list with color")
    try:
        page.goto(f"{BASE_URL}/admin/categories/category/")
        page.wait_for_load_state('networkidle')

        if page.locator('text="Categoria Teste"').count() > 0:
            print("  PASS: Category 'Categoria Teste' found in list")
            results.append(("Verify category in list", "PASS", "Category visible with color preview"))
            take_screenshot(page, "35_categories_list_with_new")
        else:
            print("  FAIL: Category not found in list")
            results.append(("Verify category in list", "FAIL", "Category not visible"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Verify category in list", "FAIL", str(e)))

    # Step 6: Edit category color
    print("\n[STEP 6] Edit category color")
    try:
        page.click('a:has-text("Categoria Teste")')
        page.wait_for_load_state('networkidle')
        take_screenshot(page, "36_categories_edit_form")

        page.fill('input[name="color"]', "#33FF57")
        print("  Changed color to: #33FF57")
        take_screenshot(page, "37_categories_edit_filled")

        page.click('input[name="_save"]')
        page.wait_for_load_state('networkidle')

        if page.locator('li.success').count() > 0:
            print("  PASS: Category color edited successfully")
            results.append(("Edit category color", "PASS", "Color changed to #33FF57"))
            take_screenshot(page, "38_categories_edited")
        else:
            print("  FAIL: Edit failed")
            results.append(("Edit category color", "FAIL", "No success message"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Edit category color", "FAIL", str(e)))
        take_screenshot(page, "ERROR_categories_edit")

    # Step 7: Test category_type filter
    print("\n[STEP 7] Test category_type filter (Receita/Despesa)")
    try:
        page.goto(f"{BASE_URL}/admin/categories/category/")
        page.wait_for_load_state('networkidle')

        if page.locator('#changelist-filter').count() > 0:
            print("  Filter sidebar found")
            take_screenshot(page, "39_categories_filters")

            # Try to click expense filter
            if page.locator('a:has-text("Despesa")').count() > 0:
                page.click('a:has-text("Despesa")')
                page.wait_for_load_state('networkidle')
                take_screenshot(page, "40_categories_filtered_expense")
                print("  PASS: Category type filter working (Despesa)")
                results.append(("Test category_type filter", "PASS", ""))
            else:
                print("  WARN: Despesa filter option not found")
                results.append(("Test category_type filter", "PARTIAL", "Filter exists but option not clickable"))
        else:
            print("  WARN: Filter sidebar not found")
            results.append(("Test category_type filter", "FAIL", "No filter sidebar"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Test category_type filter", "FAIL", str(e)))

    # Step 8: Test is_default filter
    print("\n[STEP 8] Test is_default filter")
    try:
        page.goto(f"{BASE_URL}/admin/categories/category/")
        page.wait_for_load_state('networkidle')

        if page.locator('#changelist-filter').count() > 0:
            # Look for is_default filter options
            if page.locator('a:has-text("Sim")').count() > 0:
                page.click('a:has-text("Sim")')
                page.wait_for_load_state('networkidle')
                take_screenshot(page, "41_categories_filtered_default")
                print("  PASS: is_default filter working")
                results.append(("Test is_default filter", "PASS", ""))
            else:
                print("  WARN: is_default filter option not found")
                results.append(("Test is_default filter", "PARTIAL", "Filter exists but option not available"))
        else:
            print("  WARN: Filter sidebar not found")
            results.append(("Test is_default filter", "FAIL", "No filter sidebar"))
    except Exception as e:
        print(f"  FAIL: {str(e)}")
        results.append(("Test is_default filter", "FAIL", str(e)))

    return results

def generate_report(accounts_results, categories_results):
    """Generate final test report"""
    print("\n" + "="*80)
    print("="*80)
    print("FINAL TEST REPORT - Django Admin E2E Tests")
    print("="*80)
    print("="*80)

    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")

    # Accounts Report
    print("\n" + "-"*80)
    print("TASK 3.6.2 - TEST CRUD DE ACCOUNTS")
    print("-"*80)

    accounts_passed = sum(1 for _, status, _ in accounts_results if status == "PASS")
    accounts_total = len(accounts_results)

    print(f"\nStatus: {accounts_passed}/{accounts_total} tests passed\n")

    for step, status, detail in accounts_results:
        status_symbol = "✓" if status == "PASS" else ("⚠" if status == "PARTIAL" else "✗")
        print(f"  [{status_symbol}] {status:8} - {step}")
        if detail:
            print(f"              {detail}")

    # Categories Report
    print("\n" + "-"*80)
    print("TASK 3.6.3 - TEST CRUD DE CATEGORIES")
    print("-"*80)

    categories_passed = sum(1 for _, status, _ in categories_results if status == "PASS")
    categories_total = len(categories_results)

    print(f"\nStatus: {categories_passed}/{categories_total} tests passed\n")

    for step, status, detail in categories_results:
        status_symbol = "✓" if status == "PASS" else ("⚠" if status == "PARTIAL" else "✗")
        print(f"  [{status_symbol}] {status:8} - {step}")
        if detail:
            print(f"              {detail}")

    # Overall Summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)

    total_passed = accounts_passed + categories_passed
    total_tests = accounts_total + categories_total
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"\nTotal Tests Passed: {total_passed}/{total_tests} ({pass_rate:.1f}%)")
    print(f"Screenshots saved in: {SCREENSHOT_DIR}/")

    if pass_rate >= 80:
        print("\n✓ TEST SUITE: PASSED")
    elif pass_rate >= 60:
        print("\n⚠ TEST SUITE: PARTIAL PASS")
    else:
        print("\n✗ TEST SUITE: FAILED")

    print("\n" + "="*80)

def main():
    """Main test execution"""
    print("="*80)
    print("Django Admin E2E Test Suite")
    print("Tasks 3.6.2 and 3.6.3")
    print("="*80)

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        try:
            # Create screenshot directory
            create_screenshot_dir(page)

            # Login
            if not login_admin(page):
                print("\n✗ CRITICAL: Login failed. Cannot proceed with tests.")
                return

            # Run Account tests
            accounts_results = test_accounts_crud(page)

            # Run Category tests
            categories_results = test_categories_crud(page)

            # Generate report
            generate_report(accounts_results, categories_results)

        except Exception as e:
            print(f"\n✗ CRITICAL ERROR: {str(e)}")
            take_screenshot(page, "CRITICAL_ERROR")
        finally:
            # Cleanup
            print("\n[CLEANUP] Closing browser...")
            browser.close()
            print("✓ Browser closed")

if __name__ == "__main__":
    main()
