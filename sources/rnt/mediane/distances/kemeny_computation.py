from typing import Dict, List
import numpy as np
from mediane.datasets.dataset import Dataset
from mediane.distances.enumeration import *


class KemenyComputingFactory:
    def __init__(self, distance: int, p: float):
        self.__set_distance(distance)
        self.__set_p(p)

    def __get_distance(self):
        return self.__distance

    def __get_p(self):
        return self.__p

    def __set_distance(self, distance: int):
        self.__distance = distance

    def __set_p(self, p: float):
        self.__p = p

    distance = property(__get_distance, __set_distance)
    p = property(__get_p, __set_p)

    def get_kemeny_score_with_list_rankings(
            self,
            consensus: List[List[int]],
            r: List[List[List[int]]],
    ) -> float:
        return self.get_kemeny_score_with_dataset(consensus, Dataset(r))

    def get_kemeny_score_with_dataset(
            self,
            consensus: List[List[int]],
            dataset: Dataset,
    ) -> float:
        informations = dataset.get_all_informations()
        return self.get_kemeny_score_with_pairsposmatrix(
            informations[0], consensus, informations[-1])

    def get_kemeny_score_with_pairsposmatrix(self,
                                             mapping_elem_id: Dict[int, int],
                                             cons: List[List[int]],
                                             pairs_pos: np.ndarray,
                                             ) -> float:

        coefficients = get_coeffs_dist(self.distance, self.p)
        cost_before = coefficients[0]
        cost_tied = coefficients[1]

        nb_elements = len(mapping_elem_id)
        positions_consensus = np.zeros(nb_elements) - 1

        id_bucket = 0
        for bucket in cons:
            for elem in bucket:
                positions_consensus[mapping_elem_id[elem]] = id_bucket
            id_bucket += 1

        dst = 0.
        for e1 in range(nb_elements):
            mult = e1 * nb_elements
            e2 = e1 + 1
            while e2 < nb_elements:
                if positions_consensus[e1] < positions_consensus[e2]:
                    dst += np.vdot(cost_before, pairs_pos[mult + e2])
                elif positions_consensus[e1] == positions_consensus[e2]:
                    dst += np.vdot(cost_tied, pairs_pos[mult + e2])
                else:
                    dst += np.vdot(cost_tied, pairs_pos[e1 + nb_elements*e2])
                e2 += 1
        return dst
