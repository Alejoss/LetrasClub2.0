# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0004_requestinvitacion_eliminado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuariosgrupo',
            old_name='usuario',
            new_name='perfil',
        ),
    ]
