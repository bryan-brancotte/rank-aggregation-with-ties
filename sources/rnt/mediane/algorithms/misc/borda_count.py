from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE
from mediane.algorithms.median_ranking import MedianRanking


class BordaCount(MedianRanking):
    def __init__(self):
        pass

    def compute_median_rankings(self, rankings: list, return_at_most_one_ranking: bool):
        """
        :param rankings: A set of rankings
        :type list
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type bool
        :return one or more consensus if the underlying algorithm can find multiple solution as good as each other.
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found
        """
        raise NotImplementedError("The method not implemented")

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "BordaCount"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumaration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
        )
