# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0001_initial'),
        ('libros', '0001_initial'),
        ('notificaciones', '0001_initial'),
        ('comentarios', '0001_initial'),
        ('grupos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='respuestacommentperfil',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='respuestacommentgrupo',
            name='comment_grupo',
            field=models.ForeignKey(related_name='respuestas', to='comentarios.CommentGrupo'),
        ),
        migrations.AddField(
            model_name='respuestacommentgrupo',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='respuestacommentbcompartida',
            name='comment_bcompartida',
            field=models.ForeignKey(related_name='respuestas', to='comentarios.CommentBCompartida'),
        ),
        migrations.AddField(
            model_name='respuestacommentbcompartida',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='commentperfil',
            name='muro',
            field=models.ForeignKey(related_name='muro', to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='commentperfil',
            name='perfil',
            field=models.ForeignKey(related_name='comentarista', to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='commentnotificacion',
            name='notificacion',
            field=models.ForeignKey(related_name='respuestas', to='notificaciones.Notificacion'),
        ),
        migrations.AddField(
            model_name='commentnotificacion',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='commentgrupo',
            name='grupo',
            field=models.ForeignKey(to='grupos.Grupo'),
        ),
        migrations.AddField(
            model_name='commentgrupo',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='commentbcompartida',
            name='bcompartida',
            field=models.ForeignKey(to='libros.BibliotecaCompartida'),
        ),
        migrations.AddField(
            model_name='commentbcompartida',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
    ]
