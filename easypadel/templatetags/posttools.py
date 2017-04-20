from django import template

register = template.Library()

@register.inclusion_tag('post.html')
def postview(post, user):
    return {'post': post, 'user': user}

