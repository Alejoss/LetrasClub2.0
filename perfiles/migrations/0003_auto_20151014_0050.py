# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0002_usuarioleyendo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuarioleyendo',
            old_name='usuario',
            new_name='perfil',
        ),
    ]
