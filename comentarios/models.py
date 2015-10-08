# -*- coding: utf-8 -*-
from django.db import models

from grupos.models import Grupo
from perfiles.models import Perfil


class CommentGrupo(models.Model):
	#  Guarda los comentarios que van en el muro de un Grupo
	grupo = models.ForeignKey(Grupo)
	perfil = models.ForeignKey(Perfil)
	texto = models.CharField(max_length=1000)
	eliminado = models.BooleanField(default=False)
	fecha = models.DateTimeField(auto_now_add=True)
