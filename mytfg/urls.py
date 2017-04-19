"""mytfg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from mytfg import settings
import easypadel.views

urlpatterns = [
	url(r'^$', easypadel.views.home, name='index'),
	url(r'^logout/$', easypadel.views.appLogout, name='logout'),

    url(r'^user/delete$', easypadel.views.deleteUser, name='deleteUser'),
    url(r'^user/profile/view/(?P<username>[\w\-]+)$', easypadel.views.viewPerfil, name='viewPerfil'),
    url(r'^user/profile/edit$', easypadel.views.editPerfil, name='editPerfil'),

	url(r'^jugador/registration/$', easypadel.views.registroJugador, name='registroJugador'),
    url(r'^administrador/registration/$', easypadel.views.registroAdministrador, name='registroAdministrador'),
    url(r'^empresa/registration/$', easypadel.views.registroEmpresa, name='registroEmpresa'),
	url(r'^registroCompleto/(?P<rtype>\d+)$', easypadel.views.registroCompleto, name='registroCompleto'),

    url(r'^empresa/pistas/list/(?P<user_id>[0-9]+)/$', easypadel.views.listPistas, name='listPistas'),
    url(r'^empresa/pistas/create$', easypadel.views.createPista, name='createPista'),
    url(r'^empresa/pistas/edit/(?P<pista_id>[0-9]+)/$', easypadel.views.editPista, name='editPista'),
    url(r'^empresa/pistas/delete/(?P<pista_id>[0-9]+)/$', easypadel.views.deletePista, name='deletePista'),
    url(r'^empresa/pistas/asignarHorario/(?P<pista_id>[0-9]+)/$', easypadel.views.asignarHorario, name='asignarHorario'),
    url(r'^empresa/horarios/list$', easypadel.views.listHorarios, name='listHorarios'),
    url(r'^empresa/horarios/create$', easypadel.views.createHorario, name='createHorario'),
    url(r'^empresa/horarios/delete/(?P<horario_id>[0-9]+)/$', easypadel.views.deleteHorario, name='deleteHorario'),
    
    url(r'^empresas/list$', easypadel.views.listEmpresas, name='listEmpresas'),

    url(r'^pistas/view/(?P<pista_id>[0-9]+)/$', easypadel.views.viewPista, name='viewPista'),
    url(r'^pistas/viewHorarioPista/(?P<pista_id>[0-9]+)/$', easypadel.views.viewHorarioPista, name='viewHorarioPista'),
    url(r'^horarios/view/(?P<horario_id>[0-9]+)/$', easypadel.views.viewHorario, name='viewHorario'),

    url(r'^pistas/alquilar/(?P<franjaHoraria_id>[0-9]+)/$', easypadel.views.alquilarFranja, name='alquilarFranja'),

    url(r'^admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
