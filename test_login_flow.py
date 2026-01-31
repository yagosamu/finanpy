"""
E2E Test: Login Flow
Task 1.7.2 - Test Login Flow

Tests:
1. Logout if logged in
2. Navigate to login page
3. Test login with valid credentials
4. Test login with invalid credentials
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright, expect
import time
from datetime import datetime

def test_login_flow():
    """Execute comprehensive login flow E2E tests"""

    base_url = "http://localhost:8000"
    test_email = "test-user-32633@example.com"
    test_password = "Test@123456"
    wrong_password = "WrongPassword123"

    results = {
        'flow': 'Login Flow',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'PASSED',
        'steps': [],
        'issues': [],
        'screenshots': []
    }

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        try:
            # STEP 1: Ensure fresh session (clear cookies)
            print("\n" + "="*60)
            print("STEP 1: Clear session and navigate to login")
            print("="*60)

            # Clear all cookies to ensure fresh session
            context.clear_cookies()
            print("[OK] Session cleared")

            # Navigate directly to login page
            page.goto(f"{base_url}/usuarios/login/", wait_until="domcontentloaded", timeout=10000)
            time.sleep(1)

            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\01_initial_state.png")

            results['steps'].append({
                'step': '1. Clear session',
                'status': 'OK',
                'details': 'Cleared cookies and navigated to login page'
            })
            results['screenshots'].append('01_initial_state.png - Initial fresh session state')

            print("[OK] Fresh session established")

            # STEP 2: Navigate to login page
            print("\n" + "="*60)
            print("STEP 2: Navigate to login page")
            print("="*60)

            page.goto(f"{base_url}/usuarios/login/")
            time.sleep(1)
            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\02_login_page.png")

            # Verify we're on the login page
            current_url = page.url
            if '/usuarios/login/' in current_url:
                results['steps'].append({
                    'step': '2. Navigate to login page',
                    'status': 'OK',
                    'details': f'Successfully loaded login page at {current_url}'
                })
                results['screenshots'].append('02_login_page.png - Login page initial state')
                print(f"[OK] Login page loaded: {current_url}")
            else:
                raise Exception(f"Expected login page but got: {current_url}")

            # STEP 3: Test login with valid credentials
            print("\n" + "="*60)
            print("STEP 3: Test login with valid credentials")
            print("="*60)
            print(f"Email: {test_email}")
            print(f"Password: {test_password}")

            # Find and fill email field
            email_field = page.locator('input[name="email"], input[type="email"], input#id_email')
            email_field.fill(test_email)
            print("[OK] Email field filled")

            # Find and fill password field
            password_field = page.locator('input[name="password"], input[type="password"], input#id_password')
            password_field.fill(test_password)
            print("[OK] Password field filled")

            # Take screenshot before submission
            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\03_before_valid_login.png")
            results['screenshots'].append('03_before_valid_login.png - Form filled with valid credentials')

            # Submit the form
            submit_button = page.locator('button[type="submit"], input[type="submit"]')
            submit_button.click()
            print("[OK] Form submitted")

            # Wait for navigation
            time.sleep(2)

            # Take screenshot after submission
            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\04_after_valid_login.png")
            results['screenshots'].append('04_after_valid_login.png - Page after valid login')

            # Verify redirect to dashboard
            current_url = page.url
            print(f"Current URL after login: {current_url}")

            if '/dashboard/' in current_url or current_url == f"{base_url}/":
                results['steps'].append({
                    'step': '3. Login with valid credentials',
                    'status': 'OK',
                    'details': f'Successfully logged in and redirected to {current_url}'
                })
                print(f"[OK] Successfully redirected to: {current_url}")
            else:
                # Check if still on login page (might indicate failed login)
                if '/login/' in current_url:
                    # Look for error messages
                    page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\04b_login_failed.png")
                    error_msg = page.locator('.alert, .error, .text-red-500').text_content() if page.locator('.alert, .error, .text-red-500').count() > 0 else 'No error message found'
                    results['steps'].append({
                        'step': '3. Login with valid credentials',
                        'status': 'FAILED',
                        'details': f'Login failed - still on login page. Error: {error_msg}'
                    })
                    results['issues'].append(f'Valid login failed - remained on login page. Error message: {error_msg}')
                    results['status'] = 'FAILED'
                else:
                    results['steps'].append({
                        'step': '3. Login with valid credentials',
                        'status': 'WARNING',
                        'details': f'Redirected to unexpected page: {current_url}'
                    })

            # Verify session is maintained - navigate to a protected page
            print("\nVerifying session is maintained...")
            page.goto(f"{base_url}/dashboard/")
            time.sleep(1)

            current_url = page.url
            if '/login/' in current_url:
                results['issues'].append('Session not maintained - redirected back to login when accessing dashboard')
                results['status'] = 'FAILED'
                print("[FAILED] Session NOT maintained - redirected to login")
            else:
                print(f"[OK] Session maintained - accessing protected page: {current_url}")
                results['steps'].append({
                    'step': '3a. Verify session is maintained',
                    'status': 'OK',
                    'details': 'Session maintained after login'
                })

            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\05_session_check.png")
            results['screenshots'].append('05_session_check.png - Session verification')

            # STEP 4: Logout first (clear session)
            print("\n" + "="*60)
            print("STEP 4: Test login with invalid credentials")
            print("="*60)
            print("Sub-step: Clear session")

            # Clear cookies to logout
            context.clear_cookies()
            print("[OK] Session cleared")

            # Navigate to login page
            page.goto(f"{base_url}/usuarios/login/", wait_until="domcontentloaded", timeout=10000)
            time.sleep(1)
            print("[OK] Back to login page")

            # Try to login with wrong password
            print(f"\nAttempting login with wrong password...")
            print(f"Email: {test_email}")
            print(f"Password: {wrong_password}")

            email_field = page.locator('input[name="email"], input[type="email"], input#id_email')
            email_field.fill(test_email)

            password_field = page.locator('input[name="password"], input[type="password"], input#id_password')
            password_field.fill(wrong_password)

            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\06_before_invalid_login.png")
            results['screenshots'].append('06_before_invalid_login.png - Form filled with invalid credentials')

            submit_button = page.locator('button[type="submit"], input[type="submit"]')
            submit_button.click()
            print("[OK] Form submitted with invalid credentials")

            # Wait for response
            time.sleep(2)

            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\07_after_invalid_login.png")
            results['screenshots'].append('07_after_invalid_login.png - Page after invalid login attempt')

            # Verify still on login page
            current_url = page.url
            print(f"Current URL after invalid login: {current_url}")

            if '/login/' in current_url:
                print("[OK] User NOT redirected (remained on login page)")

                # Look for error message
                error_selectors = [
                    '.alert',
                    '.error',
                    '.text-red-500',
                    '.bg-red-100',
                    '[class*="error"]',
                    '[class*="alert"]',
                    '.messages',
                    '.errorlist'
                ]

                error_found = False
                error_message = ""

                for selector in error_selectors:
                    if page.locator(selector).count() > 0:
                        error_message = page.locator(selector).first.text_content()
                        error_found = True
                        print(f"[OK] Error message displayed: {error_message}")
                        break

                if error_found:
                    results['steps'].append({
                        'step': '4. Login with invalid credentials',
                        'status': 'OK',
                        'details': f'Login correctly rejected. Error message: "{error_message}"'
                    })
                else:
                    # Check if there's any visible text that might be an error
                    page_text = page.content()
                    if any(keyword in page_text.lower() for keyword in ['erro', 'error', 'inválido', 'invalid', 'incorreto', 'incorrect']):
                        print("[OK] Error indication found in page content")
                        results['steps'].append({
                            'step': '4. Login with invalid credentials',
                            'status': 'OK',
                            'details': 'Login correctly rejected. Error indication found in page.'
                        })
                    else:
                        print("[WARNING] No clear error message displayed")
                        results['steps'].append({
                            'step': '4. Login with invalid credentials',
                            'status': 'WARNING',
                            'details': 'Login rejected but no clear error message displayed'
                        })
                        results['issues'].append('No clear error message shown for invalid login attempt')
            else:
                print(f"[FAILED] User was redirected to: {current_url}")
                results['steps'].append({
                    'step': '4. Login with invalid credentials',
                    'status': 'FAILED',
                    'details': f'User was redirected despite invalid credentials to: {current_url}'
                })
                results['issues'].append(f'Invalid login incorrectly succeeded - redirected to {current_url}')
                results['status'] = 'FAILED'

        except Exception as e:
            print(f"\n[FAILED] ERROR: {str(e)}")
            results['status'] = 'FAILED'
            results['issues'].append(f'Test execution error: {str(e)}')
            page.screenshot(path="C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots\\error_screenshot.png")
            results['screenshots'].append('error_screenshot.png - Error state')

        finally:
            # Close browser
            browser.close()

    # Print final report
    print("\n" + "="*60)
    print("TEST REPORT")
    print("="*60)
    print(f"\nFlow: {results['flow']}")
    print(f"Date: {results['date']}")
    print(f"Status: {results['status']}")

    print("\n--- Steps Executed ---")
    for i, step in enumerate(results['steps'], 1):
        print(f"{i}. {step['step']} - {step['status']}")
        print(f"   {step['details']}")

    print("\n--- Screenshots ---")
    for screenshot in results['screenshots']:
        print(f"- {screenshot}")

    if results['issues']:
        print("\n--- Issues Found ---")
        for issue in results['issues']:
            print(f"- {issue}")

    print("\n" + "="*60)

    return results

if __name__ == "__main__":
    # Create screenshots directory
    import os
    os.makedirs("C:\\Users\\Yago\\desktop\\asimov\\projetos_ia\\claude_code\\finanpy\\screenshots", exist_ok=True)

    # Run the test
    results = test_login_flow()

    # Exit with appropriate code
    exit(0 if results['status'] == 'PASSED' else 1)
