from numpy import ndarray, array
from mediane.distances.enumeration import get_coeffs_dist


class ScoringScheme:

    def __init__(self, matrix=array([[0., 1., 0.5, 0., 1., 0.5], [0., 1., 0.5, 0., 1., 0.5]])):
        self._matrix = matrix

    @property
    def matrix(self):
        return self._matrix

    def __str__(self):
        return str(self._matrix)

    @staticmethod
    def get_scoring_scheme(id_dist: str, p: float):
        return ScoringScheme(get_coeffs_dist(id_dist=id_dist, p=p))
