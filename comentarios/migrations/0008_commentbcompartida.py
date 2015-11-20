# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0012_librosrequest_grupo'),
        ('perfiles', '0003_auto_20151014_0050'),
        ('comentarios', '0007_commentperfil_respuestacommentperfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentBCompartida',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=1000)),
                ('eliminado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('bcompartida', models.ForeignKey(to='libros.BibliotecaCompartida')),
                ('perfil', models.ForeignKey(to='perfiles.Perfil')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
    ]
