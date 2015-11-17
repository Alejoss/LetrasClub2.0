# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0010_bibliotecacompartida_direccion_web'),
    ]

    operations = [
        migrations.AddField(
            model_name='librosbibliotecacompartida',
            name='eliminado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='librosdisponibles',
            name='eliminado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='librosleidos',
            name='eliminado',
            field=models.BooleanField(default=False),
        ),
    ]
