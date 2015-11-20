# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0003_auto_20151023_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='grupo',
            field=models.ForeignKey(blank=True, to='grupos.Grupo', null=True),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='libro',
            field=models.ForeignKey(blank=True, to='libros.Libro', null=True),
        ),
    ]
