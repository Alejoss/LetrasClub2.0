# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comentarios', '0002_respuestacommentgrupo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='respuestacommentgrupo',
            options={'ordering': ['-fecha']},
        ),
    ]
