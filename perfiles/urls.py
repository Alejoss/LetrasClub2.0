from django.conf.urls import url

import views

urlpatterns = [
    url(r'^registro/$', views.registro, name="registro"),
    url(r'^login/$', views.login_admin_bcompartida, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^mi_perfil/$', views.perfil_propio, name="perfil_propio"),
    url(r'^mi_perfil_libros/$', views.perfil_propio_libros, name="perfil_propio_libros"),
    url(r'^editar_perfil/$', views.editar_perfil, name="editar_perfil"),
    url(r'^redirigir_login/$', views.redirigir_login, name="redirigir_login"),

    url(r'^usuario/libros/(?P<username>[-\w.]+)/$', views.perfil_usuario_libros, name="perfil_usuario_libros"),
    url(r'^usuario/(?P<username>[-\w.]+)/$', views.perfil_usuario, name="perfil_usuario"),
    url(r'^editar_libro_leido/$', views.editar_libro_leido, name="editar_libro_leido"),
    url(r'^contactanos/(?P<razon_contacto>[-\w]+)/$', views.contactanos, name="contactanos"),
    url(r'^gracias_por_contactarnos/(?P<razon_contacto>[-\w]+)/(?P<correo_contacto>[\w\-@.]+)/$',
        views.DespuesContacto.as_view(), name="despues_contacto"),
    url(r'^nosotros/$', views.SobreNosotros.as_view(), name="sobre_nosotros"),

    # Ajax
    url(r'^leyendo_libro_ajax/$', views.leyendo_libro_ajax, name="leyendo_libro_ajax"),
    url(r'^libros_usuario_ajax/$', views.libros_usuario_ajax, name="libros_usuario_ajax"),
    url(r'^termino_leer_ajax/$', views.termino_leer_ajax, name="termino_leer_ajax"),
    url(r'^eliminar_libro_leido_ajax/$', views.eliminar_libro_leido_ajax, name="eliminar_libro_leido_ajax"),
]
