from django import template
from easypadel.models import Seguimiento

register = template.Library()

@register.inclusion_tag('post.html')
def postview(post, user):
    return {'post': post, 'user': user}

@register.filter(name='is_followed')
def is_followed(user, by):
    return Seguimiento.objects.filter(origen=by, destino=user).exists()