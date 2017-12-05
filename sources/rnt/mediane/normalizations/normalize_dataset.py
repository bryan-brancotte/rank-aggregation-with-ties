from typing import List

from mediane.normalizations.enumeration import PROJECTION, UNIFICATION, NONE
from mediane.datasets.dataset import Dataset


class Normalize:

    def normalize_rankings_to_new_rankings(rankings: List[List[List[int]]], action: int) -> List[List[List[int]]]:
        res = NONE
        if action == PROJECTION:
            res = Dataset(rankings).get_projected_rankings()
        elif action == UNIFICATION:
            res = Dataset(rankings).get_unified_rankings()
        return res

    normalize_rankings_to_new_rankings = staticmethod(normalize_rankings_to_new_rankings)

    def normalize_rankings_to_new_dataset(cls, rankings: List[List[List[int]]], action: int) -> Dataset:
        return Dataset(cls.normalize_rankings_to_new_rankings(rankings, action))

    normalize_rankings_to_new_dataset = staticmethod(normalize_rankings_to_new_dataset)

    def normalize_dataset_to_new_rankings(dataset: Dataset, action: int) -> List[List[List[int]]]:
        res = NONE
        if action == PROJECTION:
            res = dataset.get_projected_rankings()
        elif action == UNIFICATION:
            res = dataset.get_unified_rankings()
        return res

    normalize_dataset_to_new_rankings = staticmethod(normalize_dataset_to_new_rankings)

    def normalize_dataset_to_new_dataset(cls, dataset: Dataset, action: int) -> Dataset:
        return Dataset(cls.normalize_dataset_to_new_rankings(dataset, action))

    normalize_dataset_to_new_dataset = staticmethod(normalize_dataset_to_new_dataset)

