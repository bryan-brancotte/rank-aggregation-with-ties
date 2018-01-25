from typing import List, Dict
import collections
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from mediane.distances.kemeny_computation import KemenyComputingFactory
from numpy import zeros, count_nonzero, vdot, array, ndarray, shape, amax, where, nditer, argmin
from os import listdir
from mediane.median_ranking_tools import parse_ranking_with_ties_of_int


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
        n = ranking.size
        max_id_bucket = amax(ranking)
        if count_nonzero(ranking < 0) > 0:
            max_id_bucket += 1
            ranking[ranking < 0] = max_id_bucket

        delta_distance_change = zeros(n+1, dtype=float)
        delta_distance_add = zeros(n+2, dtype=float)

        leave_bucket = zeros(3, dtype=float)
        improvement = True
        dst = dst_init
        tour = 0
        while improvement:
            tour += 1
            # print("DST = ", dst)
            # print("ranking = ", ranking, " ON COMMENCE")
            improvement = False
            # print("\n\n\nGO ON")

            ind_x = 0
            for element in range(n):
                size_bucket = 0
                id_bucket_element = ranking[element]
                # print("\tElement_id = ", element, " bucket = ", id_bucket_element)

                delta_distance_change.fill(0.0)
                leave_bucket.fill(0.0)
                delta_distance_add.fill(0.0)

                for el, bucket in nditer([where(ranking < id_bucket_element), ranking[ranking < id_bucket_element]],
                                         ['zerosize_ok']):
                    a = int(el)
                    # print("\t\t\t with : ", el, " buck = ", bucket, " elem = ", id_elements.get(a))
                    delta_distance_change[bucket] += matrix[ind_x + a][2] - matrix[ind_x + a][1]
                    delta_distance_change[bucket-1] += matrix[ind_x + a][0] - matrix[ind_x + a][2]

                    delta_distance_add[bucket] += matrix[ind_x + a][0] - matrix[ind_x + a][1]
                    # print("\t\t\t", delta_distance_add)

                for el, bucket in nditer([where(ranking == id_bucket_element), ranking[ranking == id_bucket_element]]):
                    a = int(el)
                    leave_bucket += matrix[ind_x + a]
                    size_bucket += 1

                for el, bucket in nditer([where(ranking > id_bucket_element), ranking[ranking > id_bucket_element]],
                                         ['zerosize_ok']):
                    a = int(el)
                    delta_distance_change[bucket] += matrix[ind_x + a][2] - matrix[ind_x + a][0]
                    delta_distance_change[bucket+1] += matrix[ind_x + a][1] - matrix[ind_x + a][2]

                    delta_distance_add[bucket+1] += matrix[ind_x + a][1] - matrix[ind_x + a][0]

                delta_distance_change[id_bucket_element-1] += leave_bucket[0] - leave_bucket[2]
                delta_distance_change[id_bucket_element + 1] += leave_bucket[1] - leave_bucket[2]

                delta_distance_add[id_bucket_element] += leave_bucket[0] - leave_bucket[2]
                # print("\t\t\t", delta_distance_add)
                delta_distance_add[id_bucket_element-1] += leave_bucket[0] - leave_bucket[2]
                # print("\t\t\t", delta_distance_add)
                delta_distance_add[id_bucket_element + 1] += leave_bucket[1] - leave_bucket[2]
                # print("\t\t\t", delta_distance_add)

                for id_buckets in range(id_bucket_element-2, -1, -1):
                    delta_distance_change[id_buckets] += delta_distance_change[id_buckets+1]
                    delta_distance_add[id_buckets] += delta_distance_add[id_buckets+1]

                for id_buckets in range(id_bucket_element + 2, max_id_bucket + 2, 1):
                    delta_distance_change[id_buckets] += delta_distance_change[id_buckets-1]
                    delta_distance_add[id_buckets] += delta_distance_add[id_buckets-1]

                delta_distance_change[-1] = 0
                delta_distance_change[max_id_bucket + 1] = 0
                delta_distance_add[-1] = 0

                # print("delta change ", delta_distance_change)
                first_negative = argmin(delta_distance_change)
                first_negative2 = argmin(delta_distance_change)
                d1 = delta_distance_change[first_negative]
                d2 = delta_distance_add[first_negative2]
                change = False
                add = False
                if d1 < 0:
                    if d2 < d1:
                        add = True
                    else:
                        change = True
                # print("ind best neg : ", first_negative, " neg : ", delta_distance_change[first_negative])

                # print("\t\t\t", delta_distance_add)
                # first_negative = argmax(delta_distance_change < 0)
                # print("\t\tCHANGE : ", delta_distance_change)
                # print("\t\tADD : ", delta_distance_add)
                if change:
                    improvement = True
                    # print("\t\t\t\tEX RANKING : ", ranking)
                    # print("\t\tChange :", "element = ", element, "ex buck =  ", id_bucket_element, " new = ",
                    # first_negative)
                    ranking[element] = first_negative

                    dst += d1
                    if size_bucket == 1:
                        ranking[ranking > id_bucket_element] -= 1
                        max_id_bucket -= 1
                    # print("\t\t\t\t   RANKING : ", ranking, "\n\n")

                elif add:
                    # print("\t\tTENTATIVE")
                    #first_negative = argmin(delta_distance_add)
                    # print("first neg = ", first_negative)
                    # first_negative = argmax(delta_distance_add < 0)
                    #if delta_distance_add[first_negative] < 0:
                    improvement = True
                    dst += d2
                        # print("\t\t\t\tEX RANKING : ", ranking)
                        # print("\t\tAdd : element = ", element, "ex buck =  ", id_bucket_element, " new = ",
                        # first_negative)

                    if size_bucket > 1:
                        ranking[ranking >= first_negative] += 1
                        ranking[element] = first_negative

                        max_id_bucket += 1
                    else:
                        if first_negative < id_bucket_element:
                            ranking[(ranking >= first_negative) & (ranking < id_bucket_element)] += 1
                            ranking[element] = first_negative
                        else:
                            ranking[(ranking > id_bucket_element) & (ranking < first_negative)] -= 1
                            ranking[element] = first_negative - 1

                        # print("\t\t\t\t   RANKING : ", ranking, "\n\n")
                ind_x += n
            # print("end : improvment = ", improvement, " dst = ", dst)
        return dst

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
        matrix = zeros((n * n, 3))

        for e1 in range(n-1, -1, -1):
            mem = positions[e1]
            ind1 = n * e1 + e1
            ind2 = ind1
            d = count_nonzero(mem == -1)

            for e2 in range(e1-1, -1, -1):
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


# fich_output = open("/home/pierre/Bureau/final.txt", "w")
# # nb_files = 0
# sc = ScoringScheme.get_scoring_scheme("ktg", 1.0)
# alg = BioConsert(sc)
# keme = KemenyComputingFactory(sc)
#
# dossier = "/home/pierre/Documents/Doctorat/Datasets/datasets-bio/"
# for fichier_str in listdir(dossier):
#     if "GS" not in fichier_str:
#
#         # print(fichier_str)
#         fichier = open(dossier+fichier_str, "r")
#         ranks = []
#         for rng in fichier.read().split("\n"):
#             if len(rng) > 5:
#                 ranks.append(parse_ranking_with_ties_of_int(rng))
#         cons = alg.compute_median_rankings(ranks, True)[-1]
#         # print(cons)
#         fich_output.write(fichier_str + "  " + str(keme.get_distance_to_a_set_of_rankings(cons, ranks)) + "\n")
#
#         fichier.close()
# # print(nb_files)
# fich_output.close()
