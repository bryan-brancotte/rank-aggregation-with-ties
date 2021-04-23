from typing import List, Dict, Tuple
import collections
import ctypes

from mediane.algorithms.median_ranking import MedianRanking, DistanceNotHandledException
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
from mediane.normalizations.unification import Unification
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN
from numpy import zeros, array, ndarray, amin, amax, where, asarray, ctypeslib, int32, float64


class BioConsertC(MedianRanking):
    def __init__(self, starting_algorithms=None):
        is_valid = True
        if isinstance(starting_algorithms, collections.Iterable):
            for obj in starting_algorithms:
                if not isinstance(obj, MedianRanking):
                    is_valid = False
            if is_valid:
                self.starting_algorithms = starting_algorithms
            else:
                self.starting_algorithms = []
        else:
            self.starting_algorithms = []

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance,
            return_at_most_one_ranking: bool = False) -> List[List[List[int]]]:

        """
        :param rankings: A set of rankings
        :type rankings: list
        :param distance: The distance to use/consider
        :type distance: Distance
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :param sc: a scoring scheme
        :type sc: ScoringScheme
        :return one or more consensus if the underlying algorithm can find multiple solution as good as each other.
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found
        :raise DistanceNotHandledException when the algorithm cannot compute the consensus following the distance given
        as parameter
        """
        rankagg_c = ctypes.CDLL("/home/pierre/workspace/rank-aggregation-with-ties/sources/rnt/mediane/algorithms/lri/rankaggregation.so")
        sc = None
        if distance is None:
            sc = ScoringScheme.get_scoring_scheme_when_no_distance()
            scoring_scheme = asarray(sc.matrix)
        else:
            scoring_scheme = asarray(distance.scoring_scheme)
        if scoring_scheme[1][0] != scoring_scheme[1][1] or scoring_scheme[1][3] != scoring_scheme[1][4]:
            raise DistanceNotHandledException
        res = []
        elem_id = {}
        id_elements = {}
        id_elem = 0
        nb_rankings = len(rankings)
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1
        nb_elements = len(elem_id)

        positions = BioConsertC.__get_positions(rankings, elem_id)

        if nb_elements == 0:
            return [[]]

        (departure, dst_res) = self.__departure_rankings(rankings, positions, elem_id, distance)

        fct = rankagg_c.c_BioConsert
        fct.argtypes = [ctypeslib.ndpointer(dtype=int32),
                        ctypeslib.ndpointer(dtype=int32, flags=['writeable', 'contiguous', 'aligned']),
                        ctypeslib.ndpointer(dtype=float64),
                        ctypeslib.ndpointer(dtype=float64),
                        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                        ctypeslib.ndpointer(dtype=float64, flags=['writeable', 'contiguous', 'aligned']),
                        ]
        fct.returntype = None
        fct(positions, departure, scoring_scheme[0], scoring_scheme[1], nb_elements, nb_rankings, len(dst_res), dst_res)

        ranking_dict = {}

        best_rankings = departure[where(dst_res == amin(dst_res))[0]].tolist()
        distinct_rankings = set()
        for ranking_result in best_rankings:
            st_ranking = str(ranking_result)
            if st_ranking not in distinct_rankings:
                distinct_rankings.add(st_ranking)
                ranking_dict.clear()
                el = 0
                for id_bucket in ranking_result:
                    if id_bucket not in ranking_dict:
                        ranking_dict[id_bucket] = [id_elements.get(el)]
                    else:
                        ranking_dict[id_bucket].append(id_elements.get(el))
                    el += 1

                ranking_list = []
                nb_buckets_ranking_i = len(ranking_dict)
                for id_bucket in range(nb_buckets_ranking_i):
                    ranking_list.append(ranking_dict.get(id_bucket))
                res.append(ranking_list)

        return res

    @staticmethod
    def __get_positions(rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
        m = len(rankings)
        n = len(elements_id)
        positions = zeros((n, m), dtype=int32) - 1
        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def __departure_rankings(self, rankings: List[List[List[int]]], positions: ndarray, elements_id: Dict, distance) \
            -> Tuple[ndarray, ndarray]:

        dst_id = distance.id_order
        dst_ini = []
        rankings_unified = Unification.rankings_to_rankings(rankings)
        kem_comp = KendallTauGeneralizedNlogN(distance)
        if len(self.starting_algorithms) == 0:
            real_pos = array(positions).transpose()
            distinct_rankings = set()
            list_distinct_id_rankings = []

            i = 0
            for ranking in rankings_unified:
                ranking_array = real_pos[i]
                ranking_array[ranking_array == -1] = amax(ranking_array) + 1
                string_ranking = str(ranking_array)
                if string_ranking not in distinct_rankings:
                    distinct_rankings.add(string_ranking)
                    list_distinct_id_rankings.append(i)

                    dst_ini.append(
                        kem_comp.get_distance_to_a_set_of_rankings(ranking, rankings)[dst_id])

                i += 1

            dst_ini.append(kem_comp.get_distance_to_a_set_of_rankings([[*elements_id]], rankings)
                           [dst_id])
            departure = zeros((len(list_distinct_id_rankings)+1, len(elements_id)), dtype=int32)
            departure[:-1] = real_pos[asarray(list_distinct_id_rankings)]
        else:
            m = len(self.starting_algorithms)
            n = len(elements_id)
            departure = zeros((m, n), dtype=int32) - 1
            id_ranking = 0
            for algo in self.starting_algorithms:
                cons = algo.compute_median_rankings(rankings_unified, distance, True)[0]
                dst_ini.append(kem_comp.get_distance_to_a_set_of_rankings(cons, rankings)[distance.id_order])
                id_bucket = 0
                for bucket in cons:
                    for element in bucket:
                        departure[id_ranking][elements_id.get(element)] = id_bucket
                    id_bucket += 1
                id_ranking += 1

        return departure, array(dst_ini, dtype=float64)

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "BioConsert_C"

    def get_handled_distances(self):
        """
        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
        )
