# -*- coding: utf-8 -*-
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

from cities_light.models import City
from perfiles.models import Perfil
from grupos.models import Grupo


class Libro(models.Model):
    titulo = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=255)
    autor = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(null=True, blank=True, max_length=2500)

    def save(self, *args, **kwargs):
        if not self.id:
            # nuevo objeto, crear slug
            self.slug = slugify(self.titulo)

        super(Libro, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.slug

    class Meta:
        ordering = ["titulo"]


class LibrosLeidos(models.Model):
    perfil = models.ForeignKey(Perfil)
    libro = models.ForeignKey(Libro)
    fecha_lectura = models.DateTimeField(null=True)
    eliminado = models.BooleanField(default=False)

    def __unicode__(self):
        return "Libros Leidos object: %s - %s" % (self.perfil.usuario, self.libro.titulo)


class LibrosDisponibles(models.Model):
    # abierto_comunidad significa que estara disponible para todos en LetrasClub
    libro = models.ForeignKey(Libro)
    perfil = models.ForeignKey(Perfil)
    disponible = models.BooleanField(default=True)
    abierto_comunidad = models.BooleanField(default=True)
    prestado = models.BooleanField(default=False)
    ciudad = models.ForeignKey(City)
    eliminado = models.BooleanField(default=False)

    def cambiar_abierto_comunidad(self):
        if self.abierto_comunidad:
            self.abierto_comunidad = False
        else:
            self.abierto_comunidad = True

        self.save()

        return self.abierto_comunidad

    def __unicode__(self):
        return "Libro Disponible object: %s - %s" % (self.libro.titulo, self.perfil.usuario)

    class Meta:
        ordering = ["libro__titulo"]


class LibroDisponibleGrupo(models.Model):
    # Guarda los Libros que estan disponibles solamente en un grupo especifico
    libro_disponible = models.ForeignKey(LibrosDisponibles)
    grupo = models.ForeignKey(Grupo)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "Libro Disponible Grupo: %s - %s" % (self.libro_disponible.libro.titulo, self.grupo.nombre)


class LibrosPrestados(models.Model):
    libro = models.ForeignKey(Libro)
    perfil_dueno = models.ForeignKey(Perfil, related_name="perfil_dueno")
    perfil_receptor = models.ForeignKey(Perfil, related_name="perfil_receptor")
    fecha_max_devolucion = models.DateTimeField(null=True)
    fecha_prestamo = models.DateTimeField(null=True)
    fecha_devolucion = models.DateTimeField(null=True)
    mensaje_aceptacion = models.CharField(blank=True, max_length=500)
    receptor_anuncio_devolucion = models.BooleanField(default=False)

    def __unicode__(self):
        return "Libro Prestado object: %s - %s - %s" % (
            self.libro, self.perfil_dueno.usuario, self.perfil_receptor.usuario)


class LibrosRequest(models.Model):
    libro = models.ForeignKey(Libro)
    perfil_envio = models.ForeignKey(Perfil, related_name="perfil_envio")
    perfil_recepcion = models.ForeignKey(Perfil, related_name="perfil_recepcion")
    fecha_request = models.DateTimeField(auto_now=True)
    mensaje = models.CharField(max_length=500, blank=True)
    telefono = models.CharField(max_length=150, blank=True)
    email = models.CharField(max_length=255, blank=True)
    aceptado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)
    grupo = models.ForeignKey(Grupo, blank=True, null=True)

    def __unicode__(self):
        return "Libro Request object: %s - %s - %s" % (
            self.libro.titulo, self.perfil_envio.usuario, self.perfil_recepcion.usuario)


class TipoBCompartidas(models.Model):
    """
    Define las reglas que se imprimirán en la Biblioteca Compartida
    """
    nombre = models.CharField(max_length=150, unique=True)
    eliminado = models.BooleanField(default=False)

    def __unicode__(self):
        return self.nombre


class BibliotecaCompartida(models.Model):
    nombre = models.CharField(max_length=150, blank=True, unique=True)
    slug = models.SlugField(blank=True)
    ciudad = models.ForeignKey(City)
    punto_google_maps = models.CharField(max_length=500, blank=True)  # [latitude, longitude]
    direccion = models.CharField(max_length=500, blank=True)
    imagen = models.URLField(blank=True)
    eliminada = models.BooleanField(default=False)
    direccion_web = models.URLField(blank=True)
    horario_apertura = models.CharField(max_length=100, blank=True)
    tipo = models.ForeignKey(TipoBCompartidas, null=True)
    reglas_extra = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # nuevo objecto, crear slug
            self.slug = slugify(self.nombre)

        super(BibliotecaCompartida, self).save(*args, **kwargs)

    @property
    def direccion_gmaps(self, *args, **kwargs):
        if self.punto_google_maps:
            cadenas_texto = self.punto_google_maps.split(',')
            latitude = float(cadenas_texto[0])
            longitude = float(cadenas_texto[1])
            return latitude, longitude
        else:
            return None

    def __unicode__(self):
        return "%s %s" % (self.id, self.nombre)


class AdminsBibliotecaCompartida(models.Model):
    biblioteca_compartida = models.ForeignKey(BibliotecaCompartida)
    perfil = models.ForeignKey(Perfil, null=True)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s admin de %s" % (self.perfil.usuario.username, self.biblioteca_compartida.nombre)


class LibrosBibliotecaCompartida(models.Model):
    libro = models.ForeignKey(Libro)
    biblioteca_compartida = models.ForeignKey(BibliotecaCompartida)
    disponible = models.BooleanField(default=True)
    prestado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)

    def __unicode__(self):
        return "Libro BibliotecaCompartida: %s - %s" % (self.libro.titulo, self.biblioteca_compartida.nombre)

    class Meta:
        ordering = ['libro__titulo']


class LibrosPrestadosBibliotecaCompartida(models.Model):
    libro = models.ForeignKey(Libro)
    perfil_prestamo = models.ForeignKey(Perfil)
    biblioteca_compartida = models.ForeignKey(BibliotecaCompartida)
    fecha_max_devolucion = models.DateTimeField(null=True)
    fecha_prestamo = models.DateTimeField(auto_now_add=True, null=True)
    fecha_devolucion = models.DateTimeField(null=True)
    receptor_anuncio_devolucion = models.BooleanField(default=False)

    def __unicode__(self):
        return "Libro Biblioteca Compartida: %s - %s" % (self.libro.titulo, self.biblioteca_compartida.nombre)


class LibrosRequestBibliotecaCompartida(models.Model):
    libro_disponible = models.ForeignKey(LibrosBibliotecaCompartida)
    perfil_envio = models.ForeignKey(Perfil)
    fecha_request = models.DateTimeField(auto_now=True)
    aceptado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)
    retirado = models.BooleanField(
        default=False)  # Define si el usuario ya paso retirando el libro de la biblioteca compartida

    class Meta:
        ordering = ["fecha_request"]

    def __unicode__(self):
        return "Request prestamo biblioteca compartida: %s - %s" % (self.perfil_envio, self.libro_disponible)
