# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0006_auto_20160329_1542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bibliotecacompartida',
            name='perfil_admin',
        ),
    ]
