# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0008_auto_20151107_0443'),
    ]

    operations = [
        migrations.AddField(
            model_name='librosprestadosbibliotecacompartida',
            name='receptor_anuncio_devolucion',
            field=models.BooleanField(default=False),
        ),
    ]
