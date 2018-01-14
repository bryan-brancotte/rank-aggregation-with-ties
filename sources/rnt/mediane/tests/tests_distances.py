from django.test import TestCase

# Create your tests here.
# from mediane.distances.KendallTauGeneralizedNSquare import KendallTauGeneralizedNSquare
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN
from mediane.distances.enumeration import *
from mediane.median_ranking_tools import parse_ranking_with_ties_of_int

p = 0.75


class DistanceTestCase(TestCase):
    def setUp(self):
        pass

    def run_test_on_a_distance(self, dist):

        ranking1 = parse_ranking_with_ties_of_int("[[1,2],[3,4]]")
        ranking2 = parse_ranking_with_ties_of_int("[[1],[2],[3],[4]]")
        ranking3 = parse_ranking_with_ties_of_int("[[2],[1,7],[3],[6]]")
        ranking4 = parse_ranking_with_ties_of_int("[[8,3,11],[1,7],[10],[6]]")
        d = dist.get_distance_to_an_other_ranking(
            ranking1=ranking1,
            ranking2=ranking1,
        )
        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 0)
        d = dist.get_distance_to_an_other_ranking(
            ranking1=ranking1,
            ranking2=ranking2,
        )
        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 2*p)

        d = dist.get_distance_to_an_other_ranking(ranking1=ranking3, ranking2=ranking4)

        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 19)
        self.assertEqual(d[GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE], 2)
        self.assertEqual(d[PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE], 17.5)

    # def test_KendallTauGeneralizedNSquare(self):
    # self.run_test_on_a_distance(KendallTauGeneralizedNSquare())

    def test_KendallTauGeneralizedNlogN(self):
        self.run_test_on_a_distance(KendallTauGeneralizedNlogN(p=p))
