from typing import Dict, List
from mediane.distances.distance_calculator import DistanceCalculator
from mediane.distances.kemeny_computation import KemenyComputingFactory

from numpy import vdot, asarray


class KendallTauGeneralizedNlogN(DistanceCalculator):

    def __init__(self, distance: 'mediane.models.Distance'):
        self.distance = distance

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
        coeffs = asarray(self.distance.scoring_scheme)

        dst = abs(vdot(coeffs[0], vect_before)) + abs(vdot(coeffs[1], vect_tied))
        res[self.distance.id_order] = dst
        return res

    def get_distance_to_a_set_of_rankings(
            self,
            c: List[List[int]],
            rankings: List[List[List[int]]],
    ) -> Dict[int, float]:
        dst = 0
        for r in rankings:
            dst += self.get_distance_to_an_other_ranking(c, r)[self.distance.id_order]

        return {
            self.distance.id_order: dst
        }
