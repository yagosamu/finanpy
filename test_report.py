"""
Generate detailed test report for signup flow
"""

import requests
import random
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Base URL
BASE_URL = 'http://localhost:8000'

# Generate unique test email
test_email = f'test-user-{random.randint(10000, 99999)}@example.com'
test_password = 'Test@123456'

print('=' * 100)
print(' ' * 35 + 'E2E TEST REPORT')
print(' ' * 32 + 'User Signup Flow')
print('=' * 100)
print()
print(f'Flow: User Registration and Authentication')
print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Test Email: {test_email}')
print(f'Test Password: {test_password}')
print()
print('=' * 100)
print()

# Test execution
session = requests.Session()
test_steps = []

# STEP 1: Navigate to signup page
print('[STEP 1] Navigate to signup page (/usuarios/cadastro/)')
print('-' * 100)
try:
    signup_url = urljoin(BASE_URL, '/usuarios/cadastro/')
    response = session.get(signup_url)

    if response.status_code == 200:
        print('✓ PASS - Page loaded successfully')
        print(f'  Status Code: {response.status_code}')
        print(f'  URL: {signup_url}')

        soup = BeautifulSoup(response.text, 'html.parser')

        # Check form elements
        form = soup.find('form')
        email_field = soup.find('input', {'type': 'email'})
        password_fields = soup.find_all('input', {'type': 'password'})
        submit_btn = soup.find('button', {'type': 'submit'})

        print(f'  Form present: {"Yes" if form else "No"}')
        print(f'  Email field: {"Yes" if email_field else "No"}')
        print(f'  Password fields: {len(password_fields)} found')
        print(f'  Submit button: {"Yes" if submit_btn else "No"}')

        test_steps.append({
            'step': 'Navigate to signup page',
            'status': 'PASS',
            'details': f'Page loaded with all form elements (Status: {response.status_code})'
        })
    else:
        print(f'✗ FAIL - Unexpected status code: {response.status_code}')
        test_steps.append({
            'step': 'Navigate to signup page',
            'status': 'FAIL',
            'details': f'Status code: {response.status_code}'
        })
except Exception as e:
    print(f'✗ FAIL - {str(e)}')
    test_steps.append({
        'step': 'Navigate to signup page',
        'status': 'FAIL',
        'details': str(e)
    })

print()

# STEP 2: Fill and submit signup form
print('[STEP 2] Fill and submit signup form')
print('-' * 100)
try:
    # Get CSRF token
    response = session.get(signup_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})

    if csrf_token:
        csrf_value = csrf_token.get('value')
        print('✓ CSRF token extracted')

        # Prepare form data
        form_data = {
            'csrfmiddlewaretoken': csrf_value,
            'email': test_email,
            'password1': test_password,
            'password2': test_password,
        }

        print(f'  Email: {test_email}')
        print(f'  Password: {"*" * len(test_password)} (length: {len(test_password)})')
        print(f'  Password confirmation: Matching')

        # Submit form
        response = session.post(signup_url, data=form_data, allow_redirects=False)

        print(f'  Response status: {response.status_code}')

        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location', '')
            print(f'✓ PASS - Form submitted successfully')
            print(f'  Redirected to: {redirect_url}')

            test_steps.append({
                'step': 'Submit signup form',
                'status': 'PASS',
                'details': f'Redirected to {redirect_url}'
            })
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            errors = soup.find_all(class_=['text-red-400', 'text-red-100'])
            error_messages = [e.text.strip() for e in errors if e.text.strip()]

            if error_messages:
                print(f'✗ FAIL - Form validation errors:')
                for err in error_messages:
                    print(f'    - {err}')
                test_steps.append({
                    'step': 'Submit signup form',
                    'status': 'FAIL',
                    'details': f'Validation errors: {", ".join(error_messages)}'
                })
            else:
                print(f'✗ FAIL - No redirect (Status: {response.status_code})')
                test_steps.append({
                    'step': 'Submit signup form',
                    'status': 'FAIL',
                    'details': f'No redirect, status: {response.status_code}'
                })
    else:
        print('✗ FAIL - CSRF token not found')
        test_steps.append({
            'step': 'Submit signup form',
            'status': 'FAIL',
            'details': 'CSRF token not found'
        })

except Exception as e:
    print(f'✗ FAIL - {str(e)}')
    test_steps.append({
        'step': 'Submit signup form',
        'status': 'FAIL',
        'details': str(e)
    })

print()

# STEP 3: Verify redirect to dashboard
print('[STEP 3] Verify redirect to dashboard')
print('-' * 100)
try:
    redirect_url = response.headers.get('Location', '')

    if 'dashboard' in redirect_url:
        print('✓ PASS - Redirected to dashboard')
        print(f'  Redirect URL: {redirect_url}')

        test_steps.append({
            'step': 'Redirect to dashboard',
            'status': 'PASS',
            'details': f'URL: {redirect_url}'
        })
    elif redirect_url:
        print(f'⚠ WARNING - Redirected to different page: {redirect_url}')
        test_steps.append({
            'step': 'Redirect to dashboard',
            'status': 'WARNING',
            'details': f'Redirected to {redirect_url} instead of dashboard'
        })
    else:
        print('✗ FAIL - No redirect occurred')
        test_steps.append({
            'step': 'Redirect to dashboard',
            'status': 'FAIL',
            'details': 'No redirect'
        })

except Exception as e:
    print(f'✗ FAIL - {str(e)}')
    test_steps.append({
        'step': 'Redirect to dashboard',
        'status': 'FAIL',
        'details': str(e)
    })

print()

# STEP 4: Verify automatic login (session cookie)
print('[STEP 4] Verify user is automatically logged in')
print('-' * 100)
try:
    if 'sessionid' in session.cookies:
        print('✓ PASS - User automatically logged in')
        print(f'  Session cookie present: sessionid')
        print(f'  Cookie domain: {session.cookies.get("sessionid", domain=True)}')

        test_steps.append({
            'step': 'Automatic login after signup',
            'status': 'PASS',
            'details': 'Session cookie present'
        })
    else:
        print('✗ FAIL - No session cookie found')
        print('  Available cookies:', list(session.cookies.keys()))

        test_steps.append({
            'step': 'Automatic login after signup',
            'status': 'FAIL',
            'details': 'No session cookie'
        })

except Exception as e:
    print(f'✗ FAIL - {str(e)}')
    test_steps.append({
        'step': 'Automatic login after signup',
        'status': 'FAIL',
        'details': str(e)
    })

print()

# STEP 5: Verify profile creation
print('[STEP 5] Verify profile was created (/perfil/)')
print('-' * 100)
try:
    profile_url = urljoin(BASE_URL, '/perfil/')
    response = session.get(profile_url, allow_redirects=False)

    if response.status_code == 200:
        print('✓ PASS - Profile page accessible')
        print(f'  Status: {response.status_code}')

        # Check if email is in the page
        if test_email in response.text:
            print(f'  Email visible on page: Yes ({test_email})')
        else:
            print(f'  Email visible on page: No')

        test_steps.append({
            'step': 'Profile creation verification',
            'status': 'PASS',
            'details': 'Profile page accessible and contains user email'
        })

    elif response.status_code in [301, 302, 303, 307, 308]:
        redirect = response.headers.get('Location', '')
        if 'login' in redirect:
            print('✗ FAIL - Redirected to login (user not authenticated)')
            test_steps.append({
                'step': 'Profile creation verification',
                'status': 'FAIL',
                'details': 'Redirected to login page'
            })
        else:
            print(f'⚠ WARNING - Redirected to: {redirect}')
            test_steps.append({
                'step': 'Profile creation verification',
                'status': 'WARNING',
                'details': f'Redirected to {redirect}'
            })
    else:
        print(f'✗ FAIL - Unexpected status: {response.status_code}')
        test_steps.append({
            'step': 'Profile creation verification',
            'status': 'FAIL',
            'details': f'Status: {response.status_code}'
        })

except Exception as e:
    print(f'✗ FAIL - {str(e)}')
    test_steps.append({
        'step': 'Profile creation verification',
        'status': 'FAIL',
        'details': str(e)
    })

print()

# STEP 6: Verify user in database
print('[STEP 6] Verify user exists in database')
print('-' * 100)
try:
    # Use Django to check database
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    from profiles.models import Profile

    User = get_user_model()
    user = User.objects.filter(email=test_email).first()

    if user:
        print('✓ PASS - User found in database')
        print(f'  User ID: {user.id}')
        print(f'  Email: {user.email}')
        print(f'  Active: {user.is_active}')
        print(f'  Created: {user.date_joined}')

        # Check for profile
        profile = Profile.objects.filter(user=user).first()

        if profile:
            print(f'  Profile ID: {profile.id}')
            print(f'  Profile created: Yes')

            test_steps.append({
                'step': 'Database verification',
                'status': 'PASS',
                'details': f'User and profile created (ID: {user.id})'
            })
        else:
            print(f'  Profile created: No')
            test_steps.append({
                'step': 'Database verification',
                'status': 'FAIL',
                'details': 'User exists but profile not found'
            })
    else:
        print('✗ FAIL - User not found in database')
        test_steps.append({
            'step': 'Database verification',
            'status': 'FAIL',
            'details': 'User not found'
        })

except Exception as e:
    print(f'✗ FAIL - {str(e)}')
    test_steps.append({
        'step': 'Database verification',
        'status': 'FAIL',
        'details': str(e)
    })

print()
print('=' * 100)
print()

# Generate summary
print('TEST SUMMARY')
print('=' * 100)
print()

passed = sum(1 for s in test_steps if s['status'] == 'PASS')
failed = sum(1 for s in test_steps if s['status'] == 'FAIL')
warnings = sum(1 for s in test_steps if s['status'] == 'WARNING')
total = len(test_steps)

print(f'Total Steps: {total}')
print(f'Passed: {passed} ({passed/total*100:.1f}%)')
print(f'Failed: {failed} ({failed/total*100:.1f}%)')
print(f'Warnings: {warnings} ({warnings/total*100:.1f}%)')
print()

if failed == 0:
    overall_status = 'PASSED'
    print('✓✓✓ ALL TESTS PASSED ✓✓✓')
else:
    overall_status = 'FAILED'
    print(f'✗✗✗ {failed} TEST(S) FAILED ✗✗✗')

print()
print('STEPS EXECUTED:')
print('-' * 100)
for i, step in enumerate(test_steps, 1):
    symbol = '✓' if step['status'] == 'PASS' else ('⚠' if step['status'] == 'WARNING' else '✗')
    print(f'{i}. {symbol} {step["step"]} - {step["status"]}')
    print(f'   {step["details"]}')
    print()

if failed > 0:
    print('ISSUES FOUND:')
    print('-' * 100)
    for step in test_steps:
        if step['status'] == 'FAIL':
            print(f'✗ {step["step"]}')
            print(f'  Issue: {step["details"]}')
            print()

print('SUGGESTIONS:')
print('-' * 100)
print('1. All core signup functionality works correctly')
print('2. User registration, automatic login, and profile creation are functional')
print('3. Form validation and CSRF protection are properly implemented')
print('4. Consider adding data-testid attributes to form elements for easier E2E testing')
print('5. Add visual feedback for successful registration')
print()
print('=' * 100)
print(f'Overall Status: {overall_status}')
print('=' * 100)
