# -*- coding: utf-8 -*-
import re
import json
from django.db.models import Q

from datetime import datetime

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags

from cities_light.models import City
from libros.models import LibrosDisponibles, LibrosPrestados, Libro, LibrosRequest, BibliotecaCompartida, \
                          LibrosBibliotecaCompartida, LibrosPrestadosBibliotecaCompartida, LibroDisponibleGrupo, \
                          LibrosRequestBibliotecaCompartida
from perfiles.models import Perfil
from grupos.models import Grupo, UsuariosGrupo
from notificaciones.models import Notificacion

from forms import FormNuevoLibro, FormPedirLibro, NuevaBibliotecaCompartida, EditarBibliotecaCompartida, FormPrestarLibroBCompartida, \
                        FormCambiarLibroBCompartida
from letrasclub.utils import obtener_perfil, definir_fecha_devolucion, obtenerquito, mail_pedir_libro, mail_anunciar_devolucion, \
                            mail_aceptar_prestamo, obtener_avatar_large, obtener_historial_libros, mail_pedir_libro_bcompartida


def main(request):
    """
    Muestra un search de libros, las últimas acciones que han tomado los usuarios en la red,
    y algo más
    """
    template = "libros/main.html"

    try:
        notificaciones_main = Notificacion.objects.filter(leida=False)[:20]
    except:
        notificaciones_main = Notificacion.objects.filter(leida=False)  # Puede que no haya suficientes notificaciones

    context = {'notificaciones_main': notificaciones_main}
    return render(request, template, context)


@login_required
def nuevo_libro(request, tipo_dueno, username):
    """
    Muestra un formulario para la creación de un nuevo Libro.
    Recibe tipo_dueno que puede ser 'perfil' o 'biblioteca compartida' y el username del dueno
    """

    template = "libros/nuevo_libro.html"

    if request.method == "POST":
        form = FormNuevoLibro(request.POST)
        
        if form.is_valid():            
            titulo = form.cleaned_data.get("titulo", "")
            autor = form.cleaned_data.get("autor", "")            
            descripcion = form.cleaned_data.get("descripcion", "")
            disponible = form.cleaned_data.get("disponible", "")

            nuevo_libro = Libro(titulo=titulo, autor=autor, descripcion=descripcion)
            nuevo_libro.save()
            perfil_usuario = obtener_perfil(request.user)
            quito = obtenerquito()

            if disponible:
                if tipo_dueno == "perfil":
                    # !!! Falta opcionalidad para cambiar ciudad
                    # !!! Todos los libros son marcados disponibles en Quito !!!
                    libro_disponible_obj = LibrosDisponibles(libro=nuevo_libro, perfil=perfil_usuario, ciudad=quito)
                    libro_disponible_obj.save()

                    # Crear notificacion compartio libro abierto
                    Notificacion.objects.compartio_libro_abierto(perfil_usuario, nuevo_libro)

                    if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():
                        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).select_related("grupo")
                        # crear objetos LibroDisponiblesGrupo
                        for u_grupo in usuarios_grupo_obj:
                            LibroDisponibleGrupo.objects.create(libro_disponible=libro_disponible_obj, grupo=u_grupo.grupo)
                            Notificacion.objects.compartio_libro_grupo(perfil_usuario, nuevo_libro, u_grupo.grupo)
                    
                    return HttpResponseRedirect(reverse('libros:mi_biblioteca'))
                
                elif tipo_dueno == "biblioteca_compartida":
                    slug = username  # fea manera de tomar el argumento y usarlo para biblioteca_compartida
                    biblioteca_compartida = BibliotecaCompartida.objects.get(slug=slug)
                    libro_disponible_obj = LibrosBibliotecaCompartida(biblioteca_compartida=biblioteca_compartida, libro=nuevo_libro)
                    libro_disponible_obj.save()

                    return HttpResponseRedirect(reverse('libros:biblioteca_compartida', kwargs={'slug_biblioteca_compartida': slug}))

            else:
                # Si no lo marco disponible, crear el objeto LibrosDisponibles pero con abierto_comunidad=False
                LibrosDisponibles.objects.create(libro=nuevo_libro, perfil=perfil_usuario, ciudad=quito, abierto_comunidad=False, disponible=False)

                return HttpResponseRedirect(reverse('libros:mi_biblioteca'))

    else:
        form = FormNuevoLibro()

    context = {'form': form, 'tipo_dueno': tipo_dueno, 'username': username}
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


def libros_ciudad(request, slug_ciudad, id_ciudad, filtro):
    """
    Recibe como parametro una ciudad, un id de la ciudad y un filtro. 
    renderea un html con los libros ordenados por el filtro
    """
    
    template = "libros/libros_ciudad.html"
    ciudad = City.objects.get(pk=id_ciudad)
    
    perfil_usuario = None
    if request.user.is_authenticated():
        perfil_usuario = obtener_perfil(request.user)

    if filtro == "autor":
        lista_libros_disponibles = LibrosDisponibles.objects.filter(ciudad=ciudad, disponible=True, prestado=False).order_by("libro__autor")
    else:
        lista_libros_disponibles = LibrosDisponibles.objects.filter(ciudad=ciudad, disponible=True, prestado=False)

    bibliotecas_compartidas = BibliotecaCompartida.objects.filter(ciudad=ciudad, eliminada=False)
    num_libros_disponibles = LibrosDisponibles.objects.filter(ciudad=ciudad, disponible=True, prestado=False).count()

    # Paginator
    paginator = Paginator(lista_libros_disponibles, 100)
    page = request.GET.get("page")
    try:
        libros_disponibles = paginator.page(page)
    except PageNotAnInteger:
        libros_disponibles = paginator.page(1)
    except EmptyPage:
        libros_disponibles = paginator.page(paginator.num_pages)

    # Grupos abiertos de la ciudad
    grupos_abiertos = None
    if Grupo.objects.filter(ciudad=ciudad, tipo__in=[1, 2]).exists():
        grupos_abiertos = Grupo.objects.filter(ciudad=ciudad, tipo__in=[1, 2])

    grupos_usuario = None
    if perfil_usuario:
        if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():
            grupos_usuario = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True)

    context = {
        'filtro': filtro,
        'ciudad': ciudad,
        'libros_disponibles': libros_disponibles,
        'num_libros_disponibles': num_libros_disponibles,
        'paginator': paginator,
        'bibliotecas_compartidas': bibliotecas_compartidas,
        'grupos_abiertos': grupos_abiertos,
        'grupos_usuario': grupos_usuario
        }

    return render(request, template, context)


def libro(request, slug):
    """
    Esta view no está en uso, muestra el libro.
    """
    template = "libros/libro.html"
    libro = Libro.objects.get(slug=slug)

    context = {'libro': libro}
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

        return HttpResponseRedirect(reverse('libros:libros_ciudad', kwargs={'slug_ciudad': ciudad.slug, 'id_ciudad': ciudad.id, 'filtro': 'titulo'}))

    ciudades = City.objects.all()
    nombres_ciudades_importantes = ["Quito", "Guayaquil", "Cuenca"]
    ciudades_importantes = []

    for nombre in nombres_ciudades_importantes:
        ciudad = City.objects.get(name=nombre)
        ciudades_importantes.append(ciudad)

    context = {'ciudades': ciudades, 'ciudades_importantes': ciudades_importantes}

    return render(request, template, context)


@login_required
def pedir_libro(request, id_libro_disponible):
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

            request_libro = LibrosRequest(libro=libro_request, perfil_envio=perfil_envio, perfil_recepcion=perfil_recepcion, 
                                          mensaje=mensaje, telefono=telefono, email=email)
            request_libro.save()

            if perfil_recepcion.usuario.email:    
                mail_pedir_libro(request_libro, mensaje)

            return HttpResponseRedirect(reverse('perfiles:perfil_propio'))
        else:
            print "form not valid!"
    
    libro_disponible_obj = LibrosDisponibles.objects.get(id=id_libro_disponible)
    
    form_pedir_libro = FormPedirLibro(initial={
        'libro_id': libro_disponible_obj.libro.id,
        'telefono': perfil_usuario.numero_telefono_contacto,
        'email': request.user.email
        })

    avatar = obtener_avatar_large(libro_disponible_obj.perfil)

    context = {'libro_disponible': libro_disponible_obj, 'form_pedir_libro': form_pedir_libro, 'avatar': avatar}

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
                                     perfil_dueno=libro_request.perfil_recepcion, fecha_prestamo=fecha_prestamo, mensaje_aceptacion=mensaje,
                                     fecha_max_devolucion=fecha_max_devolucion)
            libro_prestado.save()

            libro_disponible_obj = LibrosDisponibles.objects.filter(libro=libro_request.libro, perfil=libro_request.perfil_recepcion).first()
            libro_disponible_obj.disponible = False
            libro_disponible_obj.prestado = True

            libro_disponible_obj.save()

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

    ldisponibles_perfil_request = LibrosDisponibles.objects.filter(perfil=perfil_request, disponible=True, prestado=False).count()

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
    Muestra formulario para creacion de BibliotecaCompartida
    """

    template = "libros/nueva_biblioteca_compartida.html"

    ciudad = get_object_or_404(City, id=id_ciudad)

    if request.method == "POST":
        form = NuevaBibliotecaCompartida(request.POST)

        if form.is_valid():
            
            biblioteca_compartida = form.save(commit=False)
            biblioteca_compartida.perfil_admin = obtener_perfil(request.user)
            biblioteca_compartida.ciudad = ciudad
            biblioteca_compartida.save()

            return HttpResponseRedirect(reverse('libros:libros_ciudad', kwargs={'slug_ciudad': ciudad.slug, 'id_ciudad': ciudad.id, 'filtro': 'titulo'}))

    else:
        form = NuevaBibliotecaCompartida()

    context = {'ciudad': ciudad, 'form': form}

    return render(request, template, context)


def biblioteca_compartida(request, slug_biblioteca_compartida):
    """
    Esta view tampoco está en uso, muestra los libros disponibles en una biblioteca compartida
    """    
 
    template = "libros/biblioteca_compartida.html"

    biblioteca_compartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)
    usuario_es_administrador = False
    
    if request.user.is_authenticated():
        perfil = obtener_perfil(request.user)
        if biblioteca_compartida.perfil_admin == perfil:
            usuario_es_administrador = True

    libros_bcompartida = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=biblioteca_compartida, disponible=True, prestado=False)
    num_libros_bcompartida = libros_bcompartida.count()

    punto_gmaps = None
    if biblioteca_compartida.direccion_gmaps:
        latitude, longitude = biblioteca_compartida.direccion_gmaps
        punto_gmaps = [latitude, longitude]

    context = {'biblioteca_compartida': biblioteca_compartida, 'usuario_es_administrador': usuario_es_administrador,
               'libros_bcompartida': libros_bcompartida, 'num_libros_bcompartida': num_libros_bcompartida, 
               'punto_gmaps': punto_gmaps}

    return render(request, template, context)


@login_required
def editar_info_bcompartida(request, slug_biblioteca_compartida):
    """
    Esta view sirve para editar la info de la biblioteca compartida
    """

    template = "libros/editar_info_bcompartida.html"

    biblioteca_compartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)

    perfil_usuario = obtener_perfil(request.user)    

    if biblioteca_compartida.perfil_admin != perfil_usuario:
        raise PermissionDenied
    else:
        pass

    if request.method == "POST":
        form = EditarBibliotecaCompartida(request.POST, instance=biblioteca_compartida)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('libros:biblioteca_compartida', 
                kwargs={'slug_biblioteca_compartida': biblioteca_compartida.slug}))
        else:
            print form.errors
    else:
        form = EditarBibliotecaCompartida(initial={
                'nombre': biblioteca_compartida.nombre,
                'direccion': biblioteca_compartida.direccion,
                'imagen': biblioteca_compartida.imagen                
            })

    context = {'biblioteca_compartida': biblioteca_compartida, 'form': form}

    return render(request, template, context)


@login_required
def editar_libros_bcompartida(request, slug_biblioteca_compartida):
    """
    Esta view no está en uso, permite editar el estado de los libros de la biblioteca compartida
    """

    template = "libros/editar_libros_bcompartida.html"
    
    biblioteca_compartida = BibliotecaCompartida.objects.get(slug=slug_biblioteca_compartida)

    libros_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=biblioteca_compartida, disponible=True, prestado=False, eliminado=False)
    libros_no_disponibles = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=biblioteca_compartida, disponible=False, 
        prestado=False, eliminado=False)
    libros_prestados = LibrosPrestadosBibliotecaCompartida.objects.filter(biblioteca_compartida=biblioteca_compartida, fecha_devolucion=None)

    libros_requests = libros_no_retirados = False
    if LibrosRequestBibliotecaCompartida.objects.filter(libro_disponible__biblioteca_compartida=biblioteca_compartida, aceptado=False, eliminado=False).exists():
        libros_requests = LibrosRequestBibliotecaCompartida.objects.filter(libro_disponible__biblioteca_compartida=biblioteca_compartida, 
            aceptado=False, eliminado=False).select_related("libro_disponible")

    if LibrosRequestBibliotecaCompartida.objects.filter(libro_disponible__biblioteca_compartida=biblioteca_compartida, aceptado=True, 
            retirado=False, eliminado=False).exists():
        libros_no_retirados = LibrosRequestBibliotecaCompartida.objects.filter(libro_disponible__biblioteca_compartida=biblioteca_compartida, 
            aceptado=True, retirado=False).select_related("libro_disponible")

    context = {'biblioteca_compartida': biblioteca_compartida, 'libros_prestados': libros_prestados, 'libros_disponibles': libros_disponibles, 
            'libros_no_disponibles': libros_no_disponibles, 'libros_requests': libros_requests,
            'libros_no_retirados': libros_no_retirados}

    return render(request, template, context)


@login_required
def prestar_libro_bcompartida(request, id_libro_compartido):
    """
    View no está en uso. Permite al admin de la biblioteca compartida aceptar el request de prestar libro
    posiblemente cambie, depende de cómo decidamos implementar las bibliotecas compartidas en la página
    """

    template = "libros/prestar_libro_bcompartida.html"

    libro_disponible_obj = LibrosBibliotecaCompartida.objects.select_related('biblioteca_compartida').get(id=id_libro_compartido)

    if request.method == "POST":
        form = FormPrestarLibroBCompartida(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('usuario', '')            
            
            # crear LibrosPrestadosBibliotecaCompartida object
            perfil_usuario_prestamo = Perfil.objects.get(usuario__username=username)
            libro_prestado = LibrosPrestadosBibliotecaCompartida(libro=libro_disponible_obj.libro, perfil_prestamo=perfil_usuario_prestamo, 
                                                                 biblioteca_compartida=libro_disponible_obj.biblioteca_compartida)
            libro_prestado.save()

            # poner no disponible a LibrosBibliotecaCompartida object
            libro_disponible_obj.disponible = False
            libro_disponible_obj.prestado = True
            libro_disponible_obj.save()

            return HttpResponseRedirect(reverse('libros:editar_libros_bcompartida', 
                kwargs={'slug_biblioteca_compartida': libro_disponible_obj.biblioteca_compartida.slug}))

    else:
        form = FormPrestarLibroBCompartida()

    ciudad = libro_disponible_obj.biblioteca_compartida.ciudad
    perfiles_obj = Perfil.objects.filter(ciudad=ciudad).select_related("usuario")
    usernames_autocomplete = [perfil.usuario.username for perfil in perfiles_obj]

    context = {'form': form, 'libro_compartido': libro_disponible_obj, 'usernames_autocomplete': json.dumps(usernames_autocomplete)}

    return render(request, template, context)


@login_required
def cambiar_libro_bcompartida(request, id_biblioteca_compartida, id_libro_compartido=None):
    """
    View rederiza y procesa el form para cambiar libro por otro en una biblioteca compartida.
    """
    template = "libros/cambiar_libro_bcompartida.html"
    
    biblioteca_compartida = BibliotecaCompartida.objects.get(id=id_biblioteca_compartida)

    libro_disponible = None
    if id_libro_compartido:
        libro_disponible = LibrosBibliotecaCompartida.objects.get(id=id_libro_compartido)

    if request.method == "POST":
        form = FormCambiarLibroBCompartida(request.POST)
        if form.is_valid():        
            id_libro_cambiado = form.cleaned_data.get("id_libro_cambiado")
            titulo_nuevo_libro = form.cleaned_data.get("titulo_recibido")
            autor_nuevo_libro = form.cleaned_data.get("autor_recibido")

            libro_cambiado = LibrosBibliotecaCompartida.objects.get(id=id_libro_cambiado)
            libro_cambiado.disponible = False
            libro_cambiado.eliminado = True
            libro_cambiado.save()

            nuevo_libro = Libro.objects.create(titulo=titulo_nuevo_libro, autor=autor_nuevo_libro)
            LibrosBibliotecaCompartida.objects.create(libro=nuevo_libro, biblioteca_compartida=biblioteca_compartida)

            # enviar mail admin de la biblioteca compartida

            return redirect('libros:editar_libros_bcompartida', slug_biblioteca_compartida=biblioteca_compartida.slug)

    else:
        if id_libro_compartido:
            form = FormCambiarLibroBCompartida(initial={
                'titulo_inicial': libro_disponible.libro.titulo,
                'id_libro_cambiado': libro_disponible.id
            })
        else:
            form = FormCambiarLibroBCompartida()

    libros_bcompartida = LibrosBibliotecaCompartida.objects.filter(biblioteca_compartida=biblioteca_compartida, disponible=True).select_related("libro")
    titulos_autocomplete = {}
    for libro_bc in libros_bcompartida:
        titulos_autocomplete[libro_bc.libro.titulo] = libro_bc.id

    context = {'form': form, 'libro_disponible': libro_disponible, 'titulos_autocomplete': json.dumps(titulos_autocomplete), 
        'biblioteca_compartida': biblioteca_compartida}

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

            libro_no_disponible = LibrosDisponibles.objects.filter(libro=libro_prestado.libro, perfil=libro_prestado.perfil_dueno).first()
            libro_no_disponible.disponible = True
            libro_no_disponible.prestado = False
            libro_no_disponible.save()

        elif tipo == "biblioteca":            
            libro_prestado = get_object_or_404(LibrosPrestadosBibliotecaCompartida, id=id_libro_prestado)
            libro_prestado.fecha_devolucion = fecha_devolucion
            libro_prestado.save()

            libro_no_disponible = LibrosBibliotecaCompartida.objects.filter(libro=libro_prestado.libro, biblioteca_compartida=libro_prestado.biblioteca_compartida).first()
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


def buscar(request, slug_ciudad, filtro):
    """
    busca un libro disponible
    """
    template = 'libros/busqueda.html'
    
    query_string = ""
    libros_disponibles = None

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        if query_string:
            if filtro == "autor":
                libros_disponibles = LibrosDisponibles.objects.filter(libro__autor__icontains=query_string, disponible=True)
            else:
                libros_disponibles = LibrosDisponibles.objects.filter(libro__titulo__icontains=query_string, disponible=True)

        context = {'query_string': query_string,
                   'libros_disponibles': libros_disponibles,
                   'filtro': filtro,
                   'ciudad': slug_ciudad.capitalize()}
        return render(request, template, context)
    else:
        return redirect('libros:libros_ciudad', slug_ciudad='quito', id_ciudad=18, filtro='titulo')


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
                grupos_libro = LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible, activo=True).select_related('grupo')
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

        update = LibroDisponibleGrupo.objects.filter(grupo=grupo, libro_disponible=libro_disponible).update(activo=False)
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
            print "nuevo estado abierto_comunidad: %s" % (nuevo_estado)
            print "Crear notificaciones"

            # crear notificaciones
            Notificacion.objects.compartio_libro_abierto(perfil_usuario, libro_disponible.libro)

            if UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).exists():                
                usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil_usuario, activo=True).select_related("grupo")
                for u_grupo in usuarios_grupo_obj:
                    Notificacion.objects.compartio_libro_grupo(perfil_usuario, libro_disponible.libro, u_grupo.grupo)

        else:
            # si marco no abierto_comunidad, revisar si está compartido con otros grupos, si no marcar no_disponible
            print "nuevo estado abierto_comunidad: %s" % (nuevo_estado)
            print "Revisar si está compartido con grupos"
            if LibroDisponibleGrupo.objects.filter(libro_disponible=libro_disponible, activo=True).exists():
                print "Sí está compartido con otros grupos"
                pass
            else:
                print "No está compartido con otro grupo, marcar disponible False"
                libro_disponible.disponible = False
                libro_disponible.save()

        return HttpResponse(nuevo_estado, status=200)

    else:
        return HttpResponse(status=400)


def pedir_bcompartida_ajax(request):

    if request.is_ajax():

        if request.method == "POST":
            id_libro_disp = int(request.POST.get('id_libro_disp', ""))
            libro_disponible = LibrosBibliotecaCompartida.objects.select_related("biblioteca_compartida").get(id=id_libro_disp)
            perfil_usuario = obtener_perfil(request.user)
            request_libro = LibrosRequestBibliotecaCompartida.objects.create(libro_disponible=libro_disponible, perfil_envio=perfil_usuario)

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

        if LibrosRequestBibliotecaCompartida.objects.filter(libro_disponible=libro_disponible, perfil_envio=perfil_usuario, aceptado=False).exists():
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
    Recibe un id de un LibrosRequestBibliotecaCompartida y lo marca como aceptado, 
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

        libro_request = LibrosRequestBibliotecaCompartida.objects.filter(id=id_request).select_related("libro_disponible").first()
        libro_request.retirado = True
        libro_request.save()

        LibrosPrestadosBibliotecaCompartida.objects.create(libro=libro_request.libro_disponible.libro, perfil_prestamo=libro_request.perfil_envio,
            biblioteca_compartida=libro_request.libro_disponible.biblioteca_compartida)

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=400)
