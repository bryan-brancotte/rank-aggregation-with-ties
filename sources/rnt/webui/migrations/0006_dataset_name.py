# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 07:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0005_job_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='name',
            field=models.CharField(default='', max_length=64, unique=True),
        ),
    ]
