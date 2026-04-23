from django import template
from django.templatetags.static import static

register = template.Library()


def get_bank_icon_path(bank_code):
    icon_name = bank_code or 'other'
    valid_icons = {
        'nubank',
        'itau',
        'bradesco',
        'santander',
        'bb',
        'caixa',
        'inter',
        'c6',
        'other',
    }
    if icon_name not in valid_icons:
        icon_name = 'other'
    return f'images/banks/{icon_name}.svg'


@register.simple_tag
def bank_icon(bank_code):
    return static(get_bank_icon_path(bank_code))
