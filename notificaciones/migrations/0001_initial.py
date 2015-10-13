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
            name='Notificacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.CharField(max_length=50)),
                ('leida', models.BooleanField(default=False)),
                ('grupo', models.ForeignKey(to='grupos.Grupo', null=True)),
                ('perfil_actor', models.ForeignKey(related_name='actor', to='perfiles.Perfil')),
                ('perfil_target', models.ForeignKey(related_name='target', to='perfiles.Perfil', null=True)),
            ],
        ),
    ]
