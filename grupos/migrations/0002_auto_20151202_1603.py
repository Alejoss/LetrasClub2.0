# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0001_initial'),
        ('grupos', '0001_initial'),
        ('cities_light', '0003_auto_20141120_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuariosgrupo',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='requestinvitacion',
            name='aceptado_por',
            field=models.ForeignKey(related_name='aceptado_por', to='perfiles.Perfil', null=True),
        ),
        migrations.AddField(
            model_name='requestinvitacion',
            name='grupo',
            field=models.ForeignKey(to='grupos.Grupo'),
        ),
        migrations.AddField(
            model_name='requestinvitacion',
            name='invitado_por',
            field=models.ForeignKey(related_name='invitado_por', to='perfiles.Perfil', null=True),
        ),
        migrations.AddField(
            model_name='requestinvitacion',
            name='usuario_invitado',
            field=models.ForeignKey(related_name='invitado', to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='grupo',
            name='ciudad',
            field=models.ForeignKey(to='cities_light.City', null=True),
        ),
    ]
