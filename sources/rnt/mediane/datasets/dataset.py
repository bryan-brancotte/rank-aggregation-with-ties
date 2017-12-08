from typing import List, Dict
import numpy as np


class Dataset:
    def __init__(self,  r: List[List[List[int]]]):
        self.__set_nb_rankings(-1)
        self.__set_nb_elements(-1)
        self.__set_is_complete(True)

        # updates previous values with right values for n, m and complete
        self.__set_rankings_and_update_properties(r)

    def __get_rankings(self) -> List[List[List[int]]]:
        return self.__rankings

    def __get_nb_elements(self) -> int:
        return self.__nb_elements

    def __get_nb_rankings(self) -> int:
        return self.__nb_rankings

    def __get_is_complete(self) -> bool:
        return self.__is_complete

    def __set_rankings_and_update_properties(self, rankings: List[List[List[int]]]):
        self.__rankings = rankings
        self.__set_nb_rankings(len(rankings))
        self.__set_is_complete(self.__check_if_rankings_complete_and_update_n())

    def __set_nb_elements(self, n: int):
        self.__nb_elements = n

    def __set_nb_rankings(self, m: int):
        self.__nb_rankings = m

    def __set_is_complete(self, complete: bool):
        self.__is_complete = complete

    n = property(__get_nb_elements, __set_nb_elements)
    m = property(__get_nb_rankings, __set_nb_rankings)
    rankings = property(__get_rankings, __set_rankings_and_update_properties)
    is_complete = property(__get_is_complete, __set_is_complete)

    def __check_if_rankings_complete_and_update_n(self):
        if len(self.rankings) == 0:
            self.n = 0
            self.m = 0
        else:
            elements = {}

            for ranking in self.rankings:
                nb_elements = 0
                for bucket in ranking:
                    nb_elements += len(bucket)
                    for element in bucket:
                        if element not in elements:
                            elements[element] = 1
                        else:
                            elements[element] += 1
            self.n = len(elements)
            self.m = len(self.rankings)
            for key in elements.keys():
                if elements[key] != self.m:
                    return False
        return True

    def get_all_informations(self) -> tuple:
        mapping_elements_id = self.map_elements_id()
        positions = self.get_positions(mapping_elements_id)
        pairs_relative_positions = self.pairs_relative_positions(positions)
        return mapping_elements_id, positions, pairs_relative_positions

    def map_elements_id(self) -> Dict[int, int]:
        h = {}
        id_elem = 0
        for ranking in self.rankings:
            for bucket in ranking:
                for elem in bucket:
                    if elem not in h:
                        h[elem] = id_elem
                        id_elem += 1
        return h

    def get_positions(self, elements_id: dict) -> np.ndarray:
        n = self.n
        m = self.m
        positions = np.zeros((n, m)) - 1
        id_ranking = 0
        for ranking in self.rankings:
            id_bucket = 0
            for bucket in ranking:
                for elem in bucket:
                    positions[elements_id.get(elem)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def pairs_relative_positions(self, positions: np.ndarray) -> np.ndarray:
        n = self.n
        m = self.m
        matrix = np.zeros((n * n, 6))
        for e1 in range(n-1, -1, -1):
            ind1 = n * e1 + e1
            ind2 = ind1
            for e2 in range(e1-1, -1, -1):
                ind1 -= 1
                ind2 -= n
                a = np.count_nonzero(positions[e1] + positions[e2] == -2)
                b = np.count_nonzero(positions[e1] == positions[e2])
                c = np.count_nonzero(positions[e2] == -1)
                d = np.count_nonzero(positions[e1] == -1)
                e = np.count_nonzero(positions[e1] < positions[e2])
                matrix[ind1] = [e-d+a, b-a, m-(a+b+c+d+e), c-a, d-a, a]
                matrix[ind2] = [e - d + a, b - a, m - (a + b + c + d + e), c - a, d - a, a]

        return matrix

    def copy_rankings(self) -> List[List[List[int]]]:
        copy = []
        for ranking in self.rankings:
            new_ranking = []
            copy.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
        return copy
