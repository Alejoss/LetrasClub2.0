# -*- coding: utf-8 -*-
import json
import bleach

from django.shortcuts import redirect
from django.http import HttpResponse

from notificaciones.models import Notificacion
from grupos.models import Grupo
from comentarios.models import CommentNotificacion, CommentPerfil, RespuestaCommentPerfil, CommentGrupo, RespuestaCommentGrupo, CommentBCompartida, \
					RespuestaCommentBCompartida

from perfiles.models import Perfil
from libros.models import BibliotecaCompartida

from letrasclub.utils import obtener_perfil


def comentar_bcompartida(request, slug_biblioteca_compartida):
	"""
	guarda un comentario en el grupo, redirige al main del grupo
	"""

	if request.method == "POST":
		comentario = bleach.clean(request.POST.get("comentario", ""))

		if comentario:
			bcompartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)
			perfil_usuario = obtener_perfil(request.user)

			# Crear comment
			CommentBCompartida.objects.create(bcompartida=bcompartida, perfil=perfil_usuario, texto=comentario)

		return redirect('libros:biblioteca_compartida', slug_biblioteca_compartida=bcompartida.slug)

	else:
		return HttpResponse(status=400)


def comentar_grupo(request, id_grupo):
	"""
	guarda un comentario en el grupo, redirige al main del grupo
	"""

	if request.method == "POST":
		comentario = bleach.clean(request.POST.get("comentario", ""))

		if comentario:
			grupo = Grupo.objects.get(id=id_grupo)
			perfil_usuario = obtener_perfil(request.user)

			# Crear comment
			CommentGrupo.objects.create(grupo=grupo, perfil=perfil_usuario, texto=comentario)

		return redirect('grupos:main_grupo_actividad', id_grupo=grupo.id)

	else:
		return HttpResponse(status=400)


def comentar_perfil(request, username):
	"""
	guarda un comentario en el grupo, redirige al main del grupo
	"""

	if request.method == "POST":
		comentario = bleach.clean(request.POST.get("comentario", ""))

		if comentario:
			perfil_muro = Perfil.objects.get(usuario__username=username)
			perfil_comenta = obtener_perfil(request.user)

			# Crear comment
			CommentPerfil.objects.create(muro=perfil_muro, perfil=perfil_comenta, texto=comentario)			

			if perfil_muro == perfil_comenta:
				# Esta comentando en su propio muro, redirigir allá
				return redirect('perfiles:perfil_propio')
			else:
				return redirect('perfiles:perfil_usuario', username=username)

		else:
			return HttpResponse(status=400)
	else:
		return HttpResponse(status=400)


# Ajax Calls
def responder_comment_bcompartida_ajax(request):
	"""
	Guarda un objeto RespuestaCommentBCompartida con FK al comment_perfil respondido
	"""

	if request.is_ajax():

		if request.method == "POST":
			comentario_id = int(request.POST.get("comment_id", ""))
			texto_respuesta_base = request.POST.get("texto_respuesta", "")

			if texto_respuesta_base:

				comment_obj = CommentBCompartida.objects.get(id=comentario_id)
				perfil_usuario = obtener_perfil(request.user)
				texto_respuesta = bleach.clean(texto_respuesta_base)

				# Crear objeto respuesta
				r = RespuestaCommentBCompartida.objects.create(comment_bcompartida=comment_obj, perfil=perfil_usuario, texto=texto_respuesta)

				respuesta = json.dumps([r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil])

				return HttpResponse(respuesta, status=201)

			else:
				return HttpResponse(status=400)
		else:
			return HttpResponse(status=400)	
	else:
		return HttpResponse(status=400)


def responder_comment_perfil_ajax(request):
	"""
	Guarda un objeto RespuestaCommentPerfil con FK al comment_perfil respondido
	"""

	if request.is_ajax():

		if request.method == "POST":
			comentario_id = int(request.POST.get("comment_id", ""))
			texto_respuesta_base = request.POST.get("texto_respuesta", "")

			if texto_respuesta_base:

				comment_obj = CommentPerfil.objects.get(id=comentario_id)
				perfil_usuario = obtener_perfil(request.user)
				texto_respuesta = bleach.clean(texto_respuesta_base)

				# Crear objeto respuesta
				r = RespuestaCommentPerfil.objects.create(comment_perfil=comment_obj, perfil=perfil_usuario, texto=texto_respuesta)

				respuesta = json.dumps([r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil])

				return HttpResponse(respuesta, status=201)

			else:
				return HttpResponse(status=400)
		else:
			return HttpResponse(status=400)	
	else:
		return HttpResponse(status=400)


def comment_notificacion_ajax(request):

	if request.is_ajax():

		if request.method == "POST":
			id_notificacion = int(request.POST.get("id_notificacion", ""))
			texto_comment = bleach.clean(request.POST.get("texto_comment", ""))
			notificacion = Notificacion.objects.get(id=id_notificacion)

			if texto_comment:

				perfil = obtener_perfil(request.user)
				# Crear objeto CommentNotificacion
				r = CommentNotificacion.objects.create(perfil=perfil, notificacion=notificacion, texto=texto_comment)

				respuesta = json.dumps([r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil])

				return HttpResponse(respuesta, status=201)

			else:
				return HttpResponse(status=400)

		else:
			return HttpResponse(status=400)

	else:
		return HttpResponse(status=400)


def respuestas_notificacion_ajax(request):

	if request.is_ajax():
		id_notificacion = int(request.GET.get("id_notificacion", ""))
		respuestas = CommentNotificacion.objects.filter(notificacion__id=id_notificacion).select_related("perfil")

		respuestas_list = []
		for r in respuestas:
			respuesta = [r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil]
			respuestas_list.append(respuesta)

		respuestas_json = json.dumps(respuestas_list)
		return HttpResponse(respuestas_json)

	else:
		return HttpResponse(status=400)


def responder_comment_grupo_ajax(request):
	"""
	guarda un objeto RespuestaCommentGrupo con FK al comment_grupo respondido
	"""

	if request.is_ajax():

		if request.method == "POST":
			comentario_id = int(request.POST.get("comment_id", ""))
			texto_respuesta_base = request.POST.get("texto_respuesta", "")

			if texto_respuesta_base:

				comment_obj = CommentGrupo.objects.get(id=comentario_id)
				perfil_usuario = obtener_perfil(request.user)
				texto_respuesta = bleach.clean(texto_respuesta_base)

				# Crear objeto respuesta
				r = RespuestaCommentGrupo.objects.create(comment_grupo=comment_obj, perfil=perfil_usuario, texto=texto_respuesta)

				respuesta = json.dumps([r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil])

				return HttpResponse(respuesta, status=201)

			else:
				return HttpResponse(status=400)
		else:
			return HttpResponse(status=400)	
	else:
		return HttpResponse(status=400)


def respuestas_comment_grupo_ajax(request):
	"""
	Recibe un id de un comentario y envía las respuestas que tiene
	"""

	if request.is_ajax():
		id_comment = int(request.GET.get("id_comment"))
		respuestas = RespuestaCommentGrupo.objects.filter(comment_grupo__id=id_comment).select_related("perfil")

		respuestas_list = []
		for r in respuestas:
			respuesta = [r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil]
			respuestas_list.append(respuesta)

		respuestas_json = json.dumps(respuestas_list)
		return HttpResponse(respuestas_json)

	else:
		return HttpResponse(status=400)


def respuestas_comment_perfil_ajax(request):
	"""
	Recibe un id de un comentario hecho en un perfil, envía las respuestas a ese comentario
	"""

	if request.is_ajax():
		id_comment = int(request.GET.get("id_comment"))
		respuestas = RespuestaCommentPerfil.objects.filter(comment_perfil__id=id_comment).select_related("perfil")

		respuestas_list = []
		for r in respuestas:
			respuesta = [r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil]
			respuestas_list.append(respuesta)

		respuestas_json = json.dumps(respuestas_list)
		return HttpResponse(respuestas_json)

	else:
		return HttpResponse(status=400)


def respuestas_comment_bcompartida_ajax(request):
	"""
	Recibe un id de un comentario hecho en una BibliotecaCompartida, envía las respuestas a ese comentario
	"""

	if request.is_ajax():
		id_comment = int(request.GET.get("id_comment"))
		respuestas = RespuestaCommentBCompartida.objects.filter(comment_bcompartida__id=id_comment).select_related("perfil")

		respuestas_list = []
		for r in respuestas:
			respuesta = [r.id, r.texto, r.perfil.usuario.username, r.perfil.imagen_perfil]
			respuestas_list.append(respuesta)

		respuestas_json = json.dumps(respuestas_list)
		return HttpResponse(respuestas_json)

	else:
		return HttpResponse(status=400)
