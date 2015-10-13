# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0004_requestinvitacion_eliminado'),
        ('perfiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=1000)),
                ('eliminado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('grupo', models.ForeignKey(to='grupos.Grupo')),
                ('perfil', models.ForeignKey(to='perfiles.Perfil')),
            ],
        ),
    ]
