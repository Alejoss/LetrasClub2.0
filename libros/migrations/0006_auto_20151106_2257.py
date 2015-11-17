# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0005_librosrequestbibliotecacompartida'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='librosrequestbibliotecacompartida',
            options={'ordering': ['fecha_request']},
        ),
        migrations.RemoveField(
            model_name='librosrequestbibliotecacompartida',
            name='biblioteca_compartida',
        ),
    ]
