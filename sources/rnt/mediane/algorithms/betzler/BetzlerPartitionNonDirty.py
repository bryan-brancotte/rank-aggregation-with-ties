from typing import List, Dict, Set

from mediane.algorithms.median_ranking import MedianRanking, DistanceNotHandledException
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.normalizations.unification import Unification
from numpy import zeros, ndarray, asarray, int32, sum


class BetzlerPartitionNonDirty(MedianRanking):
    def __init__(self, s=0.75):
        self.__s = s

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance,
            return_at_most_one_ranking: bool = False) -> List[List[List[int]]]:
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

        if scoring_scheme[1][0] != scoring_scheme[1][1] or scoring_scheme[1][3] != scoring_scheme[1][4]:
            raise DistanceNotHandledException
        elem_id = {}
        id_elements = {}
        id_elem = 0
        nb_rankings = len(rankings)

        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1
        nb_elements = len(elem_id)
        if nb_elements == 0:
            return [[]]

        proportion_before = zeros((nb_elements, nb_elements), dtype=float)
        proportion_after = zeros((nb_elements, nb_elements), dtype=float)

        positions = BetzlerPartitionNonDirty.__get_positions(rankings, elem_id)
        for i in range(0, nb_elements):
            t_i = positions[i]
            for j in range(0, nb_elements):
                t_j = positions[j]
                if i != j:
                    proportion_before[i][j] = sum(t_i < t_j)/nb_rankings
                    proportion_after[i][j] = sum(t_i > t_j)/nb_rankings

        partition_betzler = []
        BetzlerPartitionNonDirty.__compute_partition_betzler(self, partition_betzler, set(id_elements.keys()),
                                                             positions, proportion_before, proportion_after)

        consensus = []
        for ensemble in partition_betzler:
            consensus.append(list(ensemble))
        return [consensus]

    @staticmethod
    def __get_positions(rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
        m = len(rankings)
        n = len(elements_id)
        rankings_unified = Unification.rankings_to_rankings(rankings)
        positions = zeros((n, m), dtype=int32) - 1
        id_ranking = 0
        for ranking in rankings_unified:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def __compute_partition_betzler(self, partition: List[List[int]], elements: Set[int], positions: ndarray,
                                    proportion_before: ndarray, proportion_after: ndarray):
        element_propre = -1
        gauche = set()
        droite = set()
        elements_liste = list(elements)
        for element in elements:
            if sum(proportion_before[element][elements_liste] >= self.__s) \
                    + sum(proportion_after[element][elements_liste] >= self.__s) == len(elements)-1:
                element_propre = element
                before_propre = proportion_before[element_propre]
                for element_2 in elements:
                    if element_2 != element:
                        if before_propre[element_2] >= self.__s:
                            gauche.add(element_2)
                        else:
                            droite.add(element_2)
                break

        if element_propre == -1:
            partition.append(list(elements))
        else:

            if len(droite) > 0:
                BetzlerPartitionNonDirty.__compute_partition_betzler(self, partition, droite, positions,
                                                                     proportion_before, proportion_after)
            partition.append([element_propre])
            if len(gauche) > 0:
                BetzlerPartitionNonDirty.__compute_partition_betzler(self, partition, gauche, positions,
                                                                     proportion_before, proportion_after)

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "Betzler"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
        )
