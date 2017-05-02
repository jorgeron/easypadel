from django import template

register = template.Library()

@register.inclusion_tag('comentario.html')
def comentarioview(comentario, user):
    return {'comentario': comentario, 'user': user}