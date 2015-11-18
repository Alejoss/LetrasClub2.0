# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0003_auto_20151014_0050'),
        ('comentarios', '0006_auto_20151027_2136'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPerfil',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=1000)),
                ('eliminado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('muro', models.ForeignKey(related_name='muro', to='perfiles.Perfil')),
                ('perfil', models.ForeignKey(related_name='comentarista', to='perfiles.Perfil')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='RespuestaCommentPerfil',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=1000)),
                ('eliminado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('comment_perfil', models.ForeignKey(related_name='respuestas', to='comentarios.CommentPerfil')),
                ('perfil', models.ForeignKey(to='perfiles.Perfil')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
    ]