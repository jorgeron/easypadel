from django.contrib import admin
from .models import Pista, Jugador, Empresa, Administrador, Horario, FranjaHoraria

# Register your models here.
admin.site.register(Horario)
admin.site.register(FranjaHoraria)
admin.site.register(Pista)
admin.site.register(Jugador)
admin.site.register(Empresa)
admin.site.register(Administrador)