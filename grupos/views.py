# -*- coding: utf-8 -*-
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

			nuevo_grupo = form.save()

			usuario_admin = UsuariosGrupo(usuario=perfil_admin, grupo=nuevo_grupo, es_admin=True)
			
			usuario_admin.save()

			# return redirect() Falta
			return HttpResponse("Grupo Creado")
		
	else:
		form = FormCrearGrupo()

	context = {'FormCrearGrupo': form}

	return render(request, template, context)


def main_grupo(request, id_grupo):
	template = "grupos/main_grupo.html"

	grupo = Grupo.objects.get(id=id_grupo)
	usuarios = UsuariosGrupo.objects.filter(grupo=grupo)

	context = {'grupo': grupo, 'usuarios': usuarios}

	return render(request, template, context)


def invitar_ajax(request):
	
	if request.is_ajax():
		grupo_id = request.POST.get("grupo_id", "")
		usuario_invitado_id = request.POST.get("usuario_invitado_id", "")
		invitado_por_id = request.POST.get("invitado_por", "")

		if grupo_id and usuario_invitado_id and invitado_por_id:
			grupo = Grupo.objects.get(id=grupo_id)
			usuario_invitado = Perfil.objects.get(id=usuario_invitado_id)
			invitado_por = Perfil.objetcs.get(id=invitado_por_id)
		else:
			return HttpResponse(status=400, 
				reason_phrase="no se recibio un id valido. g_i: %s, u_i_i: %s, i_p: %s" % (grupo_id, usuario_invitado_id, invitado_por))

		# Si el usuario que invita es admin, aceptar la invitacion automaticamente.
		if UsuariosGrupo.objects.filter(usuario=invitado_por, grupo=grupo, es_admin=True, activo=True).exists():

			RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por, 
				aceptado_por=invitado_por, aceptado=True)  # crea un objecto de RequestInvitacion con aceptado True
			UsuariosGrupo.objects.create(usuario=usuario_invitado, grupo=grupo)

			return HttpResponse("Invitacion creada y Aceptada")

		else:
			RequestInvitacion.objects.create(grupo=grupo, usuario_invitado=usuario_invitado, invitado_por=invitado_por)

			return HttpResponse("Invitacion creada")

	else:
		return HttpResponse(status=400, "No Ajax")


def aceptar_ajax(request):
	# Acá me quedé.