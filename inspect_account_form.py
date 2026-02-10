"""
Inspect account creation form
"""

import requests
from bs4 import BeautifulSoup
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

session = requests.Session()
base_url = 'http://localhost:8000'

# Login first
response = session.get(f'{base_url}/usuarios/login/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

data = {
    'csrfmiddlewaretoken': csrf_token,
    'username': 'test_dashboard@test.com',
    'password': 'TestPass123!'
}

response = session.post(f'{base_url}/usuarios/login/', data=data, allow_redirects=True)
print(f"Login status: {response.status_code}\n")

# Get account creation form
print("=== ACCOUNT CREATION FORM ===\n")
response = session.get(f'{base_url}/accounts/nova/')
soup = BeautifulSoup(response.text, 'html.parser')

print("Page title:", soup.find('title').text if soup.find('title') else 'No title')
print()

# Find the form
form = soup.find('form')
if form:
    print("Form found!")
    print(f"  Action: {form.get('action')}")
    print(f"  Method: {form.get('method')}")
    print()

    # Find all input fields
    print("Input fields:")
    inputs = form.find_all(['input', 'select', 'textarea'])
    for inp in inputs:
        tag = inp.name
        name = inp.get('name', 'unnamed')
        inp_type = inp.get('type', 'text') if tag == 'input' else tag
        required = 'required' if inp.get('required') else ''

        print(f"  {tag.upper()} - name='{name}', type='{inp_type}' {required}")

        if tag == 'select':
            options = inp.find_all('option')
            for opt in options:
                print(f"    Option: value='{opt.get('value')}' - {opt.get_text(strip=True)}")
else:
    print("No form found!")

# Try to create an account with correct field names
print("\n\n=== ATTEMPTING TO CREATE ACCOUNT ===\n")

response = session.get(f'{base_url}/accounts/nova/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

# Try different possible field combinations
test_data = {
    'csrfmiddlewaretoken': csrf_token,
    'name': 'Teste Manual Conta',
    'account_type': 'checking',
    'initial_balance': '1500,00'
}

print("Submitting data:")
for key, val in test_data.items():
    if key != 'csrfmiddlewaretoken':
        print(f"  {key}: {val}")
print()

response = session.post(f'{base_url}/accounts/nova/', data=test_data, allow_redirects=True)
print(f"Response status: {response.status_code}")
print(f"Final URL: {response.url}")

# Check if account was created
soup = BeautifulSoup(response.text, 'html.parser')

# Look for error messages
errors = soup.find_all(['div', 'p', 'span'], class_=lambda x: x and ('error' in str(x).lower() or 'alert' in str(x).lower()))
if errors:
    print("\nErrors found:")
    for error in errors:
        text = error.get_text(strip=True)
        if text:
            print(f"  - {text}")

# Look for success messages
success = soup.find_all(['div', 'p', 'span'], class_=lambda x: x and ('success' in str(x).lower() or 'alert' in str(x).lower()))
if success:
    print("\nSuccess messages:")
    for msg in success:
        text = msg.get_text(strip=True)
        if text:
            print(f"  - {text}")

# Check accounts page
print("\n\n=== CHECKING ACCOUNTS PAGE AFTER CREATION ===\n")
response = session.get(f'{base_url}/accounts/')
soup = BeautifulSoup(response.text, 'html.parser')

if 'Nenhuma conta' in soup.get_text():
    print("❌ No accounts found - creation failed")
else:
    print("✓ Accounts found!")
    # Try to extract account info
    text_lines = [line.strip() for line in soup.get_text().split('\n') if line.strip()]
    for line in text_lines[:30]:
        if any(word in line.lower() for word in ['teste', 'saldo', 'checking', 'corrente']):
            print(f"  {line}")
