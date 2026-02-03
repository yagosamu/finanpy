"""
Debug test to understand the category form issue
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test@123456"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    # Login
    page.goto(f"{BASE_URL}/admin/")
    page.fill('input[name="username"]', ADMIN_EMAIL)
    page.fill('input[name="password"]', ADMIN_PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    print("Logged in\n")

    # Navigate to Categories
    print("Current URL:", page.url)
    page.goto(f"{BASE_URL}/admin/categories/category/")
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    print("After navigation URL:", page.url)
    print("Page title:", page.title())

    # Take screenshot
    page.screenshot(path="test_screenshots/debug_cat_list.png", full_page=True)

    # Find all "Add" links
    print("\nLooking for Add links...")
    add_links = page.locator('a.addlink').all()
    print(f"Found {len(add_links)} add links")

    for i, link in enumerate(add_links):
        href = link.get_attribute('href')
        text = link.text_content()
        print(f"  Link {i}: text='{text}', href='{href}'")

    # Try clicking the first add link
    if len(add_links) > 0:
        print("\nClicking first add link...")
        add_links[0].click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("After click URL:", page.url)
        print("Page title:", page.title())

        # Take screenshot
        page.screenshot(path="test_screenshots/debug_cat_add_form.png", full_page=True)

        # Check form fields
        print("\nChecking form fields...")
        inputs = page.locator('input[type="text"], input[type="color"]').all()
        print(f"Text/Color inputs: {len(inputs)}")
        for i, inp in enumerate(inputs):
            name = inp.get_attribute('name')
            id_attr = inp.get_attribute('id')
            input_type = inp.get_attribute('type')
            print(f"  Input {i}: name='{name}', id='{id_attr}', type='{input_type}'")

        selects = page.locator('select').all()
        print(f"\nSelect elements: {len(selects)}")
        for i, sel in enumerate(selects):
            name = sel.get_attribute('name')
            id_attr = sel.get_attribute('id')
            print(f"  Select {i}: name='{name}', id='{id_attr}'")

    input("\nPress Enter to close browser...")
    browser.close()
