from django.conf.urls import url
import views

urlpatterns = [
	url(r'^crear_grupo/$', views.crear_grupo, name="crear_grupo"),
	url(r'^main/(?P<id_libro>\d+)/$', views.main_grupo, name="main_grupo"),
	url(r'^invitar/(?P<username>[-\w.]+)/(?P<id_libro>\d+)$', views.invitar, name="invitar")
]
