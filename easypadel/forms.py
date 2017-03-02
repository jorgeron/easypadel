#from datetimewidget.widgets import DateTimeWidget, DateWidget
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelForm

from easypadel.models import Jugador

class BaseForm(ModelForm):
    required_css_class = 'required'


class JugadorForm(BaseForm):
# terms = forms.BooleanField(
#   error_messages={'required': _('You must accept the terms and conditions')},
#   label=_("I accept the <a href='/conditions'>Terms&Conditions</a>"))
    class Meta:
        model = Jugador
        fields = ['nombre', 'apellidos', 'fecha_nacimiento',
                  'telefono', 'sexo', 'localidad']
        #widgets = {'fecha_nacimiento': DateWidget(usel10n=True, bootstrap_version=3)
        #}
