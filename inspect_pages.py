"""
Script to inspect page HTML for debugging
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
print("=== LOGGING IN ===\n")
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
print(f"Login status: {response.status_code}")
print(f"Redirected to: {response.url}\n")

# Check dashboard
print("=== DASHBOARD PAGE ===\n")
response = session.get(f'{base_url}/dashboard/')
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:", soup.find('title').text if soup.find('title') else 'No title')
print("\nAll text content with 'R$':")
text = soup.get_text()
lines = [line.strip() for line in text.split('\n') if 'R$' in line and line.strip()]
for line in lines[:20]:
    print(f"  {line}")

print("\n\nAll div elements with currency-like classes:")
for div in soup.find_all('div', class_=lambda x: x and ('text-' in x or 'font-' in x)):
    if 'R$' in div.get_text():
        print(f"  Class: {div.get('class')} | Text: {div.get_text(strip=True)[:80]}")

# Check transaction form
print("\n\n=== TRANSACTION FORM PAGE ===\n")
response = session.get(f'{base_url}/transacoes/nova/')
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:", soup.find('title').text if soup.find('title') else 'No title')

# Find all select elements
selects = soup.find_all('select')
print(f"\nFound {len(selects)} select elements:")
for select in selects:
    name = select.get('name', 'unnamed')
    print(f"\n  Select name: {name}")
    options = select.find_all('option')
    print(f"  Options count: {len(options)}")
    for opt in options[:5]:
        print(f"    - value='{opt.get('value')}' : {opt.get_text(strip=True)}")

# Check account list
print("\n\n=== ACCOUNTS PAGE ===\n")
response = session.get(f'{base_url}/accounts/')
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:", soup.find('title').text if soup.find('title') else 'No title')
print("\nAccounts found:")
# Look for account cards or list items
cards = soup.find_all(['div', 'li', 'tr'], class_=lambda x: x and ('card' in str(x).lower() or 'account' in str(x).lower()))
for card in cards[:5]:
    print(f"  {card.get_text(strip=True)[:100]}")

print("\n\nLooking for any text with 'Conta':")
lines = [line.strip() for line in soup.get_text().split('\n') if 'conta' in line.lower() and line.strip()]
for line in lines[:10]:
    print(f"  {line}")
