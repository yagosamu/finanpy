"""
E2E Test Script for User Signup Flow
Tests the complete registration process including form submission and redirect
"""

import requests
import random
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Base URL
BASE_URL = 'http://localhost:8000'

# Generate unique test email
test_email = f'test-user-{random.randint(10000, 99999)}@example.com'
test_password = 'Test@123456'

print('=' * 80)
print('E2E TEST: User Signup Flow')
print('=' * 80)
print()

# Test results tracking
test_results = []

def log_test(step, status, details=''):
    """Log test step results"""
    test_results.append({
        'step': step,
        'status': status,
        'details': details
    })
    status_symbol = '✓' if status == 'PASS' else '✗'
    print(f'{status_symbol} {step}: {status}')
    if details:
        print(f'  Details: {details}')
    print()

# Step 1: Navigate to signup page
print('STEP 1: Navigate to signup page')
print('-' * 80)
try:
    signup_url = urljoin(BASE_URL, '/usuarios/cadastro/')
    response = requests.get(signup_url)

    if response.status_code == 200:
        log_test('Navigation to /usuarios/cadastro/', 'PASS', f'Status code: {response.status_code}')

        # Parse HTML to verify form elements exist
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for form
        form = soup.find('form', {'method': 'post'})
        if form:
            log_test('Signup form found', 'PASS', 'Form element exists on page')
        else:
            log_test('Signup form found', 'FAIL', 'Form element not found')

        # Check for email field
        email_field = soup.find('input', {'type': 'email'})
        if email_field:
            log_test('Email field exists', 'PASS', f'Name: {email_field.get("name")}')
        else:
            log_test('Email field exists', 'FAIL', 'Email input not found')

        # Check for password fields
        password_fields = soup.find_all('input', {'type': 'password'})
        if len(password_fields) >= 2:
            log_test('Password fields exist', 'PASS', f'Found {len(password_fields)} password fields')
        else:
            log_test('Password fields exist', 'FAIL', f'Only found {len(password_fields)} password fields')

        # Check for submit button
        submit_btn = soup.find('button', {'type': 'submit'})
        if submit_btn:
            log_test('Submit button exists', 'PASS', f'Text: {submit_btn.text.strip()}')
        else:
            log_test('Submit button exists', 'FAIL', 'Submit button not found')

    else:
        log_test('Navigation to /usuarios/cadastro/', 'FAIL', f'Status code: {response.status_code}')

except Exception as e:
    log_test('Navigation to /usuarios/cadastro/', 'FAIL', str(e))

# Step 2: Extract CSRF token and submit signup form
print('STEP 2: Submit signup form')
print('-' * 80)
try:
    # Create a session to maintain cookies
    session = requests.Session()

    # Get the signup page to extract CSRF token
    response = session.get(signup_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract CSRF token
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_token:
        csrf_value = csrf_token.get('value')
        log_test('CSRF token extraction', 'PASS', 'Token found')

        # Prepare form data
        form_data = {
            'csrfmiddlewaretoken': csrf_value,
            'email': test_email,
            'password1': test_password,
            'password2': test_password,
        }

        print(f'Test credentials:')
        print(f'  Email: {test_email}')
        print(f'  Password: {test_password}')
        print()

        # Submit the form
        response = session.post(
            signup_url,
            data=form_data,
            allow_redirects=False  # Don't follow redirects automatically
        )

        log_test('Form submission', 'PASS', f'Response status: {response.status_code}')

        # Check if redirected (302 or 301)
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location', '')
            log_test('Redirect after signup', 'PASS', f'Redirected to: {redirect_url}')

            # Check if redirected to dashboard
            if 'dashboard' in redirect_url or redirect_url == '/':
                log_test('Redirect to dashboard', 'PASS', f'URL: {redirect_url}')
            else:
                log_test('Redirect to dashboard', 'WARNING', f'Redirected to {redirect_url} instead')

            # Follow redirect to verify user is logged in
            if redirect_url:
                # Make redirect_url absolute if it's relative
                if not redirect_url.startswith('http'):
                    redirect_url = urljoin(BASE_URL, redirect_url)

                response = session.get(redirect_url)

                if response.status_code == 200:
                    log_test('Access redirected page', 'PASS', f'Status: {response.status_code}')

                    # Check for session cookie
                    if 'sessionid' in session.cookies:
                        log_test('User automatically logged in', 'PASS', 'Session cookie present')
                    else:
                        log_test('User automatically logged in', 'FAIL', 'No session cookie found')
                else:
                    log_test('Access redirected page', 'FAIL', f'Status: {response.status_code}')
        else:
            # Not redirected - might have form errors
            soup = BeautifulSoup(response.text, 'html.parser')
            errors = soup.find_all(class_=['text-red-400', 'text-red-100'])

            if errors:
                error_messages = [e.text.strip() for e in errors if e.text.strip()]
                log_test('Redirect after signup', 'FAIL', f'Form errors: {", ".join(error_messages)}')
            else:
                log_test('Redirect after signup', 'FAIL', f'Status {response.status_code}, no redirect')

    else:
        log_test('CSRF token extraction', 'FAIL', 'CSRF token not found')

except Exception as e:
    log_test('Form submission', 'FAIL', str(e))

# Step 3: Verify profile creation by accessing /perfil/
print('STEP 3: Verify profile creation')
print('-' * 80)
try:
    profile_url = urljoin(BASE_URL, '/perfil/')
    response = session.get(profile_url, allow_redirects=False)

    if response.status_code == 200:
        log_test('Access profile page', 'PASS', 'Profile page accessible')

        # Check if the page contains profile-related content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for profile indicators (email, profile form, etc.)
        if test_email in response.text:
            log_test('Profile contains user email', 'PASS', f'Email found: {test_email}')
        else:
            log_test('Profile contains user email', 'WARNING', 'Email not visible on profile page')

    elif response.status_code in [301, 302, 303, 307, 308]:
        redirect_url = response.headers.get('Location', '')
        if 'login' in redirect_url:
            log_test('Access profile page', 'FAIL', 'Redirected to login (not authenticated)')
        else:
            log_test('Access profile page', 'WARNING', f'Redirected to: {redirect_url}')
    else:
        log_test('Access profile page', 'FAIL', f'Status code: {response.status_code}')

except Exception as e:
    log_test('Access profile page', 'FAIL', str(e))

# Step 4: Verify user in database (using Django shell)
print('STEP 4: Verify user in database')
print('-' * 80)
print('Creating verification script...')

verification_script = f"""
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()

email = '{test_email}'
print(f'Checking for user: {{email}}')

try:
    user = User.objects.get(email=email)
    print(f'✓ User found in database')
    print(f'  ID: {{user.id}}')
    print(f'  Email: {{user.email}}')
    print(f'  Active: {{user.is_active}}')
    print(f'  Created: {{user.date_joined}}')

    # Check for profile
    try:
        profile = Profile.objects.get(user=user)
        print(f'✓ Profile created')
        print(f'  Profile ID: {{profile.id}}')
    except Profile.DoesNotExist:
        print(f'✗ Profile not found for user')

except User.DoesNotExist:
    print(f'✗ User not found in database')
"""

# Save verification script
with open('verify_user.py', 'w', encoding='utf-8') as f:
    f.write(verification_script)

print('Run the following command to verify user in database:')
print('python manage.py shell < verify_user.py')
print()

# Print summary
print('=' * 80)
print('TEST SUMMARY')
print('=' * 80)
print()

passed = sum(1 for r in test_results if r['status'] == 'PASS')
failed = sum(1 for r in test_results if r['status'] == 'FAIL')
warnings = sum(1 for r in test_results if r['status'] == 'WARNING')
total = len(test_results)

print(f'Total Tests: {total}')
print(f'Passed: {passed}')
print(f'Failed: {failed}')
print(f'Warnings: {warnings}')
print()

if failed == 0:
    print('✓ ALL TESTS PASSED')
else:
    print('✗ SOME TESTS FAILED')
    print()
    print('Failed tests:')
    for r in test_results:
        if r['status'] == 'FAIL':
            print(f'  - {r["step"]}: {r["details"]}')

print()
print('=' * 80)
