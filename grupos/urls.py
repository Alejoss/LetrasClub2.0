from django.conf.urls import url
import views

urlpatterns = [
	url(r'^crear_grupo/$', views.crear_grupo, name="crear_grupo"),
	url(r'^main/(?P<id_grupo>\d+)/libros/(?P<queryset>\w+)/$', views.main_grupo_libros, name="main_grupo_libros"),
	url(r'^main/(?P<id_grupo>\d+)/actividad/(?P<queryset>\w+)/$', views.main_grupo_actividad, name="main_grupo_actividad"),
	url(r'^compartir_libro_grupo/(?P<id_grupo>\d+)/$', views.compartir_libro_grupo, name="compartir_libro_grupo"),
	url(r'^invitar/(?P<id_grupo>\d+)/$', views.invitar, name="invitar"),
	url(r'^editar_grupo/(?P<id_grupo>\d+)/$', views.editar_grupo, name="editar_grupo"),
	url(r'^buscar/(?P<id_grupo>\d+)/(?P<filtro>\w+)/$', views.buscar_libro_grupo, name='buscar_libro_grupo'),

	url(r'^invitar_ajax/$', views.invitar_ajax, name="invitar_ajax"),
	url(r'^aceptar_ajax/$', views.aceptar_ajax, name="aceptar_ajax"),
	url(r'^request_entrar_ajax/$', views.request_entrar_ajax, name="request_entrar_ajax"),
	url(r'^negar_invitacion_ajax/$', views.negar_invitacion_ajax, name="negar_invitacion_ajax")
]
