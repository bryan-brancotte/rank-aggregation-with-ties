from django.utils.translation import ugettext_lazy as _

from mediane.algorithms.misc.borda_count import BordaCount


def get_median_ranking_algorithms():
    return [
        BordaCount,
    ]


def as_tuple_list():
    ret = []
    for Algo in get_median_ranking_algorithms():
        instance = Algo()
        ret.append((instance.get_full_name(), _(instance.get_full_name())))
    return ret


def get_from(id):
    for Algo in get_median_ranking_algorithms():
        if Algo().get_full_name() == id:
            return Algo
    return None
