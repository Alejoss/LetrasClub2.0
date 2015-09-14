# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render

from letrasclub.utils import obtener_perfil
from forms import FormCrearGrupo
from models import UsuariosGrupo, Grupo, RequestInvitacion
from perfiles.models import Perfil


def crear_grupo(request):
	template = "grupos/crear_grupo.html"

	if request.method == "POST":
		form = FormCrearGrupo(request.POST)
		
		if form.is_valid():

			perfil_admin = obtener_perfil(request.user)

			# Sumar un tipo al grupo (Abierto, Cerrado, Todos puede añadir, Admins pueden añadir)
			tipo_grupo = form.obtener_tipo()
			nuevo_grupo = form.save(commit=False)
			nuevo_grupo.tipo = tipo_grupo
			
			# Situar el grupo en una ciudad si es necesario
			situar_ciudad = form.cleaned_data['situar_ciudad']

			if situar_ciudad:
				nuevo_grupo.ciudad = perfil_admin.ciudad

			nuevo_grupo.save()

			usuario_admin = UsuariosGrupo(usuario=perfil_admin, grupo=nuevo_grupo, es_admin=True)
			
			usuario_admin.save()

			# return redirect() Falta
			return HttpResponse("Grupo Creado")
		
	else:
		form = FormCrearGrupo()

		perfil = obtener_perfil(request.user)

	context = {'form': form, 'perfil': perfil}

	return render(request, template, context)


def main_grupo(request, id_grupo):
	template = "grupos/main_grupo.html"

	grupo = Grupo.objects.get(id=id_grupo)
	usuarios_grupo_obj = UsuariosGrupo.objects.filter(grupo=grupo, activo=True).select_related('usuario')
	
	miembros = [usuario_grupo_obj.usuario for usuario_grupo_obj in usuarios_grupo_obj]

	requests_entrar_grupo = None

	if grupo.tipo in [2, 4]:
		# Si solo los admins pueden aceptar !!!
		# Si el usuario es admin, mostrar los requests.
		perfil_usuario = obtener_perfil(request.user)
		if UsuariosGrupo.objects.filter(usuario=perfil_usuario, grupo=grupo, es_admin=True).exists():
			requests_entrar_grupo = RequestInvitacion.objects.filter(grupo=grupo, aceptado=False)
	else:
		requests_entrar_grupo = RequestInvitacion.objects.filter(grupo=grupo, aceptado=False)

	context = {'grupo': grupo, 'miembros': miembros, 'requests_entrar_grupo': requests_entrar_grupo}

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
				usuario_invitado = Perfil.objects.get(username=invitacion['nombre_usuario'])

				# Si cualquier persona puede sumar miembros al grupo
				if grupo.tipo == 1 or grupo.tipo == 3:
					RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por, 
					aceptado_por=invitado_por, aceptado=True)  # crea un objecto de RequestInvitacion con aceptado True
					UsuariosGrupo.objects.create(usuario=usuario_invitado, grupo=grupo)  # Crea un UsuariosGrupo object

				elif UsuariosGrupo.objects.filter(usuario=invitado_por, grupo=grupo, es_admin=True, activo=True).exists():
					RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por, 
					aceptado_por=invitado_por, aceptado=True)  # crea un objecto de RequestInvitacion con aceptado True
					UsuariosGrupo.objects.create(usuario=usuario_invitado, grupo=grupo)  # Crea un UsuariosGrupo object

				else:
					RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por)

			return HttpResponse("Invitaciones Creadas", status=201)

		else:
			return HttpResponse("No encontro los args",  status=400)

	else:
		return HttpResponse("No Ajax", status=403)


def aceptar_ajax(request):
	
	if request.is_ajax():
		request_invitacion_id = request.POST.get("request_invitacion_id", "")
		request_invitacion = RequestInvitacion.objects.get(id=request_invitacion_id)

		# RequestInvitacion aceptar
		aceptado_por = Perfil.objects.get(usuario=request.user)
		request_invitacion.aceptado_por = aceptado_por
		request_invitacion.aceptado = True
		request_invitacion.save()

		# Crear UsuarioGrupo
		if UsuariosGrupo.objects.filter(usuario=request_invitacion.usuario_invitado, grupo=request_invitacion.grupo).exists():
			return HttpResponse(status=200, reason_phrase="el usuario ya es miembro")
		else:
			UsuariosGrupo.objects.create(usuario=request_invitacion.usuario_invitado, grupo=request_invitacion.grupo)
			return HttpResponse(status=201, reason_phrase="nuevo usuario de grupo creado")

	else:
		return HttpResponse(status=400, reason_phrase="No Ajax")
