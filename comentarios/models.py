# -*- coding: utf-8 -*-
from django.db import models

from grupos.models import Grupo
from perfiles.models import Perfil
from notificaciones.models import Notificacion


class CommentGrupo(models.Model):
	#  Guarda los comentarios que van en el muro de un Grupo
	grupo = models.ForeignKey(Grupo)
	perfil = models.ForeignKey(Perfil)
	texto = models.CharField(max_length=1000)
	eliminado = models.BooleanField(default=False)
	fecha = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "Comment en grupo: %s - %s" % (self.grupo, self.perfil)

	class Meta:
		ordering = ["fecha"]


class RespuestaCommentGrupo(models.Model):
	#  Respuestas para un objeto CommentGrupo
	comment_grupo = models.ForeignKey(CommentGrupo, related_name="respuestas")
	perfil = models.ForeignKey(Perfil)
	texto = models.CharField(max_length=1000)
	eliminado = models.BooleanField(default=False)
	fecha = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "Respuesta al CommentGrupo en el grupo: %s" % (self.comment_grupo.grupo.nombre)

	class Meta:
		ordering = ["fecha"]


class CommentNotificacion(models.Model):
	#  Comentarios en notificaciones
	notificacion = models.ForeignKey(Notificacion, related_name="respuestas")
	perfil = models.ForeignKey(Perfil)
	texto = models.CharField(max_length=1000)
	eliminado = models.BooleanField(default=False)
	fecha = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "Respuesta a la Notificacion: %s" % (self.notificacion)

	class Meta:
		ordering = ["fecha"]


class CommentPerfil(models.Model):
	#  Comentarios en el muro de un perfil
	muro = models.ForeignKey(Perfil, related_name="muro")
	perfil = models.ForeignKey(Perfil, related_name="comentarista")
	texto = models.CharField(max_length=1000)
	eliminado = models.BooleanField(default=False)
	fecha = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "Comentario en el perfil de: %s" % (self.muro.perfil.usuario.username)

	class Meta:
		ordering = ["fecha"]


class RespuestaCommentPerfil(models.Model):
	#  Respuestas para un objeto CommentGrupo
	comment_perfil = models.ForeignKey(CommentPerfil, related_name="respuestas")
	perfil = models.ForeignKey(Perfil)
	texto = models.CharField(max_length=1000)
	eliminado = models.BooleanField(default=False)
	fecha = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "Respuesta al comment_perfil en el grupo: %s" % (self.comment_perfil.perfil.usuario.username)

	class Meta:
		ordering = ["fecha"]
