# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0007_librosrequestbibliotecacompartida_retirado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librosprestadosbibliotecacompartida',
            name='fecha_prestamo',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
