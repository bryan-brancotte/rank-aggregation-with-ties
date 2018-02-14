from mediane.algorithms.lri.CondorcetPartitiong import CondorcetPartitioning
from mediane.algorithms.lri.ExactAlgorithm import ExactAlgorithm
from mediane.distances.ScoringScheme import ScoringScheme


class ExactAlgorithmPreprocessing(CondorcetPartitioning):
    def __init__(self, scoring_scheme=ScoringScheme()):
        super().__init__(scoring_scheme=scoring_scheme, algorithm_to_complete=ExactAlgorithm(scoring_scheme=
                                                                                             scoring_scheme))

    def get_full_name(self):
        return "ExactAlgorithm_preprocessing"
