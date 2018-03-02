from typing import List

from mediane.datasets.dataset import Dataset
from mediane.normalizations.normalize import Normalization


class Projection(Normalization):

    def rankings_to_rankings(rankings: List[List[List[int]]]) -> List[List[List[int]]]:
        elements = {}
        projected_rankings = []
        m = len(rankings)
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element in elements:
                        elements[element] += 1
                    else:
                        elements[element] = 1
        cpt = 0
        for ranking in rankings:
            cpt += 1
            new_ranking = []
            projected_rankings.append(new_ranking)
            for bucket in ranking:
                new_bucket = []
                for element in bucket:
                    if elements[element] == m:
                        new_bucket.append(element)
                if len(new_bucket) > 0:
                    new_ranking.append(new_bucket)
        return [projected_rankings]

    def rankings_to_dataset(rankings: List[List[List[int]]]) -> Dataset:
        return Dataset(Projection.rankings_to_rankings(rankings))

    def dataset_to_rankings(d: Dataset) -> List[List[List[int]]]:
        return Projection.rankings_to_rankings(d.rankings)

    def dataset_to_dataset(d: Dataset) -> Dataset:
        return Projection.rankings_to_dataset(d.rankings)

    rankings_to_rankings = staticmethod(rankings_to_rankings)
    rankings_to_dataset = staticmethod(rankings_to_dataset)
    dataset_to_rankings = staticmethod(dataset_to_rankings)
    dataset_to_dataset = staticmethod(dataset_to_dataset)

