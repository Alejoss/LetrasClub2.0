# -*- coding: utf-8 -*-
from django.db import models

from perfiles.models import Perfil


class Grupo(models.Model):
	"""
	tipo 1: Abierto, cualquier miembro puede aceptar a otro miembro
	tipo 2: Abierto, solo los admins puede aceptar a otro miembro
	tipo 3: Cerrado, cualquier miembro puede aceptar a otro miembro
	tipo 4: Cerrado, solo los admins pueden aceptar a otro miembro.
	"""
	nombre = models.CharField(max_length=255, unique=True)
	descripcion = models.CharField(max_length=2500, blank=True)
	imagen = models.URLField(blank=True)
	tipo = models.PositiveSmallIntegerField(default=1)


class UsuariosGrupo(models.Model):
	usuario = models.ForeignKey(Perfil)
	grupo = models.ForeignKey(Grupo)
	es_admin = models.BooleanField(default=False)
	activo = models.BooleanField(default=True)


class RequestInvitacion(models.Model):
	grupo = models.ForeignKey(Grupo)
	usuario_invitado = models.ForeignKey(Perfil, related_name="invitado")
	invitado_por = models.ForeignKey(Perfil, related_name="invitado_por")
	aceptado_por = models.ForeignKey(Perfil, related_name="aceptado_por", null=True)
	aceptado = models.BooleanField(default=False)
	fecha_invitacion = models.DateTimeField(auto_now_add=True)
