from django.conf.urls import url
import views

urlpatterns = [    
    url(r'^main/$', views.main, name="main"),
    url(r'^nuevo_libro/(?P<tipo_dueno>\w+)/(?P<username>[-\w.]+)/$', views.nuevo_libro, name="nuevo_libro"),
    url(r'^mi_biblioteca/$', views.mi_biblioteca, name="mi_biblioteca"),
    url(r'^ciudad/(?P<slug_ciudad>\w+)/(?P<id_ciudad>\d+)/(?P<filtro>\w+)/$', views.libros_ciudad, name="libros_ciudad"),
    url(r'^buscar_ciudad/$', views.buscar_ciudad, name="buscar_ciudad"),

    url(r'^libro/(?P<slug_libro>\w+)/(?P<id_libro>\d+)/$', views.libro, name="libro"),

    url(r'^pedirlibro/(?P<id_libro_disponible>\d+)/(?P<id_grupo>\d+)/$', views.pedir_libro, name="pedir_libro_grupo"),
    url(r'^pedirlibro/(?P<id_libro_disponible>\d+)/$', views.pedir_libro, name="pedir_libro"),
    url(r'^libro_request/(?P<libro_request_id>\d+)/$', views.libro_request, name="libro_request"),

    url(r'^prestar_libro/(?P<libro_request_id>\d+)/$', views.prestar_libro, name="prestar_libro"),
    
    url(r'^biblioteca_compartida/(?P<slug_biblioteca_compartida>[-\w]+)/$', views.biblioteca_compartida, name="biblioteca_compartida"),

    url(r'^nueva_biblioteca_compartida/(?P<slug_ciudad>\w+)/(?P<id_ciudad>\d+)/$', views.nueva_biblioteca_compartida, 
        name="nueva_biblioteca_compartida"),
    url(r'^editar_info_bcompartida/(?P<slug_biblioteca_compartida>[-\w]+)/$', views.editar_info_bcompartida, 
        name="editar_info_bcompartida"),
    url(r'^editar_libros_bcompartida/(?P<slug_biblioteca_compartida>[-\w]+)/$', views.editar_libros_bcompartida, 
        name="editar_libros_bcompartida"),
    url(r'^prestar_libro_biblioteca_compartida/(?P<id_libro_compartido>\d+)/$', views.prestar_libro_bcompartida, 
        name="prestar_libro_bcompartida"),

    url(r'^cambiar_libro_bcompartida_g/(?P<id_biblioteca_compartida>\d+)/$', views.cambiar_libro_bcompartida, 
        name="cambiar_libro_bcompartida_g"),  # url cambiar libro sin parametro id_libro_compartido
    url(r'^cambiar_libro_bcompartida/(?P<id_biblioteca_compartida>\d+)/(?P<id_libro_compartido>\d+)/$', views.cambiar_libro_bcompartida, 
        name="cambiar_libro_bcompartida"),

    url(r'^anunciar_devolucion/$', views.anunciar_devolucion, 
        name="anunciar_devolucion"),
    url(r'^cancelar_pedido/$', views.cancelar_pedido, 
        name="cancelar_pedido"),
    url(r'^cancelar_pedido_bcompartida/$', views.cancelar_pedido_bcompartida, 
        name="cancelar_pedido_bcompartida"),

    url(r'^buscar/(?P<slug_ciudad>\w+)/(?P<filtro>\w+)/$', views.buscar, name='buscar'),
    url(r'^cambiar_dueno_libros/$', views.cambiar_dueno_libros, name="cambiar_dueno_libros"),
    
    # Ajax calls
    url(r'^marcar_no_disponible/$', views.marcar_no_disponible),
    url(r'^marcar_disponible/$', views.marcar_disponible),
    url(r'^marcar_devuelto/$', views.marcar_devuelto),

    # Mi Biblioteca Ajax calls
    url(r'^info_grupos_libro_ajax/$', views.info_libro_grupos_ajax, name="info_grupos_libro"),
    url(r'^compartir_con_grupo_ajax/$', views.compartir_con_grupo_ajax),
    url(r'^no_compartir_grupo_ajax/$', views.no_compartir_grupo_ajax),
    url(r'^compartir_todos_ajax/$', views.compartir_todos_ajax, name="compartir_todos_ajax"),
    url(r'^pedir_bcompartida_ajax/$', views.pedir_bcompartida_ajax, name="pedir_bcompartida_ajax"),
    url(r'^request_existente_bcompartida_ajax/$', views.request_existente_bcompartida_ajax, name="request_existente_bcompartida_ajax"),
    url(r'^prestar_libro_bcompartida_ajax/$', views.prestar_libro_bcompartida_ajax, name="prestar_libro_bcompartida_ajax"),
    url(r'^rechazar_libro_bcompartida_ajax/$', views.rechazar_libro_bcompartida_ajax, name="rechazar_libro_bcompartida_ajax"),
    url(r'^retiro_libro_bcompartida_ajax/$', views.retiro_libro_bcompartida_ajax, name="retiro_libro_bcompartida_ajax"),
]
