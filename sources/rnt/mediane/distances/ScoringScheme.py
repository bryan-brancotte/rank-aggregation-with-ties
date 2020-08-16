from numpy import array, asarray


class ScoringScheme:

    def __init__(self, matrix=array([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])):
        self._matrix = matrix

    @property
    def matrix(self):
        return self._matrix

    def __str__(self):
        return str(self._matrix)

    @staticmethod
    def get_pseudodistance_scoring_scheme():
        return ScoringScheme(matrix=asarray([[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]))

    @staticmethod
    def get_unifying_distance_scoring_scheme():
        return ScoringScheme(matrix=asarray([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]]))

    @staticmethod
    def get_induced_measure_scoring_scheme():
        return ScoringScheme(matrix=asarray([[0., 1., 1., 0., 0., 0.], [1., 1., 0., 0., 0., 0.]]))

    @staticmethod
    def get_default():
        return ScoringScheme.get_pseudodistance_scoring_scheme()

    @staticmethod
    def get_scoring_scheme_when_no_distance():
        return ScoringScheme(matrix=asarray([[0., 1., 1., 0., 0.2, 0.], [1., 1., 0., 0.2, 0.2, 0.]]))
