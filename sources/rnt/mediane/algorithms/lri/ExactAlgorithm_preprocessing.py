from mediane.algorithms.lri.CondorcetPartitiong import CondorcetPartitioning
from mediane.algorithms.lri.ExactAlgorithm import ExactAlgorithm


class ExactAlgorithmPreprocessing(CondorcetPartitioning):
    def __init__(self):
        super().__init__(ExactAlgorithm())

    def get_full_name(self):
        return "ExactAlgorithm_preprocessing"






