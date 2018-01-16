from mediane.algorithms.lri.BioConsert import BioConsert
from mediane.algorithms.misc.borda_count import BordaCount
from mediane.distances.ScoringScheme import ScoringScheme


class BioCo(BioConsert):
    def __init__(self, scoring_scheme=ScoringScheme()):
        super().__init__(BioConsert(scoring_scheme=scoring_scheme, starting_algorithms=[BordaCount]))

    def get_full_name(self):
        return "BioCo"
