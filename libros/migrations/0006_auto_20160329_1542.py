# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0001_initial'),
        ('libros', '0005_adminsbibliotecacompartida'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adminsbibliotecacompartida',
            name='usuario',
        ),
        migrations.AddField(
            model_name='adminsbibliotecacompartida',
            name='perfil',
            field=models.OneToOneField(null=True, to='perfiles.Perfil'),
        ),
        migrations.AlterField(
            model_name='tipobcompartidas',
            name='nombre',
            field=models.CharField(unique=True, max_length=150),
        ),
    ]
