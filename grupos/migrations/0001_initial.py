# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(unique=True, max_length=255)),
                ('descripcion', models.CharField(max_length=2500, blank=True)),
                ('imagen', models.URLField(blank=True)),
                ('tipo', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='RequestInvitacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aceptado', models.BooleanField(default=False)),
                ('fecha_invitacion', models.DateTimeField(auto_now_add=True)),
                ('eliminado', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UsuariosGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('es_admin', models.BooleanField(default=False)),
                ('activo', models.BooleanField(default=True)),
                ('grupo', models.ForeignKey(to='grupos.Grupo')),
            ],
        ),
    ]
