from django.contrib import admin
from .models import Pista, Jugador, Empresa

# Register your models here.
admin.site.register(Pista)
admin.site.register(Jugador)
admin.site.register(Empresa)