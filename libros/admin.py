# -*- coding: utf-8 -*-
from django.contrib import admin
from django.shortcuts import redirect

from libros.models import Libro, LibrosRequest, BibliotecaCompartida, LibrosBibliotecaCompartida, LibrosDisponibles, \
	LibrosPrestadosBibliotecaCompartida, LibroDisponibleGrupo, TipoBCompartidas


def cambiar_dueno(modelAdmin, request, queryset):
	selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

	request.session['libros'] = selected

	return redirect('libros:cambiar_dueno_libros')

cambiar_dueno.short_description = "Cambiar Dueno"


class LibroDisponibleAdmin(admin.ModelAdmin):
	actions = [cambiar_dueno]


class BibliotecaCompartidaAdmin(admin.ModelAdmin):
	exclude = ('slug',)

admin.site.register(Libro)
admin.site.register(LibrosRequest)
admin.site.register(BibliotecaCompartida, BibliotecaCompartidaAdmin)
admin.site.register(LibrosBibliotecaCompartida)
admin.site.register(LibrosDisponibles, LibroDisponibleAdmin)
admin.site.register(LibrosPrestadosBibliotecaCompartida)
admin.site.register(LibroDisponibleGrupo)
admin.site.register(TipoBCompartidas)
