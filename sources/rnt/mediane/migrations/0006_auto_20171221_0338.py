# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 03:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediane', '0005_key_is_name_by_default_20171221_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distance',
            name='key_name',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='distance',
            name='name',
            field=models.CharField(max_length=112, unique=True),
        ),
    ]
