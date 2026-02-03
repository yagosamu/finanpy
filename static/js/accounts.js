/**
 * Accounts JavaScript Module
 *
 * Features:
 * - Delete confirmation modal
 * - Real-time form validation
 * - Brazilian currency formatting
 * - Loading states for buttons
 * - Toast notification system
 */

(function() {
  'use strict';

  // ============================================================================
  // TOAST NOTIFICATION SYSTEM
  // ============================================================================

  const Toast = {
    container: null,

    /**
     * Initialize toast container
     */
    init() {
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'fixed top-4 right-4 z-50 space-y-3 max-w-sm';
        document.body.appendChild(this.container);
      }
    },

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (default: 5000)
     */
    show(message, type = 'info', duration = 5000) {
      this.init();

      // Define colors based on type
      const colors = {
        success: {
          bg: 'bg-green-900/95',
          border: 'border-green-700',
          text: 'text-green-100',
          icon: 'text-green-400',
          iconPath: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        },
        error: {
          bg: 'bg-red-900/95',
          border: 'border-red-700',
          text: 'text-red-100',
          icon: 'text-red-400',
          iconPath: 'M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        },
        warning: {
          bg: 'bg-yellow-900/95',
          border: 'border-yellow-700',
          text: 'text-yellow-100',
          icon: 'text-yellow-400',
          iconPath: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z'
        },
        info: {
          bg: 'bg-blue-900/95',
          border: 'border-blue-700',
          text: 'text-blue-100',
          icon: 'text-blue-400',
          iconPath: 'M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z'
        }
      };

      const color = colors[type] || colors.info;

      // Create toast element
      const toast = document.createElement('div');
      toast.className = `${color.bg} border ${color.border} rounded-lg shadow-2xl p-4 flex items-start transform transition-all duration-300 ease-out translate-x-full opacity-0`;
      toast.innerHTML = `
        <svg class="w-6 h-6 ${color.icon} mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="${color.iconPath}" />
        </svg>
        <p class="${color.text} flex-1 text-sm font-medium">${message}</p>
        <button class="ml-3 ${color.text} hover:opacity-75 transition-opacity" onclick="this.parentElement.remove()">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      `;

      this.container.appendChild(toast);

      // Animate in
      setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
      }, 10);

      // Auto-dismiss
      if (duration > 0) {
        setTimeout(() => {
          this.dismiss(toast);
        }, duration);
      }

      return toast;
    },

    /**
     * Dismiss a toast
     * @param {HTMLElement} toast - Toast element to dismiss
     */
    dismiss(toast) {
      toast.classList.add('translate-x-full', 'opacity-0');
      setTimeout(() => {
        if (toast.parentElement) {
          toast.parentElement.removeChild(toast);
        }
      }, 300);
    },

    success(message, duration = 5000) {
      return this.show(message, 'success', duration);
    },

    error(message, duration = 5000) {
      return this.show(message, 'error', duration);
    },

    warning(message, duration = 5000) {
      return this.show(message, 'warning', duration);
    },

    info(message, duration = 5000) {
      return this.show(message, 'info', duration);
    }
  };

  // ============================================================================
  // DELETE CONFIRMATION MODAL
  // ============================================================================

  const DeleteModal = {
    modal: null,

    /**
     * Initialize the delete confirmation modal
     */
    init() {
      if (this.modal) return;

      // Create modal HTML
      this.modal = document.createElement('div');
      this.modal.id = 'delete-modal';
      this.modal.className = 'fixed inset-0 z-50 hidden';
      this.modal.innerHTML = `
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity" onclick="DeleteModal.close()"></div>

        <!-- Modal Content -->
        <div class="fixed inset-0 flex items-center justify-center p-4">
          <div class="bg-slate-800 rounded-xl shadow-2xl border border-red-600/30 max-w-md w-full transform transition-all scale-95 opacity-0" id="delete-modal-content">
            <!-- Icon -->
            <div class="flex items-center justify-center w-16 h-16 mx-auto mt-8 bg-red-900/30 rounded-full">
              <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>

            <!-- Content -->
            <div class="p-8 text-center">
              <h3 class="text-2xl font-bold text-slate-100 mb-3">Confirmar Exclusão</h3>
              <p class="text-slate-300 mb-2" id="delete-modal-message">
                Tem certeza que deseja excluir esta conta?
              </p>
              <p class="text-slate-400 text-sm">
                Esta ação não pode ser desfeita.
              </p>
            </div>

            <!-- Actions -->
            <div class="flex gap-3 px-8 pb-8">
              <button type="button"
                      onclick="DeleteModal.close()"
                      class="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium rounded-lg border border-slate-600 transition-all duration-200">
                Cancelar
              </button>
              <button type="button"
                      id="delete-modal-confirm"
                      class="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all duration-200">
                Confirmar Exclusão
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
     * @param {string} message - Custom message to display
     * @param {Function} onConfirm - Callback function when confirmed
     */
    show(message, onConfirm) {
      this.init();

      // Update message
      if (message) {
        document.getElementById('delete-modal-message').textContent = message;
      }

      // Set confirm action
      const confirmBtn = document.getElementById('delete-modal-confirm');
      const newConfirmBtn = confirmBtn.cloneNode(true);
      confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

      newConfirmBtn.addEventListener('click', () => {
        if (onConfirm) onConfirm();
        this.close();
      });

      // Show modal
      this.modal.classList.remove('hidden');
      setTimeout(() => {
        const content = document.getElementById('delete-modal-content');
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
      }, 10);
    },

    /**
     * Close the modal
     */
    close() {
      const content = document.getElementById('delete-modal-content');
      content.classList.add('scale-95', 'opacity-0');
      content.classList.remove('scale-100', 'opacity-100');

      setTimeout(() => {
        this.modal.classList.add('hidden');
      }, 200);
    }
  };

  // ============================================================================
  // CURRENCY FORMATTER
  // ============================================================================

  const CurrencyFormatter = {
    /**
     * Format value as Brazilian currency
     * @param {number|string} value - Value to format
     * @returns {string} Formatted value (e.g., "1.234,56")
     */
    format(value) {
      if (!value && value !== 0) return '';

      // Convert to number if string
      const num = typeof value === 'string' ? parseFloat(value.replace(/\./g, '').replace(',', '.')) : value;

      if (isNaN(num)) return '';

      // Format with Brazilian locale
      return num.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    },

    /**
     * Parse formatted value back to number
     * @param {string} value - Formatted value (e.g., "1.234,56")
     * @returns {number} Parsed number
     */
    parse(value) {
      if (!value) return 0;

      // Remove thousand separators and replace comma with dot
      const cleaned = value.replace(/\./g, '').replace(',', '.');
      const num = parseFloat(cleaned);

      return isNaN(num) ? 0 : num;
    },

    /**
     * Apply formatting to an input field
     * @param {HTMLInputElement} input - Input element to format
     */
    applyToInput(input) {
      if (!input) return;

      // Store original type if it's number
      const originalType = input.type;

      // Change type to text for formatting
      if (originalType === 'number') {
        input.type = 'text';
      }

      // Format on input
      input.addEventListener('input', (e) => {
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
      });

      // Format initial value
      if (input.value) {
        const num = parseFloat(input.value);
        if (!isNaN(num)) {
          input.value = this.format(num);
        }
      }

      // Parse on form submit
      const form = input.closest('form');
      if (form) {
        form.addEventListener('submit', (e) => {
          const parsed = this.parse(input.value);

          // Create hidden input with numeric value
          const hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = input.name;
          hiddenInput.value = parsed;

          // Disable formatted input
          input.disabled = true;

          // Add hidden input to form
          form.appendChild(hiddenInput);
        });
      }
    }
  };

  // ============================================================================
  // FORM VALIDATION
  // ============================================================================

  const FormValidator = {
    /**
     * Initialize form validation
     * @param {HTMLFormElement} form - Form element to validate
     */
    init(form) {
      if (!form) return;

      const requiredFields = form.querySelectorAll('[required]');
      const submitBtn = form.querySelector('button[type="submit"]');

      // Validate each required field
      requiredFields.forEach(field => {
        // Add blur event for validation
        field.addEventListener('blur', () => {
          this.validateField(field);
        });

        // Add input event to clear errors while typing
        field.addEventListener('input', () => {
          this.clearError(field);
          this.updateSubmitButton(form, submitBtn);
        });
      });

      // Validate on submit
      form.addEventListener('submit', (e) => {
        let isValid = true;

        requiredFields.forEach(field => {
          if (!this.validateField(field)) {
            isValid = false;
          }
        });

        if (!isValid) {
          e.preventDefault();
          Toast.error('Por favor, corrija os erros no formulário.');
        }
      });

      // Initial validation
      this.updateSubmitButton(form, submitBtn);
    },

    /**
     * Validate a single field
     * @param {HTMLInputElement|HTMLSelectElement} field - Field to validate
     * @returns {boolean} True if valid
     */
    validateField(field) {
      const value = field.value.trim();
      let errorMessage = '';

      // Check if required field is empty
      if (field.hasAttribute('required') && !value) {
        errorMessage = 'Este campo é obrigatório.';
      }

      // Validate select fields
      else if (field.tagName === 'SELECT' && value === '') {
        errorMessage = 'Por favor, selecione uma opção.';
      }

      // Validate number fields
      else if (field.type === 'number' || field.classList.contains('currency-input')) {
        const num = field.type === 'number' ? parseFloat(value) : CurrencyFormatter.parse(value);
        if (isNaN(num)) {
          errorMessage = 'Por favor, insira um valor válido.';
        }
      }

      // Validate min length
      else if (field.minLength && value.length < field.minLength) {
        errorMessage = `Mínimo de ${field.minLength} caracteres.`;
      }

      // Validate max length
      else if (field.maxLength && value.length > field.maxLength) {
        errorMessage = `Máximo de ${field.maxLength} caracteres.`;
      }

      if (errorMessage) {
        this.showError(field, errorMessage);
        return false;
      } else {
        this.clearError(field);
        return true;
      }
    },

    /**
     * Show error message for a field
     * @param {HTMLElement} field - Field element
     * @param {string} message - Error message
     */
    showError(field, message) {
      // Add error styling to field
      field.classList.remove('border-slate-700', 'focus:ring-primary-600');
      field.classList.add('border-red-500', 'focus:ring-red-500');

      // Remove existing error message
      this.clearError(field);

      // Create error message element
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

      // Insert after field or field container
      const container = field.closest('.relative') || field.parentElement;
      container.appendChild(errorDiv);
    },

    /**
     * Clear error message for a field
     * @param {HTMLElement} field - Field element
     */
    clearError(field) {
      // Remove error styling
      field.classList.remove('border-red-500', 'focus:ring-red-500');
      field.classList.add('border-slate-700', 'focus:ring-primary-600');

      // Remove error message
      const container = field.closest('.relative') || field.parentElement;
      const errorDiv = container.querySelector('.field-error');
      if (errorDiv) {
        errorDiv.remove();
      }
    },

    /**
     * Update submit button state based on form validity
     * @param {HTMLFormElement} form - Form element
     * @param {HTMLButtonElement} submitBtn - Submit button
     */
    updateSubmitButton(form, submitBtn) {
      if (!submitBtn) return;

      const requiredFields = form.querySelectorAll('[required]');
      let allValid = true;

      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          allValid = false;
        }
      });

      if (allValid) {
        submitBtn.disabled = false;
        submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      } else {
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      }
    }
  };

  // ============================================================================
  // LOADING STATE
  // ============================================================================

  const LoadingState = {
    /**
     * Add loading state to a button
     * @param {HTMLButtonElement} button - Button element
     */
    show(button) {
      if (!button) return;

      // Store original content
      button.dataset.originalContent = button.innerHTML;

      // Disable button
      button.disabled = true;
      button.classList.add('opacity-75', 'cursor-not-allowed');

      // Add loading spinner
      button.innerHTML = `
        <svg class="animate-spin h-5 w-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Salvando...
      `;
    },

    /**
     * Remove loading state from a button
     * @param {HTMLButtonElement} button - Button element
     */
    hide(button) {
      if (!button) return;

      // Restore original content
      if (button.dataset.originalContent) {
        button.innerHTML = button.dataset.originalContent;
        delete button.dataset.originalContent;
      }

      // Enable button
      button.disabled = false;
      button.classList.remove('opacity-75', 'cursor-not-allowed');
    }
  };

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  document.addEventListener('DOMContentLoaded', () => {
    // Initialize delete modal for account cards
    const deleteLinks = document.querySelectorAll('a[href*="/delete/"]');
    deleteLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();

        const accountName = link.closest('.bg-slate-800')?.querySelector('.text-xl.font-bold')?.textContent || 'esta conta';

        DeleteModal.show(
          `Tem certeza que deseja excluir "${accountName}"?`,
          () => {
            window.location.href = link.href;
          }
        );
      });
    });

    // Initialize form validation
    const accountForm = document.querySelector('form[method="post"]');
    if (accountForm) {
      FormValidator.init(accountForm);

      // Add loading state to submit button
      accountForm.addEventListener('submit', (e) => {
        const submitBtn = accountForm.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
          LoadingState.show(submitBtn);
        }
      });
    }

    // Initialize currency formatting for initial balance field
    const balanceInput = document.querySelector('#id_initial_balance');
    if (balanceInput) {
      balanceInput.classList.add('currency-input');
      CurrencyFormatter.applyToInput(balanceInput);
    }

    // Show success messages from Django
    const messages = document.querySelectorAll('.alert-success, .bg-green-900\\/30');
    messages.forEach(msg => {
      const text = msg.textContent.trim();
      if (text) {
        Toast.success(text);
        msg.style.display = 'none';
      }
    });

    // Show error messages from Django
    const errors = document.querySelectorAll('.alert-error, .bg-red-900\\/30');
    errors.forEach(err => {
      const text = err.textContent.trim();
      if (text && !err.closest('form')) {
        Toast.error(text);
        err.style.display = 'none';
      }
    });
  });

  // Make modules globally accessible for inline event handlers
  window.DeleteModal = DeleteModal;
  window.Toast = Toast;
  window.CurrencyFormatter = CurrencyFormatter;
  window.FormValidator = FormValidator;
  window.LoadingState = LoadingState;

})();
