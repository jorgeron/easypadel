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
from django.forms import formset_factory
from datetime import datetime,timedelta

from easypadel.decorators import anonymous_required, admin_group, jugadores_group, empresas_group
from easypadel.forms import JugadorForm, AdminForm, EmpresaForm, PistaForm, HorarioForm, FranjaHorariaFormSet, DiaAsignacionHorarioForm
from django.forms import inlineformset_factory

from easypadel.models import Pista, Empresa, Horario, FranjaHoraria, DiaAsignacionHorario

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
def listPistas(request):
    pistas = Pista.objects.filter(empresa=Empresa.objects.get(user=request.user))
    return render(request, 'listPistas.html', {'list':pistas})

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
            new_pista = form.save(commit=False)
            new_pista.empresa_id = (Empresa.objects.get(user=request.user)).id
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
    franjasHorarias = FranjaHoraria.objects.filter(horario__id = horario_id)
    return render(request, 'viewHorario.html', {'horario':horario, 'editable':editable,
     'franjasHorarias':franjasHorarias})

@user_passes_test(empresas_group)
def deleteHorario(request, horario_id):
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

            horario = form.save(commit=False)
            horario.empresa_id = (Empresa.objects.get(user=request.user)).id
            horario.save()
            formFranjas.save()    

            return HttpResponseRedirect(reverse('listHorarios'))
    else:
        horario = Horario()
        form = HorarioForm(instance = horario)
        formFranjas = FranjaHorariaFormSet(instance = horario)
    return render(request, 'formHorario.html', {'form':form, 'formFranjas':formFranjas, 'class':_('Horario'), 'operation':_('Crear')})



@user_passes_test(empresas_group)
def asignarHorario(request, horario_id):
    horario = Horario.objects.get(pk = horario_id)
    pistas = Pista.objects.filter(empresa=Empresa.objects.get(user=request.user))
    dia_pista_horario = DiaAsignacionHorario()

    def get_field_qs(field, **kwargs):
        formfield = field.formfield(**kwargs)
        if field.name == 'pista':
            formfield.queryset = formfield.queryset.filter(empresa=Empresa.objects.get(user=request.user))
        return formfield

    DiaAsignacionHorarioFormSet = inlineformset_factory(Horario, DiaAsignacionHorario,
    form=DiaAsignacionHorarioForm, formfield_callback=get_field_qs, extra=1, can_delete=True)

    if request.method=='POST':
        form = DiaAsignacionHorarioFormSet(request.POST, instance=horario)
        if form.is_valid():
            dia_pista_horario.dia = form.save()
            return HttpResponseRedirect(reverse('viewHorario', kwargs={'horario_id':horario_id}))
    else:
        form = DiaAsignacionHorarioFormSet(instance=horario)
    return render(request, 'formAsignarHorario.html', {'form':form, 'horario':horario,
     'class':_('Horario'), 'operation':_('Asignar')})



@login_required
def viewHorarioPista(request, pista_id):
    pista = Pista.objects.get(pk=pista_id)
    hoy = datetime.now().date()
    hoy_mas_7_dias = hoy + timedelta(days=7)
    #mostramos al principio la semana actual
    horario_pista = DiaAsignacionHorario.objects.filter(pista=pista)
    horario_pista_dias = horario_pista.filter(dia__gte=hoy, dia__lte=hoy_mas_7_dias)
    return render(request, 'viewHorarioPista.html', {'horario_pista_dias':horario_pista_dias, 'pista':pista})