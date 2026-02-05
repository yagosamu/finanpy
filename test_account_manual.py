"""
Manual test to inspect the accounts page HTML
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=500)
    context = await browser.new_context(viewport={'width': 1280, 'height': 720})
    page = await context.new_page()

    # Login
    await page.goto('http://localhost:8000/usuarios/login/')
    await page.fill('input[name="username"]', 'qa-test@finanpy.com')
    await page.fill('input[name="password"]', 'QaTest@2024!')
    await page.click('button[type="submit"]')
    await page.wait_for_load_state('networkidle')

    # Navigate to accounts
    await page.goto('http://localhost:8000/accounts/')
    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(2000)  # Wait extra time

    # Save HTML
    html = await page.content()
    with open('accounts_page.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("HTML saved to accounts_page.html")

    # Take screenshot
    await page.screenshot(path='accounts_page_full.png', full_page=True)
    print("Screenshot saved to accounts_page_full.png")

    # Try to find elements
    print("\nLooking for elements...")

    # Check for h1
    h1 = await page.query_selector('h1')
    if h1:
        h1_text = await h1.text_content()
        print(f"H1 found: {h1_text}")

    # Check for account cards with different selectors
    cards1 = await page.query_selector_all('div.bg-slate-800')
    print(f"Cards with 'div.bg-slate-800': {len(cards1)}")

    cards2 = await page.query_selector_all('[class*="bg-slate-800"]')
    print(f"Cards with '[class*=\"bg-slate-800\"]': {len(cards2)}")

    # Check all divs
    all_divs = await page.query_selector_all('div')
    print(f"Total divs on page: {len(all_divs)}")

    # Look for text content
    body_text = await page.text_content('body')
    if 'Conta Corrente BB' in body_text:
        print("✓ Found 'Conta Corrente BB' in page")
    else:
        print("✗ 'Conta Corrente BB' NOT found in page")

    if 'Nenhuma conta cadastrada' in body_text:
        print("! Empty state message found")

    # Wait before closing
    await page.wait_for_timeout(5000)

    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
