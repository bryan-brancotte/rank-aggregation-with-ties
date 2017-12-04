GENERALIZED_KENDALL_TAU_DISTANCE = 1
GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE = 2
PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE = 3
SIMILARITY_MEASURE = 4
__tuple_list = (
    (
        GENERALIZED_KENDALL_TAU_DISTANCE,
        "Generalized Kendall-tau distance"
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
