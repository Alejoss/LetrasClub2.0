# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0001_initial'),
        ('libros', '0001_initial'),
        ('notificaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='perfil_actor',
            field=models.ForeignKey(related_name='actor', blank=True, to='perfiles.Perfil', null=True),
        ),
        migrations.AddField(
            model_name='notificacion',
            name='perfil_target',
            field=models.ForeignKey(related_name='target', blank=True, to='perfiles.Perfil', null=True),
        ),
        migrations.AddField(
            model_name='notificacion',
            name='segundo_libro',
            field=models.ForeignKey(related_name='segundo_libro', blank=True, to='libros.Libro', null=True),
        ),
    ]
