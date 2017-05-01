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
    url(r'^user/followers/(?P<username>[\w\-]+)/$', easypadel.views.viewSeguidores, name='viewSeguidores'),
    url(r'^user/following/(?P<username>[\w\-]+)/$', easypadel.views.viewSiguiendo, name='viewSiguiendo'),
    url(r'^user/follow/(?P<username>[\w\-]+)$', easypadel.views.seguirUsuario, name='seguirUsuario'),
    url(r'^user/unfollow/(?P<username>[\w\-]+)$', easypadel.views.dejarSeguirUsuario, name='dejarSeguirUsuario'),


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

    url(r'^post/create$', easypadel.views.createPost, name="createPost"),
    url(r'^post/delete/(?P<post_id>[0-9]+)/$', easypadel.views.deletePost, name="deletePost"),

    url(r'^propuesta/create$', easypadel.views.createPropuesta, name="createPropuesta"),
    url(r'^propuesta/list/(?P<username>[\w\-]+)$', easypadel.views.listPropuestas, name='listPropuestas'),
    url(r'^propuesta/listAbiertas$', easypadel.views.listPropuestasAbiertas, name='listPropuestasAbiertas'),
    url(r'^propuesta/delete/(?P<propuesta_id>[0-9]+)/$', easypadel.views.deletePropuesta, name="deletePropuesta"),
    url(r'^propuesta/view/(?P<propuesta_id>[0-9]+)/$', easypadel.views.viewPropuesta, name="viewPropuesta"),
    url(r'^propuesta/join/(?P<propuesta_id>[0-9]+)/$', easypadel.views.apuntarsePartido, name="apuntarsePartido"),

    url(r'^admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
