#!/usr/bin/env python3
# https://stackoverflow.com/questions/39723310/django-standalone-script/39724171#39724171

# cd to the root of rnt,
# source ../../venv/bin/activate
# ./scripts/how_to_use_django_db_in_script.py

import os
import sys

import django
from django.utils import timezone

sys.path.append(".")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rnt.settings")
django.setup()

from mediane.models import DataSet

for d in DataSet.objects.all():
    print("Dataset:", d.name)
    print("Elt?", d.n)
    print("Ranking?", d.m)
    print("Complete?", d.complete)

# Affiche le dataset en base nommé Default, s'il existe
print(DataSet.objects.filter(name="Default").first())

d = DataSet.objects.filter(name="Wrong one").first()
if d is None:
    print("Wrong one does not exists, creating it")
    d = DataSet.objects.create(
        name="Wrong one",
        n=0,
        m=0,
        complete=False,
        transient=True,
    )
    d.content = "We should have put rankings here ! (created on %s)" % str(timezone.now())
    d.save()
    print(d)
    print(d.content)
else:
    print(d)
    print(d.content)
    print("Wrong one exists, deleting it")
    d.delete()
