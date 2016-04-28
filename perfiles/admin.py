from django.contrib import admin
from social.apps.django_app.default.models import UserSocialAuth

from perfiles.models import Perfil

admin.site.register(Perfil)
admin.site.register(UserSocialAuth)
