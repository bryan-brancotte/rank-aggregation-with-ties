import unittest
from mediane.datasets.datasets import Dataset


class NormalizationsTestCase(unittest.TestCase):
    dataset0 = Dataset([[], [], []])

    dataset1 = Dataset([[[1], [2], [3, 4, 5], [6]],
                        [[1], [2], [3, 4, 5], [6]]])

    dataset2 = Dataset([[[1], [2]],
                        [[3], [4]],
                        [[1], [2, 3, 4]]])

    dataset3 = Dataset([[[1], [2, 3, 4], [5]],
                        [[3, 5, 7], [8]],
                        [[3, 2, 4, 5, 7, 9]]])

    dataset4 = Dataset([[[1], [2]],
                        [[3], [4]],
                        [[1], [2, 3, 4]],
                        []])
    dataset5 = Dataset([[[1], [2], [3], [4]],
                        [[3], [4], [1, 2]],
                        [[1], [2, 3, 4]],
                        []])

    def test_unification(self):

        self.assertEqual(self.dataset0.get_unified_rankings(), [[], [], []])

        self.assertEqual(self.dataset1.get_unified_rankings(),
                         [[[1], [2], [3, 4, 5], [6]],
                          [[1], [2], [3, 4, 5], [6]]]
                         )

        self.assertEqual(self.dataset2.get_unified_rankings(),
                         [[[1], [2], [3, 4]],
                          [[3], [4], [1, 2]],
                          [[1], [2, 3, 4]]]
                         )

        self.assertEqual(self.dataset3.get_unified_rankings(),
                         [[[1], [2, 3, 4], [5], [7, 8, 9]],
                          [[3, 5, 7], [8], [1, 2, 4, 9]],
                          [[3, 2, 4, 5, 7, 9], [1, 8]]]
                         )

        self.assertEqual(self.dataset4.get_unified_rankings(),
                         [[[1], [2], [3, 4]],
                          [[3], [4], [1, 2]],
                          [[1], [2, 3, 4]],
                          [[1, 2, 3, 4]]])
# PROJECTION

        self.assertEqual(self.dataset0.get_projected_rankings(), [[], [], []])

        self.assertEqual(self.dataset1.get_projected_rankings(),
                         [[[1], [2], [3, 4, 5], [6]],
                          [[1], [2], [3, 4, 5], [6]]]
                         )

        self.assertEqual(self.dataset2.get_projected_rankings(),
                         [[], [], []]
                         )

        self.assertEqual(self.dataset3.get_projected_rankings(),
                         [[[3], [5]],
                          [[3, 5]],
                          [[3, 5]]]
                         )

        self.assertEqual(self.dataset5.get_projected_rankings(), [[], [], [], []])


if __name__ == '__main__':
    unittest.main()
