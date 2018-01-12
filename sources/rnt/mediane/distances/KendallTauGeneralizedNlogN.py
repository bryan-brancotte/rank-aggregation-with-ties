from typing import Dict, List
from collections import deque

from mediane.distances.distance_calculator import DistanceCalculator
from mediane.distances.enumeration import *

from numpy import zeros, asarray, sort


class KendallTauGeneralizedNlogN(DistanceCalculator):

    def __init__(self, p=1):
        self.p = p

    def get_distance_to_an_other_ranking(
            self,
            ranking1: List[List[int]],
            ranking2: List[List[int]],
    ) -> Dict[int, float]:

        elements_r1 = {}
        id_bucket = 1
        for bucket in ranking1:
            for element in bucket:
                elements_r1[element] = id_bucket
            id_bucket += 1

        return self.get_distance_to_an_other_ranking_counting_inversions(elements_r1, ranking2)

    def get_distance_to_an_other_ranking_counting_inversions(
            self,
            elements_r1: Dict,
            ranking: List[List[int]],
    ) -> Dict[int, float]:
        n1 = len(elements_r1)
        count_r2 = n1 + 1
        ranking2 = {}
        present_in_both = 0
        id_ranking = 1
        for bucket in ranking:
            bucket_r2 = deque()
            for element in bucket:
                if element in elements_r1:
                    bucket_r2.appendleft(elements_r1.get(element))
                    present_in_both += 1
                else:
                    bucket_r2.append(count_r2)
                    count_r2 += 1

            ranking2[id_ranking] = bucket_r2
            id_ranking += 1
        print(elements_r1)
        print(ranking2)

        vect = zeros(6, dtype=int)

        self.compute_inversions(ranking2, 1, len(ranking2), vect)
        res = {}

        return res

    def compute_inversions(self, ranking: Dict, left: int, right: int, vect: ndarray):
        if right == left:
            return self.manage_bucket(ranking.get(right), vect)
        else:
            middle = (right-left)//2
            return self.merge(self.compute_inversions(ranking, left, middle+left, vect),
                              self.compute_inversions(ranking, middle+left+1, right, vect), vect)

    @staticmethod
    def merge(left: ndarray, right: ndarray, vect: ndarray):
        left_copy = left.copy()
        right_copy = right.copy()
        res = zeros(len(left_copy) + len(right_copy), dtype=int)
        n = len(left)
        m = len(right)
        i = 0
        j = 0
        k = 0
        while i < n and j < m:
            if left[i] < right[j]:
                vect[0] += 1
                res[k] = left[i]
                k += 1
                i += 1
            elif left[i] > right[j]:
                vect[2] += 1
                res[k] = right[j]
                k += 1
                j += 1
            else:
                nb = left[i]
                cpt1 = 0
                cpt2 = 0
                while i < n and left[i] == nb:
                    res[k] = nb
                    k += 1
                    i += 1
                    cpt1 += 1
                while j < m and right[j] == nb:
                    res[k] = nb
                    k += 1
                    j += 1
                    cpt2 += 1

                vect[1] += cpt1 * cpt2

        while i < n:
            res[k] = left[i]
            k += 1
            i += 1
        while j < m:
            res[k] = right[j]
            k += 1
            j += 1
        return res

    @staticmethod
    def manage_bucket(bucket: List[int], vect: ndarray) -> ndarray:
        h = {}
        for elem in bucket:
            if elem not in h:
                h[elem] = 1
            else:
                h[elem] += 1
        n = len(h)
        for length_bucket_r1 in h.values():
            vect[1] += length_bucket_r1 * (n - length_bucket_r1)
        return sort(asarray(bucket), kind='mergesort')

    def get_distance_to_a_set_of_rankings(
            self,
            c: List[List[int]],
            rankings: List[List[List[int]]],
    ) -> Dict[int, float]:
        ktg = 0
        ktg_i = 0
        for r in rankings:
            distance_values = self.get_distance_to_an_other_ranking(c, r)
            ktg += distance_values[GENERALIZED_KENDALL_TAU_DISTANCE]
            ktg_i += distance_values[GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE]

        return {
            GENERALIZED_KENDALL_TAU_DISTANCE: ktg,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE: ktg_i,
        }


kt = KendallTauGeneralizedNlogN()
kt.get_distance_to_an_other_ranking([[2], [1, 7], [3]], [[8, 7], [1], [3], [10]])
