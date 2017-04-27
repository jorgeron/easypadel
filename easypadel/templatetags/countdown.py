from django import template 

register = template.Library() 

@register.inclusion_tag('countdown.html')
def countdown(ctrlid, param=None):
    return {'ctrlid': ctrlid + (str(param) if param else "")}
