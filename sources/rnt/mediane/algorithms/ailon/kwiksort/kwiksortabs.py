from mediane.algorithms.median_ranking import MedianRanking

from typing import List


class KwikSortAbs(MedianRanking):

    def compute_median_rankings(self, rankings: List[List[List[int]]], return_at_most_one_ranking: bool = False)-> \
            List[List[List[int]]]:

        """
        :param rankings: A set of rankings
        :type rankings: list
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :return one or more consensus if the underlying algorithm can find multiple solution as good as each other.
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found
        """
        consensus = []
        elements_translated_target = []
        var = self.prepare_internal_vars(elements_translated_target, rankings)
        self.kwik_sort(consensus, elements_translated_target, var)
        return [consensus]

    def prepare_internal_vars(self, elements_translated_target: List, rankings: List[List[List[int]]]):
        raise NotImplementedError("The method not implemented")
    # protected abstract U prepareInternalVars(
    # List < V > elementsTranslatedTarget, Collection < List < Collection < T >> > rankings);

    def get_pivot(self, elements: List[int], var):
        raise NotImplementedError("The method not implemented")
    # public abstract V getPivot(List < V > elements, U var);

    def where_should_it_be(self, element: int, pivot: int, elements: List[int], var):
        raise NotImplementedError("The method not implemented")
    # public abstract int whereShouldItBe(V element, V pivot, List < V > elements, U var);

    def kwik_sort(self, consensus: List[List[int]], elements: List[int], var):
        pivot = self.get_pivot(elements, var)
        after = []
        before = []
        same = [pivot]
        for element in elements:
            if element != pivot:
                pos = self.where_should_it_be(element, pivot, elements, var)
                if pos < 0:
                    before.append(element)
                elif pos > 0:
                    after.append(element)
                else:
                    same.append(element)

        if len(before) == 1:
            consensus.append(before)
        elif len(before) > 0:
            self.kwik_sort(consensus, before, var)

        consensus.append(same)

        if len(after) == 1:
            consensus.append(after)
        elif len(after) > 0:
            self.kwik_sort(consensus, after, var)

    def is_breaking_ties_arbitrarily(self):
        raise NotImplementedError("The method not implemented")

    def is_using_random_value(self):
        raise NotImplementedError("The method not implemented")

    def get_full_name(self):
        raise NotImplementedError("The method not implemented")

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        raise NotImplementedError("The method not implemented")
