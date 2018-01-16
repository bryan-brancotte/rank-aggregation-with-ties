from numpy import ndarray


class ScoringScheme:

    def __init__(self, matrix=ndarray([[0., 1., 0.5, 0., 1., 0.5], [0.5, 0.5, 0., 0.5, 0.5, 0.]])):
        self.__matrix = matrix

    def get_matrix(self):
        return self.__matrix

    def __get_matrix(self):
        return self.__matrix

    def __set_matrix(self, matrix: ndarray):
        self.__matrix = matrix

    matrix = property(__get_matrix, __set_matrix)
