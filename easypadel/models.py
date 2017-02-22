from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

# Create your models here.
class Actor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, verbose_name=_("Nombre"))
    # Add more user profile fields here. Make sure they are nullable
    # or with default values
    foto_perfil = models.ImageField(null=True, blank=True, upload_to='profile_pics/%Y-%m-%d/', verbose_name=_('Foto de perfil'))
    foto_cabecera = models.ImageField(null=True, blank=True, upload_to='header_pics/%Y-%m-%d/', verbose_name=_('Foto de cabecera'))
    #email = models.EmailField(verbose_name=_("Email"))
    telefono_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("El teléfono debe tener el siguiente formato: '+999999999'. Permitidos hasta 15 dígitos."))
    telefono = models.CharField(validators=[telefono_regex], blank=True, max_length=15,verbose_name=_("Teléfono")) # validators should be a list   
    descripcion = models.TextField(max_length=500, blank=True, null= True)
    
    def __unicode__(self):
        return self.user.username

    class Meta:
        abstract = True


class Jugador(Actor):
	SEXOS = (
		('H', 'Hombre'),
		('M', 'Mujer'),
	)

	apellidos = models.CharField(max_length=200, verbose_name=_("Apellidos"))
	fecha_nacimiento = models.DateField(verbose_name=_("Fecha de nacimiento"))
	sexo = models.CharField(max_length=1, choices=SEXOS)
	localidad = models.CharField(max_length=50, verbose_name=_('Localidad'))
	class Meta:
		verbose_name = _('Jugador')
		verbose_name_plural = _('Jugadores')

	def __unicode__(self):
		return self.nombre +' '+ self.apellidos

	def __str__(self):
		return self.nombre +' '+ self.apellidos


class Empresa(Actor):
	direccion = models.CharField(max_length=200, verbose_name=_("Dirección"))

	def __unicode__(self):
		return self.nombre

	def __str__(self):
		return self.nombre


class Pista(models.Model):
	
	TIPOS_SUPERFICIES = (
		('CESPED', 'Césped artificial'),
		('HORMIGON', 'Hormigón poroso'),
		('MOQUETA', 'Moqueta'),
	)

	COLORES = (
		('AZUL', 'Azul'),
		('VERDE', 'Verde'),
		('MARRON', 'Marrón'),
	)

	TIPOS_PARED = (
		('METACRILATO', 'Metacrilato'),
		('CEMENTO', 'Cemento'),
	)

	nombre = models.CharField(max_length=20, primary_key=True)
	tipo_superficie = models.CharField(max_length=20, choices=TIPOS_SUPERFICIES, default='CESPED')
	color = models.CharField(max_length=10, choices=COLORES, default='AZUL')
	tipo_pared = models.CharField(max_length=20, choices=TIPOS_PARED, default='METACRILATO')
	cubierta = models.BooleanField(default=False)
	descripcion = models.TextField(blank=True, null=True)
	
	def __str__(self):
		return self.nombre