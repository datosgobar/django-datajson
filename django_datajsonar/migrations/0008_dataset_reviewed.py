# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-12 12:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0007_readdatajsontask_indexing_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='reviewed',
            field=models.CharField(choices=[('REVIEWED', 'Revisado'), ('ON_REVISION', 'En revisión'), ('NOT_REVIEWED', 'No revisado')], default='NOT_REVIEWED', max_length=20),
        ),
    ]
