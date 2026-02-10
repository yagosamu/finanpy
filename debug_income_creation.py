"""
Debug income transaction creation
"""

import requests
from bs4 import BeautifulSoup
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

session = requests.Session()
base_url = 'http://localhost:8000'

# Login
response = session.get(f'{base_url}/usuarios/login/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

data = {
    'csrfmiddlewaretoken': csrf_token,
    'username': 'dashboard_test_1rqi8dh6@test.com',
    'password': 'TestPass123!'
}

session.post(f'{base_url}/usuarios/login/', data=data, allow_redirects=True)

print("=== TRYING TO CREATE INCOME TRANSACTION ===\n")

# Get form
response = session.get(f'{base_url}/transacoes/nova/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
csrf_token = csrf.get('value') if csrf else None

# Get available categories and accounts
category_select = soup.find('select', {'name': 'category'})
account_select = soup.find('select', {'name': 'account'})

print("Categories available:")
for option in category_select.find_all('option'):
    value = option.get('value')
    text = option.get_text(strip=True)
    if value:
        print(f"  {value}: {text}")

print("\nAccounts available:")
for option in account_select.find_all('option'):
    value = option.get('value')
    text = option.get_text(strip=True)
    if value:
        print(f"  {value}: {text}")

# Find an income category
income_category_id = None
for option in category_select.find_all('option'):
    value = option.get('value')
    text = option.get_text(strip=True).lower()
    if value and any(word in text for word in ['freelance', 'salário', 'salary', 'investimento']):
        income_category_id = value
        print(f"\n✓ Using income category: {value} - {text}")
        break

# Get first account
account_id = None
for option in account_select.find_all('option'):
    value = option.get('value')
    if value:
        account_id = value
        text = option.get_text(strip=True)
        print(f"✓ Using account: {value} - {text}")
        break

if not income_category_id or not account_id:
    print("\n✗ Could not find suitable category or account")
    sys.exit(1)

# Submit income transaction
from datetime import datetime

data = {
    'csrfmiddlewaretoken': csrf_token,
    'transaction_type': 'income',
    'amount': '500.00',
    'description': 'Salário teste DEBUG',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'category': income_category_id,
    'account': account_id
}

print("\n=== SUBMITTING DATA ===")
for key, val in data.items():
    if key != 'csrfmiddlewaretoken':
        print(f"  {key}: {val}")

response = session.post(f'{base_url}/transacoes/nova/', data=data, allow_redirects=True)

print(f"\nResponse status: {response.status_code}")
print(f"Final URL: {response.url}")

# Check for validation errors
soup = BeautifulSoup(response.text, 'html.parser')
page_text = soup.get_text()

if 'Este campo' in page_text or 'obrigatório' in page_text or 'válido' in page_text:
    print("\n❌ VALIDATION ERRORS:")
    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    for i, line in enumerate(lines):
        if any(word in line.lower() for word in ['este campo', 'obrigatório', 'válido', 'erro']):
            print(f"  {line}")
            if i + 1 < len(lines):
                print(f"    Context: {lines[i+1]}")
elif 'nova' in response.url:
    print("\n⚠️  Still on form page (but no explicit errors shown)")

    # Check if there's a success message that means it worked
    if 'sucesso' in page_text.lower():
        print("✓ Success message found!")
else:
    print("\n✓ Redirected away from form - likely successful")

# Verify creation
print("\n=== VERIFYING CREATION ===\n")
response = session.get(f'{base_url}/transacoes/')
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
if table:
    rows = table.find_all('tr')[1:]
    print(f"Total transactions now: {len(rows)}")

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            desc = cols[1].get_text(strip=True)
            amount = cols[4].get_text(strip=True) if len(cols) >= 5 else 'N/A'
            print(f"  - {desc}: {amount}")

    # Check specifically for income
    income_found = any('DEBUG' in row.get_text() or '500' in row.get_text() for row in rows)
    if income_found:
        print("\n✓ Income transaction found!")
    else:
        print("\n✗ Income transaction NOT found")
