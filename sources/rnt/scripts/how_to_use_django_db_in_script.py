#!/usr/bin/env python3
# https://stackoverflow.com/questions/39723310/django-standalone-script/39724171#39724171

# cd to the root of rnt,
# source ../../venv/bin/activate
# ./scripts/how_to_use_django_db_in_script.py

import os
import sys

import django
from django.contrib.auth import get_user_model
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
        name="Wrong one (created on %s)" % str(timezone.now()),
        n=100,
        m=10,
        complete=False,
        transient=True,
        owner=get_user_model().objects.all().first(),
    )
    d.content = "[[a]]"
    d.save()
    print(d)
    print(d.content)
else:
    print(d)
    print(d.content)
    print("Wrong one exists, deleting it")
    d.delete()

print("Datasets wth m >= 3")
for d in DataSet.objects.filter(m__gt=3):
    print(d)
print("Done")

print("Datasets with m = 4")
for d in DataSet.objects.filter(m=4):
    print(d)
print("Done")
