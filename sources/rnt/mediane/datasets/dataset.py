from typing import List
import numpy as np
from typing import Dict


class Dataset:
    def __init__(self,  r: List[List[List[int]]]):
        self.__set_nb_rankings(-1)
        self.__set_nb_elements(-1)
        self.__set_is_complete(True)

        # updates previous values
        self.__set_rankings(r)

    def __get_rankings(self) -> List[List[List[int]]]:
        return self.__rankings

    def __get_nb_elements(self) -> int:
        return self.__nb_elements

    def __get_nb_rankings(self) -> int:
        return self.__nb_rankings

    def __get_is_complete(self) -> bool:
        return self.__is_complete

    def __set_rankings(self, rankings: List[List[List[int]]]):
        self.__rankings = rankings
        self.__set_is_complete(self.__check_if_rankings_complete())
        self.__set_nb_rankings(len(rankings))

    def __set_nb_elements(self, n: int):
        self.__nb_elements = n

    def __set_nb_rankings(self, m: int):
        self.__nb_rankings = m

    def __set_is_complete(self, complete: bool):
        self.__is_complete = complete

    n = property(__get_nb_elements, __set_nb_elements)
    m = property(__get_nb_rankings, __set_nb_rankings)
    rankings = property(__get_rankings, __set_rankings)
    is_complete = property(__get_is_complete, __set_is_complete)

    def __check_if_rankings_complete(self):
        r = self.rankings
        r1 = r[0]
        elements = {}
        complete = True
        for bucket in r1:
            for element in bucket:
                if element not in elements:
                    elements[element] = 0
        self.n = len(elements)
        for ranking in r:
            k = 0
            if not complete:
                break
            for bucket in ranking:
                if not complete:
                    break
                k += len(bucket)
                for element in bucket:
                    if element not in elements:
                        complete = False
                        break
            if k != self.n:
                complete = False
        return complete

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
        positions = np.zeros((m, n))-1
        id_ranking = 0
        for ranking in self.rankings:
            id_bucket = 0
            for bucket in ranking:
                for elem in bucket:
                    positions[id_ranking][elements_id.get(elem)] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def pairs_relative_positions(self, positions: np.ndarray) -> np.ndarray:
        n = self.n
        m = self.m
        matrix = np.zeros((n*n, 6))
        r = 0
        while r < m:
            elem1 = 0
            while elem1 < n:
                elem2 = elem1 + 1
                while elem2 < n:
                    pos1 = positions[r][elem1]
                    pos2 = positions[r][elem2]
                    if pos1 >= 0:
                        if pos2 >= 0:
                            if pos1 < pos2:
                                matrix[n * elem1 + elem2][0] += 1
                                matrix[n * elem2 + elem1][2] += 1

                            else:
                                if pos1 > pos2:
                                    matrix[n * elem1 + elem2][2] += 1
                                    matrix[n * elem2 + elem1][0] += 1
                                else:
                                    matrix[n * elem1 + elem2][1] += 1
                                    matrix[n * elem2 + elem1][1] += 1
                        else:
                            matrix[n * elem1 + elem2][3] += 1
                            matrix[n * elem2 + elem1][4] += 1
                    else:
                        if positions[r][elem2] >= 0:
                            matrix[n * elem1 + elem2][4] += 1
                            matrix[n * elem2 + elem1][3] += 1
                        else:
                            matrix[n * elem1 + elem2][5] += 1
                            matrix[n * elem2 + elem1][5] += 1
                    elem2 += 1
                elem1 += 1
            r += 1
        return matrix

    def get_unified_rankings(self) -> List[List[List[int]]]:
        copy_rankings = []
        for ranking in self.rankings:
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
        if not self.is_complete:
            elements = {}
            dict_rankings = {}
            id_ranking = 0
            for ranking in copy_rankings:
                dict_rankings[id_ranking] = {}
                dict_of_elements = dict_rankings[id_ranking]
                for bucket in ranking:
                    for element in bucket:
                        dict_of_elements[element] = 0
                        if element not in elements:
                            elements[element] = 0
                id_ranking += 1
            id_ranking = 0
            for ranking in copy_rankings:
                dict_of_elements = dict_rankings[id_ranking]
                if len(dict_of_elements) != len(elements):
                    bucket_unif = []
                    for element in elements.keys():
                        if element not in dict_of_elements:
                            bucket_unif.append(element)
                    ranking.append(bucket_unif)
                id_ranking += 1
        return copy_rankings

    def get_projected_rankings(self) -> List[List[List[int]]]:
        rankings = self.rankings
        copy_rankings = []
        for ranking in self.rankings:
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
        if self.is_complete:
            projected_rankings = copy_rankings

        else:
            m = self.m
            elements = {}
            projected_rankings = []

            for ranking in rankings:
                for bucket in ranking:
                    for element in bucket:
                        if element not in elements:
                            elements[element] = 1
                        else:
                            elements[element] += 1

            for ranking in rankings:
                ranking_projected = []
                projected_rankings.append(ranking_projected)
                for bucket in ranking:
                    projected_bucket = []
                    for element in bucket:
                        if elements[element] == m:
                            projected_bucket.append(element)
                    if len(projected_bucket) > 0:
                        ranking_projected.append(projected_bucket)
        return projected_rankings
