import unittest
from mediane.datasets.dataset import Dataset


class NormalizationsTestCase(unittest.TestCase):
    dataset0 = Dataset([[], [], []])

    dataset1 = Dataset([[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

    dataset2 = Dataset([[[1], [2]], [[3], [4]], [[1], [2, 3, 4]]])

    dataset3 = Dataset([[[1], [2, 3, 4], [5]], [[3, 5, 7], [8]], [[3, 2, 4, 5, 7, 9]]])

    dataset4 = Dataset([[[1], [2]], [[3], [4]], [[1], [2, 3, 4]], []])

    dataset5 = Dataset([[[1], [2], [3], [4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]], []])

    dataset6 = Dataset([[[1], [2], [3]], [[2], [3], [1]], [[3], [1], [2]]])

    def test_unification(self):

        self.assertEqual(self.dataset0.get_unified_rankings(), [[], [], []])

        self.assertEqual(self.dataset1.get_unified_rankings(),
                         [[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

        self.assertEqual(self.dataset2.get_unified_rankings(),
                         [[[1], [2], [3, 4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]]])

        self.assertEqual(self.dataset3.get_unified_rankings(),
                         [[[1], [2, 3, 4], [5], [7, 8, 9]], [[3, 5, 7], [8], [1, 2, 4, 9]],
                          [[3, 2, 4, 5, 7, 9], [1, 8]]])

        self.assertEqual(self.dataset4.get_unified_rankings(),
                         [[[1], [2], [3, 4]], [[3], [4], [1, 2]], [[1], [2, 3, 4]], [[1, 2, 3, 4]]])

    def test_projection(self):

        self.assertEqual(self.dataset0.get_projected_rankings(), [[], [], []])

        self.assertEqual(self.dataset1.get_projected_rankings(),
                         [[[1], [2], [3, 4, 5], [6]], [[1], [2], [3, 4, 5], [6]]])

        self.assertEqual(self.dataset2.get_projected_rankings(), [[], [], []])

        self.assertEqual(self.dataset3.get_projected_rankings(), [[[3], [5]], [[3, 5]], [[3, 5]]])

        self.assertEqual(self.dataset5.get_projected_rankings(), [[], [], [], []])

    def test_completude(self):
        self.assertTrue(self.dataset0.is_complete)
        self.assertTrue(self.dataset1.is_complete)
        self.assertTrue(self.dataset6.is_complete)
        self.assertFalse(self.dataset2.is_complete)
        self.assertFalse(self.dataset3.is_complete)
        self.assertFalse(self.dataset4.is_complete)
        self.assertFalse(self.dataset5.is_complete)
        self.assertTrue(Dataset(self.dataset0.get_projected_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset1.get_projected_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset2.get_projected_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset3.get_projected_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset4.get_projected_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset5.get_projected_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset6.get_projected_rankings()).is_complete)

        self.assertTrue(Dataset(self.dataset0.get_unified_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset1.get_unified_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset2.get_unified_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset3.get_unified_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset4.get_unified_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset5.get_unified_rankings()).is_complete)
        self.assertTrue(Dataset(self.dataset0.get_unified_rankings()).is_complete)


if __name__ == '__main__':
    unittest.main()
