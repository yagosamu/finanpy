"""
Debug form validation errors
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

session.post(f'{base_url}/usuarios/login/', data=data, allow_redirects=True)

# Try with dot format (US)
print("=== TEST 1: US Format (1500.00) ===\n")

response = session.get(f'{base_url}/accounts/nova/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

test_data = {
    'csrfmiddlewaretoken': csrf_token,
    'name': 'Teste US Format',
    'account_type': 'checking',
    'bank': 'Banco Teste',
    'initial_balance': '1500.00'
}

response = session.post(f'{base_url}/accounts/nova/', data=test_data, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

soup = BeautifulSoup(response.text, 'html.parser')

# Extract all visible text from the page
page_text = soup.get_text()

# Look for "Este campo" which is common in Django error messages
if 'Este campo' in page_text or 'obrigatório' in page_text or 'válido' in page_text:
    print("\n❌ Validation errors found:")
    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    for i, line in enumerate(lines):
        if any(word in line.lower() for word in ['este campo', 'obrigatório', 'válido', 'erro']):
            print(f"  {line}")
            # Print context (next line might have more info)
            if i + 1 < len(lines):
                print(f"    {lines[i+1]}")
else:
    if 'nova' in response.url:
        print("❌ Still on form page - creation failed (no explicit errors shown)")
    else:
        print("✓ Redirected away from form - might be successful")

# Check accounts
response = session.get(f'{base_url}/accounts/')
if 'Nenhuma conta' in response.text:
    print("❌ No accounts found\n")
else:
    print("✓ Account created!\n")

# Try with integer only
print("=== TEST 2: Integer Only (1500) ===\n")

response = session.get(f'{base_url}/accounts/nova/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

test_data = {
    'csrfmiddlewaretoken': csrf_token,
    'name': 'Teste Integer',
    'account_type': 'savings',
    'bank': 'Banco Teste 2',
    'initial_balance': '2000'
}

response = session.post(f'{base_url}/accounts/nova/', data=test_data, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

soup = BeautifulSoup(response.text, 'html.parser')
page_text = soup.get_text()

if 'Este campo' in page_text or 'obrigatório' in page_text or 'válido' in page_text:
    print("\n❌ Validation errors found")
else:
    if 'nova' in response.url:
        print("❌ Still on form page")
    else:
        print("✓ Redirected away from form")

response = session.get(f'{base_url}/accounts/')
if 'Nenhuma conta' in response.text:
    print("❌ No accounts found\n")
else:
    print("✓ Account created!\n")

# Try without bank field (if it's optional)
print("=== TEST 3: Without Bank Field ===\n")

response = session.get(f'{base_url}/accounts/nova/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

test_data = {
    'csrfmiddlewaretoken': csrf_token,
    'name': 'Teste No Bank',
    'account_type': 'wallet',
    'initial_balance': '500'
}

response = session.post(f'{base_url}/accounts/nova/', data=test_data, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

soup = BeautifulSoup(response.text, 'html.parser')
page_text = soup.get_text()

if 'Este campo' in page_text or 'obrigatório' in page_text or 'válido' in page_text:
    print("\n❌ Validation errors found:")
    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    for i, line in enumerate(lines):
        if any(word in line.lower() for word in ['este campo', 'obrigatório', 'válido', 'banco']):
            print(f"  {line}")
else:
    if 'nova' in response.url:
        print("❌ Still on form page")
    else:
        print("✓ Redirected away from form")

response = session.get(f'{base_url}/accounts/')
soup = BeautifulSoup(response.text, 'html.parser')
if 'Nenhuma conta' in soup.get_text():
    print("❌ No accounts found\n")
else:
    print("✓ Account created!")
    # Show what we have
    text_lines = [line.strip() for line in soup.get_text().split('\n') if line.strip()]
    print("\nAccount details found:")
    for line in text_lines:
        if any(word in line.lower() for word in ['teste', 'saldo', 'r$', 'corrente', 'wallet', 'poupança']):
            print(f"  {line}")
