from django.test.testcases import TestCase

from mediane.process import evaluate_dataset_and_provide_stats


class ElementUnicityTestCase(TestCase):
    def setUp(self):
        self.rankings_str1 = ["r1 := [[A]]", "r2 := [[A], [A]]"]
        self.rankings_str2 = ["r1 := [[A, B]]", "r2 := [[A, B], [B]]"]

    def test_stats(self):
        self.assertEqual(evaluate_dataset_and_provide_stats(self.rankings_str1)['invalid'], True)
        self.assertEqual(evaluate_dataset_and_provide_stats(self.rankings_str2)['invalid'], True)


class ValidRankingsTestCase(TestCase):
    def setUp(self):
        self.rankings_str1 = ["r1 := [[A]]c", "r2 := [[A]]"]
        self.rankings_str2 = ["r1 := [[A,, B]]", "r2 := [[A, B]]"]

    def test_stats(self):
        self.assertEqual(evaluate_dataset_and_provide_stats(self.rankings_str1)['invalid'], True)
        self.assertEqual(evaluate_dataset_and_provide_stats(self.rankings_str2)['invalid'], True)


class CompleteTestCase(TestCase):
    def setUp(self):
        pass

    def test_stats(self):
        pass
