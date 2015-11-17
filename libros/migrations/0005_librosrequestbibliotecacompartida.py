# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0003_auto_20151014_0050'),
        ('libros', '0004_remove_librodisponiblegrupo_perfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibrosRequestBibliotecaCompartida',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha_request', models.DateTimeField(auto_now=True)),
                ('aceptado', models.BooleanField(default=False)),
                ('eliminado', models.BooleanField(default=False)),
                ('biblioteca_compartida', models.ForeignKey(to='libros.BibliotecaCompartida')),
                ('libro_disponible', models.ForeignKey(to='libros.LibrosBibliotecaCompartida')),
                ('perfil_envio', models.ForeignKey(to='perfiles.Perfil')),
            ],
        ),
    ]
