from perfiles.models import Perfil
from libros.models import LibrosRequest
from grupos.models import RequestInvitacion, UsuariosGrupo


def procesar_perfil(request):
	context = {}
	if request.user.is_authenticated():
		perfil, created = Perfil.objects.get_or_create(usuario=request.user)		
		context['perfil_usuario'] = perfil

	return context


def procesar_ciudad(request):
	context = {}
	if request.user.is_authenticated():
		perfil, created = Perfil.objects.get_or_create(usuario=request.user)
		if created:
			context['tiene_ciudad'] = False
		else:
			if perfil.ciudad is None:
				context['tiene_ciudad'] = False
			else:
				context['tiene_ciudad'] = True
				context['perfil_ciudad'] = perfil.ciudad

	return context


def notificaciones(request):
	"""
	Devuelve un diccionario con las notificaciones. Notificacion: tipo, notificacion
	"""
	notificaciones = None
	if request.user.is_authenticated():

		perfil_usuario = Perfil.objects.get(usuario=request.user)

		# Notificacion si tiene pedidos de libros
		requests_libros = 0
		if LibrosRequest.objects.filter(perfil_recepcion=perfil_usuario, aceptado=False, eliminado=False).exists():
			requests_libros = LibrosRequest.objects.filter(perfil_recepcion=perfil_usuario, aceptado=False, eliminado=False).count()

		# Revisar si el usuario es admin de algun grupo, notificacion para los admins si existen requests no aceptados
		requests_inv_grupos = 0
		if UsuariosGrupo.objects.filter(usuario=perfil_usuario, es_admin=True).exists():
			usuarios_grupo_obj = UsuariosGrupo.objects.filter(usuario=perfil_usuario, es_admin=True).select_related('grupo')
			grupos = [x.grupo for x in usuarios_grupo_obj]
			if RequestInvitacion.objects.filter(aceptado=False, grupo__in=grupos).exists():
				requests_inv_grupos = RequestInvitacion.objects.filter(aceptado=False, grupo__in=grupos).count()				

		notificaciones = requests_libros + requests_inv_grupos

	return {'notificaciones': notificaciones}
