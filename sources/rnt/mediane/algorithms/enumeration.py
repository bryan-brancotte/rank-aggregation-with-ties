from django.utils.translation import ugettext_lazy as _

from mediane.algorithms.misc.borda_count import BordaCount
from mediane.algorithms.ailon.pick_a_perm import PickAPerm
from mediane.algorithms.fagin.med_rank import MedRank


def get_median_ranking_algorithms():
    return [
        BordaCount, PickAPerm, MedRank,
    ]


def as_tuple_list():
    ret = []
    for Algo in get_median_ranking_algorithms():
        instance = Algo()
        ret.append((instance.get_full_name(), _(instance.get_full_name())))
    return ret


def get_from(id_alg):
    for Algo in get_median_ranking_algorithms():
        if Algo().get_full_name() == id_alg:
            return Algo
    return None
