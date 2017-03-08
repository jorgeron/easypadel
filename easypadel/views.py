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

from easypadel.decorators import anonymous_required, admin_group, jugadores_group, empresas_group
from easypadel.forms import JugadorForm, AdminForm, EmpresaForm, PistaForm
from easypadel.models import Pista, Empresa

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