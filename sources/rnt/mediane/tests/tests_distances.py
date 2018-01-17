from django.test import TestCase

# Create your tests here.
# from mediane.distances.KendallTauGeneralizedNSquare import KendallTauGeneralizedNSquare
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN
from mediane.distances.enumeration import *
from mediane.median_ranking_tools import parse_ranking_with_ties_of_int

p = 0.5


class DistanceTestCase(TestCase):
    def setUp(self):
        pass

    def run_test_on_a_distance(self, dist):

        ranking1 = parse_ranking_with_ties_of_int("[[1,2],[3,4]]")
        ranking2 = parse_ranking_with_ties_of_int("[[1],[2],[3],[4]]")
        ranking3 = parse_ranking_with_ties_of_int("[[2],[1,7],[3],[6]]")
        ranking4 = parse_ranking_with_ties_of_int("[[8,3,11],[1,7],[10],[6]]")
        ranking5 = parse_ranking_with_ties_of_int("[[6],[1,2,5],[7,8,9],[3,4]]")
        ranking6 = parse_ranking_with_ties_of_int("[[1, 3], [2, 4]]")
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

        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 16+4*p)
        self.assertEqual(d[GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE], 2)
        self.assertEqual(d[PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE], 16+2*p)

        d = dist.get_distance_to_an_other_ranking(ranking1=ranking5, ranking2=ranking6)
        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 13+13*p)
        self.assertEqual(d[GENERALIZED_KENDALL_TAU_DISTANCE], 13+13*p)
        self.assertEqual(d[GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE], 1+4*p)
        self.assertEqual(d[PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE], 13+6*p)

    # def test_KendallTauGeneralizedNSquare(self):
    # self.run_test_on_a_distance(KendallTauGeneralizedNSquare())

    def test_KendallTauGeneralizedNlogN(self):
        self.run_test_on_a_distance(KendallTauGeneralizedNlogN(p=p))
