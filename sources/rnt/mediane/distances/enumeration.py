from numpy import matrix

GENERALIZED_KENDALL_TAU_DISTANCE = 1
GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE = 2
PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE = 3
SIMILARITY_MEASURE = 4
__tuple_list = (
    (
        GENERALIZED_KENDALL_TAU_DISTANCE,
        "Generalized Kendall-tau distance",
    ),
    (
        GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
        "Generalized induced Kendall-tau distance"
    ),
    (
        PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
        "Pseudo-metric based on generalized induced kendall tau distance"
    ),
)


def as_tuple_list():
    return __tuple_list


def get_from(id_dist):
    for k, v in __tuple_list:
        if str(k) == str(id_dist):
            return v
    return None


# return a matrix (2,6)
# 1st line are coeffs for cost_before(elem1, elem2)
# 2nd line are coeffs for cost_tied(elem1, elem2)
# column 1 represents nb_rankings with elem1 before elem2
# column 2 represents nb_rankings with elem1 and elem2 are tied
# column 3 represents nb_rankings with elem1 after elem2
# column 4 represents nb_rankings with elem1 and not elem2
# column 5 represents nb_rankings with elem2 and not elem1
# column 6 represents nb_rankings with neither elem1 nor elem2

def get_coeffs_dist(id_dist: int, p: float) -> matrix:
    if id_dist == GENERALIZED_KENDALL_TAU_DISTANCE:
        return matrix([[0., p, 1., 0., 1., p], [p, 0., p, p, p, 0.]])
    elif id_dist == GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE:
        return matrix([[0., p, 1., 0., 0., 0.], [p, 0., p, 0., 0., 0.]])
    elif id_dist == PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE:
        return matrix([[0., p, 1., 0., 1., 0.], [p, 0., p, p, p, 0.]])
    else:
        return matrix([[0., 0., 0., 0., 0., 0.], [0., 0., 0., 0., 0., 0.]])
