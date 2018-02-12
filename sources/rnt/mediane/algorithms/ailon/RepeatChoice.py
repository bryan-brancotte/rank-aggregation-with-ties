from typing import List
from random import shuffle
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from numpy import zeros, argmax
from functools import cmp_to_key


class RepeatChoice(MedianRanking):

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
        nb_rankings = len(rankings)
        rankings_copy = list(rankings)
        shuffle(rankings_copy)
        h = {}
        id_ranking = 0
        for ranking in rankings_copy:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    if element not in h:
                        h[element] = zeros(nb_rankings, dtype=int) - 1
                    h[element][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1

        res = []
        for el in sorted(h.items(), key=cmp_to_key(RepeatChoice.__compare)):
            res.append([el[0]])

        # kem = KemenyComputingFactory(scoring_scheme=self.scoring_scheme)
        # kem = KendallTauGeneralizedNlogN()
        return [res]

    @staticmethod
    def __compare(e1: tuple, e2: tuple) -> int:
        first_ind_array_e1_inf_array_e2 = argmax(e1[1] < e2[1])
        first_ind_array_e2_inf_array_e1 = argmax(e2[1] < e1[1])
        if first_ind_array_e1_inf_array_e2 < first_ind_array_e2_inf_array_e1:
            return -1
        elif first_ind_array_e2_inf_array_e1 < first_ind_array_e1_inf_array_e2:
            return 1
        return 0

    def is_breaking_ties_arbitrarily(self):
        return True

    def is_using_random_value(self):
        return True

    def get_full_name(self):
        return "Repeat Choice"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
        )
