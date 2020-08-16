from mediane.algorithms.median_ranking import MedianRanking, DistanceNotHandledException
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
from typing import List
from numpy import zeros
import numpy as np


class Schulze(MedianRanking):

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance,
            return_at_most_one_ranking: bool = False)-> List[List[List[int]]]:
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

        scoring_scheme = np.asarray(distance.scoring_scheme)
        if scoring_scheme[1][0] != scoring_scheme[1][1] or scoring_scheme[1][3] != scoring_scheme[1][4]:
            raise DistanceNotHandledException
        elements_id, id_elements, positions = self.prepare_internal_vars(rankings)
        matrix_pairwise_pref = self.pairwise_preferences(positions, len(elements_id), scoring_scheme[0])
        # print("matrix_pairwise_pref : \n{}".format(matrix_pairwise_pref))
        var = self.link_strength(matrix_pairwise_pref, elements, 'margin')
        # print(var[0])
        matrix_p = self.strength_strongest_path(var[0], var[1], elements)
        # print("\nok\n{}".format(Matrix_P))
        final_scores = self.binary_relation(matrix_p, elements)
        consensus = self.compute_consensus(elements, final_scores)
        return [consensus]

    @staticmethod
    def prepare_internal_vars(rankings: List[List[List[int]]]):
        elements_id = {}
        id_elements = {}
        id_element = 0
        for ranking in rankings:
            for bucket in ranking:
                print(bucket)
                for element in bucket:
                    print(element)
                    if element not in elements_id:
                        elements_id[element] = id_element
                        id_elements[id_element] = element
                        id_element += 1

        # print(elements)

        positions = zeros((len(elements_id), len(rankings)), dtype=int) - 1

        # print(positions)

        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return elements_id, id_elements, positions

    @staticmethod
    def calculate_pairwise_score(matrix_ranking: np.ndarray, i: int, j: int, v_b: np.ndarray):

        a = np.sum(matrix_ranking[i] < matrix_ranking[j])
        b = np.sum(matrix_ranking[i] > matrix_ranking[j])
        c = np.sum(matrix_ranking[i] == -1)
        d = np.sum(matrix_ranking[j] == -1)
        e = np.sum(matrix_ranking[i] + matrix_ranking[j] == -2)
        f = np.sum(matrix_ranking[i] == matrix_ranking[j])

        return v_b[0] * (a - c) + v_b[1] * (b - d) + v_b[2] * (f - e) + v_b[3] * (d - e) + v_b[4] * (c - e) + v_b[5] * e

    @staticmethod
    def pairwise_preferences(matrix_ranking: np.ndarray, nb_elements: int, vector_b: np.ndarray):

        matrix_pairwise_pref = zeros((nb_elements, nb_elements), dtype=int)

        i = 0
        while i < nb_elements:

            j = i + 1
            while j < nb_elements:
                matrix_pairwise_pref[i][j] = Schulze.calculate_pairwise_score(matrix_ranking, i, j, vector_b)
                matrix_pairwise_pref[j][i] = Schulze.calculate_pairwise_score(matrix_ranking, j, i, vector_b)

                j += 1

            i += 1

        return matrix_pairwise_pref

    @staticmethod
    def link_strength(matrix_pairwise_pref: List[List[int]], elements: List, strength_rule_calculation='margin'):

        # séparer en différents cas fonctions. if avant les boucles+ enum

        matrix_p = zeros((len(elements), len(elements)), dtype=int)
        matrix_pred = zeros((len(elements), len(elements)), dtype=int)

        i = 0
        while i < len(elements):
            j = 0
            while j < len(elements):
                if i != j:
                    if strength_rule_calculation == 'ratio':
                        strength = matrix_pairwise_pref[i][j] / matrix_pairwise_pref[j][i]
                    elif strength_rule_calculation == 'winning_votes':
                        strength = matrix_pairwise_pref[i][j]
                    elif strength_rule_calculation == 'losing_votes':
                        strength = len(elements) - matrix_pairwise_pref[j][i]
                    else:  # strength_rule_calculation == 'margin'
                        strength = matrix_pairwise_pref[i][j] - matrix_pairwise_pref[j][i]

                    matrix_p[i][j] = strength
                    matrix_pred[i][j] = j
                else:
                    matrix_p[i][j] = 0
                    matrix_pred[i][j] = -1

                j += 1

            i += 1

        return [matrix_p, matrix_pred]

    @staticmethod
    def strength_strongest_path(matrix_p: List[List], matrix_pred: List[List], elements: List):

        i = 0
        while i < len(elements):
            j = 0
            while j < len(elements):
                if i != j:
                    k = 0
                    while k < len(elements):
                        if i != k:
                            if j != k:
                                """
                                print("i : {}, j : {}, k : {}".format(i, j, k))
                                print(Matrix_P[j][k])
                                print(Matrix_P[j][i])
                                print(Matrix_P[i][k])
                                """
                                if matrix_p[j][k] < min(matrix_p[j][i], matrix_p[i][k]):
                                    matrix_p[j][k] = min(matrix_p[j][i], matrix_p[i][k])
                                    if matrix_pred[j][k] != matrix_pred[i][k]:
                                        matrix_pred[j][k] = matrix_pred[i][k]
                        k += 1

                j += 1

            i += 1

        return matrix_p

    @staticmethod
    def binary_relation(matrix_p: List[List], elements: List):

        elements_score = []
        i = 0
        while i < len(elements):
            score = 0
            j = 0
            while j < len(elements):
                if matrix_p[i][j] > matrix_p[j][i]:
                    score += 1
                j += 1

            elements_score.append(score)
            i += 1

        return elements_score

    @staticmethod
    def compute_consensus(elements: List, final_scores: List):

        d_consensus = {}
        for i in range(0, len(final_scores)):
            if final_scores[i] not in d_consensus:
                d_consensus[final_scores[i]] = []
            d_consensus[final_scores[i]].append(elements[i])
        print(d_consensus)
        d_consensus_sorted = sorted(d_consensus)

        consensus = []
        for element in d_consensus_sorted:
            consensus.append(d_consensus[element])

        return consensus[::-1]

    def is_breaking_ties_arbitrarily(self) -> bool:
        return False

    def is_using_random_value(self) -> bool:
        return False

    def get_full_name(self) -> str:
        return "Schulze method"

    def can_be_executed(self) -> bool:
        """
        :return true if the algorithm can be run without any risk of missing lib such as cplex
        """
        return True

    def get_handled_distances(self) -> List[int]:
        """

        :return: a list of distances from distance_enumeration
        """
        return [
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
        ]