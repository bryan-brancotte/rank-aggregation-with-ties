from typing import List
from mediane.datasets.dataset import Dataset


class Normalization:
    def rankings_to_rankings(rankings: List[List[List[int]]]) -> List[List[List[int]]]:
        raise NotImplementedError("The method not implemented")

    def rankings_to_dataset(rankings: List[List[List[int]]]) -> Dataset:
        raise NotImplementedError("The method not implemented")

    def dataset_to_rankings(d: Dataset) -> List[List[List[int]]]:
        raise NotImplementedError("The method not implemented")

    def dataset_to_dataset(d: Dataset) -> Dataset:
        raise NotImplementedError("The method not implemented")

    rankings_to_rankings = staticmethod(rankings_to_rankings)
    rankings_to_dataset = staticmethod(rankings_to_dataset)
    dataset_to_rankings = staticmethod(dataset_to_rankings)
    dataset_to_dataset = staticmethod(dataset_to_dataset)
