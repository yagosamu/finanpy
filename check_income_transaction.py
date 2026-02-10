"""
Check why income transaction is missing
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

# Get transactions list and look for both
print("=== ALL TRANSACTIONS ===\n")
response = session.get(f'{base_url}/transacoes/')
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
if table:
    rows = table.find_all('tr')[1:]  # Skip header
    print(f"Total transactions: {len(rows)}\n")

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            date = cols[0].get_text(strip=True)
            desc = cols[1].get_text(strip=True)
            category = cols[2].get_text(strip=True)
            account = cols[3].get_text(strip=True)
            amount = cols[4].get_text(strip=True)

            print(f"Date: {date}")
            print(f"Description: {desc}")
            print(f"Category: {category}")
            print(f"Account: {account}")
            print(f"Amount: {amount}")
            print()

# Try filtering by type
print("\n=== FILTERING BY INCOME TYPE ===\n")
response = session.get(f'{base_url}/transacoes/?transaction_type=income')
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
if table:
    rows = table.find_all('tr')[1:]
    print(f"Income transactions: {len(rows)}")

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            desc = cols[1].get_text(strip=True)
            amount = cols[4].get_text(strip=True) if len(cols) >= 5 else 'N/A'
            print(f"  - {desc}: {amount}")
else:
    text = soup.get_text()
    if 'nenhuma transação' in text.lower():
        print("✗ No income transactions found")

print("\n=== FILTERING BY EXPENSE TYPE ===\n")
response = session.get(f'{base_url}/transacoes/?transaction_type=expense')
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
if table:
    rows = table.find_all('tr')[1:]
    print(f"Expense transactions: {len(rows)}")

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            desc = cols[1].get_text(strip=True)
            amount = cols[4].get_text(strip=True) if len(cols) >= 5 else 'N/A'
            print(f"  - {desc}: {amount}")
