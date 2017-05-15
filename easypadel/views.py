from django.shortcuts import render, get_object_or_404
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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import formset_factory
from django.db import IntegrityError
from datetime import datetime,timedelta
from django.forms.forms import NON_FIELD_ERRORS
from django.db.models import Q

from django.dispatch import receiver
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from mytfg.settings import PAYPAL_IPN_DOMAIN, PAYPAL_URL

import re


from easypadel.decorators import anonymous_required, admin_group, jugadores_group, empresas_group
from easypadel.forms import JugadorForm, AdminForm, EmpresaForm, PistaForm, HorarioForm, FranjaHorariaFormSet, DiaAsignacionHorarioForm, FiltroFechasHorariosForm, JugadorProfileForm, EmpresaProfileForm, ProfileForm, PostForm, PropuestaForm, ComentarioForm, ValoracionForm, ValoracionEmpresaForm, ValoracionJugadorForm, ValoracionPistaForm
from django.forms import inlineformset_factory

from easypadel.models import Pista, Empresa, Horario, FranjaHoraria, DiaAsignacionHorario, Jugador, Post, Seguimiento, Propuesta, Participante, Comentario, Valoracion, ValoracionEmpresa, ValoracionJugador, ValoracionPista


def get_user_actor(user):
    if jugadores_group(user):
        return Jugador.objects.get(user=user)
    if empresas_group(user):
        return Empresa.objects.get(user=user)
    if admin_group(user):
        return Administrador.objects.get(user=user)
    raise Exception()

def get_page(request, queryset, howmany=8):
    paginator = Paginator(queryset, howmany)
    page = request.GET.get('page')
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        return paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)

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
        user = User.objects.get(pk = request.user.id)
        posts = get_page(request, Post.objects.filter(Q(user=user) | Q(user__seguidores__origen=request.user)).order_by('-fecha_publicacion').distinct())


        actor = get_user_actor(user)
        num_estrellas = 0
        num_estrellas_vacias = 5
        if actor.valoracion_total:
            num_estrellas = round(actor.valoracion_total)
            num_estrellas_vacias = 5 - num_estrellas

        return render(request, 'inicio.html', {'actor':actor, 'postform': PostForm(), 'posts':posts, 'num_estrellas':range(num_estrellas), 
        'num_estrellas_vacias':range(num_estrellas_vacias)})



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
    pistas = Pista.objects.filter(empresa=Empresa.objects.get(user_id = user_id)).order_by('-valoracion_total')
    propietario = (user_id == str(request.user.id))
    return render(request, 'listPistas.html', {'list':pistas, 'propietario':propietario})

@login_required
def viewPista(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)
    editable = (request.user == pista.empresa.user)

    num_estrellas = 0
    num_estrellas_vacias = 5
    if pista.valoracion_total:
        num_estrellas = round(pista.valoracion_total)
        num_estrellas_vacias = 5 - num_estrellas
    return render(request, 'viewPista.html', {'pista':pista, 'editable':editable, 'num_estrellas':range(num_estrellas),
        'num_estrellas_vacias':range(num_estrellas_vacias)})

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
    return listPistas(request, request.user.id)

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
            return HttpResponseRedirect(reverse('listPistas', kwargs={'user_id':request.user.id}))
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
    empresas = Empresa.objects.all().order_by('-valoracion_total')
    return render(request, 'listEmpresas.html', {'list':empresas})


@user_passes_test(jugadores_group)
def alquilarFranja(request, franjaHoraria_id):
    jugador = Jugador.objects.get(user_id = request.user.id)
    franja_horaria = FranjaHoraria.objects.get(pk = franjaHoraria_id)

    if franja_horaria.disponible and not franja_horaria.jugador and franja_horaria.asignada:
        # What you want the button to do.
        paypal_dict = {
            "business": franja_horaria.horario.empresa.paypalMail,
            "amount": franja_horaria.precio,
            "item_name": 'alquilerFranja#'+str(franja_horaria.id),
            "item_number": franja_horaria.id,
            "invoice": 'easyPadel.alquilerFranja#'+str(franja_horaria.id),
            "notify_url": PAYPAL_IPN_DOMAIN + reverse('paypal-ipn'),
            #"return_url": request.META.get('HTTP_HOST')+request.get_full_path(),
            "return_url": 'http://127.0.0.1:8000/pistas/viewHorarioPista/'+str(franja_horaria.dia_asignacion.pista.id),
            "currency_code": 'EUR',
            "cancel_return": 'http://127.0.0.1:8000/pistas/viewHorarioPista/'+str(franja_horaria.dia_asignacion.pista.id),
            "custom": jugador.user.username,  # Custom command to correlate to some function later (optional)
            "rm":1,
        }

        # Create the instance.
        paypalForm = PayPalPaymentsForm(initial=paypal_dict)

        return render(request, 'payment.html', {'franjaHoraria':franja_horaria, 'paypalForm':paypalForm})
    else:
        raise Http404("No puede alquilar esta franja horaria")
    


@receiver(valid_ipn_received)
def alquilarFranjaExito(sender, **kwargs):
    if sender.payment_status != ST_PP_COMPLETED:
        return # Not a valid payment
    franja_horaria = FranjaHoraria.objects.get(pk = sender.item_number)
    if not franja_horaria or franja_horaria.jugador or not franja_horaria.asignada or not franja_horaria.disponible or sender.receiver_email != franja_horaria.horario.empresa.paypalMail or sender.mc_gross != franja_horaria.precio or sender.mc_currency != "EUR":
        print('NO VÁLIDO')
        return # Not a valid payment
    
    jugador = Jugador.objects.get(user = User.objects.get(username = sender.custom))
    franja_horaria.disponible = False
    franja_horaria.jugador = jugador
    franja_horaria.save()

@login_required
def viewPerfil(request, username):
    user = get_object_or_404(User, username=username)
    show_user = get_user_actor(user)
    editable = (show_user.user == request.user)
    posts = get_page(request, user.post_set.order_by('-fecha_publicacion'))

    num_estrellas = 0
    num_estrellas_vacias = 5
    if show_user.valoracion_total:
        num_estrellas = round(show_user.valoracion_total)
        num_estrellas_vacias = 5 - num_estrellas

    return render(request, 'profiles/show_profile.html', {'show_user': show_user, 
        'editable': editable, 'posts':posts, 'postform': PostForm(), 'num_estrellas':range(num_estrellas), 
        'num_estrellas_vacias':range(num_estrellas_vacias)})



def chooseProfileForm(instance, *args):
    if type(instance) is Jugador:
        return JugadorProfileForm(instance=instance, *args)
    if type(instance) is Empresa:
        return EmpresaProfileForm(instance=instance, *args)
    return ProfileForm(instance=instance, *args)

@login_required
def editPerfil(request):
    instance = get_user_actor(request.user)
    if request.method=='POST':
        form = chooseProfileForm(instance, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':request.user.username}))
    else:
        form = chooseProfileForm(instance)
    return render(request, 'profiles/edit_profile.html', {'profile_form':form, 'user':instance})


@login_required
def createPost(request):
    rightNow = datetime.now()
    
    if request.method=='POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.fecha_publicacion = rightNow
            new_post.user = request.user
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', new_post.texto)
            for url in urls:
                if re.search("(http://)?(www\.)?(youtube|yimg|youtu)\.([A-Za-z]{2,4}|[A-Za-z]{2}\.[A-Za-z]{2})/(watch\?v=)?[A-Za-z0-9\-_]{6,12}(&[A-Za-z0-9\-_]{1,}=[A-Za-z0-9\-_]{1,})*", url) or re.search("vimeo\.com/(\d+)", url) or "soundcloud" in url: #"youtube" or "youtu.be" or "vimeo" or "soundcloud" in url:
                    new_post.video = url
                    break
            new_post.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    raise Http404()

@login_required
def deletePost(request, post_id):
    post = Post.objects.get(pk = post_id)
    if(request.user == post.user or request.user.groups.filter(name='Administradores').exists()):
        post.delete()
    else:
        raise Http404("No tiene permiso para eliminar este post.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    


@login_required
def seguirUsuario(request, username):
    user = get_object_or_404(User, username=username)
    if user==request.user or Seguimiento.objects.filter(origen = request.user, destino = user).exists():
        return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':user.username}))
    seguimiento = Seguimiento(origen = request.user, destino = user)
    seguimiento.save()
    return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':user.username}))

@login_required
def dejarSeguirUsuario(request, username):
    user = get_object_or_404(User, username=username)
    if user==request.user or not Seguimiento.objects.filter(origen = request.user, destino = user).exists():
        return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':user.username}))
    seguimiento = Seguimiento.objects.filter(origen = request.user, destino = user)
    seguimiento.delete()
    return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':user.username}))

@login_required
def viewSeguidores(request, username):
    user = get_object_or_404(User, username=username)
    followers = Seguimiento.objects.filter(destino = user)
    seguidores = []
    for seguidor in followers:
        seguidores.append(get_user_actor(seguidor.origen))
    return render(request, 'listUsers.html', {'list':seguidores})


@login_required
def viewSiguiendo(request, username):
    user = get_object_or_404(User, username=username)
    following = Seguimiento.objects.filter(origen = user)
    siguiendo = []
    for seguido in following:
        siguiendo.append(get_user_actor(seguido.destino))
    return render(request, 'listUsers.html', {'list':siguiendo})




@user_passes_test(jugadores_group)
def createPropuesta(request):
    if request.method=='POST':
        rightNow = datetime.now()

        form = PropuestaForm(request.POST)
        if form.is_valid():
            fecha_partido = form.cleaned_data['fecha_partido']
            fecha_limite = form.cleaned_data['fecha_limite']
            fecha_partido = fecha_partido.replace(tzinfo=None)
            fecha_limite = fecha_limite.replace(tzinfo=None)
            fecha_publicacion = rightNow
            if validaFechas(fecha_publicacion, fecha_limite, fecha_partido):
                new_propuesta = form.save(commit=False)
                new_propuesta.creador = Jugador.objects.get(user = request.user)
                new_propuesta.fecha_publicacion = fecha_publicacion
                new_propuesta.save()    
                return HttpResponseRedirect(reverse('listPropuestas', kwargs={'username':request.user.username}))
            else:
                form.full_clean()
                form._errors[NON_FIELD_ERRORS] = form.error_class(['Las fechas no son correctas'])
                return render(request, 'form.html', {'form':form, 'class':_('Propuesta'), 'operation':_('Crear')})

    else:
        form = PropuestaForm()
    return render(request, 'form.html', {'form':form, 'class':_('Propuesta'), 'operation':_('Crear')})


def validaFechas(fecha_publicacion, fecha_limite, fecha_partido):
    valido = (fecha_publicacion <= fecha_partido-timedelta(hours=2))
    valido = (valido and fecha_limite <= fecha_partido-timedelta(hours=1))
    valido = (valido and fecha_limite > fecha_publicacion)
    return valido


'''def listPropuestasCreadas(request, username):
    jugador = Jugador.objects.get(user = request.user)
    propuestas_creadas = Propuesta.objects.filter(creador = jugador)
    return render(request, 'listPropuestas.html', {'list':propuestas_creadas, 'creador':True})'''

@login_required
def listPropuestas(request, username):
    jugador = Jugador.objects.get(user = request.user)
    propuestas = []
    propuestas_creadas = Propuesta.objects.filter(creador = jugador)
    propuestas_participaciones = Participante.objects.filter(jugador = jugador)

    for p in propuestas_creadas:
        propuestas.append(p)
    for p in propuestas_participaciones:
        propuestas.append(p.propuesta)

    propuestas_ordenadas = sorted(propuestas, key=lambda propuesta: propuesta.fecha_partido)
    return render(request, 'listPropuestas.html', {'list':propuestas_ordenadas, 'creador':True})

@login_required
def listPropuestasAbiertas(request):
    rightNow = datetime.now()
    propuestas = []
    propuestas_consulta = Propuesta.objects.filter(fecha_limite__gte=rightNow)
    for p in propuestas_consulta:
        if p.participante_set.count() < 3:
            propuestas.append(p)

    propuestas_ordenadas = sorted(propuestas, key=lambda propuesta: propuesta.fecha_partido)
    return render(request, 'listPropuestas.html', {'list':propuestas_ordenadas, 'creador':False})

@user_passes_test(jugadores_group)
def deletePropuesta(request, propuesta_id):
    propuesta = Propuesta.objects.get(pk = propuesta_id)
    jugador = Jugador.objects.get(user = request.user)
    participantes = Participante.objects.filter(propuesta_id = propuesta.id)
    #si no hay participantes, se puede eliminar
    if propuesta.creador == jugador and not participantes:
        propuesta.delete()
    else:
        raise Http404("No tiene permiso para eliminar esta propuesta.")
    return listPropuestas(request, request.user.username)


@login_required
def viewPropuesta(request, propuesta_id):
    propuesta = Propuesta.objects.get(pk = propuesta_id)
    participantes = Participante.objects.filter(propuesta_id = propuesta_id)
    creador = (request.user == propuesta.creador.user)
    borrable = creador and not participantes

    fecha_limite_futura = fechaLimiteFutura(propuesta)
    participante = False
    for p in participantes:
        if p.jugador.user == request.user:
            participante = True

    comentarios = get_page(request, Comentario.objects.filter(propuesta_id = propuesta_id).order_by('-fecha_publicacion').distinct())

    return render(request, 'viewPropuesta.html', {'propuesta':propuesta, 'creador':creador, 'participante':participante, 'borrable':borrable, 'participantes':participantes, 'fecha_limite_futura':fecha_limite_futura, 'comentarioform': ComentarioForm(), 'comentarios':comentarios})


@user_passes_test(jugadores_group)
def apuntarsePartido(request, propuesta_id):
    propuesta = Propuesta.objects.get(pk = propuesta_id)
    participantes = Participante.objects.filter(propuesta_id = propuesta_id)
    jugador = Jugador.objects.get(user = request.user)
    rightNow = datetime.now()

    if len(participantes) < 3 and propuesta.creador != jugador and fechaLimiteFutura(propuesta):
        participante = Participante(propuesta = propuesta, jugador = jugador)
        participante.save()
    else:
        raise Http404("No tiene permiso para unirse a este partido")

    return viewPropuesta(request, propuesta_id)


def fechaLimiteFutura(propuesta):
    rightNow = datetime.now()
    limite = propuesta.fecha_limite.replace(tzinfo=None)
    return rightNow < limite



@user_passes_test(jugadores_group)
def createComentario(request, propuesta_id):
    rightNow = datetime.now()
    propuesta = Propuesta.objects.get(pk = propuesta_id)
    jugador = Jugador.objects.get(user = request.user)

    participantes = []
    for p in (Participante.objects.filter(propuesta = propuesta)):
        participantes.append(p.jugador)
    
    if jugador == propuesta.creador or jugador in participantes:

        if request.method=='POST':
            form = ComentarioForm(request.POST, request.FILES)
            if form.is_valid():
            
                new_comentario = form.save(commit=False)
                new_comentario.fecha_publicacion = rightNow
                new_comentario.jugador = jugador

                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', new_comentario.texto)
                for url in urls:
                    if re.search("(http://)?(www\.)?(youtube|yimg|youtu)\.([A-Za-z]{2,4}|[A-Za-z]{2}\.[A-Za-z]{2})/(watch\?v=)?[A-Za-z0-9\-_]{6,12}(&[A-Za-z0-9\-_]{1,}=[A-Za-z0-9\-_]{1,})*", url) or re.search("vimeo\.com/(\d+)", url) or "soundcloud" in url: #"youtube" or "youtu.be" or "vimeo" or "soundcloud" in url:
                        new_comentario.video = url
                        break
                new_comentario.propuesta_id = propuesta.id
                new_comentario.save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    raise Http404()


@login_required
def deleteComentario(request, comentario_id):
    comentario = Comentario.objects.get(pk = comentario_id)
    jugador = Jugador.objects.get(user = request.user)
    if(jugador == comentario.jugador or request.user.groups.filter(name='Administradores').exists()):
        comentario.delete()
    else:
        raise Http404("No tiene permiso para eliminar este comentario.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@user_passes_test(jugadores_group)
def createValoracionEmpresa(request, empresa_id):
    empresa = Empresa.objects.get(pk = empresa_id)

    if request.method=='POST':
        form = ValoracionEmpresaForm(request.POST)
        if form.is_valid():

            new_valoracion_empresa = form.save(commit=False)
            new_valoracion_empresa.emisor = request.user
            new_valoracion_empresa.empresa = empresa
            new_valoracion_empresa.fecha_publicacion = datetime.now()
            new_valoracion_empresa.save()

            actualizarValoracionesEmpresa(empresa, new_valoracion_empresa)

            return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':empresa.user.username}))
    else:
        form = ValoracionEmpresaForm()
    return render(request, 'form.html', {'form':form, 'operation':'Crear', 'class':'Valoración'})


@login_required
def createValoracionJugador(request, jugador_id):
    jugador = Jugador.objects.get(pk = jugador_id)

    if request.method=='POST':
        form = ValoracionJugadorForm(request.POST)
        if form.is_valid():

            new_valoracion_jugador = form.save(commit=False)
            new_valoracion_jugador.emisor = request.user
            new_valoracion_jugador.jugador = jugador
            new_valoracion_jugador.fecha_publicacion = datetime.now()
            new_valoracion_jugador.save()

            actualizarValoracionesJugador(jugador, new_valoracion_jugador)

            return HttpResponseRedirect(reverse('viewPerfil', kwargs={'username':jugador.user.username}))
    else:
        form = ValoracionJugadorForm()
    return render(request, 'form.html', {'form':form, 'operation':'Crear', 'class':'Valoración'})


@user_passes_test(jugadores_group)
def createValoracionPista(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)

    if request.method=='POST':
        form = ValoracionPistaForm(request.POST)
        if form.is_valid():

            new_valoracion_pista = form.save(commit=False)
            new_valoracion_pista.emisor = request.user
            new_valoracion_pista.pista = pista
            new_valoracion_pista.fecha_publicacion = datetime.now()
            new_valoracion_pista.save()

            actualizarValoracionesPista(pista, new_valoracion_pista)

            return HttpResponseRedirect(reverse('viewPista', kwargs={'pista_id':pista_id}))
    else:
        form = ValoracionPistaForm()
    return render(request, 'form.html', {'form':form, 'operation':'Crear', 'class':'Valoración'})


def actualizarValoracionesEmpresa(empresa, valoracion_empresa):
    valoraciones_empresa = ValoracionEmpresa.objects.filter(empresa = empresa)

    if len(valoraciones_empresa) > 1:

        calidad_precio_sum = 0
        personal_sum = 0
        limpieza_sum = 0
        for v in valoraciones_empresa:
            calidad_precio_sum += v.calidad_precio
            personal_sum += v.personal
            limpieza_sum += v.limpieza

        empresa.calidad_precio = calidad_precio_sum / len(valoraciones_empresa)
        empresa.personal = personal_sum / len(valoraciones_empresa)
        empresa.limpieza = limpieza_sum / len(valoraciones_empresa)

    else:
        empresa.calidad_precio = valoracion_empresa.calidad_precio
        empresa.personal = valoracion_empresa.personal
        empresa.limpieza = valoracion_empresa.limpieza

    empresa.valoracion_total = (empresa.calidad_precio + empresa.personal + empresa.limpieza) / 3
    empresa.save()


def actualizarValoracionesJugador(jugador, valoracion_jugador):
    valoraciones_jugador = ValoracionJugador.objects.filter(jugador = jugador)

    if len(valoraciones_jugador) > 1:

        nivel_juego_sum = 0
        fiabilidad_reserva_sum = 0
        sociabilidad_sum = 0
        for v in valoraciones_jugador:
            nivel_juego_sum += v.nivel_juego
            fiabilidad_reserva_sum += v.fiabilidad_reserva
            sociabilidad_sum += v.sociabilidad

        jugador.nivel_juego = nivel_juego_sum / len(valoraciones_jugador)
        jugador.fiabilidad_reserva = fiabilidad_reserva_sum / len(valoraciones_jugador)
        jugador.sociabilidad = sociabilidad_sum / len(valoraciones_jugador)
    else:
        jugador.nivel_juego = valoracion_jugador.nivel_juego
        jugador.fiabilidad_reserva = valoracion_jugador.fiabilidad_reserva
        jugador.sociabilidad = valoracion_jugador.sociabilidad

    jugador.valoracion_total = (jugador.nivel_juego + jugador.fiabilidad_reserva + jugador.sociabilidad) / 3
    jugador.save()


def actualizarValoracionesPista(pista, valoracion_pista):
    valoraciones_pista = ValoracionPista.objects.filter(pista = pista)

    if len(valoraciones_pista) > 1:

        estado_sum = 0
        iluminacion_sum = 0

        for v in valoraciones_pista:
            estado_sum += v.estado
            iluminacion_sum += v.iluminacion

        pista.estado = estado_sum / len(valoraciones_pista)
        pista.iluminacion = iluminacion_sum / len(valoraciones_pista)
    else:
        pista.estado = valoracion_pista.estado
        pista.iluminacion = valoracion_pista.iluminacion

    pista.valoracion_total = (pista.estado + pista.iluminacion) / 2
    pista.save()



@login_required
def listValoracionesUsuario(request, user_id):
    user = User.objects.get(pk = user_id)
    if jugadores_group(user):
        valoraciones = get_page(request, ValoracionJugador.objects.filter(jugador = Jugador.objects.get(user=user)).order_by('-fecha_publicacion').distinct())
    else:
        valoraciones = get_page(request, ValoracionEmpresa.objects.filter(empresa = Empresa.objects.get(user=user)).order_by('-fecha_publicacion').distinct())

    return render(request, 'listValoraciones.html', {'valoraciones':valoraciones})


@login_required
def listValoracionesPista(request, pista_id):
    pista = Pista.objects.get(pk = pista_id)
    valoraciones = get_page(request, ValoracionPista.objects.filter(pista = pista).order_by('-fecha_publicacion').distinct())
    return render(request, 'listValoraciones.html', {'valoraciones':valoraciones})

