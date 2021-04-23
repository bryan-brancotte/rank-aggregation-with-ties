from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from mediane.normalizations.unification import Unification
from typing import List, Dict
from numpy import ndarray, shape, zeros, int32, sum
from igraph import Graph


class Truchon(MedianRanking):

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
        res = []
        elem_id = {}
        id_elements = {}
        id_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1
        # nb_elements = len(elem_id)

        positions = Truchon.__positions(rankings, elem_id)

        # TYPE igraph.Graph
        gr1 = self.__graph_of_elements(positions)

        # TYPE igraph.clustering.VertexClustering
        scc = gr1.components()

        for scc_i in scc:
            buck = []
            for el in scc_i:
                buck.append(id_elements.get(el))
            res.append(buck)

        return [res]

    @staticmethod
    def __graph_of_elements(positions: ndarray) -> Graph:
        graph_of_elements = Graph(directed=True)

        n = shape(positions)[0]
        m = shape(positions)[1]
        for i in range(n):
            graph_of_elements.add_vertex(name=str(i))

        edges = []
        for e1 in range(n):
            pos_e1 = positions[e1]
            for e2 in range(e1 + 1, n):
                pos_e2 = positions[e2]
                if sum(pos_e1 < pos_e2) > m/2:
                    edges.append((e1, e2))
                elif sum(pos_e2 < pos_e1) > m/2:
                    edges.append((e2, e1))
                else:
                    edges.append((e1, e2))
                    edges.append((e2, e1))

        graph_of_elements.add_edges(edges)
        return graph_of_elements

    @staticmethod
    def __positions(rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
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

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "Truchon"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return [GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
                PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE]
