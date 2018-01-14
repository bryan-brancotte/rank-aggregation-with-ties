from typing import Dict, List
from collections import deque

from mediane.distances.distance_calculator import DistanceCalculator
from mediane.distances.enumeration import *

from numpy import zeros, asarray, sort, count_nonzero, vdot


class KendallTauGeneralizedNlogN(DistanceCalculator):

    def __init__(self, p=1.0):
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

        return self.get_distance_to_an_other_ranking_counting_inversions(elements_r1, ranking2, id_bucket)

    def get_distance_to_an_other_ranking_counting_inversions(
            self, elements_r1: Dict, ranking: List[List[int]], id_max: int) -> Dict[int, float]:
        vect_before = zeros(6, dtype=int)
        vect_tied = zeros(6, dtype=int)
        not_in_r2 = {}
        in_r1_only = set(elements_r1.keys())
        n1 = len(elements_r1)
        n2 = 0
        elem_r1_and_not_r2 = n1
        count_r2 = id_max
        ranking2 = {}
        present_in_both = 0
        id_ranking = 1
        for bucket in ranking:
            bucket_r2 = deque()
            n2 += len(bucket)
            for element in bucket:
                if element in elements_r1:
                    in_r1_only.remove(element)
                    bucket_r2.appendleft(elements_r1.get(element))
                    elem_r1_and_not_r2 -= 1
                    present_in_both += 1
                else:
                    bucket_r2.append(count_r2)
                    count_r2 += 1

            ranking2[id_ranking] = bucket_r2
            id_ranking += 1

        presence = zeros(count_r2, dtype=int)
        cumulated_up = zeros(count_r2, dtype=int)
        cumulated_down = zeros(count_r2, dtype=int)

        for bucket in ranking2.values():
            for element in bucket:
                if element < id_max:
                    presence[element] += 1
        cumulated_up[0] = presence[0]
        cumulated_down[0] = n2
        for i in range(1, count_r2):
            cumulated_up[i] = cumulated_up[i-1] + presence[i]
            cumulated_down[i] = cumulated_down[i-1] - presence[i]
        for element in in_r1_only:
            id_bucket = elements_r1.get(element)
            if id_bucket not in not_in_r2:
                not_in_r2[id_bucket] = 1
            else:
                not_in_r2[id_bucket] += 1
            vect_before[3] += cumulated_up[id_bucket-1]
            vect_before[4] += cumulated_down[id_bucket]

        for size_ties_r1_both_missing_in_r2 in not_in_r2.values():
            vect_tied[5] += size_ties_r1_both_missing_in_r2 * (size_ties_r1_both_missing_in_r2 - 1) / 2

        # elem_r2_and_not_r1 = count_r2 - id_max

        # vect[3] = elem_r1_and_not_r2 * n2 + elem_r2_and_not_r1 * n1
        # vect[5] = (elem_r2_and_not_r1 * (elem_r2_and_not_r1-1) + elem_r1_and_not_r2*(elem_r1_and_not_r2-1))/2

        self.compute_inversions(ranking2, 1, len(ranking2), vect_before, vect_tied, id_max)
        res = {}
        # print("VECT1 = ", vect_before)
        # print("VECT2 = ", vect_tied)
        for distance in (GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
                         PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE):
            coeffs = get_coeffs_dist(id_dist=distance, p=self.p)
            dst = abs(vdot(coeffs[0], vect_before)) + abs(vdot(coeffs[1], vect_tied))
            res[distance] = dst
        return res

    def compute_inversions(self, ranking: Dict, left: int, right: int, vect1: ndarray, vect2: ndarray, id_max: int):
        if right == left:
            return self.manage_bucket(ranking.get(right), vect1, vect2, id_max)
        else:
            middle = (right-left)//2
            return self.merge(self.compute_inversions(ranking, left, middle+left, vect1, vect2, id_max),
                              self.compute_inversions(ranking, middle+left+1, right, vect1, vect2, id_max),
                              vect1, vect2, id_max)

    @staticmethod
    def merge(left: ndarray, right: ndarray, vect_before: ndarray, vect_tied: ndarray, id_max: int):
        left_copy = left.copy()
        right_copy = right.copy()
        res = zeros(len(left_copy) + len(right_copy), dtype=int)
        n = len(left)
        m = len(right)
        i = 0
        j = 0
        k = 0
        not_in_r1_left = count_nonzero(left >= id_max)
        not_in_r1_right = count_nonzero(right >= id_max)
        vect_before[5] += not_in_r1_left * not_in_r1_right

        while i < n and j < m:
            nb = left[i]
            nb2 = right[j]
            if nb < nb2:
                if nb < id_max:
                    vect_before[0] += m-j-not_in_r1_right
                    vect_before[3] += not_in_r1_right
                res[k] = nb
                k += 1
                i += 1
            elif nb > nb2:
                if nb2 < id_max:
                    vect_before[2] += n-i-not_in_r1_left
                    vect_before[4] += not_in_r1_left
                res[k] = nb2
                k += 1
                j += 1
            else:
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

                if nb < id_max:
                    vect_tied[0] += cpt1 * cpt2

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
    def manage_bucket(bucket: List[int], vect_before: ndarray, vect_tied: ndarray, id_max: int) -> ndarray:
        h = {}
        n = 0
        not_in_r1 = 0
        for elem in bucket:
            if elem < id_max:
                n += 1
                if elem not in h:
                    h[elem] = 1
                else:
                    h[elem] += 1
            else:
                not_in_r1 += 1
        vect_tied[5] += not_in_r1 * (not_in_r1-1) / 2
        vect_tied[3] += not_in_r1 * len(h)
        for length_bucket_r1 in h.values():
            vect_before[0] += length_bucket_r1 * (n - length_bucket_r1)
            vect_tied[1] += length_bucket_r1 * (length_bucket_r1 - 1) / 2
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


kt = KendallTauGeneralizedNlogN(0.75)
# kt.get_distance_to_an_other_ranking([[2], [1, 7], [3], [6]], [[8, 3, 11], [1, 7], [10], [6]])
kt.get_distance_to_an_other_ranking([[1, 2], [3, 4]], [[1], [2], [3], [4]])
