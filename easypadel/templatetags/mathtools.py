from django import template 

register = template.Library() 

@register.simple_tag()
def porcentaje(parte, total, *args, **kwargs):
	return (parte*100)/total