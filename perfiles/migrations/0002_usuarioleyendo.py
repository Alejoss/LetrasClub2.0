# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0004_remove_librodisponiblegrupo_perfil'),
        ('perfiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsuarioLeyendo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inicio', models.DateTimeField(auto_now_add=True)),
                ('termino', models.DateTimeField(null=True)),
                ('eliminado', models.BooleanField(default=False)),
                ('libro', models.ForeignKey(to='libros.Libro')),
                ('usuario', models.ForeignKey(to='perfiles.Perfil')),
            ],
        ),
    ]
