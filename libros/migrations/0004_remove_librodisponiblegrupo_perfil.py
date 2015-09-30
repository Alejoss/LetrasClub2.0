# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0003_auto_20150923_2033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='librodisponiblegrupo',
            name='perfil',
        ),
    ]
