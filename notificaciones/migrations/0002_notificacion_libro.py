# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0004_remove_librodisponiblegrupo_perfil'),
        ('notificaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='libro',
            field=models.ForeignKey(to='libros.Libro', null=True),
        ),
    ]
