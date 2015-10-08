# -*- coding: utf-8 -*-
from django.db import models

from grupos.models import Grupo
from perfiles.models import Perfil


class Notificacion(models.Model):
	"""
	tipos de notificaciones: compartio_libro_abierto, compartio_libro_grupo, comenzo_leer, termino_leer, 
	presto_libro, devolvio_libro
	"""
	fecha = models.DateTimeField(auto_now_add=True)
	tipo = models.CharField(max_length=50)
	perfil_actor = models.ForeignKey(Perfil, related_name="actor")  # El perfil de la persona que ocasiono la notificación
	perfil_target = models.ForeignKey(Perfil, null=True, related_name="target")  # Perfil opcional de segunda persona que debe recibir notificación
	grupo = models.ForeignKey(Grupo, null=True)  # Si le compete la notificacion a algun grupo
	leida = models.BooleanField(default=False)

	def __unicode__(self):
		return "Notificacion: %s - %s" % (self.perfil_actor, self.tipo)
