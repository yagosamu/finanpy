/**
 * Transactions JavaScript Module
 *
 * Features:
 * - Dynamic category filtering by transaction type
 * - Currency mask for amount field
 * - Real-time form validation
 * - Delete confirmation modal
 */

(function() {
  'use strict';

  // ============================================================================
  // CATEGORY FILTER MODULE
  // ============================================================================

  const CategoryFilter = {
    typeSelect: null,
    categorySelect: null,
    categoriesData: [],

    /**
     * Initialize category filter
     */
    init() {
      this.typeSelect = document.getElementById('id_transaction_type');
      this.categorySelect = document.getElementById('id_category');

      if (!this.typeSelect || !this.categorySelect) return;

      // Parse categories data from data attribute
      const dataAttr = this.categorySelect.dataset.categories;
      if (dataAttr) {
        try {
          this.categoriesData = JSON.parse(dataAttr);
        } catch (e) {
          console.warn('Failed to parse categories data:', e);
          return;
        }
      }

      // Store original selected value
      this.selectedCategoryId = this.categorySelect.value;

      // Bind event listener
      this.typeSelect.addEventListener('change', () => {
        this.filterCategories();
      });

      // Apply initial filter
      this.filterCategories();
    },

    /**
     * Filter categories based on selected transaction type
     */
    filterCategories() {
      const selectedType = this.typeSelect.value;

      // Store current selection
      const currentValue = this.categorySelect.value;

      // Clear all options except the empty one
      while (this.categorySelect.options.length > 1) {
        this.categorySelect.remove(1);
      }

      // If no type selected, show all categories
      const filteredCategories = selectedType
        ? this.categoriesData.filter(c => c.type === selectedType)
        : this.categoriesData;

      // Add filtered categories
      filteredCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        option.dataset.color = category.color;
        option.dataset.type = category.type;
        this.categorySelect.appendChild(option);
      });

      // Restore selection if the category is still available
      const stillAvailable = filteredCategories.find(c => String(c.id) === String(currentValue));
      if (stillAvailable) {
        this.categorySelect.value = currentValue;
      } else if (this.selectedCategoryId) {
        // Try to restore initial value
        const initialAvailable = filteredCategories.find(c => String(c.id) === String(this.selectedCategoryId));
        if (initialAvailable) {
          this.categorySelect.value = this.selectedCategoryId;
          this.selectedCategoryId = null;
        }
      }
    }
  };

  // ============================================================================
  // CURRENCY MASK MODULE
  // ============================================================================

  const CurrencyMask = {
    input: null,

    /**
     * Initialize currency mask for amount field
     * @param {HTMLInputElement} input - Amount input element
     */
    init(input) {
      if (!input) return;
      this.input = input;

      // Change type to text for formatting
      input.type = 'text';
      input.removeAttribute('step');
      input.removeAttribute('min');
      input.placeholder = '0,00';
      input.classList.add('currency-input');

      // Format existing value
      if (input.value) {
        const num = parseFloat(input.value);
        if (!isNaN(num) && num > 0) {
          input.value = this.format(num);
        }
      }

      // Bind events
      input.addEventListener('input', (e) => this.handleInput(e));
      input.addEventListener('blur', (e) => this.handleBlur(e));

      // On form submit, convert back to numeric value
      const form = input.closest('form');
      if (form) {
        form.addEventListener('submit', () => {
          const parsed = this.parse(input.value);

          // Create hidden input with numeric value
          const hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = input.name;
          hiddenInput.value = parsed;

          // Disable formatted input so it doesn't submit
          input.disabled = true;

          // Add hidden input to form
          form.appendChild(hiddenInput);
        });
      }
    },

    /**
     * Format a number as Brazilian currency (without R$ symbol)
     * @param {number} value - Numeric value
     * @returns {string} Formatted string (e.g., "1.234,56")
     */
    format(value) {
      if (!value && value !== 0) return '';
      return value.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    },

    /**
     * Parse formatted string back to number
     * @param {string} value - Formatted string
     * @returns {number} Parsed number
     */
    parse(value) {
      if (!value) return 0;
      const cleaned = value.replace(/\./g, '').replace(',', '.');
      const num = parseFloat(cleaned);
      return isNaN(num) ? 0 : num;
    },

    /**
     * Handle input event - apply mask
     * @param {Event} e - Input event
     */
    handleInput(e) {
      const cursorPosition = e.target.selectionStart;
      const oldValue = e.target.value;

      // Remove all non-digit characters except comma
      let value = oldValue.replace(/[^\d,]/g, '');

      // Ensure only one comma
      const parts = value.split(',');
      if (parts.length > 2) {
        value = parts[0] + ',' + parts.slice(1).join('');
      }

      // Limit to 2 decimal places
      if (parts[1] && parts[1].length > 2) {
        value = parts[0] + ',' + parts[1].substring(0, 2);
      }

      // Format with thousand separators
      if (value) {
        const [integerPart, decimalPart] = value.split(',');
        const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        value = decimalPart !== undefined ? `${formattedInteger},${decimalPart}` : formattedInteger;
      }

      e.target.value = value;

      // Restore cursor position
      const newCursorPosition = cursorPosition + (value.length - oldValue.length);
      e.target.setSelectionRange(newCursorPosition, newCursorPosition);
    },

    /**
     * Handle blur event - format with 2 decimal places
     * @param {Event} e - Blur event
     */
    handleBlur(e) {
      const value = e.target.value;
      if (value) {
        const num = this.parse(value);
        if (num > 0) {
          e.target.value = this.format(num);
        }
      }
    }
  };

  // ============================================================================
  // TRANSACTION FORM VALIDATOR
  // ============================================================================

  const TransactionFormValidator = {
    /**
     * Initialize form validation
     * @param {HTMLFormElement} form - Form element
     */
    init(form) {
      if (!form) return;

      const typeField = form.querySelector('#id_transaction_type');
      const amountField = form.querySelector('#id_amount');
      const dateField = form.querySelector('#id_date');
      const accountField = form.querySelector('#id_account');
      const categoryField = form.querySelector('#id_category');

      // Validate on blur
      if (amountField) {
        amountField.addEventListener('blur', () => this.validateAmount(amountField));
        amountField.addEventListener('input', () => this.clearError(amountField));
      }

      if (dateField) {
        dateField.addEventListener('blur', () => this.validateDate(dateField));
        dateField.addEventListener('change', () => this.clearError(dateField));
      }

      // Form submit validation
      form.addEventListener('submit', (e) => {
        let isValid = true;

        if (typeField && !typeField.value) {
          this.showError(typeField, 'Selecione o tipo da transação.');
          isValid = false;
        }

        if (amountField && !this.validateAmount(amountField)) {
          isValid = false;
        }

        if (dateField && !this.validateDate(dateField)) {
          isValid = false;
        }

        if (accountField && !accountField.value) {
          this.showError(accountField, 'Selecione uma conta.');
          isValid = false;
        }

        if (categoryField && !categoryField.value) {
          this.showError(categoryField, 'Selecione uma categoria.');
          isValid = false;
        }

        if (!isValid) {
          e.preventDefault();
        }
      });
    },

    /**
     * Validate amount field
     * @param {HTMLInputElement} field - Amount field
     * @returns {boolean} True if valid
     */
    validateAmount(field) {
      const value = field.classList.contains('currency-input')
        ? CurrencyMask.parse(field.value)
        : parseFloat(field.value);

      if (!field.value.trim()) {
        this.showError(field, 'O valor é obrigatório.');
        return false;
      }

      if (isNaN(value) || value <= 0) {
        this.showError(field, 'O valor deve ser maior que zero.');
        return false;
      }

      if (value > 99999999.99) {
        this.showError(field, 'O valor não pode ser maior que R$ 99.999.999,99.');
        return false;
      }

      this.showSuccess(field);
      return true;
    },

    /**
     * Validate date field
     * @param {HTMLInputElement} field - Date field
     * @returns {boolean} True if valid
     */
    validateDate(field) {
      if (!field.value) {
        this.showError(field, 'A data é obrigatória.');
        return false;
      }

      const selectedDate = new Date(field.value + 'T00:00:00');
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (selectedDate > today) {
        this.showError(field, 'A data não pode ser no futuro.');
        return false;
      }

      this.showSuccess(field);
      return true;
    },

    /**
     * Show success state for a field
     * @param {HTMLElement} field - Field element
     */
    showSuccess(field) {
      this.clearError(field);
      field.classList.add('border-green-500');
    },

    /**
     * Show error message for a field
     * @param {HTMLElement} field - Field element
     * @param {string} message - Error message
     */
    showError(field, message) {
      this.clearError(field);
      field.classList.add('border-red-500');

      const errorDiv = document.createElement('div');
      errorDiv.className = 'field-error mt-2';
      errorDiv.innerHTML = `
        <p class="text-sm text-red-400 flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          ${message}
        </p>
      `;

      const container = field.closest('.relative') || field.parentElement;
      container.appendChild(errorDiv);
    },

    /**
     * Clear error message for a field
     * @param {HTMLElement} field - Field element
     */
    clearError(field) {
      field.classList.remove('border-red-500', 'border-green-500');

      const container = field.closest('.relative') || field.parentElement;
      const errorDiv = container.querySelector('.field-error');
      if (errorDiv) {
        errorDiv.remove();
      }
    }
  };

  // ============================================================================
  // DELETE CONFIRMATION FOR TRANSACTIONS
  // ============================================================================

  const TransactionDeleteModal = {
    modal: null,

    /**
     * Initialize the delete confirmation modal
     */
    init() {
      if (this.modal) return;

      this.modal = document.createElement('div');
      this.modal.id = 'transaction-delete-modal';
      this.modal.className = 'fixed inset-0 z-50 hidden';
      this.modal.innerHTML = `
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity" onclick="TransactionDeleteModal.close()"></div>

        <!-- Modal Content -->
        <div class="fixed inset-0 flex items-center justify-center p-4">
          <div class="bg-slate-800 rounded-xl shadow-2xl border border-red-600/30 max-w-md w-full transform transition-all scale-95 opacity-0" id="transaction-delete-modal-content">
            <!-- Icon -->
            <div class="flex items-center justify-center w-16 h-16 mx-auto mt-8 bg-red-900/30 rounded-full">
              <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </div>

            <!-- Content -->
            <div class="p-8 text-center">
              <h3 class="text-2xl font-bold text-slate-100 mb-3">Excluir Transação</h3>
              <p class="text-slate-300 mb-2" id="transaction-delete-modal-message">
                Tem certeza que deseja excluir esta transação?
              </p>
              <p class="text-slate-400 text-sm">
                O saldo da conta será ajustado automaticamente.
              </p>
            </div>

            <!-- Actions -->
            <div class="flex gap-3 px-8 pb-8">
              <button type="button"
                      onclick="TransactionDeleteModal.close()"
                      class="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium rounded-lg border border-slate-600 transition-all duration-200">
                Cancelar
              </button>
              <button type="button"
                      id="transaction-delete-modal-confirm"
                      class="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all duration-200">
                Excluir
              </button>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(this.modal);

      // Add keyboard event listener
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
          this.close();
        }
      });
    },

    /**
     * Show the delete confirmation modal
     * @param {string} description - Description of transaction being deleted
     * @param {Function} onConfirm - Callback function when confirmed
     */
    show(description, onConfirm) {
      this.init();

      // Update message
      const messageEl = document.getElementById('transaction-delete-modal-message');
      if (messageEl && description) {
        messageEl.textContent = `Tem certeza que deseja excluir "${description}"?`;
      }

      // Set confirm action
      const confirmBtn = document.getElementById('transaction-delete-modal-confirm');
      const newConfirmBtn = confirmBtn.cloneNode(true);
      confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

      newConfirmBtn.addEventListener('click', () => {
        if (onConfirm) onConfirm();
        this.close();
      });

      // Show modal
      this.modal.classList.remove('hidden');
      setTimeout(() => {
        const content = document.getElementById('transaction-delete-modal-content');
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
      }, 10);
    },

    /**
     * Close the modal
     */
    close() {
      const content = document.getElementById('transaction-delete-modal-content');
      if (content) {
        content.classList.add('scale-95', 'opacity-0');
        content.classList.remove('scale-100', 'opacity-100');
      }

      setTimeout(() => {
        if (this.modal) {
          this.modal.classList.add('hidden');
        }
      }, 200);
    }
  };

  // ============================================================================
  // CURRENCY DISPLAY MODULE
  // ============================================================================

  const CurrencyDisplay = {
    /**
     * Format a numeric value as Brazilian Real currency
     * @param {number} value - Numeric value
     * @returns {string} Formatted string (e.g., "1.234,56")
     */
    format(value) {
      if (!value && value !== 0) return '0,00';
      const num = typeof value === 'string' ? parseFloat(value) : value;
      if (isNaN(num)) return '0,00';
      return num.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    },

    /**
     * Apply Brazilian currency formatting to all elements with data-currency attribute
     * Elements should have data-currency="1234.56" with the raw numeric value
     */
    init() {
      const elements = document.querySelectorAll('[data-currency]');
      elements.forEach(el => {
        const rawValue = parseFloat(el.dataset.currency);
        if (!isNaN(rawValue)) {
          const prefix = el.dataset.currencyPrefix || '';
          el.textContent = prefix + 'R$ ' + this.format(rawValue);
        }
      });
    }
  };

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  document.addEventListener('DOMContentLoaded', () => {
    // Initialize category filter
    CategoryFilter.init();

    // Initialize currency mask for amount field
    const amountInput = document.getElementById('id_amount');
    if (amountInput) {
      CurrencyMask.init(amountInput);
    }

    // Initialize form validation
    const transactionForm = document.querySelector('form[method="post"]');
    if (transactionForm) {
      TransactionFormValidator.init(transactionForm);
    }

    // Initialize currency display formatting
    CurrencyDisplay.init();

    // Initialize delete modals for transaction links
    const deleteLinks = document.querySelectorAll('a[href*="/excluir/"]');
    deleteLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();

        const row = link.closest('tr') || link.closest('[data-transaction]');
        const description = row?.querySelector('.transaction-description')?.textContent || 'esta transação';

        TransactionDeleteModal.show(
          description.trim(),
          () => {
            window.location.href = link.href;
          }
        );
      });
    });
  });

  // Make modules globally accessible
  window.CategoryFilter = CategoryFilter;
  window.CurrencyMask = CurrencyMask;
  window.CurrencyDisplay = CurrencyDisplay;
  window.TransactionFormValidator = TransactionFormValidator;
  window.TransactionDeleteModal = TransactionDeleteModal;

})();
