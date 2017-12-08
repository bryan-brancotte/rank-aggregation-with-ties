from typing import List

from mediane.normalizations.normalize import Normalization


class Projection(Normalization):

    def rankings_to_normalized_rankings(rankings: List[List[List[int]]]) -> List[List[List[int]]]:
        elements = {}
        projected_rankings = []
        m = len(rankings)
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element in elements:
                        elements[element] += 1
                    else:
                        elements[element] = 0

        for ranking in rankings:
            new_ranking = []
            projected_rankings.append(new_ranking)
            for bucket in ranking:
                new_bucket = []
                for element in bucket:
                    if elements[element] == m:
                        new_bucket.append(element)
                if len(new_bucket) > 0:
                    new_ranking.append(new_bucket)

        return projected_rankings

    rankings_to_normalized_rankings = staticmethod(rankings_to_normalized_rankings)
