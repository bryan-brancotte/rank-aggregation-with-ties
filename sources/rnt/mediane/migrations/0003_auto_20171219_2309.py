# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-19 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediane', '0002_dataset_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='public',
            field=models.BooleanField(default=False, help_text='Can the dataset be seen by everyone?'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='transient',
            field=models.BooleanField(help_text='Should be deleted when the associated job is removed?'),
        ),
    ]
