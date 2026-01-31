from bs4 import BeautifulSoup

html = open('signup_page.html', 'r', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
form = soup.find('form')

print('=' * 80)
print('SIGNUP FORM STRUCTURE ANALYSIS')
print('=' * 80)
print()
print(f'Form action: {form.get("action")}')
print(f'Form method: {form.get("method")}')
print()
print('Form fields:')
for inp in form.find_all('input'):
    inp_type = inp.get('type', 'text')
    inp_name = inp.get('name', 'N/A')
    inp_placeholder = inp.get('placeholder', '')
    print(f'  - {inp_type:15s} name="{inp_name}" placeholder="{inp_placeholder}"')
print()
print('Buttons:')
for btn in form.find_all('button'):
    print(f'  - {btn.get("type")} button: "{btn.text.strip()}"')
print()
print('Links:')
for link in form.parent.find_all('a'):
    href = link.get('href', '')
    text = link.text.strip()
    if text and len(text) < 50:
        print(f'  - "{text}" -> {href}')
