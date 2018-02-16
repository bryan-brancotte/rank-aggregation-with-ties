# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-15 22:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediane', '0023_auto_20180215_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultstoproducedecorator',
            name='status',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Taken for computation'), (3, 'Being computed'), (4, 'Done'), (5, 'Error')], default=1),
        ),
    ]
