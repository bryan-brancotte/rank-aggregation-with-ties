from typing import List, Dict
import collections
from mediane.distances.enumeration import get_scoring_scheme
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN
# from pympler.tracker import SummaryTracker
# from pympler import refbrowser
from numpy import zeros, count_nonzero, vdot, array, ndarray, shape


class BioConsert(MedianRanking):
    def __init__(self, scoring_scheme=ScoringScheme(), starting_algorithms=None):
        self.scoring_scheme = scoring_scheme.get_matrix()
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

    def compute_median_rankings(self, rankings: List[List[List[int]]], return_at_most_one_ranking: bool = False):
        """
        :param rankings: A set of rankings
        :type rankings: list
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :return one or more consensus if the underlying algorithm can find multiple solution as good as each other.
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found
        """

        elem_id = {}
        id_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elem += 1
        KendallTauGeneralizedNlogN()
        positions = self.departure_rankings(rankings, elem_id)
        matrix = self.cost_matrix(positions)
        id_ranking = 0
        for ranking in rankings:
            dst_init = KendallTauGeneralizedNlogN


        return []

    def departure_rankings(self, rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
        if len(self.starting_algorithms) == 0:
            m = len(rankings)
            n = len(elements_id)
            departure = zeros((n, m), dtype=int) - 1
            id_ranking = 0
            for ranking in rankings:
                id_bucket = 0
                for bucket in ranking:
                    for element in bucket:
                        departure[elements_id.get(element)][id_ranking] = id_bucket
                    id_bucket += 1
                id_ranking += 1
            departure[m].fill(0)
        else:
            m = len(self.starting_algorithms)
            n = len(elements_id)
            departure = zeros((n, m))
            id_ranking = 0
            for algo in self.starting_algorithms:
                id_bucket = 0
                for bucket in algo.compute_median_rankings(rankings, True)[0]:
                    for element in bucket:
                        departure[elements_id.get(element)][id_ranking] = id_bucket
                    id_bucket += 1
                id_ranking += 1
        return departure

    def cost_matrix(self, positions: ndarray):
        cost_before = self.scoring_scheme[0]
        cost_tied = self.scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                           cost_before[5]])
        n = shape(positions)[0]
        matrix = zeros((n * n, 3))
        for e1 in range(n-1, -1, -1):
            # print("E1 = ", e1)
            ind1 = n * e1 + e1
            ind2 = ind1
            for e2 in range(e1-1, -1, -1):
                # print("\tE2 = ", e2)
                ind1 -= 1
                ind2 -= n
                a = count_nonzero(positions[e1] + positions[e2] == -2)
                b = count_nonzero(positions[e1] == positions[e2])
                c = count_nonzero(positions[e2] == -1)
                d = count_nonzero(positions[e1] == -1)
                e = count_nonzero(positions[e1] < positions[e2])
                relative_positions = array([e-d+a, m-e-b-c+a, b-a, c-a, d-a, a])

                put_before = vdot(relative_positions, cost_before)
                put_after = vdot(relative_positions, cost_after)
                put_tied = vdot(relative_positions, cost_tied)
                matrix[ind1] = [put_before, put_after, put_tied]
                matrix[ind2] = [put_after, put_before, put_tied]
        return matrix

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "BioConsert"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
        )


r = []
for i in range(1, 5):
    r.append([i])
r2 = [[2], [1], [3]]
r3 = [[3, 1], [2]]
alg = BioConsert(get_scoring_scheme(GENERALIZED_KENDALL_TAU_DISTANCE, p=0.75))
inp = [r, r2, r3]
#alg.compute_median_rankings(inp)
