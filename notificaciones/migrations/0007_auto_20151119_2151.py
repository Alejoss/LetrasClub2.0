# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0012_librosrequest_grupo'),
        ('notificaciones', '0006_auto_20151119_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='segundo_libro',
            field=models.ForeignKey(related_name='segundo_libro', blank=True, to='libros.Libro', null=True),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='libro',
            field=models.ForeignKey(related_name='libro', blank=True, to='libros.Libro', null=True),
        ),
    ]
