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
    Distance.objects.get_or_create(
        key_name="KTGI",
        key_name_is_read_only=True,
        name="Generalized induced kendall tau distance",
        desc="",
    )
    Distance.objects.get_or_create(
        key_name="PSEUDO_METRIC_KTGI",
        key_name_is_read_only=True,
        name="Pseudo metric based on generalized induced kendall tau distance",
        desc="",
    )


class Migration(migrations.Migration):
    dependencies = [
        ('mediane', '0006_auto_20171221_0338'),
    ]

    operations = [
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]
