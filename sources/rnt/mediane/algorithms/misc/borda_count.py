from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE
from mediane.algorithms.median_ranking import MedianRanking
from typing import List


class BordaCount(MedianRanking):
    def __init__(self,  use_bucket_id=False):
        self.useBucketIdAndNotBucketSize = use_bucket_id

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
        points = {}
        for ranking in rankings:
            id_bucket = 1
            for bucket in ranking:
                for elem in bucket:
                    if elem not in points:
                        points[elem] = {}
                        points[elem][0] = 0
                        points[elem][1] = 0

                    points[elem][0] += id_bucket
                    points[elem][1] += 1
                if self.useBucketIdAndNotBucketSize:
                    id_bucket += 1
                else:
                    id_bucket += len(bucket)
        lis = []
        for elem in points.keys():
            lis.append((elem, points[elem][0] * 1.0 / points[elem][1]))
        tri = sorted(lis, key=lambda col: col[1])
        consensus = []
        bucket = []
        last = -1
        for duo in tri:
            if duo[1] != last:
                last = duo[1]
                bucket = []
                consensus.append(bucket)
            bucket.append(duo[0])
        return [consensus]

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "BordaCount"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
        )
