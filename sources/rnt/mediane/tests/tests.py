from django.test import TestCase

# Create your tests here.
from mediane.algorithms.enumeration import get_median_ranking_algorithms
from mediane.median_ranking_tools import parse_ranking_with_ties, parse_ranking_with_ties_of_str, \
    parse_ranking_with_ties_of_int
from mediane.models import Distance


class RankingParserTestCase(TestCase):
    def setUp(self):
        self.ranking = "[[1,2],[3,4]]"

    def test_parse_ranking_with_ties_to_get_str(self):
        r = parse_ranking_with_ties(
            ranking=self.ranking,
            converter=lambda x: x
        )
        self.assertIsNotNone(r)
        self.assertEqual(r, [['1', '2'], ['3', '4']])
        self.assertEqual(r, parse_ranking_with_ties_of_str(self.ranking))

    def test_parse_ranking_with_ties_to_get_int(self):
        r = parse_ranking_with_ties(
            ranking=self.ranking,
            converter=lambda x: int(x)
        )
        self.assertIsNotNone(r)
        self.assertEqual(r, [[1, 2], [3, 4]])
        self.assertEqual(r, parse_ranking_with_ties_of_int(self.ranking))


class NameAllDifferentTestCase(TestCase):
    def test_names(self):
        names = {}
        for Algo in get_median_ranking_algorithms():
            instance = Algo()
            with self.assertRaises(KeyError):
                trash = names[instance.get_full_name()]
            names[instance.get_full_name()] = instance


class FullyImplementedAlgorithmTestCase(TestCase):
    def test_basically_implemented(self):
        for Algo in get_median_ranking_algorithms():
            instance = Algo()
            self.assertTrue(
                len(instance.get_full_name()) > 0,
                'Algo %s must have a name (get_full_name)' % Algo
            )
            self.assertTrue(
                len(instance.get_handled_distances()) > 0,
                'Algo %s must handle at least one distance' % instance.get_full_name()
            )
            self.assertTrue(
                instance.is_breaking_ties_arbitrarily() or not instance.is_breaking_ties_arbitrarily(),
                'Algo %s must implement is_breaking_ties_arbitrarily' % instance.get_full_name()
            )
            self.assertTrue(
                instance.is_using_random_value() or not instance.is_using_random_value(),
                'Algo %s must implement is_using_random_value' % instance.get_full_name()
            )
            self.assertTrue(
                instance.compute_median_rankings(
                    rankings=[],
                    distance=instance.get_handled_distances()[0],
                ) == [[]],
                'Algo %s must return a array containing an empty consensus' % instance.get_full_name()
            )
            self.assertTrue(
                instance.compute_median_rankings(
                    rankings=[[[1, 2], [3, 4]], [[1, 2], [3, 4]]],
                    distance=instance.get_handled_distances()[0],
                ) is not None,
                'Algo %s must return something and not crash' % instance.get_full_name()
            )

    def test_results_with_dataset(self):
        for Algo in get_median_ranking_algorithms():
            instance = Algo()
            for rankings in (
                    [
                        [[1, 2], [3, 4]], [[1, 2], [3, 4]],
                    ],
                    [
                        [[1, 3], [2, 4], [5]],
                        [[1], [4], [2, 5], [3]],
                        [[2, 4], [3], [1], [5]],
                        [[2], [3], [1, 4, 5]]
                    ],
            ):
                cs = instance.compute_median_rankings(
                    rankings=rankings,
                    distance=instance.get_handled_distances()[0],
                )
                self.assertTrue(
                    isinstance(cs, list),
                    'Algo %s must return an array of consensus, even if not containing any consensus' % instance.get_full_name()
                )
                self.assertTrue(
                    len(cs) > 0,
                    'Algo %s must return at least one consensus' % instance.get_full_name()
                )
                self.assertTrue(
                    isinstance(cs[0], list),
                    'Algo %s must return at least one consensus, here the first thing is not an array=> not a ranking' % instance.get_full_name()
                )
                self.assertTrue(
                    isinstance(cs[0][0], list),
                    'Algo %s must return an array of consensus, here the bucket of the first thing is not an array=> not valid a bucket => not valid a ranking' % instance.get_full_name()
                )
                self.assertTrue(
                    isinstance(cs[0][0][0], int),
                    'Algo %s must return an array of consensus, here the first element of the first bucket of the first ranking is not an integer=> not an element => not valid a bucket => not valid a ranking' % instance.get_full_name()
                )
