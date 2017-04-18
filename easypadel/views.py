from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.db import IntegrityError
from datetime import datetime,timedelta
from django.forms.forms import NON_FIELD_ERRORS


from easypadel.decorators import anonymous_required, admin_group, jugadores_group, empresas_group
from easypadel.forms import JugadorForm, AdminForm, EmpresaForm, PistaForm, HorarioForm, FranjaHorariaFormSet, DiaAsignacionHorarioForm, FiltroFechasHorariosForm
from django.forms import inlineformset_factory

from easypadel.models import Pista, Empresa, Horario, FranjaHoraria, DiaAsignacionHorario, Jugador

# Create your views here.
def home(request):
    if request.user.is_anonymous():

        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = authenticate(username=request.POST[
                                    'username'], password=request.POST['password'])
                if user is not None and user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(request.GET['next'] if 'next' in request.GET else '/')
        else:
            form = AuthenticationForm()
        return render(request, 'home.html', {'form':form})

    else:
        return render(request, 'timeline.html')



@anonymous_required
def appLogin(request):
    if request.method=='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])  
            if user is not None and user.is_active:
                login(request, user)
                return HttpResponseRedirect(request.GET['next'] if 'next' in request.GET else '/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form':form})


@login_required
def appLogout(request):
    logout(request)
    return HttpResponseRedirect('/')


@anonymous_required
def registroJugador(request):
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        form2 = JugadorForm(request.POST)
        if form.is_valid():
            if form2.is_valid():
                #Comprobamos edad > 16 años (16 años = 5840 dias)
                hoy = datetime.now().date()
                hoy_menos_16_anios = hoy - timedelta(days=5840)
                if form2.cleaned_data['fecha_nacimiento'] > hoy_menos_16_anios:
                    form2.full_clean()
                    form2._errors['fecha_nacimiento'] = form.error_class(['Debes tener más de 16 años para registrarte'])
                    return render(request, 'registration.html', {'form':form, 'formJugador':form2, 'role':_("Jugador")})

                new_user = form.save()
                new_jugador = form2.save(commit=False)
                new_jugador.user_id = new_user.id
                new_jugador.save()
                g = Group.objects.get(name='Jugadores')
                g.user_set.add(new_user)     
                return HttpResponseRedirect('/registroCompleto/0')
    else:
        form = UserCreationForm()
        form2= JugadorForm()
    return render(request, 'registration.html', {'form':form, 'formJugador':form2, 'role':_("Jugador")})


@user_passes_test(admin_group)
def registroAdministrador(request):
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        form2 = AdminForm(request.POST)
        
        if form.is_valid():
            if form2.is_valid():                
                new_user = form.save()
                new_admin = form2.save(commit=False)
                new_admin.user_id = new_user.id
                new_admin.save()      
                g = Group.objects.get(name='Administrators') 
                g.user_set.add(new_user)      
                return HttpResponseRedirect('/registroCompleto/1')
    else:
        form = UserCreationForm()
        form2= AdminForm()
    return render(request, 'registration.html', {'form':form, 'formAdmin':form2, 'role':_("Administrador")})


@user_passes_test(admin_group)
def registroEmpresa(request):
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        form2 = EmpresaForm(request.POST)
        
        if form.is_valid():
            if form2.is_valid():                
                new_user = form.save()
                new_empresa = form2.save(commit=False)
                new_empresa.user_id = new_user.id
                new_empresa.save()      
                g = Group.objects.get(name='Empresas') 
                g.user_set.add(new_user)      
                return HttpResponseRedirect('/registroCompleto/2')
    else:
        form = UserCreationForm()
        form2= EmpresaForm()
    return render(request, 'registration.html', {'form':form, 'formEmpresa':form2, 'role':_("Empresa")})



def registroCompleto(request, rtype):
    return render(request, 'registroCompleto.html', {'type':rtype})

@login_required
def deleteUser(request):
    user = User.objects.get(pk = request.user.id)
    user.delete()
    return appLogout(request)


@login_required
def listPistas(request, user_id):
    pistas = Pista.objects.filter(empresa=Empresa.objects.get(user_id = user_id))
    propietario = (user_id == str(request.user.id))
    return render(request, 'listPistas.html', {'list':pistas, 'propietario':propietario})

@login_required
def viewPista(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)
    editable = (request.user == pista.empresa.user)
    return render(request, 'viewPista.html', {'pista':pista, 'editable':editable})

def auxPistaForm(instance, *args):
    return PistaForm(instance = instance, *args)

@user_passes_test(empresas_group)
def editPista(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)
    if request.method=='POST':
        form = auxPistaForm(pista, request.POST, request.FILES)
        if form.is_valid():
            #Comprobamos si existe otra pista con el mismo nombre en la misma empresa
            empresa_id = (Empresa.objects.get(user=request.user)).id
            pistas_empresa = Pista.objects.filter(empresa_id = empresa_id)
            for p in pistas_empresa:
                if (p.nombre.capitalize() == form.cleaned_data['nombre'].capitalize()) and (p.id != int(pista_id)):
                    form.full_clean()
                    form._errors['nombre'] = form.error_class(['Ya existe otra pista con el mismo nombre en estas instalaciones'])
                    return render(request, 'form.html', {'form':form, 'pista':pista,'class':_('Pista'), 'operation':_('Editar')})
                    
            form.save()
            return HttpResponseRedirect(reverse('viewPista', kwargs={'pista_id':pista_id}))
    else:
        form = PistaForm(instance = pista)
    return render(request, 'form.html', {'form':form, 'pista':pista,'class':_('Pista'), 'operation':_('Editar')})

@user_passes_test(empresas_group)
def deletePista(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)
    pista.delete()
    return listPistas(request)

@user_passes_test(empresas_group)
def createPista(request):
    if request.method=='POST':
        form = PistaForm(request.POST, request.FILES)
        if form.is_valid():
            #Comprobamos si existe otra pista con el mismo nombre en la misma empresa
            empresa_id = (Empresa.objects.get(user=request.user)).id
            pistas_empresa = Pista.objects.filter(empresa_id = empresa_id)
            for p in pistas_empresa:
                if p.nombre.capitalize() == form.cleaned_data['nombre'].capitalize():
                    form.full_clean()
                    form._errors['nombre'] = form.error_class(['Ya existe otra pista con el mismo nombre en estas instalaciones'])
                    return render(request, 'form.html', {'form':form, 'class':_('Pista'), 'operation':_('Crear')})

            new_pista = form.save(commit=False)
            new_pista.empresa_id = empresa_id
            new_pista.save()    
            return HttpResponseRedirect(reverse('listPistas'))
    else:
        form = PistaForm()
    return render(request, 'form.html', {'form':form, 'class':_('Pista'), 'operation':_('Crear')})





@login_required
def listHorarios(request):
    horarios = Horario.objects.filter(empresa=Empresa.objects.get(user=request.user))
    return render(request, 'listHorarios.html', {'list':horarios})

@login_required
def viewHorario(request, horario_id):
    horario = Horario.objects.get(pk = horario_id)
    editable = (request.user == horario.empresa.user)
    franjasHorarias = FranjaHoraria.objects.filter(horario__id = horario_id, asignada=False)
    return render(request, 'viewHorario.html', {'horario':horario, 'editable':editable,
     'franjasHorarias':franjasHorarias})

@user_passes_test(empresas_group)
def deleteHorario(request, horario_id):
    franjas_horarias = FranjaHoraria.objects.filter(horario__id = horario_id)
    for f in franjas_horarias:
        if f.dia_asignacion:
            f.dia_asignacion.delete()

    horario = Horario.objects.get(pk = horario_id)
    horario.delete()
    
    return listHorarios(request)


@user_passes_test(empresas_group)
def createHorario(request):
    horario = Horario()
    if request.method=='POST':
        form = HorarioForm(request.POST, instance = horario)
        formFranjas = FranjaHorariaFormSet(request.POST, instance = horario)
        if form.is_valid() and formFranjas.is_valid():
            empresa_id = (Empresa.objects.get(user=request.user)).id
            #comprobamos si existe otro horario con el mismo nombre en la misma empresa
            horarios_empresa = Horario.objects.filter(empresa_id = empresa_id)
            for h in horarios_empresa:
                if h.nombre.capitalize() == form.cleaned_data['nombre'].capitalize():
                    form.full_clean()
                    form._errors['nombre'] = form.error_class(['Ya existe otro horario con el mismo nombre en esta empresa'])
                    return render(request, 'formHorario.html', {'form':form, 'formFranjas':formFranjas, 'class':_('Horario'), 'operation':_('Crear')})


            horario = form.save(commit=False)
            horario.empresa_id = empresa_id
            horario.save()
            formFranjas.save()    

            return HttpResponseRedirect(reverse('listHorarios'))
    else:
        horario = Horario()
        form = HorarioForm(instance = horario)
        formFranjas = FranjaHorariaFormSet(instance = horario)
    return render(request, 'formHorario.html', {'form':form, 'formFranjas':formFranjas, 'class':_('Horario'), 'operation':_('Crear')})



''' PASAR PARÁMETROS A INLINE FORM
    def get_field_qs(field, **kwargs):
        formfield = field.formfield(**kwargs)
        if field.name == 'pista':
            formfield.queryset = formfield.queryset.filter(empresa=Empresa.objects.get(user=request.user))
        return formfield

    DiaAsignacionHorarioFormSet = inlineformset_factory(Horario, DiaAsignacionHorario,
    form=DiaAsignacionHorarioForm, formfield_callback=get_field_qs, extra=1, can_delete=True)'''


@user_passes_test(empresas_group)
def asignarHorario(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)
    horarios = Horario.objects.filter(empresa=Empresa.objects.get(user=request.user))

    horarios_validos = []
    for h in horarios:
        franjas = FranjaHoraria.objects.filter(horario_id = h.id)
        if franjas:
            horarios_validos.append(h)

    
    dia_pista_horario = DiaAsignacionHorario()
    dia_pista_horario.pista_id = pista.id
    if request.method=='POST':

        form = DiaAsignacionHorarioForm(request.POST, instance=dia_pista_horario)

        if form.is_valid():
            franjas_horarias = FranjaHoraria.objects.filter(horario_id = request.POST.get('horario'), asignada=False)
            
            try:
                dia_pista_horario = form.save()
                for f in franjas_horarias:
                    new_franja = f
                    #Para que no actualice la existente y cree una nueva, cambiamos la PK
                    new_franja.pk = None
                    new_franja.dia_asignacion = dia_pista_horario
                    new_franja.asignada = True
                    new_franja.save()

                return HttpResponseRedirect(reverse('viewPista', kwargs={'pista_id':pista_id}))

            except IntegrityError as e:
                form = DiaAsignacionHorarioForm(instance=dia_pista_horario)
                form.full_clean()
                form._errors[NON_FIELD_ERRORS] = form.error_class(['Día ya asignado'])
                return render(request, 'formAsignarHorario.html', {'form':form, 'pista':pista, 
                    'horarios':horarios_validos, 'class':_('Horario'), 'operation':_('Asignar'), 'pista_id':pista_id})
            
    else:
        form = DiaAsignacionHorarioForm(instance=dia_pista_horario)
        return render(request, 'formAsignarHorario.html', {'form':form, 'pista':pista, 
            'horarios':horarios_validos, 'class':_('Horario'), 'operation':_('Asignar')})


@login_required
def viewHorarioPista(request, pista_id):
    pista = Pista.objects.get(pk=pista_id)
    

    if request.method == 'POST':
        formFechas = FiltroFechasHorariosForm(request.POST)
        if formFechas.is_valid():
            fecha_inicio = formFechas.cleaned_data['fecha_inicio']
            fecha_fin = formFechas.cleaned_data['fecha_fin']

    else:
        formFechas = FiltroFechasHorariosForm()

        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=7)
        #mostramos al principio la semana actual
        formFechas.fecha_inicio = fecha_inicio
        formFechas.fecha_fin = fecha_fin

    horario_pista = DiaAsignacionHorario.objects.filter(pista=pista)

    dic_dias_franjas = {}
    horario_pista_dias = []
    if horario_pista:
        horario_pista_dias = horario_pista.filter(dia__gte=fecha_inicio, dia__lte=fecha_fin)
    

    if horario_pista_dias:
        for dia in horario_pista_dias:
            franjas_horarias = FranjaHoraria.objects.filter(dia_asignacion = dia)
            dic_dias_franjas[dia.id] = franjas_horarias
    
    return render(request, 'viewHorarioPista.html', {'horario_pista_dias':horario_pista_dias, 'pista':pista,
        'dic_dias_franjas':dic_dias_franjas, 'formFechas':formFechas})



@user_passes_test(jugadores_group)
def listEmpresas(request):
    empresas = Empresa.objects.all()
    return render(request, 'listEmpresas.html', {'list':empresas})

@login_required
def viewEmpresa(request, empresa_id):
    empresa = Empresa.objects.get(pk = empresa_id)
    #editable = (request.user == horario.empresa.user)
    #franjasHorarias = FranjaHoraria.objects.filter(horario__id = horario_id, asignada=False)
    return render(request, 'profiles/show_profile_empresa.html', {'empresa':empresa})

@user_passes_test(jugadores_group)
def alquilarFranja(request, franjaHoraria_id):
    jugador = Jugador.objects.get(user_id = request.user.id)
    franja_horaria = FranjaHoraria.objects.get(pk = franjaHoraria_id)
    franja_horaria.disponible = False
    franja_horaria.jugador = jugador
    franja_horaria.save()
    return render(request, 'viewPista.html', {'pista':franja_horaria.dia_asignacion.pista})