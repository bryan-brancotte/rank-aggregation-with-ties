from django.utils.translation import ugettext_lazy as _

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
