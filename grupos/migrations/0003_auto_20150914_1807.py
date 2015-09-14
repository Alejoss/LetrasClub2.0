# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0002_auto_20150902_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestinvitacion',
            name='invitado_por',
            field=models.ForeignKey(related_name='invitado_por', to='perfiles.Perfil', null=True),
        ),
    ]
