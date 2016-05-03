# -*- coding: utf-8 -*-
import json
from datetime import datetime
from itertools import chain

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.views.generic import TemplateView

from libros.models import LibrosRequest, LibrosPrestados, LibrosPrestadosBibliotecaCompartida, LibrosDisponibles, Libro, \
    BibliotecaCompartida, LibrosRequestBibliotecaCompartida, AdminsBibliotecaCompartida
from perfiles.models import Perfil, UsuarioLeyendo
from grupos.models import UsuariosGrupo, RequestInvitacion
from notificaciones.models import Notificacion
from comentarios.models import CommentPerfil

from forms import FormRegistro, FormEditarPerfil, ContactForm, LoginAdminBcompartida, FormEditarInfoPersonal
from letrasclub.utils import obtener_perfil, obtener_historial_libros, obtener_avatar_large, obtenerquito, \
    obtener_libros_perfil, obtener_usuario_leyendo, \
    notif_grupos_comenzo_leer, notif_grupos_termino_leer, enviar_mail_contactanos, obtener_muro_perfil


def registro(request):
    """
	View no está en uso, registro de nuevo usuario
	"""

    template = "perfiles/registro.html"

    if request.method == "POST":
        form = FormRegistro(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Usuario Guardado", status=201)

    else:
        form = FormRegistro()

    context = {
        'form': form
    }

    return render(request, template, context)


@login_required
def perfil_propio(request):
    """
	Muestra el perfil del usuario que está hecho login enfocado en la actividad
	"""
    template = "perfiles/perfil_propio.html"
    perfil = obtener_perfil(request.user)
    avatar = obtener_avatar_large(perfil)

    # Grupos Perfil
    grupos = None
    if UsuariosGrupo.objects.filter(perfil=perfil, activo=True).exists():
        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil, activo=True).select_related('grupo')
        grupos = [ug.grupo for ug in usuarios_grupo_obj]

    # Usuario Leyendo
    actualmente_leyendo, libros_leidos_usuario = obtener_usuario_leyendo(perfil)

    libros_disponibles = LibrosDisponibles.objects.filter(perfil=perfil).select_related('libro')

    # autocomplete Usuario Leyendo
    titulos_autocomplete = {}
    autores_autocomplete = {}
    for l in libros_disponibles:
        titulos_autocomplete[l.libro.titulo] = (l.libro.id, l.libro.autor)

    # Muro, comentarios y actividades
    actividad = []
    actividad_0 = obtener_muro_perfil(perfil)
    for act in actividad_0:
        if act.__class__.__name__ == "CommentPerfil":
            actividad.append((act, "comment"))
        else:
            actividad.append((act, "notificacion"))

    for l in libros_disponibles:
        autores_autocomplete[l.libro.autor] = l.libro.id

    # Si es admin de una biblioteca, poner link a la biblioteca
    bibliotecas_compartidas = None

    context = {'avatar': avatar, 'grupos': grupos, 'actualmente_leyendo': actualmente_leyendo,
               'libros_leidos_usuario': libros_leidos_usuario, 'titulos_autocomplete': json.dumps(titulos_autocomplete),
               'autores_autocomplete': json.dumps(autores_autocomplete), 'actividad': actividad,
               'bibliotecas_compartidas': bibliotecas_compartidas}

    return render(request, template, context)


@login_required
def perfil_propio_libros(request):
    """
	Muestra el perfil del usuario loggeado. enfocado en los libros y notificaciones
	"""
    template = "perfiles/perfil_propio_libros.html"
    perfil = obtener_perfil(request.user)
    avatar = obtener_avatar_large(perfil)

    # Libros Perfil
    libros_perfil = {
        'tiene_requests_pendientes': False,
        'tiene_libros_prestados': False,
        'tiene_libros_pedidos': False,
        'tiene_libros_pedidos_bcompartida': False
    }

    libros_requests = libros_prestados = libros_prestados_bcompartida = libros_pedidos = libros_pedidos_bcompartida = []

    if LibrosRequest.objects.filter(perfil_envio=perfil, aceptado=False, eliminado=False).exists():
        libros_perfil['tiene_libros_pedidos'] = True
        libros_pedidos = LibrosRequest.objects.filter(perfil_envio=perfil, aceptado=False, eliminado=False)

    if LibrosRequestBibliotecaCompartida.objects.filter(perfil_envio=perfil, retirado=False, eliminado=False).exists():
        libros_perfil['tiene_libros_pedidos_bcompartida'] = True
        libros_pedidos_bcompartida = LibrosRequestBibliotecaCompartida.objects.filter(perfil_envio=perfil,
                                                                                      retirado=False,
                                                                                      eliminado=False).select_related(
            "libro_disponible")

    if LibrosRequest.objects.filter(perfil_recepcion=perfil, aceptado=False, eliminado=False).exists():
        libros_perfil['tiene_requests_pendientes'] = True
        libros_requests = LibrosRequest.objects.filter(perfil_recepcion=perfil, aceptado=False, eliminado=False)

    if LibrosPrestados.objects.filter(perfil_receptor=perfil, fecha_devolucion=None).exists():
        libros_perfil['tiene_libros_prestados'] = True
        libros_prestados = LibrosPrestados.objects.filter(perfil_receptor=perfil, fecha_devolucion=None)

    if LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil, fecha_devolucion=None).exists():
        libros_perfil['tiene_libros_prestados'] = True
        libros_prestados_bcompartida = LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil,
                                                                                          fecha_devolucion=None)

    # Grupos Perfil
    grupos = None
    if UsuariosGrupo.objects.filter(perfil=perfil, activo=True).exists():
        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil, activo=True).select_related('grupo')
        grupos = [ug.grupo for ug in usuarios_grupo_obj]

    # Usuario Leyendo
    actualmente_leyendo, libros_leidos_usuario = obtener_usuario_leyendo(perfil)
    libros_disponibles = LibrosDisponibles.objects.filter(perfil=perfil).select_related('libro')

    # autocomplete Usuario Leyendo
    titulos_autocomplete = {}
    autores_autocomplete = {}
    for l in libros_disponibles:
        titulos_autocomplete[l.libro.titulo] = (l.libro.id, l.libro.autor)

    for l in libros_disponibles:
        autores_autocomplete[l.libro.autor] = l.libro.id

    # Request de entrar a grupos a los que el usuario es admin
    requests_entrar_grupo = None
    if UsuariosGrupo.objects.filter(perfil=perfil, es_admin=True).exists():
        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil, es_admin=True).select_related('grupo')
        grupos = [x.grupo for x in usuarios_grupo_obj]

        requests_entrar_grupo = RequestInvitacion.objects.filter(aceptado=False, grupo__in=grupos)

    # Si es admin de una biblioteca, poner link a la biblioteca
    bibliotecas_compartidas = None

    context = {'libros_perfil': libros_perfil, 'libros_requests': libros_requests, 'libros_prestados': libros_prestados,
               'libros_pedidos': libros_pedidos, 'libros_prestados_bcompartida': libros_prestados_bcompartida,
               'libros_pedidos_bcompartida': libros_pedidos_bcompartida, 'libros_disponibles': libros_disponibles,
               'avatar': avatar, 'grupos': grupos, 'actualmente_leyendo': actualmente_leyendo,
               'libros_leidos_usuario': libros_leidos_usuario, 'requests_entrar_grupo': requests_entrar_grupo,
               'titulos_autocomplete': json.dumps(titulos_autocomplete),
               'autores_autocomplete': json.dumps(autores_autocomplete),
               'bibliotecas_compartidas': bibliotecas_compartidas}

    return render(request, template, context)


def perfil_usuario(request, username):
    """
	Muestra el perfil de un usuario tercero, enfocado en las actividades
	"""
    template = "perfiles/perfil_usuario.html"
    perfil = Perfil.objects.get(usuario__username=username)

    # redirigir a la pagina perfil_propio si es el caso
    user_obj = User.objects.get(username=username)
    if user_obj == request.user:
        return HttpResponseRedirect(reverse('perfiles:perfil_propio'))

    # Muro, comentarios y actividades
    actividad = []
    actividad_0 = obtener_muro_perfil(perfil)
    for act in actividad_0:
        if act.__class__.__name__ == "CommentPerfil":
            actividad.append((act, "comment"))
        else:
            actividad.append((act, "notificacion"))

    # Grupos Perfil
    grupos = None
    if UsuariosGrupo.objects.filter(perfil=perfil, activo=True).exists():
        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil, activo=True).select_related('grupo')
        grupos = [ug.grupo for ug in usuarios_grupo_obj]

    historial_libros = obtener_historial_libros(perfil)

    avatar = obtener_avatar_large(perfil)

    # Si es admin de una biblioteca, poner link a la biblioteca
    bibliotecas_compartidas = None

    context = {'historial_libros': historial_libros, 'perfil': perfil, 'avatar': avatar, 'actividad': actividad,
               'grupos': grupos, 'bibliotecas_compartidas': bibliotecas_compartidas}

    return render(request, template, context)


def perfil_usuario_libros(request, username):
    """
	Muestra el perfil de un usuario tercero, enfocado en los libros disponibles
	"""
    template = "perfiles/perfil_usuario_libros.html"

    libros_perfil = {'tiene_libros_prestados': False, 'tiene_libros_disponibles': False}

    # redirigir a la pagina perfil_propio si es el caso
    user_obj = User.objects.get(username=username)
    if user_obj == request.user:
        return HttpResponseRedirect(reverse('perfiles:perfil_propio'))

    perfil = Perfil.objects.get(usuario__username=username)
    historial_libros = obtener_historial_libros(perfil)
    libros_prestados = libros_prestados_bcompartida = libros_disponibles = []

    if LibrosPrestados.objects.filter(perfil_receptor=perfil, fecha_devolucion=None).exists():
        libros_perfil['tiene_libros_prestados'] = True
        libros_prestados = LibrosPrestados.objects.filter(perfil_receptor=perfil, fecha_devolucion=None)

    if LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil, fecha_devolucion=None).exists():
        libros_perfil['tiene_libros_prestados'] = True
        libros_prestados_bcompartida = LibrosPrestadosBibliotecaCompartida.objects.filter(perfil_prestamo=perfil,
                                                                                          fecha_devolucion=None)

    if LibrosDisponibles.objects.filter(perfil=perfil, disponible=True, prestado=False).exists():
        libros_perfil['tiene_libros_disponibles'] = True
        libros_disponibles = LibrosDisponibles.objects.filter(perfil=perfil, disponible=True, prestado=False)

    # Grupos Perfil
    grupos = None
    if UsuariosGrupo.objects.filter(perfil=perfil, activo=True).exists():
        usuarios_grupo_obj = UsuariosGrupo.objects.filter(perfil=perfil, activo=True).select_related('grupo')
        grupos = [ug.grupo for ug in usuarios_grupo_obj]

    avatar = obtener_avatar_large(perfil)

    # Si es admin de una biblioteca, poner link a la biblioteca
    bibliotecas_compartidas = None

    context = {'libros_prestados': libros_prestados, 'libros_prestados_bcompartida': libros_prestados_bcompartida,
               'libros_disponibles': libros_disponibles,
               'historial_libros': historial_libros, 'libros_perfil': libros_perfil, 'perfil': perfil, 'avatar': avatar,
               'grupos': grupos,
               'bibliotecas_compartidas': bibliotecas_compartidas}

    return render(request, template, context)


def login_admin_bcompartida(request):
    template = "perfiles/login_admin_bcompartida.html"

    if request.method == "POST":
        form = LoginAdminBcompartida(request.POST)
        # Bibliotecas compartidas obtenidas de Quito
        bibliotecas_compartidas = BibliotecaCompartida.objects.filter(ciudad__id=18)
        form.fields["biblioteca_compartida"].queryset = bibliotecas_compartidas

        if form.is_valid():
            nombre_bcompartida = form.cleaned_data['biblioteca_compartida']
            password = form.cleaned_data['password']
            n_usuario = form.cleaned_data['nombre_usuario']

            bcompartida = BibliotecaCompartida.objects.get(nombre=nombre_bcompartida, eliminada=False)

            if User.objects.filter(username=n_usuario).exists():
                usuario = User.objects.get(username=n_usuario)

                perfil_admin = obtener_perfil(usuario)

                if AdminsBibliotecaCompartida.objects.filter(biblioteca_compartida=bcompartida,
                                                             perfil=perfil_admin).exists():
                    usuario_auth = authenticate(username=perfil_admin.usuario.username, password=password)

                    if usuario_auth is not None:
                        if usuario.is_active:
                            login(request, usuario_auth)
                            # Redirige al admin logeado a la pagina de su biblioteca compartida
                            return redirect('libros:biblioteca_compartida',
                                            slug_biblioteca_compartida=bcompartida.slug)
                        else:
                            form.add_error(None, "Usuario inactivo")
                    else:
                        form.add_error(None, "Nombre de usuario o contraseña incorrecta")
                else:
                    form.add_error(None, "No existe un administrador de esa biblioteca compartida con ese nombre")
            else:
                form.add_error("nombre_usuario", "Nombre de usuario incorrecto")
    else:
        form = LoginAdminBcompartida()

    # Bibliotecas compartidas obtenidas de Quito
    bibliotecas_compartidas = BibliotecaCompartida.objects.filter(ciudad__id=18)
    form.fields["biblioteca_compartida"].queryset = bibliotecas_compartidas

    context = {'form': form}

    return render(request, template, context)


@login_required
def redirigir_login(request):
    perfil = obtener_perfil(request.user)
    if AdminsBibliotecaCompartida.objects.filter(perfil=perfil).exists():
        admin_bcompartida_obj = AdminsBibliotecaCompartida.objects.filter(
            perfil=perfil).select_related('biblioteca_compartida').first()
        bcompartida = admin_bcompartida_obj.biblioteca_compartida
        return redirect('libros:biblioteca_compartida', slug_biblioteca_compartida=bcompartida.slug)
    else:
        return redirect('libros:libros_ciudad', slug_ciudad=perfil.ciudad.slug, id_ciudad=perfil.ciudad.id)


@login_required
def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse('libros:main'))


@login_required
def editar_perfil(request):
    """
	Procesa el view y el form para que el usuario edite su perfil
	"""
    template = "perfiles/editar_perfil.html"
    perfil = obtener_perfil(request.user)
    avatar = obtener_avatar_large(perfil)

    if request.method == "POST":
        form = FormEditarPerfil(request.POST, instance=perfil)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('perfiles:perfil_propio'))

    else:
        if perfil.ciudad:
            ciudad_default = perfil.ciudad
        else:
            ciudad_default = obtenerquito()
        form = FormEditarPerfil(
            initial={
                'descripcion': perfil.descripcion,
                'ciudad': ciudad_default,
                'numero_telefono_contacto': perfil.numero_telefono_contacto
            })

    context = {'form': form, 'avatar': avatar}

    return render(request, template, context)


@login_required
def editar_info_personal(request):
    """
    Permite editar info que esta en User object, incluido cambiar clave
    """
    template = "perfiles/editar_info_personal.html"
    usuario_editar = request.user

    print "metodo actual: %s" % request.method

    if request.method == "POST":

        form = FormEditarInfoPersonal(usuario_editar, request.POST)

        if form.is_valid():
            form.save()  # Cambia la contraseña

            email = form.cleaned_data['email']

            usuario_editar.email = email
            usuario_editar.save()

            print request.user

            # render html con mensaje temporal
            perfil = obtener_perfil(usuario_editar)
            admin_bcompartida = AdminsBibliotecaCompartida.objects.filter(perfil=perfil, activo=True).select_related(
                'biblioteca_compartida').first()
            razon_mensaje = 'cambio_contrasena'
            template = "perfiles/mensaje_temporal.html"
            url_redirigir = reverse('libros:biblioteca_compartida',
                                    kwargs={'slug_biblioteca_compartida': admin_bcompartida.biblioteca_compartida.slug})

            context = {'razon_mensaje': razon_mensaje, 'admin_bcompartida': admin_bcompartida,
                       'url_redirigir': url_redirigir}

            return render(request, template, context)

    else:
        form = FormEditarInfoPersonal(usuario_editar, initial={'email': usuario_editar.email})

    context = {'form': form}

    return render(request, template, context)


@login_required
def libros_usuario_ajax(request):
    """
	Crea un UsuarioLeyendo object y señala la fecha actual como inicio
	"""
    if request.is_ajax():
        perfil = obtener_perfil(request.user)
        titulos_autocomplete, autores_autocomplete = obtener_libros_perfil(perfil)
        context = {'titulos_autocomplete': json.dumps(titulos_autocomplete),
                   'autores_autocomplete': json.dumps(autores_autocomplete)}
        return HttpResponse(context, status=200)
    else:
        return HttpResponse(status=400)


def leyendo_libro_ajax(request):
    """
	Recibe un libro id o un titulo y un autor. En el primer caso, crea un objeto UsuarioLeyendo, en el segundo,
	crea un objeto Libro y luego un objeto UsuarioLeyendo
	"""
    if request.is_ajax():
        libro_id = request.POST.get("libro_id", "")
        titulo = request.POST.get("titulo", "")
        autor = request.POST.get("autor", "")
        perfil = obtener_perfil(request.user)

        if not libro_id and (not titulo or not autor):
            # Si envio valores vacíos
            return HttpResponse(status=400)

        if libro_id:
            # Significa que el libro está en su biblioteca
            libro = Libro.objects.get(id=int(libro_id))

            # Revisar si el último UsuarioLeyendo object no es el mismo que declaro estar leyendo, para evitar repeticiones
            ultimo_libro = UsuarioLeyendo.objects.filter(perfil=perfil).latest('inicio')
            if ultimo_libro.libro.titulo == titulo:
                return HttpResponse("es el mismo libro que ya está leyendo", status=400)

            # Revisar si no borro el nombre y puso otro que no está en su biblioteca (nuevo)
            # El autocomplete pudiera haber llenado el id del hidden input y luego se pudo haber quedado así,
            # a pesar de que el usuario borro el nombre del autocomplete e insertó otro título.
            if libro.titulo == titulo and libro.autor == autor:
                UsuarioLeyendo.objects.create(perfil=perfil, libro=libro)

            else:
                if not titulo or not autor:
                    # Si envio valores vacíos
                    return HttpResponse(status=400)
                # crear nuevo libro
                libro = Libro.objects.create(titulo=titulo, autor=autor)

                # crear objeto UsuarioLeyendo
                UsuarioLeyendo.objects.create(libro=libro, perfil=perfil)

            # crear notificaciones para cada grupo
            Notificacion.objects.comenzo_leer(perfil, libro)
            notif_grupos_comenzo_leer(perfil, libro)

        else:
            # Significa que el libro no está en su biblioteca
            # Revisar si el último UsuarioLeyendo object no es el mismo que declaro estar leyendo, para evitar repeticiones
            ultimo_libro = UsuarioLeyendo.objects.filter(perfil=perfil).latest('inicio')
            if ultimo_libro.libro.titulo == titulo:
                return HttpResponse("es el mismo libro que ya está leyendo", status=400)

            # Revisar si no existe ya un libro con ese titulo, para evitar repeticiones
            if Libro.objects.filter(titulo=titulo, autor=autor).exists():
                # Puede darse errores en que get returns more than 1 object. asi que mejor usar last()
                libro = Libro.objects.filter(titulo=titulo, autor=autor).last()
            else:
                # crear nuevo libro
                libro = Libro.objects.create(titulo=titulo, autor=autor)

            # crear objeto LibroDisponible, suma libro a su biblioteca, solo si no existe ya en la biblioteca
            if not LibrosDisponibles.objects.filter(libro=libro, perfil=perfil).exists():
                LibrosDisponibles.objects.create(libro=libro, perfil=perfil, disponible=False, ciudad=perfil.ciudad)

            # crear objeto UsuarioLeyendo
            UsuarioLeyendo.objects.create(libro=libro, perfil=perfil)

            # crear notificaciones para cada grupo
            Notificacion.objects.comenzo_leer(perfil, libro)
            notif_grupos_comenzo_leer(perfil, libro)

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=400)


def termino_leer_ajax(request):
    if request.is_ajax():

        libro_leido_id = request.POST.get('libro_leido_id', '')

        if not libro_leido_id:
            return HttpResponse("No recibio libro id", status=400)

        libro_leyendo = UsuarioLeyendo.objects.get(id=libro_leido_id)

        if libro_leyendo.termino is None:
            libro_leyendo.termino = datetime.today()
            libro_leyendo.save()

            perfil = obtener_perfil(request.user)

            # notificacion termino leer libro
            Notificacion.objects.termino_leer(perfil, libro_leyendo.libro)

            # notificaciones para cada grupo
            notif_grupos_termino_leer(perfil, libro_leyendo.libro)

            return HttpResponse(status=201)

        else:
            return HttpResponse("Ya había terminado ese libro", status=200)
    else:
        return HttpResponse(status=400)


@login_required
def editar_libro_leido(request):
    if request.method == "POST":

        autor = request.POST.get("autor", "")
        titulo = request.POST.get("titulo", "")
        libro_leido_id = request.POST.get("libro_leido_id", "")
        termino = request.POST.get("termino", "")

        if libro_leido_id:

            usuario_leyendo_obj = UsuarioLeyendo.objects.get(id=int(libro_leido_id))
            libro_leido = usuario_leyendo_obj.libro

            cambio_valores = False

            # Valores del objeto Libro
            if len(autor) and libro_leido.autor != autor:
                libro_leido.autor = autor
                cambio_valores = True
            if len(titulo) and libro_leido.titulo != titulo:
                libro_leido.titulo = titulo
                cambio_valores = True
            if cambio_valores:
                libro_leido.save()

            # Valores del objeto UsuarioLeyendo
            if termino and not usuario_leyendo_obj.termino:
                usuario_leyendo_obj.termino = datetime.today()
                usuario_leyendo_obj.save()

            if not termino and usuario_leyendo_obj.termino:
                usuario_leyendo_obj.termino = None
                usuario_leyendo_obj.save()

            return redirect('perfiles:perfil_propio')

        else:
            return HttpResponse(status=400)  # Bad Request

    else:
        return HttpResponse(status=400)


def eliminar_libro_leido_ajax(request):
    if request.is_ajax():

        if request.method == "POST":

            usuario_leyendo_id = request.POST("usuario_leyendo_id", "")

            if usuario_leyendo_id:
                obj = UsuarioLeyendo.objects.get(id=int(usuario_leyendo_id))
                obj.eliminado = True
                obj.save()

                return HttpResponse("objeto marcado como eliminado", status=200)

            else:
                return HttpResponse(status=400)

        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)


def contactanos(request, razon_contacto):
    template = "contactanos.html",

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():
            tema = form.cleaned_data['tema']
            mensaje = form.cleaned_data['mensaje']
            correo = form.cleaned_data['correo']
            nombre = form.cleaned_data['nombre']

            enviar_mail_contactanos(nombre, correo, tema, mensaje)

            return redirect('perfiles:despues_contacto', razon_contacto=razon_contacto, correo_contacto=correo)

    else:

        if razon_contacto == "registrar_biblioteca":

            form = ContactForm(initial={'tema': "Registrar nueva Biblioteca Compartida"})
            form.fields['mensaje'].placeholder = "Hola, deseo registrar una Biblioteca Compartida ..."

        elif razon_contacto == "donacion":

            form = ContactForm(initial={'tema': "Hacer una donación de libros"})
            form.fields[
                'mensaje'].placeholder = "Hola, deseo donar mis libros, quiero que alguien más pueda leerlos ..."

        else:
            form = ContactForm()

    context = {'form': form, 'razon_contacto': razon_contacto}
    return render(request, template, context)


class DespuesContacto(TemplateView):
    template_name = "despues_contacto.html"

    def get_context_data(self, **kwargs):
        context = super(DespuesContacto, self).get_context_data(**kwargs)
        context['razon_contacto'] = kwargs['razon_contacto']
        context['correo_contacto'] = kwargs['correo_contacto']

        return context


class SobreNosotros(TemplateView):
    template_name = "perfiles/sobre_nosotros.html"
