from django import template

register = template.Library()

@register.inclusion_tag('valoracion.html')
def valoracionview(valoracion):
    return {'valoracion': valoracion}

@register.assignment_tag()
def numeroEstrellas(pista, *args, **kwargs):
	numero_estrellas = round(pista.valoracion_total)
	iterable = []
	for i in range(numero_estrellas):
		iterable.append('*')
	return iterable

@register.assignment_tag()
def numeroEstrellasVacias(pista, *args, **kwargs):
	numero_estrellas = round(pista.valoracion_total)
	iterable = []
	for i in range(5 - numero_estrellas):
		iterable.append('*')
	return iterable