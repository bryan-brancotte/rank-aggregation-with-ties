from typing import List
import numpy as np


class Dataset:
    def __init__(self,  r: List[List[List[int]]]):
        self._rankings = r
        self._is_complete = True
        r1 = r[0]
        elements = {}
        for bucket in r1:
            for element in bucket:
                if element not in elements:
                    elements[element] = 0
        n = len(elements)
        for ranking in r:
            k = 0
            if not self._is_complete:
                break
            for bucket in ranking:
                if not self._is_complete:
                    break
                k += len(bucket)
                for element in bucket:
                    if element not in elements:
                        self._is_complete = False
                        break
            if k != n:
                self._is_complete = False

    def _get_rankings(self):
        return self._rankings

    def _set_rankings(self, r2: List[List[List[int]]]):
        self._rankings = r2

    rankings = property(_get_rankings, _set_rankings)

    def _get_is_complete(self):
        return self._is_complete

    is_complete = property(_get_is_complete,)

    def map_elements_id(self):
        h = {}
        id_elem = 0
        for ranking in self._get_rankings():
            for bucket in ranking:
                for elem in bucket:
                    if elem not in h:
                        h[elem] = id_elem
                        id_elem += 1
        return h

    def get_positions(self, elements_id: dict):
        n = len(elements_id)
        m = len(self._get_rankings())
        positions = np.zeros((m, n))-1
        id_ranking = 0
        for ranking in self._get_rankings():
            id_bucket = 0
            for bucket in ranking:
                for elem in bucket:
                    positions[id_ranking][elements_id.get(elem)] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def pairs_relative_positions(self, elements_id: dict, positions: np.ndarray):
        n = len(elements_id)
        m = len(self._get_rankings())
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

    def get_unified_rankings(self):
        copy_rankings = []
        for ranking in self._get_rankings():
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
        if not self._get_is_complete():
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

    def get_projected_rankings(self):
        rankings = self._get_rankings()
        copy_rankings = []
        for ranking in self._get_rankings():
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
        if self._get_is_complete():
            projected_rankings = copy_rankings

        else:
            m = len(rankings)
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

r1 = []
dataset = []
n = 20
m = 1000000
for i in range(n):
    r1.append([i])
for i in range(m):
    dataset.append(r1)
for i in range(10):
    dataset[-1].pop()

print(Dataset(dataset).get_projected_rankings())