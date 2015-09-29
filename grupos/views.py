# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from letrasclub.utils import obtener_perfil
from forms import FormCrearGrupo
from models import UsuariosGrupo, Grupo, RequestInvitacion
from perfiles.models import Perfil


def crear_grupo(request):
	template = "grupos/crear_grupo.html"

	if request.method == "POST":
		form = FormCrearGrupo(request.POST)
		
		if form.is_valid():

			# Sumar un tipo al grupo (Abierto, Cerrado, Todos puede añadir, Admins pueden añadir)
			tipo_grupo = form.obtener_tipo()
			nuevo_grupo = form.save(commit=False)
			nuevo_grupo.tipo = tipo_grupo
			
			# Situar el grupo en una ciudad si es necesario
			situar_ciudad = form.cleaned_data['situar_ciudad']
			perfil_admin = obtener_perfil(request.user)
			if situar_ciudad:
				nuevo_grupo.ciudad = perfil_admin.ciudad

			nuevo_grupo.save()

			# Crear usuario administrador
			usuario_admin = UsuariosGrupo(usuario=perfil_admin, grupo=nuevo_grupo, es_admin=True)
			usuario_admin.save()

			return redirect('grupos:main_grupo', id_grupo=nuevo_grupo.id)		
	else:
		form = FormCrearGrupo()
		perfil = obtener_perfil(request.user)

	context = {'form': form, 'perfil': perfil}

	return render(request, template, context)


def editar_grupo(request, id_grupo):
	template = "grupos/editar_grupo.html"

	grupo = get_object_or_404(Grupo, id=id_grupo)

	if request.method == "POST":
		form = FormCrearGrupo(request.POST, instance=grupo)

		if form.is_valid():

			# Sumar un tipo al grupo (Abierto, Cerrado, Todos puede añadir, Admins pueden añadir)
			tipo_grupo = form.obtener_tipo()
			grupo_editado = form.save(commit=False)
			grupo_editado.tipo = tipo_grupo
			
			# Situar el grupo en una ciudad si es necesario
			situar_ciudad = form.cleaned_data['situar_ciudad']
			perfil_admin = obtener_perfil(request.user)
			if situar_ciudad:
				grupo_editado.ciudad = perfil_admin.ciudad

			# Guardar cambios
			grupo_editado.save()
		
		return redirect('grupos:main_grupo', id_grupo=grupo.id)

	else:
		if grupo.ciudad is not None:
			form_situar_ciudad = True

		form = FormCrearGrupo(initial={
			'nombre': grupo.nombre,
			'descripcion': grupo.descripcion,
			'imagen': grupo.imagen,
			'tipo_apertura': grupo.obtener_tipo_apertura(),
			'tipo_invitaciones': grupo.obtener_tipo_invitaciones(),
			'situar_ciudad': form_situar_ciudad
			})

	context = {'form': form, 'grupo': grupo}
	return render(request, template, context)


def main_grupo(request, id_grupo):
	template = "grupos/main_grupo.html"

	perfil_usuario = obtener_perfil(request.user)
	grupo = Grupo.objects.get(id=id_grupo)
	usuario_es_miembro = UsuariosGrupo.objects.filter(usuario=perfil_usuario, grupo=grupo).exists()

	usuarios_grupo_obj = UsuariosGrupo.objects.filter(grupo=grupo, activo=True).select_related('usuario')
	miembros = [usuario_grupo_obj for usuario_grupo_obj in usuarios_grupo_obj]

	usuario_es_admin = False
	request_invitacion_enviada = False
	if usuario_es_miembro:
		# Si el usuario es miembro, revisar si es admin
		if UsuariosGrupo.objects.filter(usuario=perfil_usuario, grupo=grupo, es_admin=True):
			usuario_es_admin = True
	else:
		# Si el usuario no es miembro, revisar si ya envió solicitud
		if RequestInvitacion.objects.filter(grupo=grupo, usuario_invitado=perfil_usuario, aceptado=False, eliminado=False).exists():
			request_invitacion_enviada = True

	requests_entrar_grupo = None

	if usuario_es_miembro:
		if grupo.tipo in [2, 4]:
			# Si solo los admins pueden aceptar !!!
			# Si el usuario es admin, mostrar los requests.
			if usuario_es_admin:
				requests_entrar_grupo = RequestInvitacion.objects.filter(grupo=grupo, aceptado=False, eliminado=False)
		else:
			requests_entrar_grupo = RequestInvitacion.objects.filter(grupo=grupo, aceptado=False, eliminado=False)

	context = {'grupo': grupo, 'miembros': miembros, 'requests_entrar_grupo': requests_entrar_grupo, 'usuario_es_admin': usuario_es_admin,
	'usuario_es_miembro': usuario_es_miembro, 'request_invitacion_enviada': request_invitacion_enviada
	}

	return render(request, template, context)


def invitar(request, id_grupo):
	template = "grupos/invitar.html"

	grupo = Grupo.objects.get(id=id_grupo)

	perfil_obj = Perfil.objects.all()
	lista_usuarios = {}
	for perfil in perfil_obj:
		ciudad = None
		if perfil.ciudad:
			ciudad = perfil.ciudad.name
		lista_usuarios[perfil.usuario.username] = {'imagen_perfil': perfil.imagen_perfil, 'ciudad': ciudad, 'username': perfil.usuario.username}

	usernames_dict = json.dumps(lista_usuarios)

	context = {'grupo': grupo, 'usernames_dict': usernames_dict}

	return render(request, template, context)


def invitar_ajax(request):
	
	if request.is_ajax():
		grupo_id = request.POST.get("grupo_id", "")
		invitaciones = json.loads(request.POST.get("invitaciones", ""))

		if grupo_id and invitaciones:
			grupo = Grupo.objects.get(id=grupo_id)
			invitado_por = obtener_perfil(request.user)

			for invitacion in invitaciones:
				usuario_invitado = Perfil.objects.get(usuario__username=invitacion['nombre_usuario'])
				
				# Si el usuario ya es miembro del grupo
				if UsuariosGrupo.objects.filter(usuario=usuario_invitado, grupo=grupo).exists():
					pass					

				# Si cualquier persona puede sumar miembros al grupo
				elif grupo.tipo == 1 or grupo.tipo == 3:
					print "tipo 1 o 3"

					RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por,
					aceptado_por=invitado_por, aceptado=True)  # crea un objecto de RequestInvitacion con aceptado True					
					UsuariosGrupo.objects.create(usuario=usuario_invitado, grupo=grupo)  # Crea un UsuariosGrupo object

				# Si el usuario que invita es admin del grupo
				elif UsuariosGrupo.objects.filter(usuario=invitado_por, grupo=grupo, es_admin=True, activo=True).exists():
					print "tipo 2 o 4"
					RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por,
					aceptado_por=invitado_por, aceptado=True)  # crea un objecto de RequestInvitacion con aceptado True
					UsuariosGrupo.objects.create(usuario=usuario_invitado, grupo=grupo)  # Crea un UsuariosGrupo object

				else:
					# No es abierto ni es admin, crear RequestInvitacion sin aceptado=True
					print "no es abierto ni es admin"
					RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por)

			return HttpResponse("Invitaciones Creadas", status=201)

		else:
			return HttpResponse("No encontro los args",  status=400)

	else:
		return HttpResponse("No Ajax", status=403)


def aceptar_ajax(request):
	
	if request.is_ajax():
		request_invitacion_id = request.POST.get("requestId", "")
		request_invitacion = RequestInvitacion.objects.get(id=request_invitacion_id)

		# RequestInvitacion aceptar
		aceptado_por = Perfil.objects.get(usuario=request.user)
		request_invitacion.aceptado_por = aceptado_por
		request_invitacion.aceptado = True
		request_invitacion.save()

		# Crear UsuarioGrupo
		if UsuariosGrupo.objects.filter(usuario=request_invitacion.usuario_invitado, grupo=request_invitacion.grupo, activo=True).exists():
			return HttpResponse("el usuario ya es miembro", status=200)
		else:
			UsuariosGrupo.objects.create(usuario=request_invitacion.usuario_invitado, grupo=request_invitacion.grupo)
			return HttpResponse("nuevo usuario de grupo creado", status=201)

	else:
		return HttpResponse("No Ajax", status=400)


def negar_invitacion(request):

	if request.is_ajax():
		request_invitacion_id = request.POST.get("requestId", "")
		request_invitacion = RequestInvitacion.objects.get(id=request_invitacion_id)

		# Request Invitacion marcar eliminado
		request_invitacion.eliminado = True
		request_invitacion.save()

		return HttpResponse("RequestInvitacion marcada como eliminada", status=200)

	else:
		return HttpResponse("No Ajax", status=400)


def request_entrar_ajax(request):

	if request.is_ajax():
		grupo_id = request.POST.get("grupo_id", "")

		grupo = Grupo.objects.get(id=grupo_id)
		perfil_usuario_invitado = Perfil.objects.get(usuario=request.user)

		RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=perfil_usuario_invitado)

		return HttpResponse("request_invitacion creada", status=201)

	else:
		return HttpResponse("No Ajax", status=400)
