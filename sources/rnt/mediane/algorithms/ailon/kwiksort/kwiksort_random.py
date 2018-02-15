from mediane.algorithms.ailon.kwiksort.kwiksortabs import KwikSortAbs
from mediane.distances.enumeration import *

from typing import List
from random import choice
from numpy import zeros, count_nonzero, vdot


class KwikSortRandom(KwikSortAbs):

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

    def where_should_it_be(self, element: int, pivot: int, elements: List[int], var, scoring_scheme: ndarray):
        pivot_var = var[1][var[0].get(pivot)]
        element_var = var[1][var[0].get(element)]
        m = len(pivot_var)

        a = count_nonzero(pivot_var + element_var == -2)
        b = count_nonzero(pivot_var == element_var)
        c = count_nonzero(pivot_var == -1)
        d = count_nonzero(element_var == -1)
        e = count_nonzero(element_var < pivot_var)

        comp = [e-d+a, m-e-b-c+a, b-a, c-a, d-a, a]
        cost_before = vdot(scoring_scheme[0], comp)
        cost_same = vdot(scoring_scheme[1], comp)
        cost_after = vdot(scoring_scheme[0], [m-e-b-c+a,  e-d+a, b-a, d-a, c-a, a])

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
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
        )
