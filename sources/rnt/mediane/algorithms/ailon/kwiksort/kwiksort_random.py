from mediane.algorithms.ailon.kwiksort.kwiksortabs import KwikSortAbs
from mediane.distances.enumeration import *

from typing import List
from random import choice
from numpy import zeros, count_nonzero, vdot


class KwikSortRandom(KwikSortAbs):

    def __init__(self,  p=1, distance=GENERALIZED_KENDALL_TAU_DISTANCE):
        self.p = p
        self.distance = distance

    def prepare_internal_vars(self, elements_translated_target: List, rankings: List[List[List[int]]]):
        elements = {}
        id_element = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elements:
                        elements_translated_target.append(element)
                        elements[element] = id_element
                        id_element += 1

        positions = zeros((len(elements), len(rankings)), dtype=int)-1

        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        tup = (elements, positions)
        return tup

    def get_pivot(self, elements: List[int], var):
        return choice(elements)

    def where_should_it_be(self, element: int, pivot: int, elements: List[int], var):
        pivot_var = var[1][var[0].get(pivot)]
        element_var = var[1][var[0].get(element)]
        m = len(pivot_var)
        coeffs_distance = get_coeffs_dist(self.distance, self.p)

        a = count_nonzero(pivot_var + element_var == -2)
        b = count_nonzero(pivot_var == element_var)
        c = count_nonzero(pivot_var == -1)
        d = count_nonzero(element_var == -1)
        e = count_nonzero(element_var < pivot_var)

        comp = [e-d+c, b-a, m-e-2*c-b+2*a, c-a, d-a, a]
        cost_before = vdot(coeffs_distance[0], comp)
        cost_same = vdot(coeffs_distance[1], comp)
        cost_after = vdot(coeffs_distance[0], [m-e-2*c-b+2*a, b-a, e-d+c, d-a, c-a, a])

        if cost_same <= cost_before:
            if cost_same <= cost_after:
                return 0
            return 1
        else:
            if cost_before <= cost_after:
                return -1
        return 1

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return True

    def get_full_name(self):
        return "KwikSortRandomized"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
        )
