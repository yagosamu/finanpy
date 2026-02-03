"""
Simple test to debug account creation issue
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test@123456"

def take_screenshot(page, name):
    page.screenshot(path=f"test_screenshots/debug_{name}.png", full_page=True)
    print(f"Screenshot: debug_{name}.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # Login
    page.goto(f"{BASE_URL}/admin/")
    page.fill('input[name="username"]', ADMIN_EMAIL)
    page.fill('input[name="password"]', ADMIN_PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    print("Logged in")

    # Go to add account
    page.goto(f"{BASE_URL}/admin/accounts/account/add/")
    page.wait_for_load_state('networkidle')
    take_screenshot(page, "01_add_form")

    # Fill form
    page.select_option('select[name="user"]', index=1)
    page.fill('input[name="name"]', "Test Account")
    page.select_option('select[name="account_type"]', value="checking")
    page.fill('input[name="bank"]', "Test Bank")
    page.fill('input[name="initial_balance"]', "1000.00")
    take_screenshot(page, "02_form_filled")

    # Try to save
    page.click('input[name="_save"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    take_screenshot(page, "03_after_save")

    # Check for errors
    if page.locator('.errorlist').count() > 0:
        print("ERRORS FOUND:")
        errors = page.locator('.errorlist li').all_text_contents()
        for error in errors:
            print(f"  - {error}")

    # Check for success
    if page.locator('li.success').count() > 0:
        print("SUCCESS MESSAGE FOUND")
        msg = page.locator('li.success').text_content()
        print(f"  {msg}")

    # Check URL
    current_url = page.url
    print(f"Current URL: {current_url}")

    browser.close()
