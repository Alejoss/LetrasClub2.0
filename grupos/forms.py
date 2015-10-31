# -*- coding: utf-8 -*-
from django import forms

from models import Grupo


class FormCrearGrupo(forms.ModelForm):

	choices_apertura = (("cerrado", "Cerrado"), ("abierto", "Abierto"))
	choices_invitaciones = (("todos", "Todos"), ("admins", "Administradores"))

	descripcion = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control'}), label="Descripción")
	tipo_apertura = forms.ChoiceField(required=True, choices=choices_apertura, widget=forms.Select(attrs={'class': 'form-control'}),
		label="Será un grupo Abierto o Cerrado?")
	tipo_invitaciones = forms.ChoiceField(required=True, choices=choices_invitaciones, widget=forms.Select(attrs={'class': 'form-control'}),
		label="Quién podrá aceptar nuevos miembros en el grupo?")
	situar_ciudad = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
	# imagen = forms.URLField(required=False, label="Portada", help_text="Copia y pega la url a una imagen amplia, no muy alta. Luego podrás cambiarla si deseas.", 
	#	widget=forms.URLInput(attrs={'class': 'form-control'}))  -> Activar si se quiere imagen de portada en el grupo.

	def obtener_tipo(self):

		tipo_grupo = 1
		tipo_apertura = self.cleaned_data['tipo_apertura']
		tipo_invitaciones = self.cleaned_data['tipo_invitaciones']

		if tipo_apertura == "abierto":
			if tipo_invitaciones == "todos":
				tipo_grupo = 1  # Abierto, cualquier miembro puede aceptar a otro miembro
			elif tipo_invitaciones == "admins":
				tipo_grupo = 2  # Tipo 2: Abierto, solo los admins puede aceptar a otro miembro
		elif tipo_apertura == "cerrado":
			if tipo_invitaciones == "todos":
				tipo_grupo = 3  # Tipo 3: Cerrado, cualquier miembro puede aceptar a otro miembro
			elif tipo_invitaciones == "admins":
				tipo_grupo = 4  # Tipo 4: Cerrado, solo los admins pueden aceptar a otro miembro.

		return tipo_grupo

	class Meta:
		model = Grupo
		fields = ("nombre", "descripcion", "imagen")
		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'imagen': forms.URLInput(attrs={'class': 'form-control'})
		}
