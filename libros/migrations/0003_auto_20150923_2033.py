# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0004_requestinvitacion_eliminado'),
        ('perfiles', '0001_initial'),
        ('libros', '0002_auto_20150902_0056'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibroDisponibleGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activo', models.BooleanField(default=True)),
                ('grupo', models.ForeignKey(to='grupos.Grupo')),
            ],
        ),
        migrations.AddField(
            model_name='librosdisponibles',
            name='abierto_comunidad',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='librodisponiblegrupo',
            name='libro_disponible',
            field=models.ForeignKey(to='libros.LibrosDisponibles'),
        ),
        migrations.AddField(
            model_name='librodisponiblegrupo',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
    ]
