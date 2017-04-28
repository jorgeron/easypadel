from django import template

register = template.Library()

@register.inclusion_tag('propuesta.html')
def propuestaview(propuesta, user):
    return {'propuesta': propuesta, 'user': user}
