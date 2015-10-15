from django.conf.urls import url
from django.contrib.auth import views as auth_views

import views

urlpatterns = [
    url(r'^registro/$', views.registro, name="registro"),
    url(r'^login/$', auth_views.login, {'template_name': 'perfiles/login.html'}, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^mi_perfil/$', views.perfil_propio, name="perfil_propio"),
    url(r'^editar_perfil/$', views.editar_perfil, name="editar_perfil"),    
    url(r'^/perfil/(?P<username>[-\w.]+)/$', views.perfil_usuario, name="perfil_usuario"),

    url(r'^leyendo_libro_ajax/$', views.leyendo_libro_ajax, name="leyendo_libro_ajax"),
    url(r'^libros_usuario_ajax/$', views.libros_usuario_ajax, name="libros_usuario_ajax"),
]
