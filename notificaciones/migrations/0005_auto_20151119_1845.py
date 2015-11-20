# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0012_librosrequest_grupo'),
        ('notificaciones', '0004_auto_20151119_0145'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='biblioteca_compartida',
            field=models.ForeignKey(blank=True, to='libros.BibliotecaCompartida', null=True),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='perfil_target',
            field=models.ForeignKey(related_name='target', blank=True, to='perfiles.Perfil', null=True),
        ),
    ]
