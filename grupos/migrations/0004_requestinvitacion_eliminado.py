# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0003_auto_20150914_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestinvitacion',
            name='eliminado',
            field=models.BooleanField(default=False),
        ),
    ]
