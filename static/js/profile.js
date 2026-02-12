(function() {
  'use strict';

  const PhoneMask = {
    init(input) {
      input.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');

        if (value.length > 11) {
          value = value.slice(0, 11);
        }

        if (value.length >= 11) {
          value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
        } else if (value.length >= 7) {
          value = value.replace(/^(\d{2})(\d{5})(\d{0,4}).*/, '($1) $2-$3');
        } else if (value.length >= 2) {
          value = value.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
        } else if (value.length > 0) {
          value = value.replace(/^(\d*)/, '($1');
        }

        e.target.value = value;
      });
    }
  };

  const ProfileFormValidator = {
    init(form) {
      const firstNameField = document.getElementById('id_first_name');
      const lastNameField = document.getElementById('id_last_name');
      const phoneField = document.getElementById('id_phone');
      const birthDateField = document.getElementById('id_birth_date');

      if (firstNameField) {
        firstNameField.addEventListener('blur', () => {
          this.validateFirstName(firstNameField);
        });
        firstNameField.addEventListener('input', () => {
          this.clearError(firstNameField);
        });
      }

      if (lastNameField) {
        lastNameField.addEventListener('blur', () => {
          this.validateLastName(lastNameField);
        });
        lastNameField.addEventListener('input', () => {
          this.clearError(lastNameField);
        });
      }

      if (phoneField) {
        phoneField.addEventListener('blur', () => {
          this.validatePhone(phoneField);
        });
        phoneField.addEventListener('input', () => {
          this.clearError(phoneField);
        });
      }

      if (birthDateField) {
        birthDateField.addEventListener('blur', () => {
          this.validateBirthDate(birthDateField);
        });
        birthDateField.addEventListener('input', () => {
          this.clearError(birthDateField);
        });
      }

      form.addEventListener('submit', (e) => {
        let isValid = true;

        if (firstNameField && !this.validateFirstName(firstNameField)) {
          isValid = false;
        }
        if (lastNameField && !this.validateLastName(lastNameField)) {
          isValid = false;
        }
        if (phoneField && !this.validatePhone(phoneField)) {
          isValid = false;
        }
        if (birthDateField && !this.validateBirthDate(birthDateField)) {
          isValid = false;
        }

        if (!isValid) {
          e.preventDefault();
          const firstError = form.querySelector('.field-error');
          if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      });
    },

    validateFirstName(field) {
      const value = field.value.trim();

      // Optional field - empty is ok
      if (!value) {
        this.clearError(field);
        return true;
      }

      if (value.length < 2) {
        this.showError(field, 'O nome deve ter no mínimo 2 caracteres.');
        return false;
      }

      const namePattern = /^[a-zA-ZÀ-ÿ\s'-]+$/;
      if (!namePattern.test(value)) {
        this.showError(field, 'O nome deve conter apenas letras, espaços e hífens.');
        return false;
      }

      this.showSuccess(field);
      return true;
    },

    validateLastName(field) {
      const value = field.value.trim();

      // Optional field - empty is ok
      if (!value) {
        this.clearError(field);
        return true;
      }

      if (value.length < 2) {
        this.showError(field, 'O sobrenome deve ter no mínimo 2 caracteres.');
        return false;
      }

      const namePattern = /^[a-zA-ZÀ-ÿ\s'-]+$/;
      if (!namePattern.test(value)) {
        this.showError(field, 'O sobrenome deve conter apenas letras, espaços e hífens.');
        return false;
      }

      this.showSuccess(field);
      return true;
    },

    validatePhone(field) {
      const value = field.value.trim();

      // Optional field - empty is ok
      if (!value) {
        this.clearError(field);
        return true;
      }

      const digitsOnly = value.replace(/\D/g, '');

      if (digitsOnly.length < 10 || digitsOnly.length > 11) {
        this.showError(field, 'O telefone deve ter 10 ou 11 dígitos.');
        return false;
      }

      // 11 digits: mobile must have 9 as 3rd digit
      if (digitsOnly.length === 11 && digitsOnly[2] !== '9') {
        this.showError(field, 'Celular deve ter o dígito 9 após o DDD.');
        return false;
      }

      this.showSuccess(field);
      return true;
    },

    validateBirthDate(field) {
      const value = field.value.trim();

      // Optional field - empty is ok
      if (!value) {
        this.clearError(field);
        return true;
      }

      const birthDate = new Date(value + 'T00:00:00');
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (isNaN(birthDate.getTime())) {
        this.showError(field, 'Data de nascimento inválida.');
        return false;
      }

      if (birthDate >= today) {
        this.showError(field, 'A data de nascimento deve estar no passado.');
        return false;
      }

      const age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      const dayDiff = today.getDate() - birthDate.getDate();
      const actualAge = (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) ? age - 1 : age;

      if (actualAge < 18) {
        this.showError(field, 'Você deve ter pelo menos 18 anos.');
        return false;
      }

      if (actualAge > 120) {
        this.showError(field, 'Data de nascimento inválida.');
        return false;
      }

      this.showSuccess(field);
      return true;
    },

    showError(field, message) {
      this.clearError(field);
      field.classList.add('border-red-500');
      field.classList.remove('border-green-500');

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

    clearError(field) {
      field.classList.remove('border-red-500');
      field.classList.remove('border-green-500');

      const container = field.closest('.relative') || field.parentElement;
      const errorDiv = container.querySelector('.field-error');
      if (errorDiv) {
        errorDiv.remove();
      }

      const successIcon = container.querySelector('.success-icon');
      if (successIcon) {
        successIcon.remove();
      }
    },

    showSuccess(field) {
      this.clearError(field);
      field.classList.add('border-green-500');

      const container = field.closest('.relative') || field.parentElement;

      const successIcon = document.createElement('div');
      successIcon.className = 'success-icon mt-2';
      successIcon.innerHTML = `
        <p class="text-sm text-green-400 flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Válido
        </p>
      `;

      container.appendChild(successIcon);
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form[method="post"]');
    if (form) {
      ProfileFormValidator.init(form);
    }

    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
      PhoneMask.init(phoneInput);
    }
  });

  window.ProfileFormValidator = ProfileFormValidator;
  window.PhoneMask = PhoneMask;
})();
