from numpy import array


class ScoringScheme:

    def __init__(self, matrix=array([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])):
        self._matrix = matrix

    @property
    def matrix(self):
        return self._matrix

    def __str__(self):
        return str(self._matrix)

