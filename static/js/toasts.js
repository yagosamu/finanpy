/**
 * Shared Toast Notification System
 *
 * Provides toast notifications across all pages.
 * Automatically displays Django messages on page load.
 */

(function() {
  'use strict';

  const Toast = {
    container: null,

    init() {
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'fixed top-4 right-4 z-[9999] space-y-3 max-w-sm';
        this.container.setAttribute('role', 'alert');
        this.container.setAttribute('aria-live', 'polite');
        document.body.appendChild(this.container);
      }
    },

    show(message, type = 'info', duration = 5000) {
      this.init();

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

      const toast = document.createElement('div');
      toast.className = `${color.bg} border ${color.border} rounded-lg shadow-2xl p-4 flex items-start transform transition-all duration-300 ease-out translate-x-full opacity-0`;
      toast.innerHTML = `
        <svg class="w-6 h-6 ${color.icon} mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="${color.iconPath}" />
        </svg>
        <p class="${color.text} flex-1 text-sm font-medium">${this.escapeHtml(message)}</p>
        <button class="ml-3 ${color.text} hover:opacity-75 transition-opacity" aria-label="Fechar">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      `;

      toast.querySelector('button').addEventListener('click', () => this.dismiss(toast));

      this.container.appendChild(toast);

      // Animate in
      requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
      });

      // Auto-dismiss
      if (duration > 0) {
        const timeoutId = setTimeout(() => this.dismiss(toast), duration);
        toast._timeoutId = timeoutId;

        // Pause on hover
        toast.addEventListener('mouseenter', () => clearTimeout(toast._timeoutId));
        toast.addEventListener('mouseleave', () => {
          toast._timeoutId = setTimeout(() => this.dismiss(toast), 2000);
        });
      }

      return toast;
    },

    dismiss(toast) {
      if (!toast || !toast.parentElement) return;
      toast.classList.add('translate-x-full', 'opacity-0');
      setTimeout(() => {
        if (toast.parentElement) {
          toast.parentElement.removeChild(toast);
        }
      }, 300);
    },

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    },

    success(message, duration = 5000) {
      return this.show(message, 'success', duration);
    },

    error(message, duration = 7000) {
      return this.show(message, 'error', duration);
    },

    warning(message, duration = 6000) {
      return this.show(message, 'warning', duration);
    },

    info(message, duration = 5000) {
      return this.show(message, 'info', duration);
    }
  };

  // Process Django messages embedded in the page
  function processDjangoMessages() {
    const container = document.getElementById('django-messages-data');
    if (!container) return;

    const messageElements = container.querySelectorAll('[data-message]');
    messageElements.forEach((el, index) => {
      const message = el.dataset.message;
      const level = el.dataset.level || 'info';

      // Map Django message levels to toast types
      const typeMap = {
        'debug': 'info',
        'info': 'info',
        'success': 'success',
        'warning': 'warning',
        'error': 'error'
      };

      const type = typeMap[level] || 'info';

      // Stagger multiple messages
      setTimeout(() => {
        Toast[type](message);
      }, index * 200);
    });
  }

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', processDjangoMessages);

  // Expose globally
  window.Toast = Toast;

})();
