from django.test import TestCase

# Create your tests here.
from mediane import median_ranking_tools


class ParsingTestCase(TestCase):
    def setUp(self):
        self.ranking1 = "[[1,2],[3,4]]"
        self.ranking2 = "[[1,,2],[3,4]]"
        self.ranking3 = "[[1,,2],[3,4]]a"

    def test_str(self):
        self.assertEqual(
            median_ranking_tools.parse_ranking_with_ties_of_str(self.ranking1),
            [["1", "2"], ["3", "4"]],
        )
        with self.assertRaises(ValueError):
            median_ranking_tools.parse_ranking_with_ties_of_str(self.ranking2)
        with self.assertRaises(ValueError):
            median_ranking_tools.parse_ranking_with_ties_of_str(self.ranking3)

    def test_int(self):
        self.assertEqual(
            median_ranking_tools.parse_ranking_with_ties_of_int(self.ranking1),
            [[1, 2], [3, 4]],
        )
        with self.assertRaises(ValueError):
            median_ranking_tools.parse_ranking_with_ties_of_int(self.ranking2)
        with self.assertRaises(ValueError):
            median_ranking_tools.parse_ranking_with_ties_of_int(self.ranking3)
