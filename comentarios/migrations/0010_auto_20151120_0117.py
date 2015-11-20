# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0003_auto_20151014_0050'),
        ('comentarios', '0009_respuestacommentpcompartida'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespuestaCommentBCompartida',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=1000)),
                ('eliminado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('comment_bcompartida', models.ForeignKey(related_name='respuestas', to='comentarios.CommentBCompartida')),
                ('perfil', models.ForeignKey(to='perfiles.Perfil')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
        migrations.RemoveField(
            model_name='respuestacommentpcompartida',
            name='comment_bcompartida',
        ),
        migrations.RemoveField(
            model_name='respuestacommentpcompartida',
            name='perfil',
        ),
        migrations.DeleteModel(
            name='RespuestaCommentPCompartida',
        ),
    ]
