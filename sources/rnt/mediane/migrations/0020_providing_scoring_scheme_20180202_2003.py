from __future__ import unicode_literals

from django.db import migrations


def migration_code(apps, schema_editor):
    Distance = apps.get_model("mediane", "Distance")
    d = Distance.objects.get(key_name="KTG")
    d.pk = None
    d.key_name = "KTGU"
    d.save()
    Distance.objects.update_or_create(
        key_name="KTGU",
        defaults=dict(
            is_scoring_scheme_relevant=True,
            scoring_scheme_str="[[0.0, 1.0, 1.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0, 1.0, 0.0]]",
            public=True,
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('mediane', '0019_auto_20180201_2129'),
    ]

    operations = [
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]
