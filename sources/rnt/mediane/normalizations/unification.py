from typing import List

from mediane.normalizations.normalize import Normalization
from mediane.datasets.dataset import Dataset

class Unification(Normalization):

    def rankings_to_rankings(rankings: List[List[List[int]]]) -> List[List[List[int]]]:
        copy_rankings = []
        for ranking in rankings:
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))

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

    def rankings_to_dataset(rankings: List[List[List[int]]]) -> Dataset:
        return Dataset(Unification.rankings_to_rankings(rankings))

    def dataset_to_rankings(d: Dataset) -> List[List[List[int]]]:
        return Unification.rankings_to_rankings(d.rankings)

    def dataset_to_dataset(d: Dataset) -> Dataset:
        return Unification.rankings_to_dataset(d.rankings)

    rankings_to_rankings = staticmethod(rankings_to_rankings)
    rankings_to_dataset = staticmethod(rankings_to_dataset)
    dataset_to_rankings = staticmethod(dataset_to_rankings)
    dataset_to_dataset = staticmethod(dataset_to_dataset)