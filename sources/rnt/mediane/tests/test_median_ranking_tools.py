from django.test import TestCase

# Create your tests here.
from mediane import median_ranking_tools
from mediane.process import evaluate_dataset_and_provide_stats


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


class EvaluateDatasetAndProvideStatsTestCase(TestCase):
    def setUp(self):
        self.rankings_1 = [
            "[[1]]",
            "[[1],[2]]",
        ]
        self.rankings_2 = [
            "[[1,2]]",
            "[[1],[2]]",
        ]
        self.rankings_3 = [
            "[[1]]",
            "[[1],[2]]",
            "[[1],[2],[3]]",
        ]
        self.rankings_4 = [
            "[[1]]a",
            "[[1],[2]]",
        ]
        self.rankings_5 = [
            "[[1]]]",
            "[[1],[2]]",
        ]
        self.rankings_6 = [
            "[[1],[4]]",
            "[[1],[2],[4]]",
            "[[1],[2],[3],[4]]",
        ]
        self.rankings_7 = [
            "[[1],[2]]",
            "[[1]]",
        ]

    def test_1(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_1)
        assert evaluation["n"] == 2
        assert evaluation["m"] == 2
        assert not evaluation["complete"]
        assert not evaluation["invalid"]

    def test_2(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_2)
        assert evaluation["n"] == 2
        assert evaluation["m"] == 2
        assert evaluation["complete"]
        assert not evaluation["invalid"]

    def test_3(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_3)
        assert evaluation["n"] == 3
        assert evaluation["m"] == 3
        assert not evaluation["complete"]
        assert not evaluation["invalid"]

    def test_4(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_4)
        assert  evaluation["invalid"]

    def test_5(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_5)
        assert  evaluation["invalid"]

    def test_6(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_6)
        assert evaluation["n"] == 4
        assert evaluation["m"] == 3
        assert not evaluation["complete"]
        assert not evaluation["invalid"]

    def test_7(self):
        evaluation = evaluate_dataset_and_provide_stats(self.rankings_7)
        assert evaluation["n"] == 2
        assert evaluation["m"] == 2
        assert not evaluation["complete"]
        assert not evaluation["invalid"]