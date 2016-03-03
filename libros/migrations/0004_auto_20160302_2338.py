# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0003_auto_20160128_0059'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoBCompartidas',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=150)),
                ('eliminado', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='bibliotecacompartida',
            name='horario_apertura',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='bibliotecacompartida',
            name='reglas_extra',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AddField(
            model_name='bibliotecacompartida',
            name='tipo',
            field=models.ForeignKey(to='libros.TipoBCompartidas', null=True),
        ),
    ]
