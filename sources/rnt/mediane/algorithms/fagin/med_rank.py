from itertools import zip_longest
from typing import List

from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE


class MedRank(MedianRanking):
    def __init__(self,  h=0.5):
        if h < 0:
            h = 0
        elif h > 1:
            h = 1
        self.h = h

    # Complexity : 0 (2 * n) with adaptation for induced measure
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
        has = {}

        nb_rankings_needed = {}
        already_put = set()

        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in nb_rankings_needed:
                        nb_rankings_needed[element] = self.h
                    else:
                        nb_rankings_needed[element] += self.h

        bucket_res = []
        ranking_res = []

        for reorganized in zip_longest(*rankings):
            for bucket in reorganized:
                if bucket is not None:
                    for element in bucket:
                        if element not in already_put:
                            if element not in has:
                                has[element] = 1
                                if nb_rankings_needed[element] <= 1:
                                    bucket_res.append(element)
                                    already_put.add(element)
                            else:
                                has[element] += 1
                                if has[element] >= nb_rankings_needed[element]:
                                    bucket_res.append(element)
                                    already_put.add(element)
            if len(bucket_res) > 0:
                ranking_res.append(bucket_res)
                bucket_res = []

        return ranking_res if len(ranking_res) > 0 else [[]]

    def is_breaking_ties_arbitrarily(self):
        return True

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "MEDRank"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
        )
