# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-19 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediane', '0027_normalization_id_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='id_order',
            field=models.IntegerField(default=0),
        ),
    ]
