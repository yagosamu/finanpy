from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django import template
from django.utils import timezone
from django.utils.formats import number_format

register = template.Library()


@register.filter
def format_currency(value):
    '''Format value as Brazilian Real: R$ 1.234,56 or -R$ 1.234,56'''
    try:
        value = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return 'R$ 0,00'
    formatted = number_format(abs(value), decimal_pos=2, use_l10n=True, force_grouping=True)
    if value < 0:
        return f'-R$ {formatted}'
    return f'R$ {formatted}'


@register.filter
def format_currency_signed(value):
    '''Format value with explicit sign: +R$ 1.234,56 or -R$ 1.234,56'''
    try:
        value = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return 'R$ 0,00'
    formatted = number_format(abs(value), decimal_pos=2, use_l10n=True, force_grouping=True)
    if value > 0:
        return f'+R$ {formatted}'
    elif value < 0:
        return f'-R$ {formatted}'
    return 'R$ 0,00'


@register.filter
def format_date_relative(value):
    '''Format date as relative: Hoje, Ontem, or DD/MM/YYYY'''
    if not value:
        return ''
    if isinstance(value, datetime):
        value = value.date()
    today = timezone.localdate()
    delta = (today - value).days
    if delta == 0:
        return 'Hoje'
    elif delta == 1:
        return 'Ontem'
    elif 2 <= delta <= 6:
        return f'Há {delta} dias'
    return value.strftime('%d/%m/%Y')


@register.filter
def format_date_br(value):
    '''Format date as DD/MM/YYYY'''
    if not value:
        return ''
    if isinstance(value, datetime):
        return value.strftime('%d/%m/%Y')
    return value.strftime('%d/%m/%Y')


@register.filter
def format_datetime_br(value):
    '''Format datetime as DD/MM/YYYY às HH:MM'''
    if not value:
        return ''
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime('%d/%m/%Y às %H:%M')


@register.filter
def format_date_short(value):
    '''Format date as DD/MM'''
    if not value:
        return ''
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime('%d/%m')


@register.filter
def currency_class(value):
    '''Return CSS class based on value sign (positive=green, negative=red)'''
    try:
        value = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return 'text-slate-100'
    if value > 0:
        return 'text-green-400'
    elif value < 0:
        return 'text-red-400'
    return 'text-slate-100'
