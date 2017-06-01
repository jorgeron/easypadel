import calendar
import locale
from django import template

register = template.Library() 
locale.setlocale(locale.LC_ALL, 'es_ES')

@register.filter
def month_name(month_number):
    month = calendar.month_name[month_number]
    return month[:3]
