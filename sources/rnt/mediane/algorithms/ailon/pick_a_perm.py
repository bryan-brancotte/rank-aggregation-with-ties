from typing import List

from mediane.algorithms.median_ranking import MedianRanking, IncompleteRankingsNotHandledException
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, \
    GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION, PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,\
    GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN


class PickAPerm(MedianRanking):

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
        :raise Incomplete when the algorithm cannot compute the consensus following the distance given
        as parameter
        """
        elements = set()
        r0 = rankings[0]
        for bucket in r0:
            for elem in bucket:
                elements.add(elem)

        for ranking in rankings:
            nb_elem_r_i = 0
            for bucket in ranking:
                nb_elem_r_i += len(bucket)
                for elem in bucket:
                    if elem not in elements:
                        raise IncompleteRankingsNotHandledException
            if nb_elem_r_i != len(elements):
                raise IncompleteRankingsNotHandledException

        k = KendallTauGeneralizedNlogN(distance)
        dst_min = float('inf')
        consensus = [[]]
        for ranking in rankings:
            dist = k.get_distance_to_a_set_of_rankings(ranking, rankings).get(distance.id_order)
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
        return "Pick-a-Perm"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
        )
