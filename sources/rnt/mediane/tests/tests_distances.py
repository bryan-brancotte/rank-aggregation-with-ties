from django.test import TestCase

# Create your tests here.
from mediane.distances.KendallTauGeneralizedNSquare import KendallTauGeneralizedNSquare
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE
from mediane.median_ranking_tools import parse_ranking_with_ties_of_int


class DistanceTestCase(TestCase):
    def setUp(self):
        pass

    def run_test_on_a_distance(self, dist):
        ranking1 = parse_ranking_with_ties_of_int("[[1,2],[3,4]]")
        ranking2 = parse_ranking_with_ties_of_int("[[1],[2],[3],[4]]")
        d = dist.get_distance_to_an_other_ranking(
            ranking1=ranking1,
            ranking2=ranking1,
        )
        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 0)
        d = dist.get_distance_to_an_other_ranking(
            ranking1=ranking1,
            ranking2=ranking2,
        )
        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 2)

    def test_KendallTauGeneralizedNSquare(self):
        self.run_test_on_a_distance(KendallTauGeneralizedNSquare())
