from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _

from easypadel.decorators import anonymous_required, admin_group, jugadores_group, empresas_group
from easypadel.forms import JugadorForm, AdminForm, EmpresaForm

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