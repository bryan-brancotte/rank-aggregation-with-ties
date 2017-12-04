from typing import Dict, List

from mediane.distances.distance_calculator import DistanceCalculator
from mediane.distances.enumeration import SIMILARITY_MEASURE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    GENERALIZED_KENDALL_TAU_DISTANCE


class KendallTauGeneralizedNSquare(DistanceCalculator):
    def get_distance_to_an_other_ranking(
            self,
            ranking1: List[List[int]],
            ranking2: List[List[int]],
    ) -> Dict[int, float]:
        # Map<T, int[]> rankElt = new HashMap<T, int[]>();
        sng = lambda x: 1 if x > 0 else -1 if x < 0 else 0
        rank_elt = {}
        level = 0
        dst = 0
        dstP = 0
        dstQ = 0
        agree = 0
        for bucket in ranking1:
            for elt in bucket:
                rank_elt[elt] = [level, -1]
            level += 1

        level = 0
        for bucket in ranking2:
            for elt in bucket:
                try:
                    lvl = rank_elt[elt]
                    lvl[1] = level
                except KeyError:
                    lvl = [-1, level]
                    rank_elt[elt] = lvl
            level += 1

        # List<Entry<T, int[]>> elements = new Vector<Entry<T, int[]>>(rankElt.entrySet());
        # rankElt.entrySet();
        items = [(k, v) for k, v in rank_elt.items()]
        for a in range(len(items) - 1, 0, -1):
            # for (int a = elements.size() - 1; a > 0; a--) {
            #     // int[] posA = elements.get(a);
            eltA, lvlA = items[a]
            # Entry<T, int[]> posA = elements.get(a);
            if lvlA[0] != -1 and lvlA[1] != -1:
                # if (posA.getValue()[0] != -1 && posA.getValue()[1] != -1) {
                for b in range(a - 1, 0, -1):
                    # for (int b = a - 1; b >= 0; b--) {
                    #     // int[] posB = elements.get(a);
                    #     Entry<T, int[]> posB = elements.get(b);
                    eltB, lvlB = items[b]
                    if lvlB[0] != -1 and lvlB[1] != -1:
                        # if (posB.getValue()[0] != -1 && posB.getValue()[1] != -1) {
                        sngR1 = sng(lvlA[0] - lvlB[0])
                        sngR2 = sng(lvlA[1] - lvlB[1])
                        # int sngR2 = Integer.signum(posA.getValue()[1] - posB.getValue()[1]);
                        if sngR1 != sngR2:
                            if sngR1 == 0:
                                dstQ += 1
                            elif sngR2 == 0:
                                dstP += 1
                            else:
                                dst += 1
                        else:
                            agree += 1
        ktg = dst + dstP + dstQ
        return {
            GENERALIZED_KENDALL_TAU_DISTANCE: ktg,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE: ktg,
            SIMILARITY_MEASURE: None if agree + ktg == 0 else (agree - ktg) / (agree + ktg),
        }

    def get_distance_to_a_set_of_rankings(
            self,
            c: List[List[int]],
            rankings: List[List[List[int]]],
    ) -> Dict[int, float]:
        ktg = 0
        ktg_i = 0
        for r in rankings:
            distance_values = self.get_distance_to_an_other_ranking(c, r)
            ktg += distance_values[GENERALIZED_KENDALL_TAU_DISTANCE]
            ktg_i += distance_values[GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE]

        return {
            GENERALIZED_KENDALL_TAU_DISTANCE: ktg,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE: ktg_i,
        }
