from django.contrib import admin
from grupos.models import Grupo, UsuariosGrupo, RequestInvitacion

admin.site.register(Grupo)
admin.site.register(UsuariosGrupo)
admin.site.register(RequestInvitacion)
