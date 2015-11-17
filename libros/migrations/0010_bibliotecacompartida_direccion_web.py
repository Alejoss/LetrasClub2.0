# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0009_librosprestadosbibliotecacompartida_receptor_anuncio_devolucion'),
    ]

    operations = [
        migrations.AddField(
            model_name='bibliotecacompartida',
            name='direccion_web',
            field=models.URLField(blank=True),
        ),
    ]
