from typing import List, Dict
from mediane.algorithms.median_ranking import MedianRanking
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE, GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE, \
    PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE
from numpy import ndarray, array, shape, zeros, count_nonzero, vdot, asarray
from operator import itemgetter


class ExactAlgorithm(MedianRanking):

    def compute_median_rankings(
            self,
            rankings: List[List[List[int]]],
            distance,
            return_at_most_one_ranking: bool = False)-> List[List[List[int]]]:
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
        res = []
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

        positions = ExactAlgorithm.__positions(rankings, elem_id)
        if distance is None:
            scoring_scheme = [[0, 1.0, 1.0, 0, 0, 0], [[1.0, 1.0, 0, 0, 0, 0]]]
        else:
            scoring_scheme = distance.scoring_scheme
        mat_score = self.__cost_matrix(positions, asarray(scoring_scheme))

        # DEBUT ROBIN
        map_elements_cplex = {}
        my_prob = cplex.Cplex()  # initiate
        my_prob.parameters.threads.set(1)
        my_prob.set_results_stream(None)  # mute
        my_prob.parameters.mip.tolerances.mipgap.set(0.0)

        my_prob.objective.set_sense(my_prob.objective.sense.minimize)  # we want to minimize the objective function

        # indicator_i = []
        # indicator_j = []

        my_obj = []
        my_ub = []
        my_lb = []
        my_ctype = ""
        my_names = []

        cpt = 0
        # add all the variables, their bounds and the objective function
        for i in range(nb_elements):
            for j in range(nb_elements):
                if not i == j:
                    s = "x_%s_%s" % (i, j)
                    my_obj.append(mat_score[i][j][0])
                    my_ub.append(1.0)
                    my_lb.append(0.0)
                    my_ctype += "B"
                    my_names.append(s)
                    map_elements_cplex[cpt] = ("x", i, j)
                    cpt += 1
                    # indicator_i.append(i)
                    # indicator_j.append(j)

        for i in range(nb_elements):
            for j in range(i+1, nb_elements):
                s = "t_%s_%s" % (i, j)
                my_obj.append(mat_score[i][j][2])
                my_ub.append(1.0)
                my_lb.append(0.0)
                my_ctype += "B"
                my_names.append(s)
                map_elements_cplex[cpt] = ("t", i, j)
                cpt += 1

        my_prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype, names=my_names)

        # rhs = right hand side
        my_rhs = []
        my_rownames = []

        # sens des inequations : E for Equality, G for >=  and L for <=
        my_sense = ""

        #
        rows = []

        # add the binary order constraints
        count = 0
        for i in range(0, nb_elements - 1):
            for j in range(i + 1, nb_elements):
                if not i == j:
                    my_rhs.append(1)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    # sens : egalite
                    my_sense += "E"
                    first_var = "x_%s_%s" % (i, j)
                    second_var = "x_%s_%s" % (j, i)
                    third_var = "t_%s_%s" % (i, j)

                    row = [[first_var, second_var, third_var], [1.0, 1.0, 1.0]]
                    rows.append(row)

        # add the transitivity constraints
        for i in range(0, nb_elements):
            for j in range(i+1, nb_elements):
                for k in range(j+1, nb_elements):
                    my_rhs.append(2)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (j, i)
                    second_var = "x_%s_%s" % (k, j)
                    third_var = "x_%s_%s" % (i, k)
                    row = [[first_var, second_var, third_var], [1.0, 1.0, 1.0]]
                    rows.append(row)

                    my_rhs.append(2)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (i, j)
                    second_var = "x_%s_%s" % (j, k)
                    third_var = "x_%s_%s" % (k, i)
                    row = [[first_var, second_var, third_var], [1.0, 1.0, 1.0]]
                    rows.append(row)

                    # i with j and j with k -> i with k
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "t_%s_%s" % (i, j)
                    second_var = "t_%s_%s" % (j, k)
                    third_var = "t_%s_%s" % (i, k)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "t_%s_%s" % (i, k)
                    second_var = "t_%s_%s" % (j, k)
                    third_var = "t_%s_%s" % (i, j)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "t_%s_%s" % (i, j)
                    second_var = "t_%s_%s" % (i, k)
                    third_var = "t_%s_%s" % (j, k)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 1
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (i, j)
                    second_var = "t_%s_%s" % (j, k)
                    third_var = "x_%s_%s" % (i, k)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 2
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (i, k)
                    second_var = "t_%s_%s" % (j, k)
                    third_var = "x_%s_%s" % (i, j)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 3
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (j, i)
                    second_var = "t_%s_%s" % (i, k)
                    third_var = "x_%s_%s" % (j, k)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 4
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (j, k)
                    second_var = "t_%s_%s" % (i, k)
                    third_var = "x_%s_%s" % (j, i)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 5
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (k, i)
                    second_var = "t_%s_%s" % (i, j)
                    third_var = "x_%s_%s" % (k, j)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 6
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (k, j)
                    second_var = "t_%s_%s" % (i, j)
                    third_var = "x_%s_%s" % (k, i)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 7
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (j, i)
                    second_var = "t_%s_%s" % (j, k)
                    third_var = "x_%s_%s" % (k, i)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 8
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (k, i)
                    second_var = "t_%s_%s" % (j, k)
                    third_var = "x_%s_%s" % (j, i)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 9
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (i, j)
                    second_var = "t_%s_%s" % (i, k)
                    third_var = "x_%s_%s" % (k, j)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 10
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (k, j)
                    second_var = "t_%s_%s" % (i, k)
                    third_var = "x_%s_%s" % (i, j)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 11
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (i, k)
                    second_var = "t_%s_%s" % (i, j)
                    third_var = "x_%s_%s" % (j, k)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

                    # 12
                    my_rhs.append(3)
                    s = "c%s" % count
                    count += 1
                    my_rownames.append(s)
                    my_sense += "L"
                    first_var = "x_%s_%s" % (j, k)
                    second_var = "t_%s_%s" % (i, j)
                    third_var = "x_%s_%s" % (i, k)
                    row = [[first_var, second_var, third_var], [2.0, 2.0, -1.0]]
                    rows.append(row)

        my_prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs=my_rhs, names=my_rownames)

        # my_prob.write("/home/pierre/Bureau/cplex_test.lp")

        # start = my_prob.get_dettime()
        my_prob.solve()  # solve
        # end = my_prob.get_dettime()
        # elapsed = end - start
        # print(" elapsed det time: %s" % elapsed)

        # print(" Solution value  = %s" % my_prob.solution.get_objective_value())  # print optimal value

        # retrieving solution
        # numcol = nb of variables for cplex
        numcols = my_prob.variables.get_num()

        # x = vector of solutions
        x = my_prob.solution.get_values()

        count_after = {}
        for i in range(nb_elements):
            count_after[i] = 0

        for var in range(numcols):
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
                res.append(bucket)
                bucket = [id_elements.get(elem)]
                current_nb_def = nb_defeats

        res.append(bucket)
        return [res]

    @staticmethod
    def __cost_matrix(positions: ndarray, matrix_scoring_scheme: ndarray) -> ndarray:
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
