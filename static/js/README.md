# Accounts JavaScript Module

## Overview

The `accounts.js` file provides client-side functionality for the accounts app with a focus on enhancing user experience through real-time validation, interactive modals, currency formatting, and toast notifications.

## Features

### 1. Toast Notification System

A flexible toast notification system that displays temporary messages in the top-right corner of the screen.

**Types:**
- `success` - Green themed, for successful operations
- `error` - Red themed, for errors and failures
- `warning` - Yellow themed, for warnings
- `info` - Blue themed, for informational messages

**Usage:**
```javascript
// Show a success toast
Toast.success('Conta criada com sucesso!');

// Show an error toast
Toast.error('Erro ao salvar a conta.');

// Show a warning toast
Toast.warning('Atenção: Saldo baixo!');

// Show an info toast
Toast.info('Carregando dados...');

// Custom duration (default is 5000ms)
Toast.success('Mensagem', 3000);
```

**Auto-dismiss:**
- Toasts automatically dismiss after 5 seconds (configurable)
- Users can manually dismiss by clicking the X button
- Animated in/out with smooth transitions

### 2. Delete Confirmation Modal

A reusable modal component that intercepts delete actions and shows a confirmation dialog.

**Features:**
- Backdrop with blur effect
- Warning icon and messaging
- Confirm/Cancel actions
- Keyboard support (ESC to close)
- Animated entrance/exit

**Automatic Integration:**
The modal automatically intercepts all delete links (URLs containing `/delete/`) and shows a confirmation dialog before proceeding.

**Manual Usage:**
```javascript
DeleteModal.show(
  'Tem certeza que deseja excluir "Conta Corrente"?',
  () => {
    // Callback when user confirms
    window.location.href = deleteUrl;
  }
);

// Close the modal programmatically
DeleteModal.close();
```

### 3. Currency Formatter

Brazilian Real (BRL) currency formatting for monetary input fields.

**Features:**
- Format as user types: `1234.56` → `1.234,56`
- Thousand separators with dots (.)
- Decimal separator with comma (,)
- Limits to 2 decimal places
- Parses formatted value back to number on form submission

**Usage:**
```javascript
// Apply to an input field
const balanceInput = document.querySelector('#id_initial_balance');
CurrencyFormatter.applyToInput(balanceInput);

// Format a value programmatically
const formatted = CurrencyFormatter.format(1234.56);
// Returns: "1.234,56"

// Parse formatted value back to number
const parsed = CurrencyFormatter.parse('1.234,56');
// Returns: 1234.56
```

**Automatic Integration:**
The script automatically applies currency formatting to the `#id_initial_balance` field.

### 4. Form Validation

Real-time client-side validation for account forms.

**Features:**
- Validates required fields
- Validates select dropdowns
- Validates number/currency fields
- Shows inline error messages with icons
- Disables submit button until form is valid
- Removes errors as user types

**Validation Rules:**
- Required fields must not be empty
- Select fields must have a value selected
- Number fields must contain valid numeric values
- Min/max length validation (if specified)

**Automatic Integration:**
The validator automatically initializes on forms with `method="post"`.

**Manual Usage:**
```javascript
// Initialize validation on a specific form
const form = document.querySelector('#my-form');
FormValidator.init(form);

// Validate a single field
const isValid = FormValidator.validateField(inputElement);

// Show error on a field
FormValidator.showError(inputElement, 'Este campo é obrigatório.');

// Clear error from a field
FormValidator.clearError(inputElement);
```

### 5. Loading State

Adds loading spinners and disabled states to buttons during form submission.

**Features:**
- Animated spinner icon
- "Salvando..." text
- Disabled button state
- Restores original content when done

**Automatic Integration:**
Loading state is automatically applied to submit buttons on form submission.

**Manual Usage:**
```javascript
const button = document.querySelector('button[type="submit"]');

// Show loading state
LoadingState.show(button);

// Hide loading state
LoadingState.hide(button);
```

## HTML Integration

### Including the Script

Add the script to your Django templates:

```django
{% load static %}

{% block extra_js %}
{{ block.super }}
<script src="{% static 'js/accounts.js' %}"></script>
{% endblock %}
```

### Required Template Structure

The script expects certain HTML structures and IDs to work properly:

**Currency Input:**
```html
<input type="number"
       id="id_initial_balance"
       name="initial_balance"
       class="currency-input"
       required>
```

**Form with Validation:**
```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="name" required>
    <select name="account_type" required>
        <option value="">Selecione</option>
        <option value="checking">Conta Corrente</option>
    </select>
    <button type="submit">Salvar</button>
</form>
```

**Delete Links:**
```html
<a href="{% url 'accounts:delete' account.pk %}">Excluir</a>
```

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features used (arrow functions, template literals, const/let)
- Vanilla JavaScript (no dependencies)

## Customization

All modules are exposed to the global scope for easy customization:

```javascript
// Customize toast duration globally
window.Toast.show('Message', 'success', 10000); // 10 seconds

// Customize modal messages
window.DeleteModal.show('Custom message', callback);

// Add custom validation rules
window.FormValidator.validateField(field);
```

## Development Notes

### Adding New Features

To extend functionality:

1. Add new functions to the appropriate module object
2. Expose to global scope if needed for inline handlers
3. Initialize in the DOMContentLoaded event listener

### Styling

All components use TailwindCSS utility classes for styling. To customize:

1. Modify the class names in the HTML string templates
2. Ensure dark theme compatibility (bg-slate-*, text-slate-*)
3. Use the established color palette (primary, secondary, success, error)

### Testing

Test the following scenarios:

1. **Toast Notifications:**
   - Multiple toasts appearing simultaneously
   - Toast auto-dismiss timing
   - Manual dismissal
   - Different toast types

2. **Delete Modal:**
   - Opening/closing modal
   - ESC key to close
   - Backdrop click to close
   - Confirm action execution

3. **Currency Formatter:**
   - Typing numbers
   - Pasting formatted values
   - Decimal place limits
   - Form submission parsing

4. **Form Validation:**
   - Empty required fields
   - Invalid data types
   - Error message display
   - Submit button state
   - Real-time validation

5. **Loading State:**
   - Submit button spinner
   - Button disabled during loading
   - Content restoration

## Performance Considerations

- Event listeners are attached once during initialization
- DOM queries are cached where possible
- Animations use CSS transitions (hardware accelerated)
- Toast container is created once and reused
- Modal HTML is created once and shown/hidden as needed

## Accessibility

The implementation includes basic accessibility features:

- Keyboard support (ESC to close modal)
- ARIA labels on interactive elements
- Focus management in modals
- High contrast colors for visibility
- Screen reader friendly error messages

## Future Enhancements

Potential improvements:

1. Add form dirty state tracking
2. Implement custom validation rules API
3. Add toast notification stacking with max limit
4. Support for custom modal templates
5. Add internationalization (i18n) support
6. Implement field-level async validation
7. Add animation options/customization
8. Create a form auto-save feature
