from typing import List

from mediane.normalizations.normalize import Normalization
from mediane.datasets.dataset import Dataset


class Unification(Normalization):

    def rankings_to_rankings(rankings: List[List[List[int]]]) -> List[List[List[int]]]:
        copy_rankings = []
        elements = set()
        for ranking in rankings:
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
                for element in bucket:
                    elements.add(element)

        for ranking in copy_rankings:
            elem_ranking = set(elements)
            for bucket in ranking:
                for element in bucket:
                    elem_ranking.remove(element)
            if len(elem_ranking) > 0:
                copy_rankings.append(list(elem_ranking))

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