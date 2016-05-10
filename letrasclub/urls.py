from django.conf.urls import include, url
from django.contrib import admin

from libros import views

urlpatterns = [
    url(r'^$', views.main, name='main_redirect'),
    url(r'^libros/', include('libros.urls', namespace="libros")),
    url(r'^grupos/', include('grupos.urls', namespace="grupos")),
    url(r'^perfil/', include('perfiles.urls', namespace="perfiles")),
    url(r'^comments/', include('comentarios.urls', namespace="comments")),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls))
]
