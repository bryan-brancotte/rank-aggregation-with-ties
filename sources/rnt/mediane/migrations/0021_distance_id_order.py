# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-02 20:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediane', '0020_providing_scoring_scheme_20180202_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='distance',
            name='id_order',
            field=models.IntegerField(default=0),
        ),
    ]