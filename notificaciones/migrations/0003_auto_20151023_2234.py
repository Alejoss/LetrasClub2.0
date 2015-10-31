# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0002_notificacion_libro'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notificacion',
            options={'ordering': ['-fecha']},
        ),
    ]
