# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0005_auto_20151119_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='perfil_actor',
            field=models.ForeignKey(related_name='actor', blank=True, to='perfiles.Perfil', null=True),
        ),
    ]
