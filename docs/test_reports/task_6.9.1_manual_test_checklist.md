# Manual Test Checklist: Transaction Creation (Task 6.9.1)

**Date:** _____________  **Tester:** _____________  **Browser:** _____________

**Test Credentials:** qa-test@finanpy.com / TestPass123!
**Base URL:** http://127.0.0.1:8000

---

## Quick Test Execution

### TEST 1: Create Income Transaction ✓ CRITICAL

- [ ] Login successful
- [ ] Navigate to /transacoes/nova/ - page loads without errors
- [ ] Select Type: "Receita"
- [ ] **VERIFY:** Category dropdown shows ONLY income categories
- [ ] Fill Amount: 1500.00
- [ ] Select Date: 2025-01-15
- [ ] Select Account: "Conta Corrente Itau"
- [ ] Select Category: "Salario"
- [ ] Description: "Salario de janeiro - teste E2E"
- [ ] Click "Criar Transacao"
- [ ] **VERIFY:** Redirect to list, success message shown
- [ ] **VERIFY:** Transaction appears with correct data

**Result:** PASS / FAIL
**Notes:** ___________________________________________

---

### TEST 2: Create Expense Transaction ✓ CRITICAL

- [ ] Navigate to /transacoes/nova/
- [ ] Select Type: "Despesa"
- [ ] **VERIFY:** Category dropdown shows ONLY expense categories
- [ ] Fill Amount: 250.50
- [ ] Select Date: 2025-01-16
- [ ] Select Account: "Carteira Pessoal"
- [ ] Select Category: "Alimentacao"
- [ ] Description: "Compras supermercado - teste E2E"
- [ ] Click "Criar Transacao"
- [ ] **VERIFY:** Success and transaction appears

**Result:** PASS / FAIL
**Notes:** ___________________________________________

---

### TEST 3: Verify Balance Updates ✓ CRITICAL

Navigate to /accounts/ and verify:

- [ ] Conta Corrente Itau: **R$ 4,000.00** (was 2,500 + 1,500 income)
- [ ] Carteira Pessoal: **R$ 100.25** (was 350.75 - 250.50 expense)
- [ ] Poupanca Nubank: **R$ 10,000.00** (unchanged)

**Result:** PASS / FAIL
**Actual Balances:** ___________________________________________

---

### TEST 4: Empty Fields Validation

- [ ] Open /transacoes/nova/
- [ ] Leave all fields empty
- [ ] Click submit
- [ ] **VERIFY:** Validation prevents submission OR shows error messages

**Result:** PASS / FAIL

---

### TEST 5: Future Date Validation ✓ IMPORTANT

- [ ] Open /transacoes/nova/
- [ ] Fill all fields correctly
- [ ] Set Date: 2027-06-01 (future)
- [ ] Click submit
- [ ] **VERIFY:** Error: "A data da transacao nao pode ser no futuro."

**Result:** PASS / FAIL

---

### TEST 6: Zero/Negative Amount Validation

- [ ] Open /transacoes/nova/
- [ ] Fill all fields, but Amount: 0
- [ ] Click submit
- [ ] **VERIFY:** Error: "O valor deve ser maior que zero."

**Result:** PASS / FAIL

---

### TEST 7: Category Type Mismatch (DevTools Required)

- [ ] Open /transacoes/nova/
- [ ] Select Type: "Receita"
- [ ] Open DevTools Console
- [ ] Execute: `document.getElementById('id_category').innerHTML = '<option value="1">Alimentacao</option>'; document.getElementById('id_category').value = '1';`
- [ ] Submit form
- [ ] **VERIFY:** Server error: "O tipo da categoria deve corresponder ao tipo da transacao."

**Result:** PASS / FAIL

---

### TEST 8: Transaction List Display

- [ ] Open /transacoes/
- [ ] **VERIFY:** Income transaction visible (green badge, green amount)
- [ ] **VERIFY:** Expense transaction visible (red badge, red amount)
- [ ] **VERIFY:** All data displayed correctly

**Result:** PASS / FAIL

---

### TEST 9: Responsive Design (DevTools Required)

Test at widths: 375px, 768px, 1280px

- [ ] Mobile (375px): Fields stack vertically, no scroll
- [ ] Tablet (768px): Two-column grid works
- [ ] Desktop (1280px): Layout optimal
- [ ] Dark theme consistent across all sizes

**Result:** PASS / FAIL

---

### TEST 10: JavaScript Functionality ✓ CRITICAL

- [ ] Open /transacoes/nova/
- [ ] Open DevTools Console
- [ ] **VERIFY:** No JavaScript errors
- [ ] Select Type "Receita" → categories filter instantly
- [ ] Select Type "Despesa" → categories filter instantly
- [ ] Type Amount "1234.56" → formats to "1.234,56" on blur
- [ ] Submit form → sends numeric value correctly

**Result:** PASS / FAIL

---

## Visual Checks (Quick Scan)

- [ ] Dark theme: slate-900 background, slate-800 cards
- [ ] Purple gradient on primary button
- [ ] Smooth transitions on hover
- [ ] Required fields marked with red asterisk (*)
- [ ] Error messages display with red icon
- [ ] Proper spacing and alignment

**Result:** PASS / FAIL

---

## Overall Test Result

**Total Tests:** 10
**Passed:** _____
**Failed:** _____
**Pass Rate:** _____%

**Critical Issues Found:**
___________________________________________
___________________________________________
___________________________________________

**Minor Issues Found:**
___________________________________________
___________________________________________
___________________________________________

**Recommendation:**
- [ ] READY FOR DEPLOYMENT
- [ ] NEEDS FIXES BEFORE DEPLOYMENT
- [ ] BLOCKER ISSUES FOUND

---

**Tester Signature:** _____________  **Date:** _____________

**Reviewed By:** _____________  **Date:** _____________
