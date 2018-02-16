# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-16 22:42
from __future__ import unicode_literals

from django.db import migrations, models


def migration_code(apps, schema_editor):
    Job = apps.get_model("mediane", "Job")
    for j in Job.objects.all():
        # as the save is overridden to create a random identifier when None is set
        j.identifier = None
        j.save()


class Migration(migrations.Migration):
    dependencies = [
        ('mediane', '0024_resultstoproducedecorator_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='identifier',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]