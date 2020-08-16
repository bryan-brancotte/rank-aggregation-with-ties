import operator
from typing import List, Dict
from numpy import vdot, ndarray, count_nonzero, shape, array, zeros, asarray
from mediane.algorithms.median_ranking import MedianRanking, DistanceNotHandledException
from mediane.distances.ScoringScheme import ScoringScheme
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION, \
    GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE


class CopelandMethod(MedianRanking):

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance=None,
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

        if distance is None:
            scoring_scheme = ScoringScheme([[0., 1., .5, 0., 1., 0.], [0.5, 0.5, 0, 0.5, 0.5, 0.]]).matrix
        else:
            scoring_scheme = asarray(distance.scoring_scheme)

        if scoring_scheme[1][0] != scoring_scheme[1][1] or scoring_scheme[1][3] != scoring_scheme[1][4]:
            raise DistanceNotHandledException

        res = []
        elem_id = {}
        id_elements = {}
        id_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem          # dictionnaire pour retrouver l'id a partir d'un element
                        # (id commence a 0)
                        id_elements[id_elem] = element      # dictionnaire pour retrouver l'element a partir de son id
                        id_elem += 1

        # nb_elements = len(elem_id)

        positions = CopelandMethod.__positions(rankings, elem_id)    # matrice de positions
        n = shape(positions)[0]  # nombre d'elements
        m = shape(positions)[1]  # nombre de classements
        cost_before = scoring_scheme[0]     # definition des differents couts
        cost_tied = scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        id_scores = {}                                      # dictionnaire pour retrouver le score d'un element
        # a partir de son id
        for i in range(0, n, 1):                # initialisation du dictionnaire
            id_scores[i] = 0
        for id_el1 in range(0, n, 1):
            mem = positions[id_el1]             # tableau de rangs de el1
            d = count_nonzero(mem == -1)    # nombre de fois ou seulement el1 est absent
            for id_el2 in range(id_el1 + 1, n, 1):
                a = count_nonzero(mem + positions[id_el2] == -2)  # nombre de fois ou el1 et el2 sont absents
                b = count_nonzero(mem == positions[id_el2])     # nombre de fois ou el1 et el2 sont en egalites
                c = count_nonzero(positions[id_el2] == -1)      # nombre de fois ou seulement el2 est absent
                e = count_nonzero(mem < positions[id_el2])      # nombre de fois ou el1 est avant el2
                relative_positions = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])  # vecteur omega
                put_before = vdot(relative_positions, cost_before)  # cout de placer el1 avant el2
                put_after = vdot(relative_positions, cost_after)    # cout de placer el1 apres el2
                put_tied = vdot(relative_positions, cost_tied)      # cout de placer el1 a egalite avec el2
                if put_before < put_after and put_before < put_tied:
                    id_scores[id_el1] += 1
                    id_scores[id_el2] -= 1
                elif put_after < put_before and put_after < put_tied:
                    id_scores[id_el1] -= 1
                    id_scores[id_el2] += 1
        sorted_ids = CopelandMethod.sorted_dictionary_keys(id_scores)  # liste des cles du dictionnaire trie par
        # valeurs decroissantes
        bucket = []
        previous_id = sorted_ids[0]
        for id_elem in sorted_ids:
            if id_scores.get(previous_id) == id_scores.get(id_elem):  # si l'elem actuel a le meme score que l'element
                # precedent
                bucket.append(id_elements.get(id_elem))                  # on le place dans le meme bucket que celui ci
            else:
                res.append(bucket)                                  # sinon, on concatene le bucket a la liste resultat
                bucket = [id_elements.get(id_elem)]                 # on reinitialise le bucket avec le candidat actuel
            previous_id = id_elem
        res.append(bucket)                  # on concatene le dernier bucket a la liste resultat
        return [res]

    # tri du dictionnaire dans l'ordre decroissant des scores, tri "timsort" par defaut. Complexite O(nlog n)
    # au pire des cas
    # retourne la liste des cles ordonnées par valeurs decroissantes
    @staticmethod
    def sorted_dictionary_keys(d):
        d = (sorted(d.items(), key=operator.itemgetter(1), reverse=True))
        res = []
        for (k, v) in d:
            res.append(k)
        return res

    @staticmethod
    def __positions(rankings: List[List[List[int]]],
                    elements_id: Dict) -> ndarray:
        positions = zeros((len(elements_id), len(rankings)), dtype=int) - 1
        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def is_breaking_ties_arbitrarily(self) -> bool:
        return False

    def is_using_random_value(self) -> bool:
        return False

    def get_full_name(self) -> str:
        return "CopelandMethod"

    def can_be_executed(self) -> bool:
        return True

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
