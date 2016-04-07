# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0007_remove_bibliotecacompartida_perfil_admin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='libro',
            options={'ordering': ['titulo']},
        ),
        migrations.AlterModelOptions(
            name='librosbibliotecacompartida',
            options={'ordering': ['libro__titulo']},
        ),
        migrations.AlterField(
            model_name='adminsbibliotecacompartida',
            name='biblioteca_compartida',
            field=models.ForeignKey(to='libros.BibliotecaCompartida'),
        ),
        migrations.AlterField(
            model_name='adminsbibliotecacompartida',
            name='perfil',
            field=models.ForeignKey(to='perfiles.Perfil', null=True),
        ),
    ]
