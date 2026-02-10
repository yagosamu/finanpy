"""
Verify transactions were actually created in database
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

response = session.post(f'{base_url}/usuarios/login/', data=data, allow_redirects=True)
print(f"Login status: {response.status_code}\n")

# Check transactions list page
print("=== TRANSACTIONS LIST PAGE ===\n")
response = session.get(f'{base_url}/transacoes/')
soup = BeautifulSoup(response.text, 'html.parser')

print("Page title:", soup.find('title').text if soup.find('title') else 'No title')

# Look for transaction rows
table = soup.find('table')
if table:
    rows = table.find_all('tr')
    print(f"\nFound {len(rows)} rows in table (including header)")

    for idx, row in enumerate(rows):
        cols = row.find_all(['td', 'th'])
        if cols:
            row_text = ' | '.join([col.get_text(strip=True) for col in cols])
            print(f"  Row {idx}: {row_text[:150]}")
else:
    print("\nNo table found")

    # Look for "Nenhuma transação"
    if 'nenhuma transação' in soup.get_text().lower():
        print("✗ 'Nenhuma transação' message found - no transactions in database")
    else:
        print("? Could not determine transaction status")

# Check raw dashboard HTML for recent_transactions
print("\n\n=== RAW DASHBOARD DATA ===\n")
response = session.get(f'{base_url}/dashboard/')
soup = BeautifulSoup(response.text, 'html.parser')

# Find the recent transactions section
recent_section = soup.find('h2', string='Transações Recentes')
if recent_section:
    parent = recent_section.find_parent('div', class_=lambda x: x and 'bg-slate-800' in x)
    if parent:
        print("Recent transactions section found")

        # Check if empty state is shown
        empty_state = parent.find('div', class_=lambda x: x and 'text-center' in x and 'py-12' in x)
        if empty_state and 'Nenhuma transação cadastrada' in empty_state.get_text():
            print("✗ Empty state shown - recent_transactions is empty/None")
        else:
            # Look for transaction items
            transaction_divs = parent.find_all('div', class_=lambda x: x and 'flex items-center justify-between' in x)
            print(f"✓ Found {len(transaction_divs)} transaction items")

            for idx, div in enumerate(transaction_divs[:3], 1):
                text = div.get_text(strip=True)
                print(f"  Transaction {idx}: {text[:100]}...")
else:
    print("Recent transactions section not found in template")
