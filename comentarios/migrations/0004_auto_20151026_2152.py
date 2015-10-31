# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0003_auto_20151023_2234'),
        ('perfiles', '0003_auto_20151014_0050'),
        ('comentarios', '0003_auto_20151024_0154'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentNotificacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=1000)),
                ('eliminado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('notificacion', models.ForeignKey(to='notificaciones.Notificacion')),
                ('perfil', models.ForeignKey(to='perfiles.Perfil')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
        migrations.AlterModelOptions(
            name='commentgrupo',
            options={'ordering': ['fecha']},
        ),
        migrations.AlterModelOptions(
            name='respuestacommentgrupo',
            options={'ordering': ['fecha']},
        ),
    ]
