# -*- coding: utf-8 -*-
from django import forms
from django.forms import TextInput, URLInput, Textarea, CheckboxInput, HiddenInput, Select

from models import BibliotecaCompartida


class FormNuevoLibro(forms.Form):
    titulo = forms.CharField(max_length=255, required=True, widget=TextInput(attrs={'class': 'form-control'}))
    autor = forms.CharField(max_length=255, required=True, widget=TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(max_length=2500, required=False, widget=Textarea(attrs={'class': 'form-control',
                                                                                          'placeholder': 'Edición, traductor, un link a Amazon que muestre la versión del libro que tienes, el estado del libro o cualquier información extra que desees compartir.'}))
    disponible = forms.BooleanField(required=False, initial=True,
                                    help_text="Este libro será compartido con tu ciudad y tus grupos",
                                    widget=CheckboxInput())


class FormPedirLibro(forms.Form):
    libro_id = forms.IntegerField(required=False, widget=HiddenInput())
    mensaje = forms.CharField(max_length=500, required=False,
                              widget=Textarea(attrs={'class': 'form-control', 'placeholder': 'Hola ...'}))
    telefono = forms.CharField(required=False, widget=TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Importante. Para que pueda contactarte.'}))
    email = forms.CharField(max_length=500, required=False, widget=TextInput(attrs={'class': 'form-control'}))


class NuevaBibliotecaCompartida(forms.ModelForm):
    class Meta:
        model = BibliotecaCompartida
        fields = ('nombre', 'direccion', 'imagen', 'horario_apertura')

        widgets = {
            'nombre': TextInput(attrs={'class': 'form-control'}),
            'direccion': Textarea(attrs={'class': 'form-control'}),
            'horario_apertura': TextInput(attrs={'class': 'form-control'}),
            'imagen': URLInput(attrs={'class': 'form-control'}),
            'punto_google_maps': TextInput(attrs={'class': 'form-control'}),
            'direccion_web': URLInput(attrs={'class': 'form-control'})
        }


class EditarBibliotecaCompartida(NuevaBibliotecaCompartida):

    class Meta(NuevaBibliotecaCompartida.Meta):
        fields = ('nombre', 'direccion', 'imagen', 'punto_google_maps', 'direccion_web', 'horario_apertura')


class FormPrestarLibroBCompartida(forms.Form):
    usuario = forms.CharField(max_length=255, required=True, label="Prestar a:",
                              widget=TextInput(attrs={'class': 'form-control', 'id': 'input_libro'}))


class FormCambiarLibroBCompartida(forms.Form):
    _choices = [("0", "Cambiar con una usuario que no es miembro de Letras.Club"),
                ("1", "Cambiar con un usuario de Letras.Club")]

    titulo_inicial = forms.CharField(max_length=255, required=True, label="Título del libro cambiado",
                                     widget=TextInput(attrs={'class': 'form-control', 'id': 'titulo_inicial'}))
    id_libro_cambiado = forms.IntegerField(required=True, widget=HiddenInput(
        attrs={'class': 'form-control', 'id': 'id_libro_cambiado'}))
    titulo_recibido = forms.CharField(max_length=255, required=True, label="Título del libro recibido",
                                      widget=TextInput(attrs={'class': 'form-control', 'id': 'titulo_recibido'}))
    autor_recibido = forms.CharField(max_length=255, required=True, label="Autor del libro recibido",
                                     widget=TextInput(attrs={'class': 'form-control', 'id': 'autor_recibido'}))
    usuario_cambiar = forms.CharField(max_length=255, required=False, label="Usuario con el que cambiaste el libro",
                                      widget=TextInput(attrs={'class': 'form-control', 'id': 'usuario_cambiar'}))
