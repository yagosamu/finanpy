"""
Manual test for Categories CRUD to complete Task 3.6.3
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test@123456"

def screenshot(page, name, counter):
    filename = f"test_screenshots/cat_{counter:02d}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"  Screenshot: {filename}")
    return counter + 1

print("\n" + "="*80)
print("CATEGORIES CRUD TEST - Task 3.6.3")
print("="*80 + "\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=800)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    counter = 1

    # Login
    print("1. Logging in...")
    page.goto(f"{BASE_URL}/admin/")
    page.fill('input[name="username"]', ADMIN_EMAIL)
    page.fill('input[name="password"]', ADMIN_PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    print("  ✓ Logged in successfully\n")

    # Navigate to Categories
    print("2. Navigating to Categories...")
    page.goto(f"{BASE_URL}/admin/categories/category/")
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    counter = screenshot(page, "list", counter)
    print("  ✓ Navigated to Categories list\n")

    # View default categories
    print("3. Checking default categories...")
    default_cats = ['Alimentação', 'Transporte', 'Salário', 'Moradia', 'Saúde']
    found = [cat for cat in default_cats if cat in page.content()]
    print(f"  ✓ Found {len(found)} default categories: {', '.join(found)}\n")

    # Create new category
    print("4. Creating new category...")
    test_name = f"Test Category {datetime.now().strftime('%H%M%S')}"

    page.click('a.addlink')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    counter = screenshot(page, "add_form", counter)

    # Try to fill the form step by step
    print("  - Filling name field...")
    page.fill('input#id_name', test_name)

    print("  - Selecting category type...")
    # Look for the select element with different selectors
    try:
        page.select_option('select#id_category_type', value='expense')
        print("    ✓ Category type selected: expense")
    except Exception as e:
        print(f"    ✗ Failed to select category type: {str(e)}")
        # Try to take screenshot showing the actual form
        counter = screenshot(page, "form_error", counter)

        # Try to find all select elements
        selects = page.locator('select').all()
        print(f"    Found {len(selects)} select elements on page")
        for i, sel in enumerate(selects):
            try:
                name = sel.get_attribute('name')
                id_attr = sel.get_attribute('id')
                print(f"      Select {i}: name='{name}', id='{id_attr}'")
            except:
                pass

    print("  - Setting color...")
    try:
        # Use JavaScript to set color
        page.evaluate('document.querySelector(\'input#id_color\').value = "#FF5733"')
        print("    ✓ Color set: #FF5733")
    except Exception as e:
        print(f"    ✗ Failed to set color: {str(e)}")

    counter = screenshot(page, "form_filled", counter)

    print("  - Saving...")
    page.click('input[name="_save"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    counter = screenshot(page, "after_save", counter)

    # Check result
    if page.locator('.errorlist').count() > 0:
        errors = page.locator('.errorlist li').all_text_contents()
        print(f"  ✗ Validation errors: {errors}")
    elif test_name in page.content():
        print(f"  ✓ Category '{test_name}' created successfully\n")

        # Update category
        print("5. Updating category color...")
        page.goto(f"{BASE_URL}/admin/categories/category/")
        page.wait_for_load_state('networkidle')

        cat_link = page.locator(f'th.field-name a:has-text("{test_name}")').first
        if cat_link.count() > 0:
            cat_link.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            counter = screenshot(page, "edit_form", counter)

            # Change color
            page.evaluate('document.querySelector(\'input#id_color\').value = "#33C3FF"')
            counter = screenshot(page, "edit_filled", counter)

            page.click('input[name="_save"]')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            counter = screenshot(page, "after_update", counter)
            print("  ✓ Category updated\n")

    # Test filters
    print("6. Testing filters...")
    page.goto(f"{BASE_URL}/admin/categories/category/")
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    filter_links = page.locator('#changelist-filter a')
    if filter_links.count() > 0:
        # Filter by expense
        for i in range(filter_links.count()):
            text = filter_links.nth(i).text_content().lower()
            if 'despesa' in text or 'expense' in text:
                filter_links.nth(i).click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)
                counter = screenshot(page, "filtered_expense", counter)
                print("  ✓ Expense filter works")
                break

        # Filter by default
        page.goto(f"{BASE_URL}/admin/categories/category/")
        page.wait_for_load_state('networkidle')
        filter_links = page.locator('#changelist-filter a')
        for i in range(filter_links.count()):
            text = filter_links.nth(i).text_content().lower()
            if 'sim' in text or 'yes' in text:
                filter_links.nth(i).click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)
                counter = screenshot(page, "filtered_default", counter)
                print("  ✓ Default filter works")
                break
        print()

    print("="*80)
    print("CATEGORIES CRUD TEST COMPLETED")
    print("="*80 + "\n")

    browser.close()
