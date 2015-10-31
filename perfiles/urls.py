from django.conf.urls import url
from django.contrib.auth import views as auth_views

import views

urlpatterns = [
    url(r'^registro/$', views.registro, name="registro"),
    url(r'^login/$', auth_views.login, {'template_name': 'perfiles/login.html'}, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^mi_perfil/$', views.perfil_propio, name="perfil_propio"),
    url(r'^mi_perfil_libros/$', views.perfil_propio_libros, name="perfil_propio_libros"),
    url(r'^editar_perfil/$', views.editar_perfil, name="editar_perfil"),    
    
    url(r'^usuario/libros/(?P<username>[-\w.]+)/$', views.perfil_usuario_libros, name="perfil_usuario_libros"),
    url(r'^usuario/(?P<username>[-\w.]+)/$', views.perfil_usuario, name="perfil_usuario"),
    url(r'^editar_libro_leido/$', views.editar_libro_leido, name="editar_libro_leido"),

    # Ajax
    url(r'^leyendo_libro_ajax/$', views.leyendo_libro_ajax, name="leyendo_libro_ajax"),
    url(r'^libros_usuario_ajax/$', views.libros_usuario_ajax, name="libros_usuario_ajax"),
    url(r'^termino_leer_ajax/$', views.termino_leer_ajax, name="termino_leer_ajax"),
    url(r'^eliminar_libro_leido_ajax/$', views.eliminar_libro_leido_ajax, name="eliminar_libro_leido_ajax"),
]
