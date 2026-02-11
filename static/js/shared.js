/**
 * Shared UI Components
 *
 * Provides:
 * - Delete confirmation modal (intercepts all delete links)
 * - Unsaved changes warning on forms
 * - Loading states on form submit buttons
 */

(function() {
  'use strict';

  // ============================================================================
  // DELETE CONFIRMATION MODAL
  // ============================================================================

  const DeleteModal = {
    modal: null,

    init() {
      if (this.modal) return;

      this.modal = document.createElement('div');
      this.modal.id = 'shared-delete-modal';
      this.modal.className = 'fixed inset-0 z-[9998] hidden';
      this.modal.setAttribute('role', 'dialog');
      this.modal.setAttribute('aria-modal', 'true');
      this.modal.setAttribute('aria-labelledby', 'delete-modal-title');
      this.modal.innerHTML = `
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity" data-dismiss="modal"></div>
        <div class="fixed inset-0 flex items-center justify-center p-4">
          <div class="bg-slate-800 rounded-xl shadow-2xl border border-red-600/30 max-w-md w-full transform transition-all duration-200 scale-95 opacity-0" id="shared-delete-modal-content">
            <div class="flex items-center justify-center w-16 h-16 mx-auto mt-8 bg-red-900/30 rounded-full">
              <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div class="p-8 text-center">
              <h3 class="text-2xl font-bold text-slate-100 mb-3" id="delete-modal-title">Confirmar Exclusão</h3>
              <p class="text-slate-300 mb-2" id="shared-delete-modal-message">
                Tem certeza que deseja excluir este item?
              </p>
              <p class="text-slate-400 text-sm">
                Esta ação não pode ser desfeita.
              </p>
            </div>
            <div class="flex gap-3 px-8 pb-8">
              <button type="button" data-dismiss="modal"
                      class="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium rounded-lg border border-slate-600 transition-all duration-200">
                Cancelar
              </button>
              <button type="button" id="shared-delete-modal-confirm"
                      class="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all duration-200">
                Confirmar Exclusão
              </button>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(this.modal);

      // Close on backdrop click
      this.modal.querySelectorAll('[data-dismiss="modal"]').forEach(el => {
        el.addEventListener('click', () => this.close());
      });

      // Close on Escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
          this.close();
        }
      });
    },

    show(message, onConfirm) {
      this.init();

      if (message) {
        document.getElementById('shared-delete-modal-message').textContent = message;
      }

      const confirmBtn = document.getElementById('shared-delete-modal-confirm');
      const newConfirmBtn = confirmBtn.cloneNode(true);
      confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

      newConfirmBtn.addEventListener('click', () => {
        if (onConfirm) onConfirm();
        this.close();
      });

      this.modal.classList.remove('hidden');
      requestAnimationFrame(() => {
        const content = document.getElementById('shared-delete-modal-content');
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
      });

      // Trap focus
      newConfirmBtn.focus();
    },

    close() {
      const content = document.getElementById('shared-delete-modal-content');
      content.classList.add('scale-95', 'opacity-0');
      content.classList.remove('scale-100', 'opacity-100');

      setTimeout(() => {
        this.modal.classList.add('hidden');
      }, 200);
    }
  };

  // ============================================================================
  // UNSAVED CHANGES WARNING
  // ============================================================================

  const UnsavedChanges = {
    forms: new Map(),

    init() {
      const forms = document.querySelectorAll('form[method="post"]');
      forms.forEach(form => {
        // Skip delete confirmation forms (they only have csrf token)
        if (form.querySelectorAll('input:not([type="hidden"]), select, textarea').length === 0) return;

        const initialData = this.serializeForm(form);
        this.forms.set(form, initialData);

        // Track changes
        form.addEventListener('input', () => this.markDirty(form));
        form.addEventListener('change', () => this.markDirty(form));

        // Clear dirty flag on submit
        form.addEventListener('submit', () => {
          form.dataset.submitting = 'true';
        });
      });

      // Warn on page leave
      window.addEventListener('beforeunload', (e) => {
        if (this.hasDirtyForms()) {
          e.preventDefault();
          e.returnValue = '';
        }
      });
    },

    serializeForm(form) {
      const data = new FormData(form);
      const entries = [];
      for (const [key, value] of data.entries()) {
        if (key !== 'csrfmiddlewaretoken') {
          entries.push(`${key}=${value}`);
        }
      }
      return entries.sort().join('&');
    },

    markDirty(form) {
      const initialData = this.forms.get(form);
      const currentData = this.serializeForm(form);
      form.dataset.dirty = (initialData !== currentData) ? 'true' : 'false';
    },

    hasDirtyForms() {
      for (const [form] of this.forms) {
        if (form.dataset.dirty === 'true' && form.dataset.submitting !== 'true') {
          return true;
        }
      }
      return false;
    }
  };

  // ============================================================================
  // LOADING STATES
  // ============================================================================

  const LoadingState = {
    init() {
      const forms = document.querySelectorAll('form[method="post"]');
      forms.forEach(form => {
        form.addEventListener('submit', () => {
          const submitBtn = form.querySelector('button[type="submit"]');
          if (submitBtn && !submitBtn.disabled) {
            this.show(submitBtn);
          }
        });
      });
    },

    show(button) {
      if (!button) return;

      button.dataset.originalContent = button.innerHTML;
      button.disabled = true;
      button.classList.add('opacity-75', 'cursor-not-allowed');

      const isDeleteBtn = button.textContent.includes('Exclu');
      const loadingText = isDeleteBtn ? 'Excluindo...' : 'Salvando...';

      button.innerHTML = `
        <svg class="animate-spin h-5 w-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        ${loadingText}
      `;
    },

    hide(button) {
      if (!button || !button.dataset.originalContent) return;

      button.innerHTML = button.dataset.originalContent;
      delete button.dataset.originalContent;
      button.disabled = false;
      button.classList.remove('opacity-75', 'cursor-not-allowed');
    }
  };

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  document.addEventListener('DOMContentLoaded', () => {
    // Initialize delete modal for all delete links
    const deleteLinks = document.querySelectorAll('a[href*="/excluir/"]');
    deleteLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();

        // Try to find a meaningful name from the card context
        const card = link.closest('[class*="bg-slate-800"]') || link.closest('[class*="border-slate"]');
        const nameEl = card?.querySelector('h3, .text-xl, .font-bold:not(.text-3xl)');
        const itemName = nameEl?.textContent?.trim() || 'este item';

        DeleteModal.show(
          `Tem certeza que deseja excluir "${itemName}"?`,
          () => {
            window.location.href = link.href;
          }
        );
      });
    });

    // Initialize unsaved changes warning
    UnsavedChanges.init();

    // Initialize loading states
    LoadingState.init();
  });

  // Expose globally
  window.DeleteModal = DeleteModal;
  window.UnsavedChanges = UnsavedChanges;
  window.LoadingState = LoadingState;

})();
