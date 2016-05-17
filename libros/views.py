# -*- coding: utf-8 -*-
import json

from datetime import datetime

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from social.apps.django_app.default.models import UserSocialAuth

from cities_light.models import City
from libros.models import LibrosDisponibles, LibrosPrestados, Libro, LibrosRequest, BibliotecaCompartida, \
    LibrosBibliotecaCompartida, LibrosPrestadosBibliotecaCompartida, LibroDisponibleGrupo, \
    LibrosRequestBibliotecaCompartida, AdminsBibliotecaCompartida
from perfiles.models import Perfil
from grupos.models import Grupo, UsuariosGrupo
from notificaciones.models import Notificacion

from forms import FormNuevoLibro, FormPedirLibro, NuevaBibliotecaCompartida, EditarBibliotecaCompartida, \
    FormPrestarLibroBCompartida, \
    FormCambiarLibroBCompartida
from letrasclub.utils import obtener_perfil, definir_fecha_devolucion, obtenerquito, mail_pedir_libro, \
    mail_anunciar_devolucion, \
    mail_aceptar_prestamo, obtener_avatar_large, obtener_historial_libros, mail_pedir_libro_bcompartida, \
    obtener_muro_bcompartida


def main(request):
    """
    Muestra un search de libros, las últimas acciones que han tomado los usuarios en la red,
    y algo más
    """
    template = "libros/inicio.html"

    # PKs de las bcompartidas que salen en la portada
    pks_bcompartidas_portada = {'Mercado de Libros': 2, 'Red de Libros': 3, 'Renacer Cultural': 5, 'CafeArte': 4,
                                'Z Lifestyle Gallery': 13, 'La Cafeteria': 14, 'Thani': 15, 'Biblos Mauricio': 16,
                                'UWI': 17, 'Andoteca de Guapulo': 8, 'Andoteca Pobre Diablo': 12, 'Andoteca Nayon': 11}
    pks_list = []

    for bcompartida_pk in pks_bcompartidas_portada.itervalues():
        pks_list.append(bcompartida_pk)

    bibliotecas_compartidas = BibliotecaCompartida.objects.filter(pk__in=pks_list)

    context = {'bibliotecas_compartidas': bibliotecas_compartidas}
    return render(request, template, context)


@login_required
def nuevo_libro(request, tipo_dueno, slug_biblioteca_compartida):
    """
    Muestra un formulario para la creación de un nuevo Libro.
    Recibe tipo_dueno que puede ser 'perfil' o 'biblioteca compartida' y el username del dueno
    """

    template = "libros/nuevo_libro.html"
    bcompartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)

    if request.method == "POST":
        form = FormNuevoLibro(request.POST)

        if form.is_valid():
            titulo = form.cleaned_data.get("titulo", "")
            autor = form.cleaned_data.get("autor", "")
            descripcion = form.cleaned_data.get("descripcion", "")
            disponible = form.cleaned_data.get("disponible", "")

            libro_creado = Libro(titulo=titulo, autor=autor, descripcion=descripcion)
            libro_creado.save()
            perfil_usuario = obtener_perfil(request.user)
            quito = obtenerquito()

            if disponible:
                if tipo_dueno == "perfil":
                    # Esto no esta en uso
                    # !!! Falta opcionalidad para cambiar ciudad
                    # !!! Todos los libros son marcados disponibles en Quito !!!
                    libro_disponible_obj = LibrosDisponibles(libro=libro_creado, perfil=perfil_usuario, ciudad=quito)
                    libro_disponible_obj.save()

                    # Crear notificacion compartio libro abierto
                    Notificacion.objects.compartio_libro_abierto(perfil_usuario, libro_creado)

                    if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():
                        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil_usuario,
                                                                          activo=True).select_related("grupo")
                        # crear objetos LibroDisponiblesGrupo
                        for u_grupo in usuarios_grupo_obj:
                            LibroDisponibleGrupo.objects.create(libro_disponible=libro_disponible_obj,
                                                                grupo=u_grupo.grupo)
                            Notificacion.objects.compartio_libro_grupo(perfil_usuario, libro_creado, u_grupo.grupo)

                    return HttpResponseRedirect(reverse('libros:mi_biblioteca'))

                elif tipo_dueno == "biblioteca_compartida":
                    libro_disponible_obj = LibrosBibliotecaCompartida(biblioteca_compartida=bcompartida,
                                                                      libro=libro_creado)
                    libro_disponible_obj.save()

                    return HttpResponseRedirect(
                        reverse('libros:editar_libros_bcompartida',
                                kwargs={'slug_biblioteca_compartida': bcompartida.slug}))

            else:
                # Si no lo marco disponible, crear el objeto LibrosDisponibles pero con abierto_comunidad=False
                LibrosDisponibles.objects.create(libro=libro_creado, perfil=perfil_usuario, ciudad=quito,
                                                 abierto_comunidad=False, disponible=False)

                return HttpResponseRedirect(reverse('libros:mi_biblioteca'))

    else:
        form = FormNuevoLibro()

    context = {'form': form, 'tipo_dueno': tipo_dueno, 'biblioteca_compartida': bcompartida}
    return render(request, template, context)


@login_required
def mi_biblioteca(request):
    """
    Muestra los libros que ha subido el usuario, tanto prestados como disponibles
    """
    template = "libros/mi_biblioteca.html"
    perfil_usuario = obtener_perfil(request.user)
    grupos_usuario = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).select_related("grupo")
    libros_disponibles = LibrosDisponibles.objects.filter(perfil=perfil_usuario, disponible=True, prestado=False)
    libros_no_disponibles = LibrosDisponibles.objects.filter(perfil=perfil_usuario, disponible=False, prestado=False)
    libros_prestados = LibrosPrestados.objects.filter(perfil_dueno=perfil_usuario, fecha_devolucion=None)

    grupos_list = [(g.grupo.id, g.grupo.nombre) for g in grupos_usuario]
    grupos_json = json.dumps(grupos_list)

    context = {
        'grupos_json': grupos_json,
        'libros_disponibles': libros_disponibles,
        'libros_prestados': libros_prestados,
        'libros_no_disponibles': libros_no_disponibles
    }

    return render(request, template, context)


def libros_ciudad(request, slug_ciudad, id_ciudad):
    """
    Recibe como parametro una ciudad, un id de la ciudad y un filtro. 
    renderea un html con los libros ordenados por el filtro
    """

    template = "libros/libros_ciudad.html"
    ciudad = City.objects.get(pk=id_ciudad)

    perfil_usuario = None
    if request.user.is_authenticated():
        perfil_usuario = obtener_perfil(request.user)

    libros_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida__ciudad=ciudad,
                                                                   disponible=True)
    num_libros_disponibles = libros_disponibles.count()
    bibliotecas_compartidas = BibliotecaCompartida.objects.filter(ciudad=ciudad)

    # Muestra libros disponibles, dos libro de cada bcompartida.
    lista_libros_disponibles = []
    for bcompartida in bibliotecas_compartidas:
        libro_bcompartida = libros_disponibles.filter(biblioteca_compartida=bcompartida, disponible=True).last()
        if libro_bcompartida:
            lista_libros_disponibles.append(libro_bcompartida)

    # Puntos Goolge Maps
    gmap_bcompartidas = []
    for b in bibliotecas_compartidas:
        if b.punto_google_maps:
            latlong = b.punto_google_maps.split(", ")
            marker_gmaps = [b.nombre, latlong[0].strip(), latlong[1].strip(), b.slug, b.tipo.nombre]
            gmap_bcompartidas.append(marker_gmaps)

    gmap_bcompartidas = json.dumps(gmap_bcompartidas)

    # Grupos abiertos de la ciudad
    grupos_abiertos = None
    if Grupo.objects.filter(ciudad=ciudad, tipo__in=[1, 2]).exists():
        grupos_abiertos = Grupo.objects.filter(ciudad=ciudad, tipo__in=[1, 2])

    grupos_usuario = None
    if perfil_usuario:
        if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():
            grupos_usuario = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True)

    context = {
        'ciudad': ciudad,
        'lista_libros_disponibles': lista_libros_disponibles,
        'num_libros_disponibles': num_libros_disponibles,
        'bibliotecas_compartidas': bibliotecas_compartidas,
        'gmap_bcompartidas': gmap_bcompartidas,
        'grupos_abiertos': grupos_abiertos,
        'grupos_usuario': grupos_usuario
    }

    return render(request, template, context)


def lista_libros_ciudad(request, slug_ciudad, filtro):
    """
    Muestra todos los libros disponibles en Bcompartidas en una ciudad
    """
    template = "libros/lista_libros_ciudad.html"

    ciudad = City.objects.get(slug=slug_ciudad)

    if filtro == "titulo":
        libros_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida__ciudad=ciudad,
                                                                       disponible=True).select_related(
            "libro").order_by("libro__titulo")
    else:
        libros_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida__ciudad=ciudad,
                                                                       disponible=True).select_related(
            "libro").order_by("libro__autor")

    # Paginator
    paginator = Paginator(libros_disponibles, 100)
    page = request.GET.get("page")
    try:
        libros_disponibles = paginator.page(page)
    except PageNotAnInteger:
        libros_disponibles = paginator.page(1)
    except EmptyPage:
        libros_disponibles = paginator.page(paginator.num_pages)

    context = {'ciudad': ciudad, 'libros_disponibles': libros_disponibles, 'filtro': filtro, 'paginator': paginator}

    return render(request, template, context)


def libro(request, slug):
    """
    Esta view no está en uso, muestra el libro.
    """
    template = "libros/libro.html"
    libro_object = Libro.objects.get(slug=slug)

    context = {'libro': libro_object}
    return render(request, template, context)


def buscar_ciudad(request):
    """
    Esta view no está en uso. Muestra un form de búsqueda de ciudad y procesa la búsqeda
    """
    template = "libros/buscar_ciudad.html"

    if request.method == "POST":
        id_ciudad = request.POST.get("ciudades", "")
        set_city = request.POST.get("set_city", "")

        ciudad = City.objects.get(id=id_ciudad)

        if set_city:
            perfil_usuario = obtener_perfil(request.user)
            perfil_usuario.ciudad = ciudad
            perfil_usuario.save()

        return HttpResponseRedirect(reverse('libros:libros_ciudad',
                                            kwargs={'slug_ciudad': ciudad.slug, 'id_ciudad': ciudad.id,
                                                    'filtro': 'titulo'}))

    ciudades = City.objects.all()
    nombres_ciudades_importantes = ["Quito", "Guayaquil", "Cuenca"]
    ciudades_importantes = []

    for nombre in nombres_ciudades_importantes:
        ciudad = City.objects.get(name=nombre)
        ciudades_importantes.append(ciudad)

    context = {'ciudades': ciudades, 'ciudades_importantes': ciudades_importantes}

    return render(request, template, context)


@login_required
def pedir_libro(request, id_libro_disponible, id_grupo=None):
    template = "libros/pedir_libro.html"
    """
    Recibe un id de un objeto LibrosDisponibles, renderiza un form con un mensaje editable que le va a llegar
    al dueño del libro    
    """
    perfil_usuario = obtener_perfil(request.user)

    if request.method == "POST":

        form = FormPedirLibro(request.POST)

        if form.is_valid():

            mensaje = form.cleaned_data.get("mensaje", "")
            telefono = form.cleaned_data.get("telefono", "")
            email = form.cleaned_data.get("email", "")
            libro_id = form.cleaned_data.get("libro_id", "")

            libro_request = Libro.objects.get(id=libro_id)
            perfil_envio = obtener_perfil(request.user)
            perfil_recepcion = LibrosDisponibles.objects.get(id=id_libro_disponible).perfil

            if id_grupo:
                grupo = Grupo.objects.get(id=id_grupo)
                request_libro = LibrosRequest(libro=libro_request, perfil_envio=perfil_envio,
                                              perfil_recepcion=perfil_recepcion,
                                              mensaje=mensaje, telefono=telefono, email=email, grupo=grupo)
            else:
                request_libro = LibrosRequest(libro=libro_request, perfil_envio=perfil_envio,
                                              perfil_recepcion=perfil_recepcion,
                                              mensaje=mensaje, telefono=telefono, email=email)
            request_libro.save()

            if perfil_recepcion.usuario.email:
                mail_pedir_libro(request_libro, mensaje)

            return HttpResponseRedirect(reverse('perfiles:perfil_propio'))

    libro_disponible_obj = LibrosDisponibles.objects.get(id=id_libro_disponible)

    form_pedir_libro = FormPedirLibro(initial={
        'libro_id': libro_disponible_obj.libro.id,
        'telefono': perfil_usuario.numero_telefono_contacto,
        'email': request.user.email,
    })

    avatar = obtener_avatar_large(libro_disponible_obj.perfil)

    context = {'libro_disponible': libro_disponible_obj, 'form_pedir_libro': form_pedir_libro, 'avatar': avatar,
               'id_grupo': id_grupo}

    return render(request, template, context)


@login_required
def libro_request(request, libro_request_id):
    """
    view en la que el usuario acepta o niega el pedido de préstamo de libro
    """
    template = "libros/libro_request.html"
    libro_request = get_object_or_404(LibrosRequest, id=libro_request_id, eliminado=False)

    if request.user != libro_request.perfil_recepcion.usuario:
        raise PermissionDenied

    if request.method == "POST":
        decision = request.POST.get("prestar", "")
        if decision == "prestado":
            libro_request.aceptado = True
            libro_request.save()
            mensaje = strip_tags(request.POST.get("mensaje_aceptacion", ""))
            tiempo_prestamo = request.POST.get("tiempo_max_devolucion", "")
            fecha_max_devolucion = definir_fecha_devolucion(datetime.today(), tiempo_prestamo)

            fecha_prestamo = datetime.today()
            libro_prestado = LibrosPrestados(libro=libro_request.libro, perfil_receptor=libro_request.perfil_envio,
                                             perfil_dueno=libro_request.perfil_recepcion, fecha_prestamo=fecha_prestamo,
                                             mensaje_aceptacion=mensaje,
                                             fecha_max_devolucion=fecha_max_devolucion)
            libro_prestado.save()

            libro_disponible_obj = LibrosDisponibles.objects.filter(libro=libro_request.libro,
                                                                    perfil=libro_request.perfil_recepcion).first()
            libro_disponible_obj.disponible = False
            libro_disponible_obj.prestado = True

            libro_disponible_obj.save()

            # Si el request fue hecho en un grupo, hay que marcar no activo en ese LibroDisponibleGrupo
            if libro_request.grupo:
                if LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible_obj,
                                                       grupo=libro_request.grupo).exists():
                    libro_disponible_grupo = LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible_obj,
                                                                                 grupo=libro_request.grupo).first()
                    libro_disponible_grupo.activo = False
                    libro_disponible_grupo.save()

            # Crear notificacion y si es necesario, notificacion en el grupo
            if libro_request.grupo:
                Notificacion.objects.presto_libro(libro_prestado.perfil_dueno, libro_prestado.perfil_receptor,
                                                  libro_prestado.libro, libro_request.grupo)
            else:
                Notificacion.objects.presto_libro(libro_prestado.perfil_dueno, libro_prestado.perfil_receptor,
                                                  libro_prestado.libro)

            if libro_prestado.perfil_receptor.usuario.email:
                mail_aceptar_prestamo(libro_prestado)

            return HttpResponseRedirect(reverse('libros:mi_biblioteca'))

        elif decision == "no_prestar":
            libro_request.aceptado = False
            libro_request.eliminado = True
            libro_request.save()

            return HttpResponseRedirect(reverse('libros:mi_biblioteca'))
    else:
        pass

    perfil_request = libro_request.perfil_envio

    historial_libros = obtener_historial_libros(perfil_request)
    avatar = obtener_avatar_large(perfil_request)

    ldisponibles_perfil_request = LibrosDisponibles.objects.filter(perfil=perfil_request, disponible=True,
                                                                   prestado=False).count()

    context = {'libro_request': libro_request, 'avatar': avatar, 'historial_libros': historial_libros,
               'ldisponibles_perfil_request': ldisponibles_perfil_request}

    return render(request, template, context)


@login_required
def prestar_libro(request, libro_request_id):
    """
    view que muestra un mensaje al usuario que ha aceptado prestar un libro
    """
    template = "libros/prestar_libro.html"

    libro_request = LibrosRequest.objects.get(id=libro_request_id)
    datos_contacto = libro_request.perfil_envio.datos_contacto()

    context = {'libro_request': libro_request, 'datos_contacto': datos_contacto}

    return render(request, template, context)


@login_required
def nueva_biblioteca_compartida(request, slug_ciudad, id_ciudad):
    """
    Muestra formulario para creacion de BibliotecaCompartida NO ESTA EN USO
    """

    template = "libros/nueva_biblioteca_compartida.html"

    ciudad = get_object_or_404(City, id=id_ciudad)

    if request.method == "POST":
        form = NuevaBibliotecaCompartida(request.POST)

        if form.is_valid():
            #  !!! Crear AdminBibliotecaCompartida object
            biblioteca_compartida = form.save(commit=False)
            biblioteca_compartida.ciudad = ciudad
            biblioteca_compartida.save()

            return HttpResponseRedirect(reverse('libros:libros_ciudad',
                                                kwargs={'slug_ciudad': ciudad.slug, 'id_ciudad': ciudad.id,
                                                        'filtro': 'titulo'}))

    else:
        form = NuevaBibliotecaCompartida()

    context = {'ciudad': ciudad, 'form': form}

    return render(request, template, context)


def biblioteca_compartida(request, slug_biblioteca_compartida):
    template = "libros/biblioteca_compartida.html"

    bcompartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)
    usuario_es_administrador = False

    if request.user.is_authenticated():
        perfil = obtener_perfil(request.user)

        if AdminsBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida, perfil=perfil):
            usuario_es_administrador = True

    libros_bcompartida = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida,
                                                                   disponible=True, prestado=False)
    num_libros_bcompartida = libros_bcompartida.count()

    punto_gmaps = None
    if bcompartida.direccion_gmaps:
        latitude, longitude = bcompartida.direccion_gmaps
        punto_gmaps = [latitude, longitude]

    actividad = []
    actividad_0 = obtener_muro_bcompartida(bcompartida)
    for act in actividad_0:
        if act.__class__.__name__ == "CommentBCompartida":
            actividad.append((act, "comment"))
        else:
            actividad.append((act, "notificacion"))

    context = {'biblioteca_compartida': bcompartida, 'usuario_es_administrador': usuario_es_administrador,
               'libros_bcompartida': libros_bcompartida, 'num_libros_bcompartida': num_libros_bcompartida,
               'punto_gmaps': punto_gmaps, 'actividad': actividad}

    return render(request, template, context)


def cinco_libros_bcompartida(request):
    """
    AJAX obtiene 5 libros disponibles de una biblioteca compartida
    """
    if request.is_ajax():
        biblioteca_slug = request.GET.get("bcompartida_slug")
        biblioteca_compartida = get_object_or_404(BibliotecaCompartida, slug=biblioteca_slug)
        libros = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=biblioteca_compartida, disponible=True,
                                                           eliminado=False, prestado=False).select_related('libro')[:5]
        lista_libros = [(l.libro.titulo).title() for l in libros]
        bcompartida_url = reverse('libros:biblioteca_compartida',
                                  kwargs={'slug_biblioteca_compartida': unicode(biblioteca_compartida.slug)})
        libros_json = json.dumps(
            {'libros': lista_libros, 'datos_bcompartida': [bcompartida_url, biblioteca_compartida.nombre]})

        return HttpResponse(libros_json)

    else:
        return HttpResponse(status=400)


@login_required
def editar_info_bcompartida(request, slug_biblioteca_compartida):
    """
    Esta view sirve para editar la info de la biblioteca compartida
    """

    template = "libros/editar_info_bcompartida.html"
    bcompartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)
    perfil_usuario = obtener_perfil(request.user)

    if AdminsBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida, perfil=perfil_usuario).exists():
        pass
    else:
        raise PermissionDenied

    if request.method == "POST":
        form = EditarBibliotecaCompartida(request.POST, instance=bcompartida)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('libros:biblioteca_compartida',
                                                kwargs={'slug_biblioteca_compartida': bcompartida.slug}))
    else:
        form = EditarBibliotecaCompartida(initial={
            'punto_google_maps': bcompartida.punto_google_maps,
            'nombre': bcompartida.nombre,
            'direccion': bcompartida.direccion,
            'imagen': bcompartida.imagen,
            'direccion_web': bcompartida.direccion_web,
            'horario_apertura': bcompartida.horario_apertura,
        })

    # Si no es un usuario que hiso login con Facebook, entonces hay que mostrar link a editar_info_personal
    if UserSocialAuth.objects.filter(user=request.user).exists():
        es_usuario_social = True
    else:
        es_usuario_social = False

    context = {'biblioteca_compartida': bcompartida, 'form': form, 'es_usuario_social': es_usuario_social}

    return render(request, template, context)


@login_required
def editar_libros_bcompartida(request, slug_biblioteca_compartida):
    """
    Permite editar los libros de la Biblioteca Compartida
    """

    template = "libros/editar_libros_bcompartida.html"

    bcompartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)

    libros_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida,
                                                                   disponible=True, prestado=False, eliminado=False)
    libros_no_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida,
                                                                      disponible=False,
                                                                      prestado=False, eliminado=False)

    context = {'biblioteca_compartida': bcompartida,
               'libros_disponibles': libros_disponibles,
               'libros_no_disponibles': libros_no_disponibles}

    return render(request, template, context)


@login_required
def prestar_libro_bcompartida(request, id_libro_compartido):
    """
    Permite al admin de la biblioteca compartida aceptar el request de prestar libro    
    """

    template = "libros/prestar_libro_bcompartida.html"

    libro_disponible_obj = LibrosBibliotecaCompartida.objects.select_related('biblioteca_compartida').get(
        id=id_libro_compartido)

    if request.method == "POST":
        form = FormPrestarLibroBCompartida(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('usuario', '')

            # crear LibrosPrestadosBibliotecaCompartida object
            perfil_usuario_prestamo = Perfil.objects.get(usuario__username=username)
            libro_prestado = LibrosPrestadosBibliotecaCompartida(libro=libro_disponible_obj.libro,
                                                                 perfil_prestamo=perfil_usuario_prestamo,
                                                                 biblioteca_compartida=libro_disponible_obj.biblioteca_compartida)
            libro_prestado.save()

            # poner no disponible a LibrosBibliotecaCompartida object
            libro_disponible_obj.disponible = False
            libro_disponible_obj.prestado = True
            libro_disponible_obj.save()

            # Crear notificacion
            Notificacion.objects.bcompartida_presto(libro_disponible_obj.biblioteca_compartida, perfil_usuario_prestamo,
                                                    libro_disponible_obj.libro)

            return HttpResponseRedirect(reverse('libros:editar_libros_bcompartida',
                                                kwargs={
                                                    'slug_biblioteca_compartida': libro_disponible_obj.biblioteca_compartida.slug}))

    else:
        form = FormPrestarLibroBCompartida()

    ciudad = libro_disponible_obj.biblioteca_compartida.ciudad
    perfiles_obj = Perfil.objects.filter(ciudad=ciudad).select_related("usuario")
    usernames_autocomplete = [perfil.usuario.username for perfil in perfiles_obj]

    context = {'form': form, 'libro_compartido': libro_disponible_obj,
               'usernames_autocomplete': json.dumps(usernames_autocomplete)}

    return render(request, template, context)


@login_required
def cambiar_libro_bcompartida(request, id_biblioteca_compartida, id_libro_compartido=None):
    """
    View rederiza y procesa el form para cambiar libro por otro en una biblioteca compartida.
    """
    template = "libros/cambiar_libro_bcompartida.html"

    bcompartida = BibliotecaCompartida.objects.get(id=id_biblioteca_compartida)

    libro_disponible = None
    if id_libro_compartido:
        libro_disponible = LibrosBibliotecaCompartida.objects.get(id=id_libro_compartido)

    if request.method == "POST":
        form = FormCambiarLibroBCompartida(request.POST)
        if form.is_valid():
            id_libro_cambiado = form.cleaned_data.get("id_libro_cambiado")
            titulo_nuevo_libro = form.cleaned_data.get("titulo_recibido")
            autor_nuevo_libro = form.cleaned_data.get("autor_recibido")
            #  = form.cleaned_data.get("usuario_cambiar", None)

            libro_cambiado = LibrosBibliotecaCompartida.objects.get(id=id_libro_cambiado)
            libro_cambiado.disponible = False
            libro_cambiado.eliminado = True
            libro_cambiado.save()

            nuevo_libro = Libro.objects.create(titulo=titulo_nuevo_libro, autor=autor_nuevo_libro)
            LibrosBibliotecaCompartida.objects.create(libro=nuevo_libro, biblioteca_compartida=bcompartida)

            # Crear notificacion
            # if username_cambiar:
            #     if Perfil.objects.filter(usuario__username=username_cambiar).exists():
            #         usuario_cambiar = Perfil.objects.get(usuario__username=username_cambiar)
            #         Notificacion.objects.bcompartida_cambio(biblioteca_compartida, libro_cambiado.libro, nuevo_libro,
            #                                                 usuario_cambiar)

            Notificacion.objects.bcompartida_cambio(bcompartida, libro_cambiado.libro, nuevo_libro)

            return redirect('libros:editar_libros_bcompartida', slug_biblioteca_compartida=bcompartida.slug)

    else:
        if id_libro_compartido:
            form = FormCambiarLibroBCompartida(initial={
                'titulo_inicial': libro_disponible.libro.titulo,
                'id_libro_cambiado': libro_disponible.id
            })
        else:
            form = FormCambiarLibroBCompartida()

    libros_bcompartida = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida,
                                                                   disponible=True).select_related("libro")
    titulos_autocomplete = {}
    for libro_bc in libros_bcompartida:
        titulos_autocomplete[libro_bc.libro.titulo] = libro_bc.id

    usuarios_autocomplete_obj = Perfil.objects.filter(ciudad=bcompartida.ciudad).select_related("usuario")
    usernames_autocomplete = [perfil.usuario.username for perfil in usuarios_autocomplete_obj]

    context = {'form': form, 'libro_disponible': libro_disponible,
               'titulos_autocomplete': json.dumps(titulos_autocomplete),
               'biblioteca_compartida': bcompartida,
               'usernames_autocomplete': json.dumps(usernames_autocomplete)}

    return render(request, template, context)


# Ajax Calls
@login_required
def marcar_no_disponible(request):
    """
    Ajax view que procesa un libro disponible y la marca como no disponible"
    """
    if request.is_ajax():
        id_libro_disponible = request.POST.get('id_libro_disp', '')
        tipo = request.POST.get('tipo', '')

        if not id_libro_disponible or not tipo:
            return HttpResponse(status=400)  # Bad Request

        if tipo == "perfil":
            libro_disponible = get_object_or_404(LibrosDisponibles, id=id_libro_disponible)
            libro_disponible.disponible = False
            libro_disponible.save()

        elif tipo == "biblioteca":
            libro_disponible_obj = get_object_or_404(LibrosBibliotecaCompartida, id=id_libro_disponible)
            libro_disponible_obj.disponible = False
            libro_disponible_obj.save()

        return HttpResponse("libro marcado como no disponible", status=200)
    else:
        return HttpResponse("No es ajax")


@login_required
def marcar_disponible(request):
    """
    Ajax request, marca el libro como disponible
    """

    if request.is_ajax():
        # !!! Notificacion??

        id_libro = request.POST.get('id_libro', '')
        tipo = request.POST.get('tipo', '')

        if not id_libro or not tipo:
            return HttpResponse(status=400)  # Bad Request

        if tipo == "perfil":
            libro_no_disponible = get_object_or_404(LibrosDisponibles, id=id_libro)
            libro_no_disponible.disponible = True
            libro_no_disponible.save()

            return HttpResponse("libo marcado como disponible", status=200)

        elif tipo == "biblioteca":
            libro_bcompartida_obj = get_object_or_404(LibrosBibliotecaCompartida, id=id_libro)
            libro_bcompartida_obj.disponible = True
            libro_bcompartida_obj.save()

            return HttpResponse("libro marcado como disponible", status=200)
    else:
        return HttpResponse("No es ajax")


@login_required
def marcar_devuelto(request):
    """
    Marca un libro no disponible como disponible 
    Marca el objeto correspondiente al libro prestado como devuelto y guarda la fecha
    """
    if request.is_ajax():
        id_libro_prestado = request.POST.get('id_libro', '')
        tipo = request.POST.get('tipo', '')
        fecha_devolucion = datetime.today()

        if not id_libro_prestado or not tipo:
            return HttpResponse(status=400)  # Bad Request

        if tipo == "perfil":
            libro_prestado = get_object_or_404(LibrosPrestados, id=id_libro_prestado)
            libro_prestado.devuelto = True
            libro_prestado.fecha_devolucion = fecha_devolucion
            libro_prestado.save()

            libro_no_disponible = LibrosDisponibles.objects.filter(libro=libro_prestado.libro,
                                                                   perfil=libro_prestado.perfil_dueno).first()
            libro_no_disponible.disponible = True
            libro_no_disponible.prestado = False
            libro_no_disponible.save()

        elif tipo == "biblioteca":
            libro_prestado = get_object_or_404(LibrosPrestadosBibliotecaCompartida, id=id_libro_prestado)
            libro_prestado.fecha_devolucion = fecha_devolucion
            libro_prestado.save()

            libro_no_disponible = LibrosBibliotecaCompartida.objects.filter(libro=libro_prestado.libro,
                                                                            biblioteca_compartida=libro_prestado.biblioteca_compartida).first()
            libro_no_disponible.disponible = True
            libro_no_disponible.prestado = False
            libro_no_disponible.save()

        return HttpResponse("libro marcado como devuelto", status=200)
    else:
        return HttpResponse("No es ajax")


@login_required
def anunciar_devolucion(request):
    """
    Sirve para enviar un mail al dueño del libro cuando el que recibió el libro_id
    ya lo devolvió. 
    """

    if request.method == "POST":

        id_libro_prestado = request.POST.get("id_libro_prestado")
        tipo = request.POST.get("tipo", "")
        perfil_usuario = obtener_perfil(request.user)

        if tipo == "bcompartida":
            libro_prestado = LibrosPrestadosBibliotecaCompartida.objects.get(id=id_libro_prestado)

            if libro_prestado.perfil_prestamo != perfil_usuario:
                raise PermissionDenied
            else:
                libro_prestado.receptor_anuncio_devolucion = True
                libro_prestado.save()

                # !!! falta enviar email a los admins

        else:
            libro_prestado = LibrosPrestados.objects.get(id=id_libro_prestado)

            if libro_prestado.perfil_receptor != perfil_usuario:
                raise PermissionDenied
            else:
                libro_prestado.receptor_anuncio_devolucion = True
                libro_prestado.save()

                if libro_prestado.perfil_dueno.usuario.email:
                    mail_anunciar_devolucion(libro_prestado)

        return HttpResponseRedirect(reverse('perfiles:perfil_propio'))
    else:
        raise PermissionDenied


@login_required
def cancelar_pedido(request):
    """
    Cancela un pedido de préstamo de un libro
    """
    if request.method == "POST":
        request_id = request.POST.get("request_id", "")
        perfil_usuario = obtener_perfil(request.user)
        libro_request = LibrosRequest.objects.get(id=request_id)

        if libro_request.perfil_envio != perfil_usuario:
            raise PermissionDenied
        else:
            libro_request.eliminado = True
            libro_request.save()

            return HttpResponse("request de libro cancelado", status=200)
    else:
        raise PermissionDenied


@login_required
def cancelar_pedido_bcompartida(request):
    """
    Cancela un pedido de préstamo de un libro
    """
    if request.method == "POST":
        request_id = request.POST.get("request_id", "")
        perfil_usuario = obtener_perfil(request.user)
        libro_request = LibrosRequestBibliotecaCompartida.objects.get(id=request_id)

        if libro_request.perfil_envio != perfil_usuario:
            raise PermissionDenied
        else:
            libro_request.eliminado = True
            libro_request.save()

            return HttpResponse("request de libro cancelado", status=200)
    else:
        raise PermissionDenied


def buscar_ajax(request, id_ciudad):
    """
    busca un libro disponible con ajax SOLAMENTE entre libros compartidos en una Biblioteca Compartida
    """
    print "llego buscar_ajax"
    if request.is_ajax():

        if request.method == "GET":
            if ('q' in request.GET) and request.GET['q'].strip():
                query_string = request.GET['q']
                filtro = request.GET['filtro']
                lista_libros_disponibles = []
                if query_string:
                    # obtener ciudad
                    ciudad = City.objects.get(id=id_ciudad)
                    if filtro == "titulo":
                        libros_disponibles = LibrosBibliotecaCompartida.objects.filter(
                            libro__titulo__icontains=query_string,
                            disponible=True, biblioteca_compartida__ciudad=ciudad).select_related('libro')
                    else:
                        libros_disponibles = LibrosBibliotecaCompartida.objects.filter(
                            libro__autor__icontains=query_string,
                            disponible=True, biblioteca_compartida__ciudad=ciudad).select_related('libro')

                    for libro_disp in libros_disponibles:
                        libro_disp_dict = {'autor': libro_disp.libro.autor, 'titulo': libro_disp.libro.titulo,
                                           'url_bcompartida': 'falta',
                                           'nombre_bcompartida': libro_disp.biblioteca_compartida.nombre}
                        lista_libros_disponibles.append(libro_disp_dict)

                    lista_libros_disponibles = json.dumps(lista_libros_disponibles)
                    print "list_libros_disponibles: %s" % lista_libros_disponibles

                    return HttpResponse(unicode(lista_libros_disponibles), status=200)
                else:
                    return HttpResponse("No query_string en request", status=400)
            else:
                return HttpResponse("No q en request", status=400)
        else:
            return HttpResponse("Solo GET permitido", status=400)

    return HttpResponse("Ajax requerido", status=400)


@login_required
def cambiar_dueno_libros(request):
    """
    Acción para el admin, cambia el dueño de los libros seleccionados
    """
    template = 'cambiar_dueno_libro.html'

    if not request.user.is_superuser:
        raise PermissionDenied

    libros_ids = request.session['libros']
    libros = []

    for l_id in libros_ids:
        libro = LibrosDisponibles.objects.get(id=l_id)
        libros.append(libro)

    if request.method == "POST":

        nuevo_usuario = request.POST.get('nuevo_dueno', '')

        if nuevo_usuario:
            perfil_dueno = Perfil.objects.get(usuario__username=nuevo_usuario)

            for libro in libros:
                libro.perfil = perfil_dueno
                libro.save()

            return redirect('admin:inedx')

        else:
            pass

    perfiles = Perfil.objects.all()

    context = {'libros': libros, 'perfiles': perfiles}

    return render(request, template, context)


# Ajax Calls
def info_bcompartida(request):
    # Responde con la informacion basica de la biblioteca compartida
    if request.is_ajax():
        id_bcompartida = request.GET.get("id_bcompartida", "")

        if id_bcompartida:
            bcompartida = get_object_or_404(BibliotecaCompartida, id=id_bcompartida)
            dict_bcompartida = {'nombre': bcompartida.nombre, 'ciudad': bcompartida.ciudad.name,
                                'punto_google_maps': bcompartida.punto_google_maps,
                                'direccion': bcompartida.direccion, 'imagen': bcompartida.imagen,
                                'tipo': bcompartida.tipo.nombre}

            bcompartida_json = json.dumps(dict_bcompartida)

            return HttpResponse(bcompartida_json)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)


def info_libro_grupos_ajax(request):
    # Responde con los grupos en que está compartido el libro y si está compartido con todos
    if request.is_ajax():
        id_libro_disponible = request.GET.get('id_libro_disponible')
        libro_disponible = LibrosDisponibles.objects.get(id=id_libro_disponible)

        data_response = [libro_disponible.abierto_comunidad]

        grupos = {}
        grupos_libro = None
        if LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible).exists():
            # Revisa si el libro esta prestado en algun Grupo en especifico
            grupos_libro = LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible,
                                                               activo=True).select_related('grupo')
            for g in grupos_libro:
                grupos[g.grupo.id] = [g.grupo.nombre]

        data_response.append(grupos)

        return HttpResponse(json.dumps(data_response), status=200)

    else:
        return HttpResponse(status=400)


def compartir_con_grupo_ajax(request):
    # Ajax para compartir libro con grupo desde Mi Biblioteca

    if request.is_ajax():
        grupo_id = request.POST.get('grupo_id')
        libro_disp_id = request.POST.get('libro_disp_id', "")

        grupo = Grupo.objects.get(id=grupo_id)
        libro_disponible = LibrosDisponibles.objects.get(id=libro_disp_id)
        libro_grupo, creado = LibroDisponibleGrupo.objects.get_or_create(grupo=grupo, libro_disponible=libro_disponible)
        if not creado:
            # Si no se creo el obj, asegurarse que este activo
            libro_grupo.activo = True
            libro_grupo.save()

        # crear notificacion
        perfil_usuario = obtener_perfil(request.user)
        Notificacion.objects.compartio_libro_grupo(perfil_usuario, libro_disponible.libro, grupo)

        return HttpResponse("Libro compartido", status=200)

    else:
        return HttpResponse(status=400)


def no_compartir_grupo_ajax(request):
    if request.is_ajax():
        grupo_id = request.POST.get('grupo_id')
        libro_disp_id = request.POST.get('libro_disp_id')

        grupo = Grupo.objects.get(id=grupo_id)
        libro_disponible = LibrosDisponibles.objects.get(id=libro_disp_id)

        update = LibroDisponibleGrupo.objects.filter(grupo=grupo, libro_disponible=libro_disponible).update(
            activo=False)
        # update guarda el numero de fields que fueron hechos update, posiblemente mandar una señal 
        # o un loggin si es mayor a 1, significa que hay datos duplicados

        return HttpResponse(update, "Libro marcado como No compartido")

    else:

        return HttpResponse(status=400)


def compartir_todos_ajax(request):
    if request.is_ajax():
        libro_disp_id = request.POST.get('libro_disp_id', "")
        libro_disponible = LibrosDisponibles.objects.get(id=libro_disp_id)

        # como es un chackbox, cambiar el Boolean abierto_comunidad del modelo LibrosDisponibles
        nuevo_estado = libro_disponible.cambiar_abierto_comunidad()
        perfil_usuario = obtener_perfil(request.user)

        if nuevo_estado:

            # crear notificaciones
            Notificacion.objects.compartio_libro_abierto(perfil_usuario, libro_disponible.libro)

            if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():
                usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).select_related(
                    "grupo")
                for u_grupo in usuarios_grupo_obj:
                    Notificacion.objects.compartio_libro_grupo(perfil_usuario, libro_disponible.libro, u_grupo.grupo)

        else:
            # si marco no abierto_comunidad, revisar si está compartido con otros grupos, si no marcar no_disponible
            if LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible, activo=True).exists():
                pass
            else:
                libro_disponible.disponible = False
                libro_disponible.save()

        return HttpResponse(nuevo_estado, status=200)

    else:
        return HttpResponse(status=400)


def pedir_bcompartida_ajax(request):
    if request.is_ajax():

        if request.method == "POST":
            id_libro_disp = int(request.POST.get('id_libro_disp', ""))
            libro_disponible = LibrosBibliotecaCompartida.objects.select_related("biblioteca_compartida").get(
                id=id_libro_disp)
            perfil_usuario = obtener_perfil(request.user)
            request_libro = LibrosRequestBibliotecaCompartida.objects.create(libro_disponible=libro_disponible,
                                                                             perfil_envio=perfil_usuario)

            # enviar mail a admin de la biblioteca
            mail_pedir_libro_bcompartida(request_libro, libro_disponible.biblioteca_compartida)

            return HttpResponse(status=201)

        else:
            return HttpResponse(status=400)

    else:
        return HttpResponse(status=400)


def request_existente_bcompartida_ajax(request):
    """
    Recibe un id de un libro disponible (en biblioteca compartida) y responde con 403 si ya existe un request para ese libro
    por parte de ese usuario. Si no existe, responde con 200
    """

    if request.is_ajax():

        id_libro_disp = int(request.GET.get('id_libro_disp', ""))
        libro_disponible = LibrosBibliotecaCompartida.objects.get(id=id_libro_disp)
        perfil_usuario = obtener_perfil(request.user)

        if LibrosRequestBibliotecaCompartida.objects.filter(libro_disponible=libro_disponible,
                                                            perfil_envio=perfil_usuario, aceptado=False).exists():
            return HttpResponse(status=403)
        else:
            return HttpResponse(status=200)

    else:
        return HttpResponse(status=400)


def prestar_libro_bcompartida_ajax(request):
    """
    Recibe un id de un LibrosRequestBibliotecaCompartida y lo marca como aceptado, 
    !!! enviar mail al usuario que pidio el libro
    """

    if request.is_ajax():

        id_request = int(request.POST.get('id_request', ""))

        libro_request = LibrosRequestBibliotecaCompartida.objects.get(id=id_request)
        libro_request.aceptado = True

        libro_request.save()

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=400)


def rechazar_libro_bcompartida_ajax(request):
    """
    Recibe un id de un LibrosRequestBibliotecaCompartida y lo marca como eliminado,
    !!! enviar mail al usuario que pidio el libro
    """

    if request.is_ajax():

        id_request = int(request.POST.get('id_request', ""))

        libro_request = LibrosRequestBibliotecaCompartida.objects.get(id=id_request)
        libro_request.eliminado = True

        libro_request.save()

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=400)


def retiro_libro_bcompartida_ajax(request):
    """
    Recibe un id de un LibrosRequestBibliotecaCompartida y lo marca como retirado, luego crea un objeto LibrosPrestadosBibliotecaCompartida 
    !!! enviar mail al usuario que se llevó el libro
    """

    if request.is_ajax():

        id_request = int(request.POST.get('id_request', ""))

        libro_request = LibrosRequestBibliotecaCompartida.objects.filter(id=id_request).select_related(
            "libro_disponible").first()
        libro_request.retirado = True
        libro_request.save()

        LibrosPrestadosBibliotecaCompartida.objects.create(libro=libro_request.libro_disponible.libro,
                                                           perfil_prestamo=libro_request.perfil_envio,
                                                           biblioteca_compartida=libro_request.libro_disponible.biblioteca_compartida)

        # crear notificacion
        Notificacion.objects.bcompartida_presto(libro_request.libro_disponible.biblioteca_compartida,
                                                libro_request.perfil_envio, libro_request.libro_disponible.libro)

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=400)


@csrf_exempt
def crear_libros_bcompartida(request):
    json_enviado = request.body

    if not json_enviado:
        return HttpResponse("No json en el request.body", status=404)

    json_enviado = json.loads(json_enviado)
    json_enviado = json_enviado['libros_json']

    try:
        biblioteca_compartida_nombre = json_enviado['biblioteca_compartida_nombre']
    except KeyError:
        return HttpResponse("No biblioteca_compartida_nombre en el json ", status=404)

    if BibliotecaCompartida.objects.filter(nombre=biblioteca_compartida_nombre).exists():
        bcompartida = BibliotecaCompartida.objects.get(nombre=biblioteca_compartida_nombre)
    else:
        return HttpResponse("No se encontro una Biblioteca Compartida con ese nombre", status=404)

    libros_creados = []
    libros = json_enviado['libros']
    for num, libro in libros.iteritems():
        libro_enviado = [libro['titulo']]
        if Libro.objects.filter(titulo=libro['titulo'], autor=libro['autor']).exists():
            libro_enviado.append("Libro ya existe")
            libro = Libro.objects.get(titulo=libro['titulo'], autor=libro['autor'])
        else:
            libro = Libro.objects.create(titulo=libro['titulo'], autor=libro['autor'], descripcion=libro['descripcion'])
            libro_enviado.append("Libro creado")

        if LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida, libro=libro).exists():
            libro_enviado.append("LibroBCompartida YA EXISTE")
        else:
            libro_disponible_obj = LibrosBibliotecaCompartida.objects.create(biblioteca_compartida=bcompartida,
                                                                             libro=libro)

            Notificacion.objects.bcompartida_compartio(bcompartida, libro_disponible_obj.libro)
            libro_enviado.append("LibroBCompartida CREADO")

        libros_creados.append(libro_enviado)

    return HttpResponse(json.dumps(libros_creados), status=201)
