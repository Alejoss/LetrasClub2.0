# -*- coding: utf-8 -*-
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from libros.models import LibrosRequest, LibrosPrestados, LibrosPrestadosBibliotecaCompartida, LibrosDisponibles, Libro
from perfiles.models import Perfil, UsuarioLeyendo
from grupos.models import UsuariosGrupo
from notificaciones.models import Notificacion

from forms import formRegistro, formEditarPerfil
from letrasclub.utils import obtener_perfil, obtener_historial_libros, obtener_avatar_large, obtenerquito, obtener_libros_perfil, obtener_usuario_leyendo


def registro(request):
	"""
	View no está en uso, registro de nuevo usuario
	"""
	template = "perfiles/registro.html"

	if request.method == "POST":
		form = formRegistro(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse("Usuario Guardado", status=201)
	
	else:		
		form = formRegistro()

	context = {
		'form': form
	}
	
	return render(request, template, context)


@login_required
def perfil_propio(request):
	"""
	Muestra el perfil del usuario que está hecho login
	"""
	template = "perfiles/perfil_propio.html"
	perfil_usuario = obtener_perfil(request.user)
	avatar = obtener_avatar_large(perfil_usuario)
	
	# Libros Perfil
	libros_perfil = {
		'tiene_requests_pendientes': False,
		'tiene_libros_prestados': False,
		'tiene_libros_pedidos': False
		}

	libros_requests = libros_prestados = libros_prestados_bcompartida = libros_pedidos = []

	if LibrosRequest.objects.filter(perfil_envio=perfil_usuario, aceptado=False, eliminado=False).exists():
		libros_perfil['tiene_libros_pedidos'] = True
		libros_pedidos = LibrosRequest.objects.filter(perfil_envio=perfil_usuario, aceptado=False, eliminado=False)

	if LibrosRequest.objects.filter(perfil_recepcion=perfil_usuario, aceptado=False, eliminado=False).exists():
		libros_perfil['tiene_requests_pendientes'] = True
		libros_requests = LibrosRequest.objects.filter(perfil_recepcion=perfil_usuario, aceptado=False, eliminado=False)

	if LibrosPrestados.objects.filter(perfil_receptor=perfil_usuario, fecha_devolucion=None).exists():
		libros_perfil['tiene_libros_prestados'] = True
		libros_prestados = LibrosPrestados.objects.filter(perfil_receptor=perfil_usuario, fecha_devolucion=None)

	if LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil_usuario, fecha_devolucion=None).exists():
		libros_perfil['tiene_libros_prestados'] = True
		libros_prestados_bcompartida = LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil_usuario, fecha_devolucion=None)

	# Grupos Perfil
	grupos = None
	if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():
		usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).select_related('grupo')
		grupos = [ug.grupo for ug in usuarios_grupo_obj]

	# Usuario Leyendo
	actualmente_leyendo, libros_leidos_usuario = obtener_usuario_leyendo(perfil_usuario)

	libros_disponibles = LibrosDisponibles.objects.filter(perfil=perfil_usuario).select_related('libro')
	# autocomplete Usuario Leyendo
	titulos_autocomplete = {}
	autores_autocomplete = {}
	for l in libros_disponibles:
		titulos_autocomplete[l.libro.titulo] = (l.libro.id, l.libro.autor)

	for l in libros_disponibles:
		autores_autocomplete[l.libro.autor] = l.libro.id

	context = {'libros_perfil': libros_perfil, 'libros_requests': libros_requests, 'libros_prestados': libros_prestados,
	           'libros_pedidos': libros_pedidos, 'libros_prestados_bcompartida': libros_prestados_bcompartida, 
	           'libros_disponibles': libros_disponibles, 'avatar': avatar, 'grupos': grupos, 'actualmente_leyendo': actualmente_leyendo,
	           'libros_leidos_usuario': libros_leidos_usuario, 'titulos_autocomplete': json.dumps(titulos_autocomplete), 
	           'autores_autocomplete': json.dumps(autores_autocomplete)}
	
	return render(request, template, context)


def perfil_usuario(request, username):
	"""
	Muestra el perfil de un usuario tercero
	"""	
	template = "perfiles/perfil_usuario.html"
	libros_perfil = {'tiene_libros_prestados': False, 'tiene_libros_disponibles': False}

	# redirigir a la pagina perfil_propio si es el caso
	user_obj = User.objects.get(username=username)
	if user_obj == request.user:
		return HttpResponseRedirect(reverse('perfiles:perfil_propio'))

	perfil = Perfil.objects.get(usuario__username=username)
	historial_libros = obtener_historial_libros(perfil)
	libros_prestados = libros_prestados_bcompartida = libros_disponibles = []

	if LibrosPrestados.objects.filter(perfil_receptor=perfil, fecha_devolucion=None).exists():
		libros_perfil['tiene_libros_prestados'] = True
		libros_prestados = LibrosPrestados.objects.filter(perfil_receptor=perfil, fecha_devolucion=None)

	if LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil, fecha_devolucion=None).exists():
		libros_perfil['tiene_libros_prestados'] = True
		libros_prestados_bcompartida = LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil, fecha_devolucion=None)

	if LibrosDisponibles.objects.filter(perfil=perfil, disponible=True, prestado=False).exists():
		libros_perfil['tiene_libros_disponibles'] = True
		libros_disponibles = LibrosDisponibles.objects.filter(perfil=perfil, disponible=True, prestado=False)

	avatar = obtener_avatar_large(perfil)

	context = {'libros_prestados': libros_prestados, 'libros_prestados_bcompartida': libros_prestados_bcompartida, 'libros_disponibles': libros_disponibles,
	           'historial_libros': historial_libros, 'libros_perfil': libros_perfil, 'perfil': perfil, 'avatar': avatar}

	return render(request, template, context)


@login_required
def logout_view(request):
	logout(request)

	return HttpResponseRedirect(reverse('libros:main'))


@login_required
def editar_perfil(request):
	"""
	Procesa el view y el form para que el usuario edite su perfil
	"""
	template = "perfiles/editar_perfil.html"
	perfil_usuario = obtener_perfil(request.user)

	if request.method == "POST":
		form = formEditarPerfil(request.POST, instance=perfil_usuario)

		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('perfiles:perfil_propio'))

	else:
		if perfil_usuario.ciudad:
			ciudad_default = perfil_usuario.ciudad
		else:
			ciudad_default = obtenerquito()
		form = formEditarPerfil(
			initial={
				'descripcion': perfil_usuario.descripcion,
				'ciudad': ciudad_default,
				'numero_telefono_contacto': perfil_usuario.numero_telefono_contacto
			})

	context = {'form': form}

	return render(request, template, context)


@login_required
def libros_usuario_ajax(request):
	"""
	Crea un UsuarioLeyendo object y señala la fecha actual como inicio
	"""
	if request.is_ajax():
		perfil_usuario = obtener_perfil(request.user)
		titulos_autocomplete, autores_autocomplete = obtener_libros_perfil(perfil_usuario)
		context = {'titulos_autocomplete': json.dumps(titulos_autocomplete), 'autores_autocomplete': json.dumps(autores_autocomplete)}
		return HttpResponse(context, status=200)
	else:
		return HttpResponse(status=400)


def leyendo_libro_ajax(request):
	"""
	Recibe un libro id o un titulo y un autor. En el primer caso, crea un objeto UsuarioLeyendo, en el segundo,
	crea un objeto Libro y luego un objeto UsuarioLeyendo
	"""
	if request.is_ajax():
		libro_id = request.POST.get("libro_id", "")
		titulo = request.POST.get("titulo", "")
		autor = request.POST.get("autor", "")
		perfil_usuario = obtener_perfil(request.user)

		if libro_id:
			# Significa que el libro está en su biblioteca
			libro = Libro.objects.get(id=int(libro_id))

			# Revisar si el último UsuarioLeyendo object no es el mismo que declaro estar leyendo, para evitar repeticiones
			ultimo_libro = UsuarioLeyendo.objects.filter(perfil=perfil_usuario).latest('inicio')
			if ultimo_libro.libro.titulo == titulo:
				return HttpResponse("es el mismo libro que ya está leyendo", status=400)

			# Revisar si no borro el nombre y puso otro que no está en su biblioteca (nuevo)
			# El autocomplete pudiera haber llenado el id del hidden input y luego se pudo haber quedado así,
			# a pesar de que el usuario borro el nombre del autocomplete e insertó otro título.
			if libro.titulo == titulo and libro.autor == autor:
				print "recibio libro id y coincide el libro obtenido con el titulo y el autor"
				UsuarioLeyendo.objects.create(perfil=perfil_usuario, libro=libro)
				
			else:
				# crear nuevo libro
				print "recibio libro id pero no coincide el libro obtenido con el titulo y el autor"
				nuevo_libro = Libro.objects.create(titulo=titulo, autor=autor)

				# crear objeto UsuarioLeyendo
				UsuarioLeyendo.objects.create(libro=nuevo_libro, perfil=perfil_usuario)

			# crear notificaciones para cada grupo			

		else:
			# Significa que el libro no está en su biblioteca
			# Revisar si el último UsuarioLeyendo object no es el mismo que declaro estar leyendo, para evitar repeticiones
			ultimo_libro = UsuarioLeyendo.objects.filter(perfil=perfil_usuario).latest('inicio')
			if ultimo_libro.libro.titulo == titulo:
				return HttpResponse("es el mismo libro que ya está leyendo", status=400)

			# Revisar si no existe ya un libro con ese titulo, para evitar repeticiones
			if Libro.objects.filter(titulo=titulo, autor=autor).exists():
				libro = Libro.objects.get(titulo=titulo, autor=autor)
				print "ya existe un libro con ese titulo y autor"
			else:
				# crear nuevo libro
				print "no existe un libro así, crear objeto nuevo"
				libro = Libro.objects.create(titulo=titulo, autor=autor)

			# crear objeto LibroDisponible, suma libro a su biblioteca, solo si no existe ya en la biblioteca
			if not LibrosDisponibles.objects.filter(libro=libro, perfil=perfil_usuario).exists():
				print "no existe ese libro en su biblioteca, crear nuevo"
				LibrosDisponibles.objects.create(libro=libro, perfil=perfil_usuario, disponible=False, ciudad=perfil_usuario.ciudad)

			# crear objeto UsuarioLeyendo
			UsuarioLeyendo.objects.create(libro=libro, perfil=perfil_usuario)

			# !!! crear notificacion

		return HttpResponse(status=200)

	else:
		return HttpResponse(status=400)
