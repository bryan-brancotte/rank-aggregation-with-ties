from typing import Dict, List


class DistanceCalculator:
    def get_distance_to_an_other_ranking(
            self,
            ranking1: List[List[int]],
            ranking2: List[List[int]],
    ) -> Dict[int, float]:
        raise NotImplementedError("The method not implemented")

    def get_distance_to_a_set_of_rankings(
            self,
            c: List[List[int]],
            rankings: List[List[List[int]]],
    ) -> Dict[int, float]:
        raise NotImplementedError("The method not implemented")
