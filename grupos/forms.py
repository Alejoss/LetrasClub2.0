# -*- coding: utf-8 -*-
from django import forms

from models import Grupo


class FormCrearGrupo(forms.ModelForm):

	choices_apertura = (("1", "Cerrado"), ("2", "Abierto"))
	choices_invitaciones = (("1", "Todos"), ("2", "Admins"))

	descripcion = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control'}), label="Descripción")
	tipo_apertura = forms.ChoiceField(required=True, choices=choices_apertura, widget=forms.Select(attrs={'class': 'form-control'}),
		label="Será un grupo Abierto o Cerrado?")
	tipo_invitaciones = forms.ChoiceField(required=True, choices=choices_invitaciones, widget=forms.Select(attrs={'class': 'form-control'}),
		label="Quién podrá aceptar a alguien en el grupo?")
	situar_ciudad = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

	def obtener_tipo(self):

		tipo_grupo = 1
		tipo_apertura = int(self.cleaned_data['tipo_apertura'])
		tipo_invitaciones = int(self.cleaned_data['tipo_invitaciones'])

		print "tipo_apertura: %s" % (tipo_apertura)
		print "tipo_invitaciones: %s" % (tipo_invitaciones)

		if tipo_apertura == 1:
			if tipo_invitaciones == 1:
				tipo_grupo = 1  #  Abierto, cualquier miembro puede aceptar a otro miembro
			elif tipo_invitaciones == 2:
				tipo_grupo = 2  #  Tipo 2: Abierto, solo los admins puede aceptar a otro miembro
		elif tipo_apertura == 2:
			if tipo_invitaciones == 1:
				tipo_grupo = 3  #  Tipo 3: Cerrado, cualquier miembro puede aceptar a otro miembro
			elif tipo_invitaciones == 2:
				tipo_grupo = 4  #  Tipo 4: Cerrado, solo los admins pueden aceptar a otro miembro.

		print "tipo_grupo: %s" % (tipo_grupo)
		return tipo_grupo

	class Meta:
		model = Grupo
		fields = ("nombre", "descripcion", "imagen")
		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'imagen': forms.URLInput(attrs={'class': 'form-control'})
		}
