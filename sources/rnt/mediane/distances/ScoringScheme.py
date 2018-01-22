from numpy import ndarray, array
from mediane.distances.enumeration import get_coeffs_dist


class ScoringScheme:

    def __init__(self, mat=array([[0., 1., 0.5, 0., 1., 0.5], [0., 1., 0.5, 0., 1., 0.5]])):
        self.__matrix = mat

    def __get_matrix(self):
        return self.__matrix

    def __set_matrix(self, matrix: ndarray):
        self.__matrix = matrix

    matrix = property(__get_matrix, __set_matrix)

    @staticmethod
    def get_scoring_scheme(id_dist: str, p: float):
        return ScoringScheme(get_coeffs_dist(id_dist=id_dist, p=p))
