# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0005_auto_20151015_0123'),
        ('libros', '0011_auto_20151111_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='librosrequest',
            name='grupo',
            field=models.ForeignKey(blank=True, to='grupos.Grupo', null=True),
        ),
    ]
