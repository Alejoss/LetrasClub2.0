# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0001_initial'),
        ('grupos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.CharField(max_length=50)),
                ('leida', models.BooleanField(default=False)),
                ('biblioteca_compartida', models.ForeignKey(blank=True, to='libros.BibliotecaCompartida', null=True)),
                ('grupo', models.ForeignKey(blank=True, to='grupos.Grupo', null=True)),
                ('libro', models.ForeignKey(related_name='libro', blank=True, to='libros.Libro', null=True)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
    ]
