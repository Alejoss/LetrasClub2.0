from django.db import models

from perfiles.models import Perfil


class Grupo(models.Model):
	nombre = models.CharField(max_length=255, blank=True)
	descripcion = models.CharField(max_length=2500, blank=True)
	imagen = models.URLField(blank=True)
	tipo = models.CharField(blank=True, max_length=50)


class UsuariosGrupo(models.Model):
	usuario = models.ForeignKey(Perfil)
	grupo = models.ForeignKey(Grupo)
	es_admin = models.BooleanField(default=False)
	activo = models.BooleanField(default=True)


class RequestGrupo(models.Model):
	usuario_invitado = models.ForeignKey(Perfil, related_name="invitado")
	invitado_por = models.ForeignKey(Perfil, related_name="invitado_por")
	aceptado_por = models.ForeignKey(Perfil, related_name="aceptado_por")
	aceptado = models.BooleanField(default=False)
	fecha_invitacion = models.DateTimeField(auto_now_add=True)
