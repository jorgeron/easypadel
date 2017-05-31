from django import template
from easypadel.models import Resultado, FranjaHoraria

register = template.Library()

@register.inclusion_tag('resultado.html')
def resultadoview(resultado):
    return {'resultado': resultado}

@register.filter(name='tiene_resultado')
def tiene_resultado(franja):
    return Resultado.objects.filter(franja_horaria = franja).exists()