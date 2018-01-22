from typing import List, Dict
import collections
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from mediane.distances.kemeny_computation import KemenyComputingFactory
# from pympler.tracker import SummaryTracker
# from pympler import refbrowser
from numpy import zeros, count_nonzero, vdot, array, ndarray, shape, amax, where, nditer


class BioConsert(MedianRanking):
    def __init__(self, scoring_scheme=ScoringScheme(), starting_algorithms=None):
        self.scoring_scheme = scoring_scheme
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

        res = []
        kem = KemenyComputingFactory(scoring_scheme=self.scoring_scheme)
        elem_id = {}
        id_elements = {}
        id_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1
        n = len(elem_id)
        # m = len(rankings)

        positions = self.__departure_rankings(rankings, elem_id)
        matrix = self.__cost_matrix(positions)
        result = {}
        dst_min = float('inf')
        id_ranking = 0

        for ranking in rankings:
            dst_init = kem.get_distance_to_a_set_of_rankings(ranking, rankings)
            dst_ranking = self.__bio_consert(positions[:, id_ranking], dst_init, matrix)
            if dst_ranking <= dst_min:
                if dst_ranking < dst_min:
                    result.clear()
                result[str(positions[:, id_ranking])] = id_ranking
                dst_min = dst_ranking
            id_ranking += 1
        dst_ranking = self.__bio_consert(positions[:, id_ranking], kem.get_distance_to_a_set_of_rankings(
                                        [list(elem_id.keys())], rankings), matrix)
        if dst_ranking <= dst_min:
            if dst_ranking < dst_min:
                result.clear()
            result[str(positions[:, id_ranking])] = id_ranking
        ranking_dict = {}

        for id_ranking in result.values():
            to_be_translated = positions[:, id_ranking]
            ranking_dict.clear()
            for el in range(n):
                id_bucket = to_be_translated[el]
                if id_bucket not in ranking_dict:
                    ranking_dict[id_bucket] = [id_elements.get(el)]
                else:
                    ranking_dict[id_bucket].append(id_elements.get(el))
            ranking_list = []
            nb_buckets_ranking_i = len(ranking_dict)
            for id_bucket in range(nb_buckets_ranking_i):
                ranking_list.append(ranking_dict.get(id_bucket))
            res.append(ranking_list)
        # rankings_hash = {}
        # for cons in result:
        #    rankings_hash.clear()
        #    for id_bucket in cons:

        return res

    def __bio_consert(self, ranking: ndarray, dst_init: float, matrix: ndarray) -> float:
        n = ranking.shape[1]
        id_max_bucket = amax(ranking) + 1
        ranking[ranking < 0] = id_max_bucket
        delta_distance = zeros(n, dtype=float)
        improvement = True
        ind_x = 0
        while improvement:
            improvement = False
            for element in range(n):
                id_bucket_element = ranking[element]
                delta_distance.fill(0.0)
                for el, bucket in nditer([where(ranking < id_bucket_element), ranking[ranking < id_bucket_element]]):
                    delta_distance[bucket] += matrix[ind_x+el][2] - matrix[ind_x + el][1]

                ind_x += n




        return 0.0

    def __departure_rankings(self, rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
        if len(self.starting_algorithms) == 0:
            m = len(rankings)
            n = len(elements_id)
            departure = zeros((n, m+1), dtype=int) - 1
            id_ranking = 0
            for ranking in rankings:
                id_bucket = 0
                for bucket in ranking:
                    for element in bucket:
                        departure[elements_id.get(element)][id_ranking] = id_bucket
                    id_bucket += 1
                id_ranking += 1
            departure[:, m].fill(0)
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

    def __cost_matrix(self, positions: ndarray):
        matrix_scoring_scheme = self.scoring_scheme.matrix
        cost_before = matrix_scoring_scheme[0]
        cost_tied = matrix_scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                           cost_before[5]])
        n = shape(positions)[0]
        m = shape(positions)[1]
        matrix = zeros((n * n, 3))

        e1 = n - 1
        for mem in positions:
            # print("E1 = ", e1)
            ind1 = n * e1 + e1
            ind2 = ind1
            d = count_nonzero(mem == -1)

            for e2 in range(e1-1, -1, -1):
                # print("\tE2 = ", e2)
                ind1 -= 1
                ind2 -= n
                a = count_nonzero(mem + positions[e2] == -2)
                b = count_nonzero(mem == positions[e2])
                c = count_nonzero(positions[e2] == -1)
                e = count_nonzero(mem < positions[e2])
                relative_positions = array([e-d+a, m-e-b-c+a, b-a, c-a, d-a, a])

                put_before = vdot(relative_positions, cost_before)
                put_after = vdot(relative_positions, cost_after)
                put_tied = vdot(relative_positions, cost_tied)
                matrix[ind1] = [put_before, put_after, put_tied]
                matrix[ind2] = [put_after, put_before, put_tied]
            e1 -= 1
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
for i in range(1, 500):
    r.append([i])
r2 = [[2], [1], [3]]
r3 = [[3, 1], [2]]
BioConsert(ScoringScheme.get_scoring_scheme(id_dist="ktg", p=0.75)).compute_median_rankings([r, r2, r3])
print("OK")
