from django.utils.translation import ugettext_lazy as _

from mediane.algorithms.ailon.pick_a_perm import PickAPerm
from mediane.algorithms.fagin.med_rank import MedRank
from mediane.algorithms.misc.borda_count import BordaCount
from mediane.algorithms.ailon.kwiksort.kwiksort_random import KwikSortRandom
from mediane.algorithms.misc.CopelandMethod import CopelandMethod
from mediane.algorithms.lri.BioConsert import BioConsert
from mediane.algorithms.lri.BioCo import BioCo
from mediane.algorithms.lri.CondorcetPartitiong import CondorcetPartitioning


class AlgorithmEnumeration:
    __tuple_list = None
    __median_ranking_algorithms = [
        BordaCount, PickAPerm, MedRank, KwikSortRandom, CopelandMethod, BioConsert, BioCo, CondorcetPartitioning
    ]

    def __init__(self):
        self.__tuple_list = []
        for Algo in self.__median_ranking_algorithms:
            instance = Algo()
            self.__tuple_list.append((instance.get_full_name(), _(instance.get_full_name())))

    def as_tuple_list(self):
        return self.__tuple_list

    def get_from(self, id_alg):
        for Algo in self.__median_ranking_algorithms:
            if Algo().get_full_name() == id_alg:
                return Algo
        return None

    def get_name_from(self, id_alg, default=None):
        for id_algs, name in self.__tuple_list:
            if id_algs == id_alg:
                return name
        return default

    def get_median_ranking_algorithms(self):
        return self.__median_ranking_algorithms


algorithmEnumeration = AlgorithmEnumeration()


def get_median_ranking_algorithms():
    return [
        BordaCount, PickAPerm, MedRank, KwikSortRandom, BioConsert, BioCo, CondorcetPartitioning
    ]


def as_tuple_list():
    return algorithmEnumeration.as_tuple_list()


def get_from(id_alg):
    return algorithmEnumeration.get_from(id_alg)


def get_name_from(id_alg):
    return algorithmEnumeration.get_name_from(id_alg)
