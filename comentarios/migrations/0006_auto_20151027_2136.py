# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comentarios', '0005_auto_20151027_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentnotificacion',
            name='notificacion',
            field=models.ForeignKey(related_name='respuestas', to='notificaciones.Notificacion'),
        ),
    ]
