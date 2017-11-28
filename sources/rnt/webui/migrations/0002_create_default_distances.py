from __future__ import unicode_literals

from django.db import migrations


def migration_code(apps, schema_editor):
    Distance = apps.get_model("webui", "Distance")
    Distance.objects.get_or_create(
        name="Generalized kendall tau distance",
        desc="",
    )


class Migration(migrations.Migration):
    dependencies = [
        ('webui', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]
