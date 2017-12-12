from typing import List

from mediane.datasets.dataset import Dataset
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.kemeny_computation import KemenyComputingFactory
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE


class PickAPerm(MedianRanking):
    def __init__(self,  p=1):
        self.p = p

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
        k = KemenyComputingFactory(GENERALIZED_KENDALL_TAU_DISTANCE, self.p)
        d = Dataset(rankings)
        informations = d.get_all_informations()
        dst_min = float('inf')
        consensus = []

        for ranking in rankings:
            dist = k.get_kemeny_score_with_pairsposmatrix(informations[0], ranking, informations[-1])
            if dist < dst_min:
                dst_min = dist
                consensus.clear()
                consensus.append(ranking)
            elif dist == dst_min and not return_at_most_one_ranking:
                consensus.append(ranking)

        return consensus

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "Pick a Perm"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
        )
