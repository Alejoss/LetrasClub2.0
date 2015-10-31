# -*- coding: utf-8 -*-
from django.db import models

from grupos.models import Grupo
from perfiles.models import Perfil
from libros.models import Libro


class NManager(models.Manager):
	"""
	Manager para el modelo Notificacion. Suma funciones para crear notificaciones
	"""

	def compartio_libro_abierto(self, perfil_actor, libro):
		notificacion = self.create(perfil_actor=perfil_actor, libro=libro, tipo="compartio_libro_abierto")

		return notificacion

	def compartio_libro_grupo(self, perfil_actor, libro, grupo):
		notificacion = self.create(perfil_actor=perfil_actor, libro=libro, grupo=grupo, tipo="compartio_libro_grupo")

		return notificacion

	def comenzo_leer(self, perfil_actor, libro, grupo=None):
		# comenzo_leer y termino_leer recibe grupo opcional, para enviar notificacion específica al grupo
		if grupo:
			notificacion = self.create(perfil_actor=perfil_actor, libro=libro, grupo=grupo, tipo="comenzo_leer")
		else:
			notificacion = self.create(perfil_actor=perfil_actor, libro=libro, tipo="comenzo_leer")

		return notificacion

	def termino_leer(self, perfil_actor, libro, grupo=None):
		if grupo:
			notificacion = self.create(perfil_actor=perfil_actor, libro=libro, grupo=grupo, tipo="termino_leer")
		else:
			notificacion = self.create(perfil_actor=perfil_actor, libro=libro, tipo="termino_leer")

		return notificacion


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
	libro = models.ForeignKey(Libro, null=True)
	leida = models.BooleanField(default=False)

	# model manager con metodos para crear notificaciones
	objects = NManager()

	class Meta:
		ordering = ["-fecha"]

	def __unicode__(self):
		return "Notificacion: %s - %s - %s" % (self.perfil_actor, self.tipo, self.libro.titulo)
