from typing import List
from itertools import zip_longest
from math import ceil

from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE


class MedRank(MedianRanking):
    def __init__(self,  h=0.5):
        self.h = h

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
        h = {}
        already_put = set()
        m = len(rankings)
        nb_rankings_needed = ceil(self.h * m)
        if nb_rankings_needed < 1:
            nb_rankings_needed = 1
        if nb_rankings_needed > m:
            nb_rankings_needed = m

        bucket_res = []
        ranking_res = []

        for reorganized in zip_longest(*rankings):
            for bucket in reorganized:
                if bucket is not None:
                    for element in bucket:
                        if element not in already_put:
                            if element not in h:
                                h[element] = 1
                                if nb_rankings_needed == 1:
                                    bucket_res.append(element)
                                    already_put.add(element)
                            else:
                                h[element] += 1
                                if h[element] == nb_rankings_needed:
                                    bucket_res.append(element)
                                    already_put.add(element)
            if len(bucket_res) > 0:
                ranking_res.append(bucket_res)
                bucket_res = []

        return ranking_res

    def is_breaking_ties_arbitrarily(self):
        return True

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "Med Rank"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
        )
