from django.test import TestCase

from mediane.datasets.dataset import Dataset
from mediane.normalizations.projection import Projection
from mediane.normalizations.unification import Unification


class Test_general(TestCase):
    dataset0 = Dataset([[], [], []])

    dataset1 = Dataset([[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

    dataset2 = Dataset([[[1], [2]], [[3], [4]], [[1], [2, 3, 4]]])

    dataset3 = Dataset([[[1], [2, 3, 4], [5]], [[3, 5, 7], [8]], [[3, 2, 4, 5, 7, 9]]])

    dataset4 = Dataset([[[1], [2]], [[3], [4]], [[1], [2, 3, 4]], []])

    dataset5 = Dataset([[[1], [2], [3], [4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]], []])

    dataset6 = Dataset([[[1], [2], [3]], [[2], [3], [1]], [[3], [1], [2]]])

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
