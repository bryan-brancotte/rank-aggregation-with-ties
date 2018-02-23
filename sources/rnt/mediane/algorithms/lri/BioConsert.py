from typing import List, Dict
import collections
from mediane.algorithms.median_ranking import MedianRanking, DistanceNotHandledException
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
from numpy import zeros, count_nonzero, vdot, array, ndarray, shape, amax, where, nditer, argmax, sum as np_sum, \
    cumsum, asarray


class BioConsert(MedianRanking):
    def __init__(self, starting_algorithms=None):
        is_valid = True
        if isinstance(starting_algorithms, collections.Iterable):
            for obj in starting_algorithms:
                if not isinstance(obj, MedianRanking):
                    is_valid = False
            if is_valid:
                self.starting_algorithms = starting_algorithms
            else:
                self.starting_algorithms = []
        else:
            self.starting_algorithms = []

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance,
            return_at_most_one_ranking: bool = False) -> List[List[List[int]]]:
        """
        :param rankings: A set of rankings
        :type rankings: list
        :param distance: The distance to use/consider
        :type distance: Distance
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :return one or more consensus if the underlying algorithm can find multiple solution as good as each other.
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found
        :raise DistanceNotHandledException when the algorithm cannot compute the consensus following the distance given
        as parameter
        """
        scoring_scheme = asarray(distance.scoring_scheme)
        if scoring_scheme[1][0] != scoring_scheme[1][1] or scoring_scheme[1][3] != scoring_scheme[1][4]:
            raise DistanceNotHandledException
        res = []
        # kem = KemenyComputingFactory(scoring_scheme=self.scoring_scheme)
        # kem = KendallTauGeneralizedNlogN()
        elem_id = {}
        id_elements = {}
        id_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1
        nb_elements = len(elem_id)

        if nb_elements == 0:
            return [[]]

        departure = self.__departure_rankings(rankings, elem_id)

        if len(self.starting_algorithms) == 0:
            matrix = self.__cost_matrix(departure[:, :-1], distance)
        else:
            matrix = self.__cost_matrix(departure, distance)

        result = set()
        dst_min = float('inf')

        memoi = set()
        id_ranking = 0

        while id_ranking < len(rankings) + 1:
            ranking_array = departure[:, id_ranking]
            ranking_string = str(ranking_array)
            if ranking_string not in memoi:
                memoi.add(ranking_string)
                # dst_init = kem.get_distance_to_a_set_of_rankings(ranking, rankings)
                dst_ranking = self.__bio_consert(ranking_array, matrix, memoi)
                # print("STOP  DST = ", dst_ranking)

                if dst_ranking <= dst_min:
                    if dst_ranking < dst_min or return_at_most_one_ranking:
                        result.clear()
                    result.add(id_ranking)
                    dst_min = dst_ranking
            id_ranking += 1

        ranking_dict = {}

        for id_ranking in result:
            to_be_translated = departure[:, id_ranking]
            ranking_dict.clear()
            el = 0
            for id_bucket_arr in nditer(to_be_translated):
                id_bucket = id_bucket_arr.item()
                if id_bucket not in ranking_dict:
                    ranking_dict[id_bucket] = [id_elements.get(el)]
                else:
                    ranking_dict[id_bucket].append(id_elements.get(el))
                el += 1

            ranking_list = []
            nb_buckets_ranking_i = len(ranking_dict)
            for id_bucket in range(nb_buckets_ranking_i):
                ranking_list.append(ranking_dict.get(id_bucket))
            res.append(ranking_list)

        return res

    @staticmethod
    def __bio_consert(ranking: ndarray, matrix: ndarray, memoi: set) -> float:

        sum_before = 0.0
        sum_tied = 0.0

        el = 0
        for id_buck_arr in nditer(ranking):
            mat = matrix[el]
            # print("mat = ", mat)
            id_buck = id_buck_arr.item()
            sum_before += np_sum(mat[where(ranking < id_buck)[0]][:, 1])
            sum_tied += np_sum(mat[where(ranking == id_buck)[0]][:, 2])
            el += 1
        n = ranking.size
        max_id_bucket = amax(ranking)
        if count_nonzero(ranking < 0) > 0:
            max_id_bucket += 1
            ranking[ranking < 0] = max_id_bucket

        improvement = True
        dst = sum_before + sum_tied / 2
        while improvement:
            improvement = False
            for element in range(n):
                cha = zeros(max_id_bucket + 2, dtype=float)
                add = zeros(max_id_bucket + 3, dtype=float)

                bucket_elem = ranking[element]
                alone = BioConsert._compute_delta_costs(ranking, element, matrix, max_id_bucket, cha, add)
                to, diff = BioConsert._search_to_change_bucket(bucket_elem, cha, max_id_bucket)
                if to >= 0:
                    improvement = True
                    # change
                    dst += diff
                    BioConsert._change_bucket(ranking, element, bucket_elem, to, alone)
                    if alone:
                        max_id_bucket -= 1
                    st = str(ranking)
                    if st in memoi:
                        return float('inf')
                    memoi.add(st)
                else:
                    to, diff = BioConsert._search_to_add_bucket(bucket_elem, add, max_id_bucket)
                    if to >= 0:

                        improvement = True
                        dst += diff

                        BioConsert._add_bucket(ranking, element, bucket_elem, to, alone)
                        if not alone:
                            max_id_bucket += 1
                        st = str(ranking)
                        if st in memoi:
                            return float('inf')
                        memoi.add(st)
        return dst

    @staticmethod
    def _compute_delta_costs(
            ranking: ndarray,
            element: int, matrix:
            ndarray, max_id_bucket: int,
            delta_change: ndarray,
            delta_add: ndarray) -> bool:
        costs = matrix[element]
        id_bucket_element = ranking[element]

        for el in nditer(where(ranking < id_bucket_element)[0], ['zerosize_ok']):
            el_int = el.item()
            bucket = ranking[el_int]

            delta_change[bucket] += costs[el_int][2] - costs[el_int][1]
            delta_change[bucket - 1] += costs[el_int][0] - costs[el_int][2]

            delta_add[bucket] += costs[el_int][0] - costs[el_int][1]

        same = where(ranking == id_bucket_element)[0]

        leave_bucket = np_sum(costs[same], axis=0)

        for el in nditer(where(ranking > id_bucket_element)[0], ['zerosize_ok']):
            el_int = el.item()
            bucket = ranking[el_int]

            delta_change[bucket] += costs[el_int][2] - costs[el_int][0]
            delta_change[bucket + 1] += costs[el_int][1] - costs[el_int][2]

            delta_add[bucket + 1] += costs[el_int][1] - costs[el_int][0]

        delta_change[id_bucket_element - 1] += leave_bucket[0] - leave_bucket[2]
        delta_change[id_bucket_element + 1] += leave_bucket[1] - leave_bucket[2]

        delta_add[id_bucket_element] += leave_bucket[0] - leave_bucket[2]
        delta_add[id_bucket_element + 1] += leave_bucket[1] - leave_bucket[2]

        # BE CAREFUL, index < current bucket are inverted !!!!
        delta_change[0:id_bucket_element] = cumsum(delta_change[0:id_bucket_element][::-1])
        delta_change[id_bucket_element:max_id_bucket+1] = cumsum(delta_change[id_bucket_element:max_id_bucket+1])

        delta_add[0:id_bucket_element+1] = cumsum(delta_add[0:id_bucket_element+1][::-1])
        delta_add[id_bucket_element+1:max_id_bucket+2] = cumsum(delta_add[id_bucket_element+1:max_id_bucket+2])

        delta_change[-1] = -1
        delta_add[-1] = -1

        return same.shape[0] == 1

    @staticmethod
    def _search_to_change_bucket(buck_elem: int, change_costs: ndarray, max_id_bucket: int) -> tuple:
        """
        :param buck_elem: the id of the bucket where the current elem is
        :type buck_elem: int
        :param change_costs: The difference of cost for each bucket change of elem
        :type change_costs: ndarray
        :param max_id_bucket: the max of id buckets
        :type max_id_bucket: int
        :return the id of the future bucket of current element if a change can decrease the score, -1 otherwise
        and the diff of score as 2nd parameter
        """
        # first, search at the right of the current position : the 1s position with negative value
        arrival = argmax(change_costs[buck_elem:] < 0).item() + buck_elem
        # if arrival is within [current position, max_id_bucket] : elment will change bucket
        if arrival <= max_id_bucket:
            # print("DIFF ", change_costs[arrival])

            return arrival, change_costs[arrival]
        # if no change at right can be done : check left values
        arrival = argmax(change_costs[:buck_elem+1] < 0).item()
        if arrival > 0 or change_costs[arrival] < 0:
            return buck_elem - arrival - 1, change_costs[arrival]
        return -1, 0.0

    @staticmethod
    def _change_bucket(ranking: ndarray, element: int, old_pos: int, new_pos: int, alone_in_old_bucket: bool):

        """
        :param ranking: the current ranking in array version
        :type ranking: ndarray
        :param element: the element to move
        :type element: int
        :param old_pos : the old positon of the element to move
        :type old_pos: int
        :param new_pos : the new positon of the element to move
        :type new_pos: int
        :param alone_in_old_bucket : is element elone in its current bucket
        :type old_pos: bool
        """
        ranking[element] = new_pos
        if alone_in_old_bucket:
            ranking[ranking > old_pos] -= 1

    @staticmethod
    def _search_to_add_bucket(buck_elem: int, add_costs: ndarray, max_id_bucket: int) -> tuple:
        """
        :param buck_elem: the id of the bucket where the current elem is
        :type buck_elem: int
        :param add_costs: The difference of cost for each bucket add for elem
        :type add_costs: ndarray
        :param max_id_bucket: the max of id buckets
        :type max_id_bucket: int
        :return the future position of the element if a change can decrease the score, -1 otherwise and the diff of
        score as 2nd parameter
        """
        new_pos = argmax(add_costs[buck_elem+1:] < 0).item() + buck_elem + 1
        if new_pos <= max_id_bucket + 1:
            return new_pos, add_costs[new_pos]
        new_pos = argmax(add_costs[0:buck_elem+1] < 0).item()
        if new_pos > 0 or add_costs[0] < 0:
            return buck_elem - new_pos, add_costs[new_pos]
        return -1, 0.0

    @staticmethod
    def _add_bucket(ranking: ndarray, element: int, old_pos: int, new_pos: int, alone_in_old_bucket: bool):

        """
        :param ranking: the current ranking in array version
        :type ranking: ndarray
        :param element: the element to move
        :type element: int
        :param old_pos : the old positon of the element to move
        :type old_pos: int
        :param new_pos : the id of the bucket beside which the element will be put
        :type new_pos: int
        :param alone_in_old_bucket : is element elone in its current bucket
        :type old_pos: bool
        """
        if old_pos < new_pos:
            if alone_in_old_bucket:
                ranking[(ranking > old_pos) & (ranking < new_pos)] -= 1
                ranking[element] = new_pos - 1
            else:
                ranking[ranking >= new_pos] += 1
                ranking[element] = new_pos

        else:
            if alone_in_old_bucket:
                ranking[(ranking >= new_pos) & (ranking < old_pos)] += 1
                ranking[element] = new_pos

            else:
                ranking[ranking >= new_pos] += 1
                ranking[element] = new_pos

    def __departure_rankings(self, rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
        if len(self.starting_algorithms) == 0:
            m = len(rankings)
            n = len(elements_id)
            departure = zeros((n, m+1), dtype=int) - 1
            id_ranking = 0
            for ranking in rankings:
                id_bucket = 0
                for bucket in ranking:
                    for element in bucket:
                        departure[elements_id.get(element)][id_ranking] = id_bucket
                    id_bucket += 1
                id_ranking += 1
            departure[:, -1] = zeros(n)
        else:
            m = len(self.starting_algorithms)
            n = len(elements_id)
            departure = zeros((n, m))
            id_ranking = 0
            for algo in self.starting_algorithms:
                id_bucket = 0
                for bucket in algo.compute_median_rankings(rankings, True)[0]:
                    for element in bucket:
                        departure[elements_id.get(element)][id_ranking] = id_bucket
                    id_bucket += 1
                id_ranking += 1
        return departure

    @staticmethod
    def __cost_matrix(positions: ndarray, distance) -> ndarray:
        matrix_scoring_scheme = distance.scoring_scheme
        cost_before = matrix_scoring_scheme[0]
        cost_tied = matrix_scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        n = shape(positions)[0]
        m = shape(positions)[1]
        matrix = zeros((n, n, 3))

        for e1 in range(n):
            mem = positions[e1]
            d = count_nonzero(mem == -1)
            for e2 in range(e1 + 1, n):
                a = count_nonzero(mem + positions[e2] == -2)
                b = count_nonzero(mem == positions[e2])
                c = count_nonzero(positions[e2] == -1)
                e = count_nonzero(mem < positions[e2])
                relative_positions = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])
                put_before = vdot(relative_positions, cost_before)
                put_after = vdot(relative_positions, cost_after)
                put_tied = vdot(relative_positions, cost_tied)
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]
        return matrix

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "BioConsert"

    def get_handled_distances(self):
        """

        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE,
            GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
        )
