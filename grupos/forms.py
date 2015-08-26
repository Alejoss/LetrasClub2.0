from django import forms
from django.forms import Textarea

from models import Grupo


class FormCrearGrupo(forms.ModelForm):

	choices = 
	descripcion = forms.CharField(required=True, widget=Textarea())


	class Meta:
		model = Grupo
		fields = ("nombre", "descripcion", "imagen", "tipo")



