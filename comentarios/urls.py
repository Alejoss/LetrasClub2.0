from django.conf.urls import url
import views

urlpatterns = [	
	url(r'^perfil/(?P<username>[-\w.]+)/$', views.comentar_perfil, name="comentar_perfil"),
	url(r'^grupo/(?P<id_grupo>\d+)/$', views.comentar_grupo, name="comentar_grupo"),

	# Ajax
	url(r'^responder_comment_perfil/$', views.responder_comment_perfil_ajax, name="responder_comment_perfil_ajax"),
	url(r'^responder_comment_grupo/$', views.responder_comment_ajax, name="responder_comment_grupo_ajax"),
	url(r'^comment_notificacion_grupo/$', views.comment_notificacion_ajax, name="comment_notificacion_ajax"),


	url(r'^respuestas_comment_perfil/$', views.respuestas_comment_perfil_ajax, name="respuestas_comment_perfil_ajax"),
	url(r'^respuestas_comment_grupo/$', views.respuestas_comment_ajax, name="respuestas_comment_ajax"),
	url(r'^respuestas_notificacion/$', views.respuestas_notificacion_ajax, name="respuestas_notificacion_ajax")
]
