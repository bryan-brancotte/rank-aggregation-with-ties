from __future__ import unicode_literals

from django.db import migrations


def migration_code(apps, schema_editor):
    Distance = apps.get_model("mediane", "Distance")
    Distance.objects.update_or_create(
        key_name="KTG",
        defaults=dict(
            is_scoring_scheme_relevant=True,
            scoring_scheme_str="[[0.0, 1.0, 1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0, 1.0, 1.0]]",
            public=True,
        ),
    )
    Distance.objects.update_or_create(
        key_name="KTGI",
        defaults=dict(
            is_scoring_scheme_relevant=True,
            scoring_scheme_str="[[0.0, 1.0, 1.0, 0.0, 0.0, 0.0], [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]]",
            public=True,
        ),
    )
    Distance.objects.update_or_create(
        key_name="PSEUDO_METRIC_KTGI",
        defaults=dict(
            is_scoring_scheme_relevant=True,
            scoring_scheme_str="[[0.0, 1.0, 0.5, 0.0, 1.0, 0.0], [0.5, 0.5, 0.0, 0.5, 0.5, 0.0]]",
            public=True,
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('mediane', '0017_distance_is_scoring_scheme_relevant'),
    ]

    operations = [
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]
