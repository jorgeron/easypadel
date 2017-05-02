from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget
from django.forms.widgets import ClearableFileInput, CheckboxInput, NumberInput, TimeInput
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.utils.html import conditional_escape
from django.forms import inlineformset_factory
from datetime import datetime,timedelta

from easypadel.models import Actor, Jugador, Administrador, Empresa, Pista, Horario, FranjaHoraria, DiaAsignacionHorario, Post, Propuesta, Comentario


class ImageInputWidget(ClearableFileInput):
    template_normal = (
        u'<div class="input-group">'
        u'<span class="input-group-btn"><span class="btn btn-info btn-file"> <span class="glyphicon glyphicon-upload"></span> %(input)s</span></span>'
        u'<input type="text" class="form-control" placeholder="%(placetext)s" readonly>'
        u'</div>'
    )
    template_with_initial = (
        u'%(initial_text)s: <img src="%(initial_url)s" alt="%(initial)s" style="max-height:100px"> '
        u'%(clear_template)s<br />%(input_text)s: ' + template_normal
    )
    template_with_clear = u'%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = self.template_normal
        substitutions['placetext'] = _("No image selected")
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)
        if self.is_initial(value):
            template = self.template_with_initial
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions
        return mark_safe(template % substitutions)



class BaseForm(ModelForm):
    required_css_class = 'required'

class UserCreationForm(UserCreationForm, BaseForm):
    pass

class JugadorForm(BaseForm):
# terms = forms.BooleanField(
#   error_messages={'required': _('You must accept the terms and conditions')},
#   label=_("I accept the <a href='/conditions'>Terms&Conditions</a>"))
    class Meta:
        model = Jugador
        fields = ['nombre', 'apellidos', 'fecha_nacimiento', 'email',
                  'telefono', 'sexo', 'localidad']
        widgets = {'fecha_nacimiento': DateWidget(usel10n=True, bootstrap_version=3)
        }

class AdminForm(BaseForm):
    class Meta:
        model = Administrador
        fields = ['nombre', 'email','telefono']

class EmpresaForm(BaseForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'email','telefono', 'direccion']

class PistaForm(BaseForm):
    class Meta:
        model = Pista
        fields = ['nombre', 'tipo_superficie', 'tipo_pared', 'cubierta', 
                    'descripcion', 'foto' ]
        widgets = {
            'foto': ImageInputWidget,
        }

class HorarioForm(BaseForm):
    class Meta:
        model = Horario
        fields = ['nombre']

class FranjaHorariaForm(ModelForm):
    class Meta:
        model = FranjaHoraria
        exclude = ('dia_asignacion', 'asignada')
        widgets = {
            'hora_inicio' : TimeInput(attrs={'placeholder':'HH:MM', 'format':'%H:%M'}),
            'hora_fin' : TimeInput(attrs={'placeholder':'HH:MM', 'format':'%H:%M'})
        }

FranjaHorariaFormSet = inlineformset_factory(Horario, FranjaHoraria,
                                            form=FranjaHorariaForm, extra=1, can_delete=True)

class DiaAsignacionHorarioForm(ModelForm):
    class Meta:
        model = DiaAsignacionHorario
        exclude = ('pista',)
        widgets = {'dia' : DateWidget(usel10n=True, bootstrap_version=3)}

class FiltroFechasHorariosForm(forms.Form):
    hoy = datetime.now().date()
    hoy_mas_7_dias = hoy + timedelta(days=7)

    fecha_inicio = forms.DateField(initial=hoy, widget=DateWidget(usel10n=True, bootstrap_version=3, attrs={'class':'datepicker'}))
    fecha_fin = forms.DateField(initial=hoy_mas_7_dias, widget=DateWidget(usel10n=True, bootstrap_version=3, attrs={'class':'datepicker'}))



class ProfileForm(BaseForm):
    class Meta:
        model = Actor
        fields = ['nombre', 'email', 'telefono', 'descripcion', 'foto_perfil', 'foto_cabecera']
        widgets = {
            'foto_perfil': ImageInputWidget,
            'foto_cabecera': ImageInputWidget,
        }

class JugadorProfileForm(ProfileForm):
    class Meta:
        model = Jugador
        fields = ['apellidos', 'localidad'] + ProfileForm.Meta.fields
        widgets = ProfileForm.Meta.widgets

class EmpresaProfileForm(ProfileForm):
    class Meta:
        model = Empresa
        fields = ['direccion'] + ProfileForm.Meta.fields
        widgets = ProfileForm.Meta.widgets


class PostForm(BaseForm):
    class Meta:
        model = Post
        fields = ['texto', 'foto']
        widgets = {
          'texto': forms.Textarea(attrs={'rows':4, 'cols':15, 'style':'resize:none;', 'placeholder':'Introduzca el texto aquí. Máximo 200 caracteres.'}),
          'foto': ImageInputWidget,
        }
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['texto'].label = ''


class ComentarioForm(BaseForm):
    class Meta:
        model = Comentario
        fields = ['texto', 'foto']
        widgets = {
          'texto': forms.Textarea(attrs={'rows':4, 'cols':15, 'style':'resize:none;', 'placeholder':'Introduzca el texto aquí. Máximo 200 caracteres.'}),
          'foto': ImageInputWidget,
        }
    def __init__(self, *args, **kwargs):
        super(ComentarioForm, self).__init__(*args, **kwargs)
        self.fields['texto'].label = ''

class PropuestaForm(BaseForm):
    class Meta:
        model = Propuesta
        fields = ['titulo', 'descripcion', 'fecha_partido', 'fecha_limite', 'tipo_partido', 'sitio']
        widgets = {
          'descripcion': forms.Textarea(attrs={'rows':4, 'cols':15, 'style':'resize:none;'}),
          'fecha_partido': DateTimeWidget(usel10n = True, bootstrap_version=3),
          'fecha_limite': DateTimeWidget(usel10n = True, bootstrap_version=3),
        }