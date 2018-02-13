from django.contrib.auth.models import User
from django.test.testcases import TestCase

from mediane.models import DataSet


class StrIsOkTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@toto.re', password='top_secret')
        id = 1
        self.d1 = DataSet.objects.create(name="d%i" % id, step=3, complete=False, content="[[A]]\n[[A]]", owner=self.user)
        id += 1
        self.d2 = DataSet.objects.create(name="d%i" % id, complete=False, content="[[A]]\n[[A]]", owner=self.user)
        id += 1
        self.d3 = DataSet.objects.create(name="d%i" % id, step=56, complete=False, content="[[A]]\n[[A]]\n[[A,B,C,D,E,F]]", owner=self.user)
        id += 1
        self.d4 = DataSet.objects.create(name="d%i" % id, n=1, m=6, complete=False, content="[[A]]\n[[A]]\n[[A]]\n[[A]]\n[[A]]", owner=self.user)
        id += 1
        self.d5 = DataSet.objects.create(name="d%i tralalaëèé" % id, n=122, m=434, step=5623, complete=False, content="[[A]]\n[[A]]\n[[A]]\n[[A]]\n[[A]]",
                               owner=self.user)

    def test_names(self):
        self.assertEqual(str(self.d1), 'd1 (n=1, m=2, step=3)')
        self.assertEqual(str(self.d2), 'd2 (n=1, m=2)')
        self.assertEqual(str(self.d3), 'd3 (n=6, m=3, step=56)')
        self.assertEqual(str(self.d4), 'd4 (n=1, m=5)')
        self.assertEqual(str(self.d5), 'd5 tralalaëèé (n=1, m=5, step=5623)')
