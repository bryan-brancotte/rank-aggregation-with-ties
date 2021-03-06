from typing import List, Dict, Tuple
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from numpy import ndarray, array, shape, zeros, count_nonzero, vdot, asarray
from operator import itemgetter


class ExactAlgorithm(MedianRanking):
    def __init__(self, limit_time_sec=0, scoring_scheme=None):
        if limit_time_sec > 0:
            self.__limit_time_sec = limit_time_sec
        else:
            self.__limit_time_sec = 0
        self.__scoring_scheme = scoring_scheme

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance,
            return_at_most_one_ranking: bool = False) -> List[List[List[int]]]:
        import cplex
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
        nb_elem = len(elem_id)
        if nb_elem == 0:
            return [[]]

        positions = ExactAlgorithm.__positions(rankings, elem_id)
        if distance is None:
            if self.__scoring_scheme is None:
                scoring_scheme = [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]
            else:
                scoring_scheme = self.__scoring_scheme
        else:
            scoring_scheme = distance.scoring_scheme
        mat_score, ties_must_be_checked = self.__cost_matrix(positions, asarray(scoring_scheme))
        map_elements_cplex = {}
        my_prob = cplex.Cplex()  # initiate
        my_prob.set_results_stream(None)  # mute
        my_prob.parameters.mip.tolerances.mipgap.set(0.0)
        my_prob.parameters.mip.pool.absgap.set(0.0)
        if self.__limit_time_sec > 0:
            my_prob.parameters.tuning.timelimit.set(self.__limit_time_sec)
        my_prob.objective.set_sense(my_prob.objective.sense.minimize)  # we want to minimize the objective function
        if not return_at_most_one_ranking:
            my_prob.parameters.mip.pool.intensity.set(4)
            my_prob.parameters.mip.limits.populate.set(10000000)

        my_obj = []
        my_ub = []
        my_lb = []
        my_names = []

        cpt = 0
        for i in range(nb_elem):
            for j in range(nb_elem):
                if not i == j:
                    s = "x_%s_%s" % (i, j)
                    my_obj.append(mat_score[i][j][0])
                    my_ub.append(1.0)
                    my_lb.append(0.0)
                    my_names.append(s)
                    map_elements_cplex[cpt] = ("x", i, j)
                    cpt += 1
                    # indicator_i.append(i)
                    # indicator_j.append(j)

        for i in range(nb_elem):
            for j in range(i+1, nb_elem):
                s = "t_%s_%s" % (i, j)
                my_obj.append(mat_score[i][j][2])
                my_ub.append(1.0)
                my_lb.append(0.0)
                my_names.append(s)
                map_elements_cplex[cpt] = ("t", i, j)
                cpt += 1
        my_prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types="B"*cpt, names=my_names)

        # rhs = right hand side
        my_rhs = []
        my_rownames = []

        # sens des inequations : E for Equality, G for >=  and L for <=
        my_sense = "E" * int(nb_elem*(nb_elem-1)/2) + "L" * (3*nb_elem * (nb_elem-1) * (nb_elem-2))

        rows = []

        # add the binary order constraints
        count = 0
        for i in range(0, nb_elem - 1):
            for j in range(i + 1, nb_elem):
                if not i == j:
                    s = "c%s" % count
                    count += 1
                    my_rhs.append(1)
                    my_rownames.append(s)
                    first_var = "x_%s_%s" % (i, j)
                    second_var = "x_%s_%s" % (j, i)
                    third_var = "t_%s_%s" % (i, j)

                    row = [[first_var, second_var, third_var], [1.0, 1.0, 1.0]]
                    rows.append(row)
        # add the transitivity constraints
        for i in range(0, nb_elem):
            for j in range(nb_elem):
                if j != i:
                    i_bef_j = "x_%s_%s" % (i, j)
                    if i < j:
                        i_tie_j = "t_%s_%s" % (i, j)
                    else:
                        i_tie_j = "t_%s_%s" % (j, i)
                    for k in range(nb_elem):
                        if k != i and k != j:
                            my_rownames.append("c%s" % count)
                            my_rhs.append(1)
                            count += 1
                            if j < k:
                                j_tie_k = "t_%s_%s" % (j, k)
                            else:
                                j_tie_k = "t_%s_%s" % (k, j)
                            rows.append([[i_bef_j, "x_%s_%s" % (j, k), j_tie_k, "x_%s_%s" % (i, k)], [1., 1., 1., -1.]])

                            my_rownames.append("c%s" % count)
                            my_rhs.append(1)
                            count += 1
                            rows.append([[i_bef_j, i_tie_j, "x_%s_%s" % (j, k), "x_%s_%s" % (i, k)], [1., 1., 1., -1.]])

                            if i < k:
                                i_tie_k = "t_%s_%s" % (i, k)
                            else:
                                i_tie_k = "t_%s_%s" % (k, i)

                            my_rownames.append("c%s" % count)
                            my_rhs.append(3)
                            count += 1
                            rows.append([[i_tie_j, j_tie_k, i_tie_k], [2.0, 2.0, -1.0]])

        # if tie is not the single best choice for any pair x,y, then there is a permutation median
        if not ties_must_be_checked:
            my_sense += "E" * int(nb_elem*(nb_elem-1)/2)
            for i in range(0, nb_elem - 1):
                for j in range(i + 1, nb_elem):
                    if not i == j:
                        s = "c%s" % count
                        count += 1
                        my_rhs.append(0)
                        my_rownames.append(s)
                        row = [["t_%s_%s" % (i, j)], [1]]
                        rows.append(row)

        my_prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs=my_rhs, names=my_rownames)
        medianes = []

        if not return_at_most_one_ranking:
            my_prob.populate_solution_pool()

            nb_optimal_solutions = my_prob.solution.pool.get_num()
            for i in range(nb_optimal_solutions):
                names = my_prob.solution.pool.get_values(i)
                medianes.append(ExactAlgorithm.__create_consensus(nb_elem, names, map_elements_cplex, id_elements))
        else:
            my_prob.solve()
            x = my_prob.solution.get_values()
            medianes.append(ExactAlgorithm.__create_consensus(nb_elem, x, map_elements_cplex, id_elements))

        return medianes

    @staticmethod
    def __create_consensus(nb_elem: int, x: List, map_elements_cplex: Dict, id_elements: Dict):
        ranking = []
        count_after = {}
        for i in range(nb_elem):
            count_after[i] = 0
        for var in range(len(x)):
            if abs(x[var] - 1) < 0.001:
                tple = map_elements_cplex[var]
                if tple[0] == "x":
                    count_after[tple[2]] += 1

        current_nb_def = 0
        bucket = []
        for elem, nb_defeats in (sorted(count_after.items(), key=itemgetter(1))):
            if nb_defeats == current_nb_def:
                bucket.append(id_elements.get(elem))
            else:
                ranking.append(bucket)
                bucket = [id_elements.get(elem)]
                current_nb_def = nb_defeats
        ranking.append(bucket)
        return ranking

    @staticmethod
    def __cost_matrix(positions: ndarray, matrix_scoring_scheme: ndarray) -> Tuple[ndarray, bool]:
        cost_before = matrix_scoring_scheme[0]
        cost_tied = matrix_scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        n = shape(positions)[0]
        m = shape(positions)[1]

        matrix = zeros((n, n, 3))
        ties_must_be_checked = False
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
                if put_tied < put_after and put_tied < put_before:
                    ties_must_be_checked = True

        return matrix, ties_must_be_checked

    @staticmethod
    def __positions(rankings: List[List[List[int]]], elements_id: Dict) -> ndarray:
        positions = zeros((len(elements_id), len(rankings)), dtype=int) - 1
        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def is_breaking_ties_arbitrarily(self):
        return False

    def is_using_random_value(self):
        return False

    def get_full_name(self):
        return "Exact Algorithm"

    def get_handled_distances(self):
        """
        :return: a list of distances from distance_enumeration
        """
        return (
            GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
            PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
        )

    def can_be_executed(self) -> bool:
        try:
            import cplex
            return True
        except ImportError:
            return False
