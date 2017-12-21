from __future__ import unicode_literals

from django.db import migrations


def migration_code(apps, schema_editor):
    Distance = apps.get_model("mediane", "Distance")
    Distance.objects.get_or_create(
        key_name="KTG",
        key_name_is_read_only=True,
        name="Generalized kendall tau distance",
        desc="",
    )
    for d in Distance.objects.filter(key_name=""):
        d.key_name = d.name
        d.save()


class Migration(migrations.Migration):
    dependencies = [
        ('mediane', '0004_auto_20171221_0333'),
    ]

    operations = [
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]
