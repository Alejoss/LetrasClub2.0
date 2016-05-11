from django.conf.urls import include, url
from django.contrib import admin

from libros import views

from django.views.generic import TemplateView
from django.views.defaults import page_not_found, server_error


urlpatterns = [
    url(r'^$', views.main, name='main_redirect'),
    url(r'^libros/', include('libros.urls', namespace="libros")),
    url(r'^grupos/', include('grupos.urls', namespace="grupos")),
    url(r'^perfil/', include('perfiles.urls', namespace="perfiles")),
    url(r'^comments/', include('comentarios.urls', namespace="comments")),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),

    # Probar errores
    url(r'^400/$', TemplateView.as_view(template_name='400.html')),
    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
    url(r'^404/$', page_not_found),
    url(r'^500/$', server_error),
]
