from django.conf.urls import url
import views

urlpatterns = [
	url(r'^crear_grupo/$', views.crear_grupo, name="crear_grupo"),
	url(r'^main/(?P<id_grupo>\d+)/$', views.main_grupo, name="main_grupo"),
	url(r'^invitar/(?P<id_grupo>\d+)/$', views.invitar, name="invitar"),
	url(r'^invitar_ajax/$', views.invitar_ajax, name="invitar_ajax"),
	url(r'^aceptar_ajax/$', views.aceptar_ajax, name="aceptar_ajax"),
	url(r'^request_entrar_ajax/$', views.request_entrar_ajax, name="request_entrar_ajax"),
	url(r'^negar_invitacion/$', views.negar_invitacion, name="negar_invitacion"),
	url(r'^editar_grupo/(?P<id_grupo>\d+)/$', views.editar_grupo, name="editar_grupo")
]
