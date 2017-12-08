from django.test import TestCase

from mediane.datasets.dataset import Dataset
from mediane.normalizations.projection import Projection
from mediane.normalizations.unification import Unification


class Tests(TestCase):
    dataset0 = Dataset([[], [], []])

    dataset1 = Dataset([[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

    dataset2 = Dataset([[[1], [2]], [[3], [4]], [[1], [2, 3, 4]]])

    dataset3 = Dataset([[[1], [2, 3, 4], [5]], [[3, 5, 7], [8]], [[3, 2, 4, 5, 7, 9]]])

    dataset4 = Dataset([[[1], [2]], [[3], [4]], [[1], [2, 3, 4]], []])

    dataset5 = Dataset([[[1], [2], [3], [4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]], []])

    dataset6 = Dataset([[[1], [2], [3]], [[2], [3], [1]], [[3], [1], [2]]])

    dataset7 = Dataset([])

    def test_unification(self):

        self.assertEqual(Unification.dataset_to_rankings(self.dataset0), [[], [], []])

        self.assertEqual(Unification.dataset_to_rankings(self.dataset1),
                         [[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

        self.assertEqual(Unification.dataset_to_rankings(self.dataset2),
                         [[[1], [2], [3, 4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]]])

        self.assertEqual(Unification.dataset_to_rankings(self.dataset3),
                         [[[1], [2, 3, 4], [5], [7, 8, 9]], [[3, 5, 7], [8], [1, 2, 4, 9]],
                          [[3, 2, 4, 5, 7, 9], [1, 8]]])

        self.assertEqual(Unification.dataset_to_rankings(self.dataset4),
                         [[[1], [2], [3, 4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]], [[1, 2, 3, 4]]])

    def test_projection(self):

        self.assertEqual(Projection.dataset_to_rankings(self.dataset0), [[], [], []])

        self.assertEqual(Projection.dataset_to_rankings(self.dataset1),
                         [[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

        self.assertEqual(Projection.dataset_to_rankings(self.dataset2), [[], [], []])

        self.assertEqual(Projection.dataset_to_rankings(self.dataset3), [[[3], [5]], [[3, 5]], [[3, 5]]])

        self.assertEqual(Projection.dataset_to_rankings(self.dataset4), [[], [], [], []])

        self.assertEqual(Projection.dataset_to_rankings(self.dataset5), [[], [], [], []])

    def test_completude(self):
        self.assertTrue(self.dataset0.is_complete)
        self.assertTrue(self.dataset1.is_complete)
        self.assertTrue(self.dataset6.is_complete)
        self.assertFalse(self.dataset2.is_complete)
        self.assertFalse(self.dataset3.is_complete)
        self.assertFalse(self.dataset4.is_complete)
        self.assertFalse(self.dataset5.is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset0).is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset1).is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset2).is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset3).is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset4).is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset5).is_complete)
        self.assertTrue(Projection.dataset_to_dataset(self.dataset6).is_complete)

        self.assertTrue(Unification.dataset_to_dataset(self.dataset0).is_complete)
        self.assertTrue(Unification.dataset_to_dataset(self.dataset1).is_complete)
        self.assertTrue(Unification.dataset_to_dataset(self.dataset2).is_complete)
        self.assertTrue(Unification.dataset_to_dataset(self.dataset3).is_complete)
        self.assertTrue(Unification.dataset_to_dataset(self.dataset4).is_complete)
        self.assertTrue(Unification.dataset_to_dataset(self.dataset5).is_complete)
        self.assertTrue(Unification.dataset_to_dataset(self.dataset6).is_complete)

    # Check integrity of original datasets
        self.assertTrue(self.dataset0.is_complete)
        self.assertTrue(self.dataset1.is_complete)
        self.assertTrue(self.dataset6.is_complete)
        self.assertFalse(self.dataset2.is_complete)
        self.assertFalse(self.dataset3.is_complete)
        self.assertFalse(self.dataset4.is_complete)
        self.assertFalse(self.dataset5.is_complete)

    def test_m(self):
        self.assertEqual(self.dataset0.m, 3)
        self.assertEqual(self.dataset1.m, 2)
        self.assertEqual(self.dataset2.m, 3)
        self.assertEqual(self.dataset3.m, 3)
        self.assertEqual(self.dataset4.m, 4)
        self.assertEqual(self.dataset5.m, 4)
        self.assertEqual(self.dataset6.m, 3)
        self.assertEqual(self.dataset7.m, 0)

        self.assertEqual(Unification.dataset_to_dataset(self.dataset0).m, 3)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset1).m, 2)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset2).m, 3)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset3).m, 3)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset4).m, 4)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset5).m, 4)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset6).m, 3)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset7).m, 0)

        self.assertEqual(Projection.dataset_to_dataset(self.dataset0).m, 3)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset1).m, 2)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset2).m, 3)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset3).m, 3)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset4).m, 4)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset5).m, 4)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset6).m, 3)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset7).m, 0)

    def test_n(self):
        self.assertEqual(self.dataset0.n, 0)
        self.assertEqual(self.dataset1.n, 6)
        self.assertEqual(self.dataset2.n, 4)
        self.assertEqual(self.dataset3.n, 8)
        self.assertEqual(self.dataset4.n, 4)
        self.assertEqual(self.dataset5.n, 4)
        self.assertEqual(self.dataset6.n, 3)
        self.assertEqual(self.dataset7.n, 0)

        self.assertEqual(Unification.dataset_to_dataset(self.dataset0).n, 0)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset1).n, 6)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset2).n, 4)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset3).n, 8)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset4).n, 4)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset5).n, 4)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset6).n, 3)
        self.assertEqual(Unification.dataset_to_dataset(self.dataset7).n, 0)

        self.assertEqual(Projection.dataset_to_dataset(self.dataset0).n, 0)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset1).n, 6)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset2).n, 0)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset3).n, 2)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset4).n, 0)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset5).n, 0)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset6).n, 3)
        self.assertEqual(Projection.dataset_to_dataset(self.dataset7).n, 0)
