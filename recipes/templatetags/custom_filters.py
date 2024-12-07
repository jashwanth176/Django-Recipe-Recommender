from django import template

register = template.Library()

@register.filter
def newline_comma(value):
    return value.replace(',', '\n').replace('.', '\n')
