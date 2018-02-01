from typing import List


class DistanceNotHandledException(Exception):
    pass


class MedianRanking:
    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance: 'mediane.models.Distance',
            return_at_most_one_ranking: bool = True,
    ) -> List[List[List[int]]]:
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
        raise NotImplementedError("The method not implemented")

    def is_breaking_ties_arbitrarily(self) -> bool:
        raise NotImplementedError("The method not implemented")

    def is_using_random_value(self) -> bool:
        raise NotImplementedError("The method not implemented")

    def get_full_name(self) -> str:
        raise NotImplementedError("The method not implemented")

    def get_handled_distances(self) -> List[int]:
        """

        :return: a list of distances from distance_enumeration
        """
        raise NotImplementedError("The method not implemented")
