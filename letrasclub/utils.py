# -*- coding: utf-8 -*-
import datetime
from itertools import chain

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Count

from django.conf import settings
from perfiles.models import Perfil, UsuarioLeyendo
from libros.models import LibrosPrestados, LibrosPrestadosBibliotecaCompartida, LibrosDisponibles
from cities_light.models import City
from notificaciones.models import Notificacion
from grupos.models import UsuariosGrupo
from comentarios.models import CommentPerfil, CommentBCompartida


# Devuelve el modelo de Quito
def obtenerquito():
	return City.objects.get(name="Quito")


# Perfil y Editar Perfil
def obtener_avatar_large(perfil):
    # Obtiene un perfil y devuelve la imagen de perfil grande.
    avatar_large = None
    if perfil.imagen_perfil is not None:
        if "facebook" in perfil.imagen_perfil:
            avatar_large = "%s?type=large" % (perfil.imagen_perfil)        
        elif "google" in perfil.imagen_perfil:
            avatar_large = (perfil.imagen_perfil).replace("sz=50", "sz=400")
        else:
            avatar_large = perfil.imagen_perfil
    else:
        avatar_large = "https://s3.amazonaws.com/epona/assets/images/letrasclub/books_biblioteca.jpg"

    return avatar_large


def obtener_perfil(usuario):
	perfil, created = Perfil.objects.get_or_create(usuario=usuario)

	return perfil


def definir_fecha_devolucion(fecha_prestamo, tiempo_prestamo):
	fecha_devolucion = None
	if tiempo_prestamo == "2_semanas":
		fecha_devolucion = fecha_prestamo + datetime.timedelta(weeks=3)
	elif tiempo_prestamo == "1_mes":
		fecha_devolucion = fecha_prestamo + datetime.timedelta(weeks=5)
	elif tiempo_prestamo == "2_meses":
		fecha_devolucion = fecha_prestamo + datetime.timedelta(weeks=9)
	elif tiempo_prestamo == "3_meses":
		fecha_devolucion = fecha_prestamo + datetime.timedelta(weeks=13)
	else:
		pass

	return fecha_devolucion


def obtener_historial_libros(perfil):

	libros_recibidos_usuario = LibrosPrestados.objects.filter(perfil_receptor=perfil)
	libros_recibidos_bcompartida = LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil)
	libros_prestados_por_usuario = LibrosPrestados.objects.filter(perfil_dueno=perfil)

	return {'libros_recibidos_usuario': libros_recibidos_usuario, 'libros_recibidos_bcompartida': libros_recibidos_bcompartida, 
	'libros_prestados_por_usuario': libros_prestados_por_usuario}


def crear_perfil(backend, user, response, *args, **kwargs):
	"""
	Pipeline de Python Social Auth, crea el perfil y le asigna un avatar que extrae de la red social
	"""
	perfil, creado = Perfil.objects.get_or_create(usuario=user)

	perfil.ciudad = obtenerquito()
	
	if backend.name == "facebook":
		imagen_url_backend = 'http://graph.facebook.com/{0}/picture'.format(response['id'])
		perfil.imagen_perfil = imagen_url_backend
		perfil.save()

	elif backend.name == "google-oauth2":
		if response['image'].get('url') is not None:
			imagen_url_backend = response['image'].get('url')
			perfil.imagen_perfil = imagen_url_backend
			perfil.save()

	return None


def mail_pedir_libro(request_libro, mensaje):
	"""
	Envía un mail al dueño del libro notificándole del pedido
	"""

	titulo = "%s te ha pedido un libro" % (request_libro.perfil_envio.usuario.username)
	mensaje_texto = ("%s te ha pedido que le prestes el libro %s, por favor visita tu perfil en Letras.Club" 
		% (request_libro.perfil_envio.usuario.username, request_libro.libro.titulo))
	html_message = render_to_string("pedir_libro_mail.html", {'usuario_receptor_mail': request_libro.perfil_recepcion.usuario.username, 
				'nombre_usuario_envio': request_libro.perfil_envio.usuario.username, 'mensaje': mensaje,
				'titulo_libro': request_libro.libro.titulo, 'autor_libro': request_libro.libro.autor, 
				'telefono': request_libro.perfil_envio.numero_telefono_contacto})

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=[request_libro.perfil_recepcion.usuario.email],
			fail_silently=True,
			html_message=html_message
		)

	return None


def mail_pedir_libro_bcompartida(request_libro, biblioteca_compartida):
	"""
	Envía un mail al admin de la biblioteca compartida cuando alguien pide un libro. No envía un mensaje
	escrito por el usuario
	"""

	titulo = "%s ha pedido un libro a %s" % (request_libro.perfil_envio.usuario.username, biblioteca_compartida.nombre)
	mensaje_texto = ("%s te ha pedido que le prestes el libro %s, por favor visita la biblioteca compartida %s en Letras.Club" 
		% (request_libro.perfil_envio, request_libro.libro_disponible.libro.titulo, biblioteca_compartida.nombre))
	html_message = render_to_string("pedir_libro_bcompartida_mail.html", {'usuario_receptor_mail': biblioteca_compartida.perfil_admin.usuario.username, 
				'nombre_usuario_envio': request_libro.perfil_envio.usuario.username, 'biblioteca_compartida_nombre': biblioteca_compartida.nombre,
				'titulo_libro': request_libro.libro_disponible.libro.titulo, 'autor_libro': request_libro.libro_disponible.libro.autor, 
				'telefono': request_libro.perfil_envio.numero_telefono_contacto})

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=[request_libro.perfil_recepcion.usuario.email],
			fail_silently=True,
			html_message=html_message
		)	


def mail_anunciar_devolucion(libro_prestado):
	"""
	Envía un mail al dueño del libro notificándole que el usuario que lo recibió
	ya lo marcó como devuelto
	"""

	titulo = "%s ha marcado un libro tuyo como devuelto" % (libro_prestado.perfil_receptor.usuario.username)
	mensaje_texto = ("%s ha marcado tu libro %s como devuelto, si ya lo tienes,\
	 por favor visita tu biblioteca en Letras.Club") % (libro_prestado.perfil_receptor.usuario.username, libro_prestado.libro.titulo)
	html_message = render_to_string("anunciar_devolucion_mail.html", {'usuario_receptor_mail': libro_prestado.perfil_dueno.usuario.username,
		'usuario_devolucion': libro_prestado.perfil_receptor.usuario.username, 'titulo_libro': libro_prestado.libro.titulo, 
		'autor_libro': libro_prestado.libro.titulo})

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=[libro_prestado.perfil_dueno.usuario.email],
			fail_silently=True,
			html_message=html_message
		)

	return None


def mail_aceptar_prestamo(libro_prestado):
	"""
	Envía un mail al usuario que pidió el libro notificándole que sí le van a prestar el libro
	"""

	titulo = "%s ha aceptado prestarte el libro %s" % (libro_prestado.perfil_dueno.usuario.username, libro_prestado.libro.titulo)
	mensaje_texto = "%s ha aceptado prestarte el libro %s de %s, por favor visita tu perfil en Letras.Club"
	html_message = render_to_string("aceptar_prestamo_mail.html", {'usuario_receptor_mail': libro_prestado.perfil_receptor.usuario.username,
		'usuario_dueno_libro': libro_prestado.perfil_dueno.usuario.username, 'titulo_libro': libro_prestado.libro.titulo, 
		'autor_libro': libro_prestado.libro.autor, 'mensaje': libro_prestado.mensaje_aceptacion})

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=[libro_prestado.perfil_receptor.usuario.email],
			fail_silently=True,
			html_message=html_message
		)

	return None


def mail_agregar_a_grupo(invitado_por, usuario_invitado, grupo):
	"""
	Envía un mail al usuario notificándole que se le ha invitado a formar parte de un grupo en LetrasClub
	"""

	titulo = "%s te ha invitado al grupo %s de LetrasClub" % (invitado_por, grupo.nombre)
	mensaje_texto = "Hola %s, %s te ha invitado al grupo %s de literatura en el cual podrás compartir libros físicos y comentar sobre ellos\
	en www.letras.club, una red social dedicada a los lectores que buscan compartir sus libros y formar grupos  \
	localizados de lectura" % (usuario_invitado.usuario.username, invitado_por.usuario.username, grupo.nombre)

	html_message = render_to_string("invitar_grupo_mail.html", {'usuario_invitado': usuario_invitado.usuario.username, 'invitado_por': invitado_por.usuario.username, 
		'nombre_grupo': grupo.nombre})

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=[usuario_invitado.usuario.email],
			fail_silently=True,
			html_message=html_message
		)

	return None


def mail_request_entrar_grupo(usuario_request, admins, grupo):
	"""
	Envía un mail a los admins del grupo con el request de entrar del usuario_request
	"""
	titulo = "%s ha solicitado ser parte del grupo %s de LetrasClub" % (usuario_request.usuario.username, grupo.nombre)
	mensaje_texto = "%s ha solicitado entrar al grupo %s de LetrasClub. Por favor, revisa el grupo en LetrasClub"

	html_message = render_to_string("request_entrar_grupo_mail.html", {'usuario_request': usuario_request.usuario.username, 'grupo': grupo.nombre})

	receptores = [admin.usuario.email for admin in admins]

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=receptores,
			fail_silently=True,
			html_message=html_message
		)

	return None


def enviar_mail_contactanos(nombre, correo, tema, mensaje):
	"""
	Envía un mail a los admins de la pagina con el mensaje de contacto y el correo de respuesta
	"""
	titulo = "%s ha contactado a LetrasClub" % (nombre)
	mensaje_texto = "Mensaje: %s" % (mensaje)
	html_message = render_to_string("contactanos_mail.html", {'nombre': nombre, 'correo': correo, 'tema': tema, 'mensaje': mensaje})

	receptores = [admin[1] for admin in settings.ADMINS]

	send_mail(
			subject=titulo,
			message=mensaje_texto,
			from_email="letras.club@no-reply.com",
			recipient_list=receptores,
			fail_silently=True,
			html_message=html_message
		)

	return None


def obtener_libros_perfil(perfil_usuario):
	"""
	responde con dos diccionarios listos para el autocomplete de titulo / autor
	"""
	libros_disponibles_obj = LibrosDisponibles.objects.filter(perfil=perfil_usuario).select_related("libro")
	titulos_autocomplete = {}
	autores_autocomplete = {}
	for l in libros_disponibles_obj:
		titulos_autocomplete[l.libro.titulo] = (l.id, l.libro.autor)

	for l in libros_disponibles_obj:
		autores_autocomplete[l.libro.autor] = l.id

	return titulos_autocomplete, autores_autocomplete


def obtener_usuario_leyendo(perfil_usuario):
	"""
	responde con el libro que esta leyendo el usuario o con None
	"""	
	usuario_leyendo_obj = None
	actualmente_leyendo = None
	if UsuarioLeyendo.objects.filter(perfil=perfil_usuario).exists():
		usuario_leyendo_obj = UsuarioLeyendo.objects.filter(perfil=perfil_usuario, eliminado=False).order_by('-inicio')

		if usuario_leyendo_obj.filter(termino__isnull=True).exists():
			actualmente_leyendo = usuario_leyendo_obj.filter(termino__isnull=True).latest('inicio')

	return actualmente_leyendo, usuario_leyendo_obj


def notif_grupos_comenzo_leer(perfil_usuario, libro):
	"""
	crea una notificacion usuario_leyendo con fk a cada grupo al que pertenece el usuario
	"""
	grupos_usuario = UsuariosGrupo.objects.filter(perfil=perfil_usuario)

	for g_u in grupos_usuario:
		Notificacion.objects.comenzo_leer(perfil_usuario, libro=libro, grupo=g_u.grupo)


def notif_grupos_termino_leer(perfil_usuario, libro):
	"""
	crea una notificacion termino_leer con fk a cada grupo al que pertenece el usuario
	"""

	grupos_usuario = UsuariosGrupo.objects.filter(perfil=perfil_usuario)

	for g_u in grupos_usuario:
		Notificacion.objects.termino_leer(perfil_usuario, libro=libro, grupo=g_u.grupo)


def obtener_muro_perfil(perfil):

	tipos_excluir_query = ["comenzo_leer", "termino_leer", "bcompartida_presto", "bcompartida_cambio"]
	# se debe excluir algunos querys para evitar repeticion de notificaciones que se muestran en dos muros,
	# es un relajo, hay que arreglar esto.
	
	comentarios = CommentPerfil.objects.filter(muro=perfil, eliminado=False).annotate(num_respuestas=Count("respuestas"))
	n_excluir = Notificacion.objects.filter(perfil_actor=perfil).exclude(tipo__in=tipos_excluir_query).annotate(num_respuestas=Count("respuestas"))
	n_generales = Notificacion.objects.filter(perfil_actor=perfil, grupo=None).annotate(num_respuestas=Count("respuestas"))
	
	actividad = list(chain(comentarios, n_excluir, n_generales))
	actividad.sort(key=lambda x: x.fecha)  # Ordena comentarios y notificaciones alternados por fecha.
	actividad.reverse()  # Ordena desde el más reciente.

	return actividad


def obtener_muro_bcompartida(biblioteca_compartida):

	comentarios = CommentBCompartida.objects.filter(bcompartida=biblioteca_compartida, eliminado=False).annotate(num_respuestas=Count("respuestas"))
	notificaciones = Notificacion.objects.filter(biblioteca_compartida=biblioteca_compartida).annotate(num_respuestas=Count("respuestas"))

	actividad = list(chain(comentarios, notificaciones))
	actividad.sort(key=lambda x: x.fecha)  # Ordena comentarios y notificaciones alternados por fecha.
	actividad.reverse()  # Ordena desde el más reciente.

	return actividad
