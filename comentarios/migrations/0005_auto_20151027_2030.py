# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comentarios', '0004_auto_20151026_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='respuestacommentgrupo',
            name='comment_grupo',
            field=models.ForeignKey(related_name='respuestas', to='comentarios.CommentGrupo'),
        ),
    ]
