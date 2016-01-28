# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0002_auto_20151202_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libro',
            name='slug',
            field=models.SlugField(max_length=255, null=True, blank=True),
        ),
    ]
