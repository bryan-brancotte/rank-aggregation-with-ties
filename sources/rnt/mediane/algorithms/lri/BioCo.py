from mediane.algorithms.lri.BioConsert import BioConsert
from mediane.algorithms.misc.borda_count import BordaCount
from mediane.distances.enumeration import GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE


class BioCo(BioConsert):
    def __init__(self):
        super().__init__(starting_algorithms=[BordaCount])

    def get_full_name(self):
        return "BioCo"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
        )
