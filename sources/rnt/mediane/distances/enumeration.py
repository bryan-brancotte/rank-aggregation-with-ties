from django.utils.translation import ugettext_lazy as _
from numpy import ndarray, array

GENERALIZED_KENDALL_TAU_DISTANCE = 'KTG'
GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE = 'KTGI'
PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE = 'PSEUDO_METRIC_KTGI'
GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION = 'KTGU'
SIMILARITY_MEASURE = 'SIM_MEASURE_BRYAN'
__tuple_list = (
    (
        GENERALIZED_KENDALL_TAU_DISTANCE,
        _(GENERALIZED_KENDALL_TAU_DISTANCE + "_name"),
    ),
    (
        GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
        _(GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE + "_name"),
    ),
    (
        PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE,
        _(PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE + "_name"),
    ),
    (
        GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION,
        _(GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION + "_name"),
    ),
)


def as_tuple_list():
    return __tuple_list


def get_from(id_dist):
    for k, v in __tuple_list:
        if str(k) == str(id_dist):
            return v
    return None


def __dummy_method_to_have_translations():
    _('KTG_name')
    _('KTGI_name')
    _('PSEUDO_METRIC_KTGI_name')
    _('KTG_desc')
    _('KTGI_desc')
    _('PSEUDO_METRIC_KTGI_desc')
    _('KTGU_name')
    _('KTGU_desc')


# return a matrix (2,6)
# 1st line are coeffs for cost_before(elem1, elem2)
# 2nd line are coeffs for cost_tied(elem1, elem2)
# column 1 represents nb_rankings with elem1 before elem2
# column 2 represents nb_rankings with elem1 and elem2 are tied
# column 3 represents nb_rankings with elem1 after elem2
# column 4 represents nb_rankings with elem1 and not elem2
# column 5 represents nb_rankings with elem2 and not elem1
# column 6 represents nb_rankings with neither elem1 nor elem2

def get_coeffs_dist(id_dist: str, p: float) -> ndarray:
    upper = id_dist.upper()
    if upper == GENERALIZED_KENDALL_TAU_DISTANCE:
        return array([[0., 1.0, p, 0., 1., p], [p, p, 0., p, p, 0.]])
    elif upper == GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE:
        return array([[0., 1., p, 0., 0., 0.], [p, p, 0, 0., 0., 0.]])
    elif upper == PSEUDO_METRIC_BASED_ON_GENERALIZED_INDUCED_KENDALL_TAU_DISTANCE:
        return array([[0., 1., p, 0., 1., 0.], [p, p, 0, p, p, 0.]])
    else:
        return array([[0., 0., 0., 0., 0., 0.], [0., 0., 0., 0., 0., 0.]])
