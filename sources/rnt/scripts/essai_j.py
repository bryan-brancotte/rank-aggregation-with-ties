#!/usr/bin/env python3
# https://stackoverflow.com/questions/39723310/django-standalone-script/39724171#39724171

# cd to the root of rnt,
# source ../../venv/bin/activate
# ./scripts/how_to_use_django_db_in_script.py
import median_ranking_tools
#from mediane.algorithms.Schulze.Schulze import Schulze
from mediane.algorithms.lri.ExactAlgorithm_bis import ExactAlgorithmBis
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN
import os
import sys

import django
from django.contrib.auth import get_user_model
from django.utils import timezone

sys.path.append(".")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rnt.settings")
django.setup()

from mediane.models import Distance

# afficher toutes les distrances de la base
for d in Distance.objects.all():
    print("Distance:", d.id, " ", d.scoring_scheme)

# id = 7: pseudo distance du papier ConQuR-Bio
ma_distance = Distance.objects.filter(id=7).first()
ma_distance_2 = Distance.objects.filter(id=3).first()


# recuperation de l'ensemble des classements dont on veut calculer un consensus
classements = median_ranking_tools.get_rankings_from_file("/home/pierre/Bureau/ex_these")
# l'algo de calcul de consensus
algorithme = ExactAlgorithmBis()
print(classements)
# calcul du consensus
print("consensus p = 1")
consensus_1 = algorithme.compute_median_rankings(classements, ma_distance)
for conse in consensus_1:
    print(conse)
kt = KendallTauGeneralizedNlogN(distance=ma_distance)
dst = kt.get_distance_to_a_set_of_rankings(c=consensus_1[0], rankings=classements)[ma_distance.id_order]
print("dst")
print(dst)

print("consensus p = 0.5")
consensus_05 = algorithme.compute_median_rankings(classements, ma_distance_2)
for conse in consensus_05:
    print(conse)
kt = KendallTauGeneralizedNlogN(distance=ma_distance_2)
dst = kt.get_distance_to_a_set_of_rankings(c=consensus_05[0], rankings=classements)[ma_distance_2.id_order]
print("dst")
print(dst)
