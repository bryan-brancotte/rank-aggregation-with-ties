from typing import List, Dict, Tuple
import collections
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from mediane.distances.kemeny_computation import KemenyComputingFactory
from numpy import zeros, count_nonzero, vdot, array, ndarray, shape, amax, where, nditer, argmax, sum as np_sum
# from os import listdir
# from mediane.median_ranking_tools import parse_ranking_with_ties_of_int


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

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance, return_at_most_one_ranking:
            bool = False)-> List[List[List[int]]]:
        """
        :param rankings: A set of rankings
        :type rankings: list
        :param distance: The distance to use/consider
        :type distance: Distance
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :return one or more consensus if the underlying algorithm can find multiple solution as good as each other.
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found
        :raise DistanceNotHandledException when the algorithm cannot compute the consensus following the distance given
        as parameter
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
        all_together = zeros(n, dtype=int)

        dst_ranking = BioConsert.__bio_consert(all_together, kem.get_distance_to_a_set_of_rankings(
            [list(elem_id.keys())], rankings), matrix)
        if dst_ranking <= dst_min:
            if dst_ranking < dst_min or return_at_most_one_ranking:
                result.clear()
            result[str(all_together)] = id_ranking
        ranking_dict = {}

        for id_ranking in result.values():
            if id_ranking < len(rankings):
                to_be_translated = positions[:, id_ranking]
            else:
                to_be_translated = all_together
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

    @staticmethod
    def __bio_consert(ranking: ndarray, dst_init: float, matrix: ndarray) -> float:
        print("\n\n\t\t\t\t\tNEW BEGINING")
        n = ranking.size
        max_id_bucket = amax(ranking)
        if count_nonzero(ranking < 0) > 0:
            max_id_bucket += 1
            ranking[ranking < 0] = max_id_bucket

        improvement = True
        dst = dst_init
        while improvement:
            improvement = False
            # print("\n\n\nGO ON")
            for element in range(n):
                bucket_elem = ranking[element]
                change, add, alone = BioConsert._compute_delta_costs(ranking, element, matrix, max_id_bucket)
                to = BioConsert._search_to_change_bucket(bucket_elem, change, max_id_bucket)
                if to != 0:
                    improvement = True
                    # change
                    if BioConsert.change_bucket(ranking, element, bucket_elem, bucket_elem + to, alone):
                        max_id_bucket -= 1
                else:
                    to = BioConsert._search_to_add_bucket(bucket_elem, add, max_id_bucket)
                    if to != 0:
                        improvement = True
                        if BioConsert._add_bucket(ranking, element, bucket_elem, bucket_elem + to, alone):
                            max_id_bucket += 1

        return dst

    @staticmethod
    def _compute_delta_costs(
            ranking: ndarray,
            element: int, matrix:
            ndarray, max_id_bucket: int) -> Tuple[ndarray, ndarray, bool]:

        costs = matrix[element]
        id_bucket_element = ranking[element]
        # print("\tElement_id = ", element, " bucket = ", id_bucket_element)
        # print("\tetat ranking : ", ranking)

        delta_distance_change = zeros(max_id_bucket + 2, dtype=float)
        delta_distance_add = zeros(max_id_bucket + 3, dtype=float)

        for el in nditer(where(ranking < id_bucket_element)[0], ['zerosize_ok']):
            el_int = el.item()
            bucket = ranking[el_int]
            delta_distance_change[bucket] += costs[el_int][2] - costs[el_int][1]
            delta_distance_change[bucket - 1] += costs[el_int][0] - costs[el_int][2]

            delta_distance_add[bucket] += costs[el_int][0] - costs[el_int][1]

        same = where(ranking == id_bucket_element[0])

        leave_bucket = np_sum(costs[same], axis=0)

        for el, bucket in nditer([where(ranking > id_bucket_element), ranking[ranking > id_bucket_element]],
                                 ['zerosize_ok']):
            el_int = el.item()
            bucket = ranking[el_int]

            delta_distance_change[bucket] += costs[el_int][2] - costs[el_int][0]
            delta_distance_change[bucket + 1] += costs[el_int][1] - costs[el_int][2]

            delta_distance_add[bucket + 1] += costs[el_int][1] - costs[el_int][0]

        delta_distance_change[id_bucket_element - 1] += leave_bucket[0] - leave_bucket[2]
        delta_distance_change[id_bucket_element + 1] += leave_bucket[1] - leave_bucket[2]

        delta_distance_add[id_bucket_element] += leave_bucket[0] - leave_bucket[2]
        delta_distance_add[id_bucket_element - 1] += leave_bucket[0] - leave_bucket[2]
        delta_distance_add[id_bucket_element + 1] += leave_bucket[1] - leave_bucket[2]

        # print("begin loop1")
        for id_buckets in range(id_bucket_element - 2, -1, -1):
            delta_distance_change[id_buckets] += delta_distance_change[id_buckets + 1]
            delta_distance_add[id_buckets] += delta_distance_add[id_buckets + 1]
        # print("begin loop2")

        for id_buckets in range(id_bucket_element + 2, max_id_bucket + 2, 1):
            delta_distance_change[id_buckets] += delta_distance_change[id_buckets - 1]
            delta_distance_add[id_buckets] += delta_distance_add[id_buckets - 1]

        delta_distance_change[-1] = -1
        delta_distance_add[-1] = -1
        return delta_distance_change, delta_distance_add, same.shape[0] > 1

    @staticmethod
    def _search_to_change_bucket(buck_elem: int, change_costs: ndarray, max_id_bucket: int) -> int:
        """
        :param buck_elem: the id of the bucket where the current elem is
        :type buck_elem: int
        :param change_costs: The difference of cost for each bucket change of elem
        :type change_costs: ndarray
        :param max_id_bucket: the max of id buckets
        :type max_id_bucket: int
        :return the difference between actuel position of elem and the future position if distance can be improved
                0 is returned if no changing move can decrease the score
        """
        # first, search at the right of the current position : the 1s position with negative value
        arrival = int(argmax(change_costs[buck_elem:] < 0)) + buck_elem
        # if arrival is within [current position, max_id_bucket] : elment will change bucket
        print(change_costs[buck_elem:])
        if arrival <= max_id_bucket:
            return arrival - buck_elem
        # if no change at right can be done : check left values
        return -int(argmax(change_costs[:buck_elem+1][::-1] < 0))

    @staticmethod
    def change_bucket(ranking: ndarray, element: int, old_pos: int, new_pos: int, alone_in_old_bucket: bool) -> bool:

        """
        :param ranking: the current ranking in array version
        :type ranking: ndarray
        :param element: the element to move
        :type element: int
        :param old_pos : the old positon of the element to move
        :type old_pos: int
        :param new_pos : the new positon of the element to move
        :type new_pos: int
        :param alone_in_old_bucket : is element elone in its current bucket
        :type old_pos: bool
        :return true if after moving the element in its new bucket, its old bucket must be deleted
        """

        ranking[element] = new_pos
        if alone_in_old_bucket:
            ranking[ranking > old_pos] -= 1
        return alone_in_old_bucket

    @staticmethod
    def _search_to_add_bucket(buck_elem: int, change_costs: ndarray, max_id_bucket: int) -> int:
        return 0

    @staticmethod
    def _add_bucket(ranking: ndarray, element: int, old_pos: int, new_pos: int, alone_in_old_bucket: bool) -> bool:

        """
        :param ranking: the current ranking in array version
        :type ranking: ndarray
        :param element: the element to move
        :type element: int
        :param old_pos : the old positon of the element to move
        :type old_pos: int
        :param new_pos : the id of the bucket beside which the element will be put
        :type new_pos: int
        :param alone_in_old_bucket : is element elone in its current bucket
        :type old_pos: bool
        :return true if after moving the element, the number of buckets has increased
        """

        if old_pos < new_pos:
            if alone_in_old_bucket:
                ranking[ranking >= new_pos] += 1
                ranking[element] = new_pos
            else:
                ranking[(ranking > old_pos) & (ranking < new_pos)] -= 1
                ranking[element] = new_pos - 1

        else:
            if alone_in_old_bucket:
                ranking[ranking >= new_pos] += 1
                ranking[element] = new_pos
            else:
                ranking[(ranking >= new_pos) & (ranking < old_pos)] += 1
                ranking[element] = new_pos
        return not alone_in_old_bucket

    def __departure_rankings(self, rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
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

    def __cost_matrix(self, positions: ndarray) -> ndarray:
        matrix_scoring_scheme = self.scoring_scheme.matrix
        cost_before = matrix_scoring_scheme[0]
        cost_tied = matrix_scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        n = shape(positions)[0]
        m = shape(positions)[1]
        matrix = zeros((n, n, 3))

        for e1 in range(n):
            mem = positions[e1]
            d = count_nonzero(mem == -1)
            for e2 in range(e1 + 1, n):
                a = count_nonzero(mem + positions[e2] == -2)
                b = count_nonzero(mem == positions[e2])
                c = count_nonzero(positions[e2] == -1)
                e = count_nonzero(mem < positions[e2])
                relative_positions = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])
                put_before = vdot(relative_positions, cost_before)
                put_after = vdot(relative_positions, cost_after)
                put_tied = vdot(relative_positions, cost_tied)
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]

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


# fich_output = open("/home/pierre/Bureau/final.txt", "w")
# nb_files = 0
# sc = ScoringScheme.get_scoring_scheme("ktg", 1.0)
# alg = BioConsert(sc)
# keme = KemenyComputingFactory(sc)

# dossier = "/home/pierre/Documents/Doctorat/Datasets/datasets-bio/"
# for fichier_str in listdir(dossier):
#    if "GS" not in fichier_str:

        # print(fichier_str)
#        fichier = open(dossier + fichier_str, "r")
#        ranks = []
#        for rng in fichier.read().split("\n"):
#            if len(rng) > 5:
#                ranks.append(parse_ranking_with_ties_of_int(rng))
        # cons = alg.compute_median_rankings(ranks, True)[-1]
        # print(cons)
        # fich_output.write(fichier_str + "  " + str(keme.get_distance_to_a_set_of_rankings(cons, ranks)) + "\n")

#        fichier.close()
# print(nb_files)
# fich_output.close()
