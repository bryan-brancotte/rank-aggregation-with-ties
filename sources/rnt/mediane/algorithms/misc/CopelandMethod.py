from typing import List
from mediane.algorithms.median_ranking import MedianRanking, DistanceNotHandledException
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, \
    GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
from mediane.normalizations.unification import Unification
import operator

from numpy import array, asarray, array_equal


class CopelandMethod(MedianRanking):

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

        scoring_scheme = asarray(distance.scoring_scheme)
        if array_equal(scoring_scheme, array([[0, 1, 1, 0, 1, 1], [1, 1, 0, 1, 1, 0]])):
            dst = 0
        elif array_equal(scoring_scheme, array([[0, 1, 1, 1, 1, 1], [1, 1, 0, 1, 1, 1]])):
            dst = 1
        else:
            raise DistanceNotHandledException

        if dst == 0:
            rankings_to_use = Unification.rankings_to_rankings(rankings)
        else:
            rankings_to_use = rankings

        elements = {}
        for ranking in rankings_to_use:
            win = 0
            lose = 0
            for bucket in ranking:
                win += len(bucket)
            for bucket in ranking:
                win -= len(bucket)
                for element in bucket:
                    if element in elements:
                        elements[element] += win - lose
                    else:
                        elements[element] = win - lose
                lose += len(bucket)
        bucket = []
        consensus = []
        old_value = -1
        # sorted_elements = sorted(elements.items(), key=operator.itemgetter(1))
        # old_value = sorted_elements[0][1]
        for key, val in sorted(elements.items(), key=operator.itemgetter(1), reverse=True):
            if val != old_value:
                bucket = []
                consensus.append(bucket)
                old_value = val
            bucket.append(key)
        return [consensus]

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "CopelandMethod"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
        )

