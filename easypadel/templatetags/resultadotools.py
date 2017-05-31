from django import template
from easypadel.models import Resultado, FranjaHoraria

register = template.Library()


@register.filter(name='tiene_resultado')
def tiene_resultado(franja):
    return Resultado.objects.filter(franja_horaria = franja).exists()