# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-25 23:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediane', '0035_merge_20180225_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='complete',
            field=models.BooleanField(help_text='Is each element present in each ranking of the dataset?'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='public',
            field=models.BooleanField(default=False, help_text='Can the dataset appear in the public database?'),
        ),
    ]
