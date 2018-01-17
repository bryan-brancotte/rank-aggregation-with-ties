from typing import Dict, List
from mediane.distances.distance_calculator import DistanceCalculator
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, get_coeffs_dist
from mediane.distances.kemeny_computation import KemenyComputingFactory

from numpy import vdot


class KendallTauGeneralizedNlogN(DistanceCalculator):

    def __init__(self, p=1.0):
        self.p = p

    def get_distance_to_an_other_ranking(
            self,
            ranking1: List[List[int]],
            ranking2: List[List[int]],
    ) -> Dict[int, float]:
        elements_r1 = {}
        size_buckets = {}
        id_bucket = 1
        for bucket in ranking1:
            size_buckets[id_bucket] = len(bucket)
            for element in bucket:
                elements_r1[element] = id_bucket
            id_bucket += 1

        return self.get_distance_to_an_other_ranking_counting_inversions(elements_r1, size_buckets, ranking2, id_bucket)

    def get_distance_to_an_other_ranking_counting_inversions(
            self, elements_r1: Dict, size_buckets: Dict, ranking: List[List[int]], id_max: int) -> Dict[int, float]:
        (vect_before, vect_tied) = KemenyComputingFactory.get_before_tied_counting(elements_r1, size_buckets, ranking,
                                                                                   id_max)
        res = {}
        for distance in (GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
                         PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE):
            coeffs = get_coeffs_dist(id_dist=distance, p=self.p)
            dst = abs(vdot(coeffs[0], vect_before)) + abs(vdot(coeffs[1], vect_tied))
            res[distance] = dst
        return res

    def get_distance_to_a_set_of_rankings(
            self,
            c: List[List[int]],
            rankings: List[List[List[int]]],
    ) -> Dict[int, float]:
        ktg = 0
        ktg_i = 0
        pktg_i = 0
        for r in rankings:
            distance_values = self.get_distance_to_an_other_ranking(c, r)
            ktg += distance_values[GENERALIZED_KENDALL_TAU_DISTANCE]
            ktg_i += distance_values[GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE]
            pktg_i += distance_values[PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE]

        return {
            GENERALIZED_KENDALL_TAU_DISTANCE: ktg,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE: ktg_i,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE: pktg_i,
        }
