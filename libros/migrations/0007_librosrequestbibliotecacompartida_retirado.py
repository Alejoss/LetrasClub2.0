# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0006_auto_20151106_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='librosrequestbibliotecacompartida',
            name='retirado',
            field=models.BooleanField(default=False),
        ),
    ]
