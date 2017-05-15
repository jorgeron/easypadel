from django import template

register = template.Library()

@register.inclusion_tag('valoracion.html')
def valoracionview(valoracion):
    return {'valoracion': valoracion}
