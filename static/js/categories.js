/**
 * Categories JavaScript Module
 *
 * Features:
 * - Color picker with real-time preview
 * - Suggested color palette
 * - Delete confirmation modal
 * - Form validation
 */

(function() {
  'use strict';

  // ============================================================================
  // COLOR PICKER MODULE
  // ============================================================================

  const ColorPicker = {
    colorInput: null,
    previewElement: null,
    paletteContainer: null,
    suggestedColors: [],

    /**
     * Initialize the color picker
     * @param {HTMLInputElement} input - Color input element
     */
    init(input) {
      if (!input) return;

      this.colorInput = input;

      // Get suggested colors from data attribute
      const suggestedData = input.dataset.suggestedColors;
      if (suggestedData) {
        try {
          this.suggestedColors = JSON.parse(suggestedData);
        } catch (e) {
          console.warn('Failed to parse suggested colors:', e);
          this.suggestedColors = [];
        }
      }

      // Create preview element
      this.createPreview();

      // Create color palette
      this.createPalette();

      // Add event listeners
      this.addEventListeners();

      // Set initial preview
      this.updatePreview();
    },

    /**
     * Create the color preview element
     */
    createPreview() {
      const wrapper = this.colorInput.closest('.color-picker-wrapper') || this.colorInput.parentElement;

      // Create preview container
      const previewContainer = document.createElement('div');
      previewContainer.className = 'flex items-center gap-3 mt-2';

      // Create preview box
      this.previewElement = document.createElement('div');
      this.previewElement.className = 'w-10 h-10 rounded-lg border-2 border-slate-600 shadow-inner';
      this.previewElement.style.backgroundColor = this.colorInput.value || '#3B82F6';

      // Create color code display
      const colorCode = document.createElement('span');
      colorCode.className = 'color-code text-slate-300 font-mono text-sm';
      colorCode.textContent = this.colorInput.value || '#3B82F6';

      previewContainer.appendChild(this.previewElement);
      previewContainer.appendChild(colorCode);

      // Insert after input
      this.colorInput.parentElement.appendChild(previewContainer);
    },

    /**
     * Create the suggested colors palette
     */
    createPalette() {
      if (this.suggestedColors.length === 0) return;

      const wrapper = this.colorInput.closest('.color-picker-wrapper') || this.colorInput.parentElement;

      // Create palette container
      this.paletteContainer = document.createElement('div');
      this.paletteContainer.className = 'mt-3';

      // Create palette label
      const label = document.createElement('p');
      label.className = 'text-sm text-slate-400 mb-2';
      label.textContent = 'Cores sugeridas:';

      // Create color grid
      const colorGrid = document.createElement('div');
      colorGrid.className = 'flex flex-wrap gap-2';

      // Add color buttons
      this.suggestedColors.forEach(color => {
        const colorBtn = document.createElement('button');
        colorBtn.type = 'button';
        colorBtn.className = 'w-8 h-8 rounded-lg border-2 border-slate-600 hover:border-slate-400 transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-slate-800';
        colorBtn.style.backgroundColor = color;
        colorBtn.title = color;
        colorBtn.dataset.color = color;

        colorBtn.addEventListener('click', () => {
          this.selectColor(color);
        });

        colorGrid.appendChild(colorBtn);
      });

      this.paletteContainer.appendChild(label);
      this.paletteContainer.appendChild(colorGrid);
      wrapper.appendChild(this.paletteContainer);
    },

    /**
     * Add event listeners to color input
     */
    addEventListeners() {
      // Update preview on input change
      this.colorInput.addEventListener('input', () => {
        this.updatePreview();
      });

      // Also handle change event for text input fallback
      this.colorInput.addEventListener('change', () => {
        this.updatePreview();
      });
    },

    /**
     * Update the preview with current color
     */
    updatePreview() {
      const color = this.colorInput.value || '#3B82F6';

      if (this.previewElement) {
        this.previewElement.style.backgroundColor = color;
      }

      const colorCode = this.previewElement?.parentElement.querySelector('.color-code');
      if (colorCode) {
        colorCode.textContent = color.toUpperCase();
      }

      // Update active state in palette
      this.updatePaletteActiveState(color);
    },

    /**
     * Select a color from the palette
     * @param {string} color - Color hex code
     */
    selectColor(color) {
      this.colorInput.value = color;
      this.updatePreview();

      // Trigger change event for form validation
      const event = new Event('change', { bubbles: true });
      this.colorInput.dispatchEvent(event);
    },

    /**
     * Update active state in palette buttons
     * @param {string} activeColor - Currently selected color
     */
    updatePaletteActiveState(activeColor) {
      if (!this.paletteContainer) return;

      const buttons = this.paletteContainer.querySelectorAll('button');
      buttons.forEach(btn => {
        const btnColor = btn.dataset.color;
        if (btnColor && btnColor.toUpperCase() === activeColor.toUpperCase()) {
          btn.classList.add('ring-2', 'ring-primary-500', 'ring-offset-2', 'ring-offset-slate-800');
        } else {
          btn.classList.remove('ring-2', 'ring-primary-500', 'ring-offset-2', 'ring-offset-slate-800');
        }
      });
    }
  };

  // ============================================================================
  // DELETE CONFIRMATION FOR CATEGORIES
  // ============================================================================

  const CategoryDeleteModal = {
    modal: null,

    /**
     * Initialize the delete confirmation modal
     */
    init() {
      if (this.modal) return;

      this.modal = document.createElement('div');
      this.modal.id = 'category-delete-modal';
      this.modal.className = 'fixed inset-0 z-50 hidden';
      this.modal.innerHTML = `
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity" onclick="CategoryDeleteModal.close()"></div>

        <!-- Modal Content -->
        <div class="fixed inset-0 flex items-center justify-center p-4">
          <div class="bg-slate-800 rounded-xl shadow-2xl border border-red-600/30 max-w-md w-full transform transition-all scale-95 opacity-0" id="category-delete-modal-content">
            <!-- Icon -->
            <div class="flex items-center justify-center w-16 h-16 mx-auto mt-8 bg-red-900/30 rounded-full">
              <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </div>

            <!-- Content -->
            <div class="p-8 text-center">
              <h3 class="text-2xl font-bold text-slate-100 mb-3">Excluir Categoria</h3>
              <p class="text-slate-300 mb-2" id="category-delete-modal-message">
                Tem certeza que deseja excluir esta categoria?
              </p>
              <p class="text-slate-400 text-sm">
                Esta ação não pode ser desfeita.
              </p>
            </div>

            <!-- Actions -->
            <div class="flex gap-3 px-8 pb-8">
              <button type="button"
                      onclick="CategoryDeleteModal.close()"
                      class="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium rounded-lg border border-slate-600 transition-all duration-200">
                Cancelar
              </button>
              <button type="button"
                      id="category-delete-modal-confirm"
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
     * @param {string} categoryName - Name of category being deleted
     * @param {string} categoryColor - Color of category (for visual reference)
     * @param {Function} onConfirm - Callback function when confirmed
     */
    show(categoryName, categoryColor, onConfirm) {
      this.init();

      // Update message
      const messageEl = document.getElementById('category-delete-modal-message');
      if (messageEl) {
        messageEl.innerHTML = `
          Tem certeza que deseja excluir a categoria
          <span class="inline-flex items-center px-2 py-1 rounded text-sm font-medium mx-1" style="background-color: ${categoryColor}20; color: ${categoryColor}">
            <span class="w-2 h-2 rounded-full mr-1.5" style="background-color: ${categoryColor}"></span>
            ${categoryName}
          </span>?
        `;
      }

      // Set confirm action
      const confirmBtn = document.getElementById('category-delete-modal-confirm');
      const newConfirmBtn = confirmBtn.cloneNode(true);
      confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

      newConfirmBtn.addEventListener('click', () => {
        if (onConfirm) onConfirm();
        this.close();
      });

      // Show modal
      this.modal.classList.remove('hidden');
      setTimeout(() => {
        const content = document.getElementById('category-delete-modal-content');
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
      }, 10);
    },

    /**
     * Close the modal
     */
    close() {
      const content = document.getElementById('category-delete-modal-content');
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
  // FORM VALIDATION FOR CATEGORIES
  // ============================================================================

  const CategoryFormValidator = {
    /**
     * Initialize form validation
     * @param {HTMLFormElement} form - Form element to validate
     */
    init(form) {
      if (!form) return;

      const nameField = form.querySelector('#id_name');
      const typeField = form.querySelector('#id_category_type');
      const colorField = form.querySelector('#id_color');

      // Validate name field
      if (nameField) {
        nameField.addEventListener('blur', () => {
          this.validateName(nameField);
        });

        nameField.addEventListener('input', () => {
          this.clearError(nameField);
        });
      }

      // Validate color field
      if (colorField) {
        colorField.addEventListener('change', () => {
          this.validateColor(colorField);
        });
      }

      // Form submit validation
      form.addEventListener('submit', (e) => {
        let isValid = true;

        if (nameField && !this.validateName(nameField)) {
          isValid = false;
        }

        if (typeField && !typeField.value) {
          isValid = false;
          this.showError(typeField, 'Selecione o tipo da categoria.');
        }

        if (colorField && !this.validateColor(colorField)) {
          isValid = false;
        }

        if (!isValid) {
          e.preventDefault();
        }
      });
    },

    /**
     * Validate name field
     * @param {HTMLInputElement} field - Name input field
     * @returns {boolean} True if valid
     */
    validateName(field) {
      const value = field.value.trim();

      if (!value) {
        this.showError(field, 'O nome da categoria é obrigatório.');
        return false;
      }

      if (value.length < 2) {
        this.showError(field, 'O nome deve ter pelo menos 2 caracteres.');
        return false;
      }

      this.clearError(field);
      return true;
    },

    /**
     * Validate color field
     * @param {HTMLInputElement} field - Color input field
     * @returns {boolean} True if valid
     */
    validateColor(field) {
      const value = field.value.trim().toUpperCase();
      const hexPattern = /^#[0-9A-F]{6}$/;

      if (!value) {
        this.showError(field, 'Selecione uma cor para a categoria.');
        return false;
      }

      if (!hexPattern.test(value)) {
        this.showError(field, 'Cor inválida. Use o formato #RRGGBB.');
        return false;
      }

      this.clearError(field);
      return true;
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
      field.classList.remove('border-red-500');

      const container = field.closest('.relative') || field.parentElement;
      const errorDiv = container.querySelector('.field-error');
      if (errorDiv) {
        errorDiv.remove();
      }
    }
  };

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  document.addEventListener('DOMContentLoaded', () => {
    // Initialize color picker
    const colorInput = document.querySelector('#id_color');
    if (colorInput) {
      ColorPicker.init(colorInput);
    }

    // Initialize form validation
    const categoryForm = document.querySelector('form[method="post"]');
    if (categoryForm) {
      CategoryFormValidator.init(categoryForm);
    }

    // Initialize delete modals for category cards
    const deleteLinks = document.querySelectorAll('a[href*="/excluir/"]');
    deleteLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();

        const categoryCard = link.closest('[data-category-name]');
        const categoryName = categoryCard?.dataset.categoryName || 'esta categoria';
        const categoryColor = categoryCard?.dataset.categoryColor || '#6366F1';

        CategoryDeleteModal.show(
          categoryName,
          categoryColor,
          () => {
            window.location.href = link.href;
          }
        );
      });
    });
  });

  // Make modules globally accessible
  window.ColorPicker = ColorPicker;
  window.CategoryDeleteModal = CategoryDeleteModal;
  window.CategoryFormValidator = CategoryFormValidator;

})();
